FROM python:3.10-slim

# Install uv for ultra-fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .

EXPOSE 8000

# Use dynamic $PORT assigned by Render (defaults to 8000 if not set)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]