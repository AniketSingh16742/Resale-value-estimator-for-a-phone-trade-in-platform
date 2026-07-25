import streamlit as st
import requests
import os

st.set_page_config(
    page_title="ReTech | AI Device Valuation Platform",
    page_icon="⚡",
    layout="wide"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------
# Custom High-Contrast Techy CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Dark Theme Background */
    .stApp {
        background: linear-gradient(135deg, #0a0c16 0%, #060812 100%);
        color: #f8fafc !important;
    }
    
    /* FIX FOR PALE SUBHEADERS & HEADINGS */
    h1, h2, h3, h4, .stMarkdown h3 {
        color: #00f2fe !important; /* Bright Glowing Cyan */
        font-weight: 800 !important;
        letter-spacing: 0.5px;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    
    /* Subheader Underline Accent */
    .stMarkdown h3 {
        border-bottom: 2px solid rgba(0, 242, 254, 0.4);
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* FIX FOR PALE FORM LABELS & TEXT */
    label, p, .stWidgetLabel {
        color: #f8fafc !important; /* Crisp White Text */
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(10, 12, 22, 0.85), rgba(6, 8, 18, 0.95)), 
                    url('https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1200') center/cover;
        padding: 40px 30px;
        border-radius: 20px;
        border: 1px solid rgba(0, 242, 254, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        text-align: center;
        margin-bottom: 25px;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #cbd5e1 !important;
    }
    
    /* Trust Badges */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 15px;
        font-size: 0.95rem;
        color: #38bdf8;
        font-weight: 700;
    }

    /* Custom Form Cards */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 30px;
        backdrop-filter: blur(10px);
    }
    
    /* Result Box Gradient */
    .result-card {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 0 35px rgba(2, 132, 199, 0.5);
        margin-top: 25px;
    }
    
    .result-price {
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        margin: 10px 0;
    }

    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* Target the text inside the button */
    div[data-testid="stFormSubmitButton"] > button p {
        color: #060812 !important; /* CHANGE THIS TO YOUR DESIRED TEXT COLOR */
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
    }

    /* Hover Effect */
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">⚡ ReTech AI Valuation</div>
    <div class="hero-subtitle">Get instant, guaranteed trade-in quotes powered by Machine Learning</div>
    <div class="badge-container">
        <span>🤖 XGBoost AI Powered</span> • 
        <span>⚡ 100% Free Quote</span> • 
        <span>🛡️ Instant Evaluation</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Input Form
# ---------------------------------------------------------
with st.form("tradein_form"):
    
    # 1. Device Category Selection
    st.subheader("1. Select Device Category")
    
    col_cat1, col_cat2 = st.columns([1, 2])
    with col_cat1:
        device_type = st.radio("Device Type", ["📱 Smartphone", "📟 Tablet"], horizontal=True)
        is_tablet = 1 if "Tablet" in device_type else 0
        
    with col_cat2:
        brand = st.selectbox("Brand", ["Apple", "Samsung", "Xiaomi", "Oppo", "Vivo", "OnePlus", "Huawei", "Google", "Motorola", "Lava", "Others"])

    col1, col2 = st.columns(2)
    with col1:
        os_type = st.selectbox("Operating System", ["iOS", "Android", "Windows", "Others"])
        release_year = st.number_input("Release Year", min_value=2017, max_value=2026, value=2025)
    with col2:
        original_price = st.number_input("Original Purchase Price ($)", min_value=50.0, max_value=3000.0, value=799.0)
        # Capped days_used at 1095 (3 years) to prevent Out-of-Distribution tree glitches
        days_used = st.number_input("Age / Days Used (Max 3 Years)", min_value=1, max_value=1000, value=265)

    # 2. Condition & Functionality
    st.subheader("2. Physical Condition & Functionality")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        condition_score = st.slider("Physical Condition Score (1 = Scratched/Dented, 10 = Flawless)", 1, 10, 8)
    with col_c2:
        working_status = st.radio("Functional Status", ["Fully Functional", "Defective / Screen Damaged"], horizontal=True)
        is_working = 1 if "Fully Functional" in working_status else 0

    # 3. Hardware Specs
    st.subheader("3. Hardware Specs")
    col3, col4, col5 = st.columns(3)
    with col3:
        ram = st.number_input("RAM (GB)", min_value=1, max_value=32, value=8)
        internal_memory = st.number_input("Storage (GB)", min_value=8, max_value=1024, value=128)
    with col4:
        rear_camera_mp = st.number_input("Rear Camera (MP)", min_value=2.0, max_value=200.0, value=48.0)
        front_camera_mp = st.number_input("Front Camera (MP)", min_value=2.0, max_value=60.0, value=12.0)
    with col5:
        battery = st.number_input("Battery Capacity (mAh)", min_value=500, max_value=12000, value=4500 if is_tablet == 0 else 7500)
        default_screen = 10.5 if is_tablet == 1 else 6.1
        screen_size = st.number_input("Screen Size (Inches)", min_value=3.5, max_value=15.0, value=default_screen)
    
    weight = st.number_input("Weight (grams)", min_value=50.0, max_value=800.0, value=180.0 if is_tablet == 0 else 480.0)

    # 4. Connectivity
    st.subheader("4. Connectivity Specs")
    col6, col7 = st.columns(2)
    with col6:
        is_4g = st.checkbox("4G LTE Connectivity", value=True)
    with col7:
        is_5g = st.checkbox("5G Cellular Support", value=True)

    submit = st.form_submit_button("⚡ GENERATE INSTANT TRADE-IN QUOTE", use_container_width=True)

# ---------------------------------------------------------
# Processing & Display Results
# ---------------------------------------------------------
if submit:
    payload = {
        "original_price": original_price,
        "days_used": days_used,
        "screen_size": screen_size,
        "rear_camera_mp": rear_camera_mp,
        "front_camera_mp": front_camera_mp,
        "internal_memory": internal_memory,
        "ram": ram,
        "battery": battery,
        "weight": weight,
        "release_year": release_year,
        "is_4g": 1 if is_4g else 0,
        "is_5g": 1 if is_5g else 0,
        "brand": brand,
        "os": os_type,
        "condition_score": condition_score,
        "is_working": is_working,
        "is_tablet": is_tablet
    }
    
    try:
        with st.spinner("Analyzing market valuation via XGBoost AI model..."):
            response = requests.post(f"{BACKEND_URL}/predict", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.balloons()
                
                st.markdown(f"""
                <div class="result-card">
                    <div style="font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px;">Estimated Trade-In Value</div>
                    <div class="result-price">${result['estimated_resale_price']:.2f}</div>
                    <div style="font-size: 1rem; opacity: 0.9;">Retained Value: <b>{result['predicted_retention_percentage']}</b> of Original Price (${result['original_price']:.2f})</div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error(f"Error from Valuation Engine: {response.text}")
    except Exception as e:
        st.error(f"Could not connect to backend engine: {e}")

# ---------------------------------------------------------
# FAQ Section
# ---------------------------------------------------------
st.divider()
st.subheader("💡 Frequently Asked Questions")

with st.expander("How is my trade-in price calculated?"):
    st.write("Our model analyzes historical secondary market transactions, device age, battery degradation, physical condition scores, and hardware specifications using a tuned XGBoost algorithm.")

with st.expander("How do I lock in this quote?"):
    st.write("Quotes are valid for 14 days. Once accepted, ship your device with our prepaid label or bring it to an authorized trade-in partner location.")