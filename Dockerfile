# Image légère Python
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper_local.py ./

# Variables par défaut (surchargées au run si besoin)
ENV SITE_URL="https://immobilier-au-senegal.com/list-layout/" \
    S3_KEY_PREFIX="scraping/"

CMD ["python", "scraper_local.py"]
