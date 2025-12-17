import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import csv
import boto3
from botocore.exceptions import BotoCoreError, ClientError

SITE_URL = os.environ.get("SITE_URL", "https://immobilier-au-senegal.com/list-layout/")
# Configuration S3
S3_BUCKET = os.environ.get("S3_BUCKET", "m2dsia-mouhamed-diouf")  # Votre bucket par défaut
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


def upload_to_s3(file_path, bucket_name=None, object_name=None):
    """
    Téléverse un fichier vers un bucket S3
    
    Args:
        file_path (str): Chemin local du fichier à téléverser
        bucket_name (str, optional): Nom du bucket S3. Par défaut: m2dsia-mouhamed-diouf
        object_name (str, optional): Nom de l'objet dans S3. Par défaut: nom du fichier
    
    Returns:
        bool: True si le téléversement a réussi, False sinon
    """
    try:
        if bucket_name is None:
            bucket_name = S3_BUCKET
            
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        # S'assurer que le préfixe se termine par un /
        if S3_KEY_PREFIX and not S3_KEY_PREFIX.endswith('/'):
            full_key = f"{S3_KEY_PREFIX}/{object_name}"
        else:
            full_key = f"{S3_KEY_PREFIX}{object_name}"
            
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, full_key)
        print(f"Fichier uploadé avec succès vers: s3://{bucket_name}/{full_key}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'upload vers S3: {str(e)}")
        return False


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
    print(f"Début du scraping sur {SITE_URL}")
    data = scrape_site(SITE_URL)
    print(f"{len(data)} annonces récupérées")

    if not data:
        print("Aucune donnée à sauvegarder. Arrêt du script.")
        exit(1)

    # Sauvegarder localement
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"annonces_{timestamp}.csv"
    local_path = save_to_local_csv(data, csv_filename)

    # Upload vers S3
    if upload_file_s3(local_path):
        print("Téléversement S3 réussi!")
    else:
        print("Échec du téléversement S3, vérifiez les logs pour plus de détails")
