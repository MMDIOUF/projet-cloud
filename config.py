#!/usr/bin/env python3
"""
Configuration pour le scraper keur-immo.com
"""

# URLs et paramètres de base
BASE_URL = "https://keur-immo.com"
TARGET_URLS = {
    'terrains_dakar': "https://keur-immo.com/senegal/terrains-a-vendre-dakar/",
    'maisons_dakar': "https://keur-immo.com/senegal/maisons-a-vendre-dakar/",
    'appartements_dakar': "https://keur-immo.com/senegal/appartements-a-vendre-dakar/",
    'terrains_thies': "https://keur-immo.com/senegal/terrains-a-vendre-thies/",
    'terrains_senegal': "https://keur-immo.com/senegal/terrains-a-vendre/"
}

# Sélecteurs CSS personnalisés (basés sur l'analyse du site réel)
SELECTORS = {
    'property_cards': [
        'article.g5ere__property-item',
        'article[class*="g5ere__property-item"]',
        'div.g5ere__property-item',
        'article.property'
    ],
    'title': [
        'h3.g5ere__loop-property-title',
        '.g5ere__loop-property-title',
        '.g5ere__property-title',
        'h3.g5ere__loop-property-title a',
        'h1', 'h2', 'h3', 'h4'
    ],
    'price': [
        '.g5ere__loop-property-price',
        '.g5ere__lpp-price',
        'span.g5ere__loop-property-price',
        'span.g5ere__lpp-price',
        '.price', '.prix'
    ],
    'location': [
        '.g5ere__loop-property-location',
        '.g5ere__property-location',
        '.property-city', '.property-state',
        '[class*="property-city"]', '[class*="property-state"]',
        '.location', '.localisation', '.address'
    ],
    'surface': [
        '.g5ere__loop-property-meta',
        '.g5ere__property-meta',
        '.g5ere__loop-property-size',
        '.surface', '.area', '.size', '.superficie'
    ],
    'description': [
        '.g5ere__property-excerpt',
        '.g5ere__loop-property-excerpt',
        '.g5ere__property-excerpt p',
        '.description', '.excerpt', '.summary'
    ],
    'images': [
        '.g5core__entry-thumbnail',
        '.g5ere__view-gallery',
        '.g5ere__property-featured img',
        'img', '.gallery img'
    ],
    'contact': [
        '.contact', '.agent-info', '.seller-info', '.agent'
    ],
    'features': [
        '.features', '.characteristics', '.details', '.specs',
        'ul.features', 'div.features'
    ]
}

# Mots-clés pour l'extraction automatique
KEYWORDS = {
    'currency': ['FCFA', 'CFA', '€', '$', 'franc'],
    'surface_units': ['m²', 'hectare', 'ha', 'are', 'superficie'],
    'locations_dakar': [
        'dakar', 'pikine', 'guédiawaye', 'rufisque', 'parcelles assainies',
        'grand yoff', 'ouakam', 'ngor', 'almadies', 'plateau', 'medina',
        'fann', 'mermoz', 'sacré-coeur', 'point e', 'hann', 'bel air'
    ],
    'features': [
        'clôturé', 'titre foncier', 'viabilisé', 'électricité', 'eau',
        'égout', 'bitumé', 'cadastré', 'loti', 'zone résidentielle'
    ],
    'legal': [
        'titre foncier', 'cadastre', 'permis', 'autorisation', 'zone',
        'bail', 'propriété', 'acte', 'notaire'
    ]
}

# Paramètres de scraping
SCRAPING_CONFIG = {
    'delay_between_requests': 1,  # secondes
    'delay_between_details': 2,   # secondes
    'max_retries': 3,
    'timeout': 10,  # secondes
    'max_properties_per_run': None,  # None = illimité
    'save_html_samples': True,
    'get_property_details': True,
    'extract_images': True,
    'extract_coordinates': True
}

# Headers HTTP
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Fichiers de sortie
OUTPUT_FILES = {
    'json': 'keur_immo_terrains_complet.json',
    'csv': 'keur_immo_terrains_complet.csv',
    'excel': 'keur_immo_terrains_complet.xlsx',
    'html_sample': 'page_sample.html',
    'log': 'scraping.log'
}

# Champs à extraire (dans l'ordre pour le CSV)
FIELDS_ORDER = [
    'id_propriete', 'titre', 'prix', 'prix_detaille', 'localisation',
    'surface', 'surface_detaillee', 'type', 'statut', 'description',
    'description_complete', 'agent', 'telephone', 'date_publication',
    'derniere_mise_a_jour', 'nombre_images', 'lien', 'caracteristiques',
    'caracteristiques_detaillees', 'informations_legales', 'coordonnees',
    'contact_detaille', 'images', 'galerie_images', 'proprietes_similaires'
]