import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import csv
import boto3
from botocore.exceptions import BotoCoreError, ClientError

SITE_URL = os.environ.get("SITE_URL", "https://immobilier-au-senegal.com/list-layout/")
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY_PREFIX = os.environ.get("S3_KEY_PREFIX", "scraping/")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def save_to_local_csv(data, filename):
    filepath = os.path.join(BASE_DIR, filename)

    # Champs du CSV
    fieldnames = ['titre', 'prix', 'localisation', 'type_bien', 'nombre_chambres', 'surface']

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Fichier CSV sauvegardé localement : {filepath}")
    return filepath


def upload_to_s3(filepath, bucket, key):
    """Upload le fichier local vers S3 si la configuration est fournie."""
    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(filepath, bucket, key)
        print(f"Fichier uploadé sur S3 : s3://{bucket}/{key}")
    except (BotoCoreError, ClientError) as exc:
        print(f"⚠️  Échec de l'upload S3 : {exc}")

def scrape_site(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, timeout=15, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    annonces = soup.select("article.rh_list_card")
    for ann in annonces:
        titre = ann.select_one("h3")
        
        # Prix - chercher dans tout l'article
        prix = None
        prix_elements = ann.find_all(string=lambda text: text and ('Fr' in text or 'FCFA' in text or 'CFA' in text or '€' in text))
        if prix_elements:
            prix = prix_elements[0].strip()
        
        # Localisation - extraire du titre
        localisation = None
        if titre:
            titre_text = titre.get_text(strip=True)
            if 'Sénégal' in titre_text:
                localisation = titre_text
        
        # Type de bien
        type_bien = None
        if titre:
            titre_text = titre.get_text(strip=True).lower()
            if 'terrain' in titre_text:
                type_bien = 'Terrain'
            elif 'maison' in titre_text:
                type_bien = 'Maison'
            elif 'appartement' in titre_text:
                type_bien = 'Appartement'
            elif 'villa' in titre_text:
                type_bien = 'Villa'
        
        # Surface - extraire du titre
        surface = None
        if titre:
            titre_text = titre.get_text(strip=True)
            surface_match = re.search(r'(\d+(?:\s*\d+)*)\s*(?:mètres|m²|m2)', titre_text)
            if surface_match:
                surface = surface_match.group(0)
        
        # Nombre de chambres (non applicable pour les terrains)
        nb_chambres = None
        if type_bien and type_bien != 'Terrain':
            nb_chambres = ann.select_one(".chambres, .bedrooms")
            if nb_chambres:
                nb_chambres = nb_chambres.get_text(strip=True)

        result = {
            "titre": titre.get_text(strip=True) if titre else None,
            "prix": prix,
            "localisation": localisation,
            "type_bien": type_bien,
            "nombre_chambres": nb_chambres.get_text(strip=True) if nb_chambres else None,
            "surface": surface,
        }

        results.append(result)

    return results

if __name__ == "__main__":
    data = scrape_site(SITE_URL)
    print(f"{len(data)} annonces récupérées")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"annonces_{timestamp}.csv"
    
    # Sauvegarde locale en CSV
    local_path = save_to_local_csv(data, csv_filename)

    # Upload S3 automatique si configuration disponible
    if S3_BUCKET:
        s3_key = f"{S3_KEY_PREFIX.rstrip('/')}/{csv_filename}"
        upload_to_s3(local_path, S3_BUCKET, s3_key)
    else:
        print("⚠️  S3_BUCKET non défini : upload S3 ignoré.")
