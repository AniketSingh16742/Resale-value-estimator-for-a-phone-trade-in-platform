# 📱 Resale-value estimator for a phone trade-in platform

Predicts the resale value of a used smartphone/tablet based on its specs, age, and physical condition — built end-to-end from raw data to a deployed web app.

**Live demo:** https://resale-estimator-frontend.onrender.com
**Note:** hosted on Render's free tier — the first request after a period of inactivity may take 30-60 seconds while the service spins back up.

---

## The problem

Existing "used phone price" datasets predict a device's price from its specs alone — but real resale platforms (Cashify, OLX, etc.) price primarily on **condition and functionality**, not just RAM and camera megapixels. This project reframes the problem: instead of predicting a flat price, it predicts **how much value a device retains** given its age, specs, and condition — then applies that retention rate to a real starting price to produce a usable ₹ estimate.

## Dataset

[Used Phones & Tablets Pricing Dataset](https://www.kaggle.com/datasets/ahsan81/used-handheld-device-data) (Kaggle) — ~3,450 rows of used device listings with brand, OS, screen size, RAM, storage, cameras, battery, release year, days used, and normalized new/used prices.

**Two things about this dataset required extra investigation before modeling could start:**

1. **The price columns were normalized with an undisclosed formula.** Empirical testing (checking the value range against plausible real-world prices) confirmed it was a natural log transform, not min-max or z-score scaling. This meant the target had to be reconstructed correctly: `depreciation_ratio = exp(normalized_used_price − normalized_new_price)`, not a naive division of the two columns — dividing log-transformed values directly would have produced a mathematically meaningless target.
2. **The dataset has no condition or functionality data**, which real resale pricing depends on heavily. `condition_score` (1-10) and `working` (yes/no) were synthetically engineered from device age (`days_used`) plus randomized variability, explicitly **not** derived from price, to avoid leaking the target into the features. This is a known, documented limitation — see [Limitations](#limitations) below.

## Why not live data from OLX / Cashify?

Before settling on the Kaggle dataset, I attempted to source real, India-specific resale data by scraping OLX's used mobile phones listings. This was worth documenting rather than skipping over silently:

- **Initial inspection looked promising** — OLX's listings pages appeared to be standard server-rendered HTML with no obvious JavaScript-rendering barrier, so a lightweight `requests` + `BeautifulSoup` scraper seemed viable.
- **In practice, every request timed out** — and critically, this happened identically in two independent environments (Google Colab and a local Jupyter notebook). Ruling out a local network or IP-reputation issue (a fresh residential IP failing the same way as a cloud IP points elsewhere), the most likely explanation is bot-detection that silently stalls suspected script traffic rather than returning a clean "blocked" response — a deliberate anti-scraping tactic used by many high-traffic sites.
- **Cashify was assessed as an even harder target** — its pricing tool is almost certainly a dynamic, API-backed calculator rather than static listings, which would require either reverse-engineering a private API (fragile, and a legal gray area) or full browser automation.
- **Decision: prioritize the ML work over scraping infrastructure.** Reliably defeating modern bot protection generally requires browser automation, fingerprint/header rotation, and ongoing maintenance — effectively a separate project in itself. Since the goal here was to demonstrate data science and deployment skills, not scraping engineering, I made a deliberate call to use a clean, publicly available dataset instead, and reserved the time saved for feature engineering, model comparison, and deployment.

This was a pragmatic trade-off, not a hard technical wall — with enough dedicated scraping engineering, live marketplace data is likely obtainable. It just wasn't the best use of time for what this project set out to demonstrate.


## Methodology

1. **EDA** — distribution checks, correlation heatmap, missing-value investigation (verified missingness was random data-entry gaps, not structural, before choosing an imputation strategy) since some features are 
synthetically simulated and the dataset set used was very small (~3200 rows)
the tree model can behave a bit strangely sometimes. 
2. **Feature engineering**
   - `depreciation_ratio` (target) — reconstructed from log-transformed price columns
   - `condition_score`, `working` — synthetically simulated from age + randomness
   - `is_tablet` — screen-size threshold identified from a visible gap in the distribution
3. **Missing value handling** — grouped-median imputation (brand + release year, with progressive fallback) rather than a blind global fill, informed by checking whether missingness was structural or random first
4. **Preprocessing** — `StandardScaler` for linear models, one-hot encoding for nominal categoricals, native categorical handling for XGBoost
5. **Modeling** — baseline comparison across five models (see results below)
6. **Evaluation** — MAE and R² on a held-out test set, benchmarked against a dummy (mean-prediction) baseline to confirm real signal

## Model results

| Model | MAE | R² |
|---|---|---|
| Dummy baseline (predicts mean) | 0.050 | ~0.00 |
| Linear Regression | 0.079359 | 0.617661 |
| Ridge | 0.079442 | 0.617517 |
| Lasso | 0.079431 | 0.621251 |
| Random Forest | 0.072890 | 0.690109 |
| **XGBoost (selected)** | **0.071007** | **0.705025** |

**XGBoost was selected as the production model** — chosen deliberately over LightGBM as well, since XGBoost's level-wise tree growth is more conservative on a smaller dataset (~3,450 rows) than LightGBM's leaf-wise growth, which is more overfit-prone at this scale.

## Key findings

- Linear models plateaued around R² ≈ 0.28, and the correlation heatmap confirmed why — no single spec correlates strongly with depreciation rate on its own, pointing to non-linear feature interactions.
- Adding the features like working and condition_score helps the user to be more transparent about the product and makes it more easier for the model to predict however due to lack of these features from the original dataset i have to synthetically with the help of days_used form these features which ofcourse was not much accurate but was important for this kind of project.
- For random forest regressor normalised_new_price was the most important feature, but for xgboost release_year was the most important feature.

## Tech stack & architecture

- **Modeling**: pandas, scikit-learn, XGBoost
- **Backend**: FastAPI — serves predictions from the trained model (`best_xgb.joblib`)
- **Frontend**: Streamlit — interactive UI for entering device specs/condition
- **Containerization**: Docker (separate images for backend and frontend)
- **Deployment**: Render (Blueprint-based dual-service deployment)

```
phone-resale-app/
├── backend/          # FastAPI microservice — prediction API
├── frontend/         # Streamlit microservice — user interface
├── model_training/   # EDA, feature engineering, model comparison notebook
├── render.yaml        # Render Blueprint for both services
└── docker-compose.yml # local multi-container testing
```

## Running locally

```bash
# Backend
cd backend
uv pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (in a separate terminal)
cd frontend
uv pip install -r requirements.txt
streamlit run app.py
```

Or with Docker Compose:
```bash
docker-compose up --build
```

## Limitations

- `condition_score` and `working` are **synthetically simulated**, not real seller-reported data — modeled from device age plus randomized variability, deliberately without any dependence on price to avoid leaking the target variable. A production version would need real condition data collected from actual listings or user submissions.
- The dataset's absolute price scale could not be recovered (the normalization formula for the original currency/scale was never disclosed) — the model predicts a **depreciation ratio**, which is then applied to a user-provided or looked-up real price rather than predicting currency directly.
- Trained on a relatively small dataset (~3,450 rows); performance on device types, brands, or price ranges underrepresented in the data may be less reliable.

## Possible future improvements

- Replace synthetic condition/working labels with real data (e.g., a small hand-labeled sample from live listings)
- Add SHAP-based explainability to the deployed app, showing users *why* a price was estimated
- Expand to India-specific listings for local market accuracy