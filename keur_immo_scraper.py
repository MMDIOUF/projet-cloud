#!/usr/bin/env python3
"""
Scraper pour keur-immo.com - Terrains à vendre à Dakar
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from urllib.parse import urljoin, urlparse
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeurImmoScraper:
    def __init__(self):
        self.base_url = "https://keur-immo.com"
        self.target_url = "https://keur-immo.com/senegal/terrains-a-vendre-dakar/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.properties = []
    
    def get_page(self, url, retries=3):
        """Récupère une page avec gestion des erreurs et retry"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Tentative {attempt + 1} échouée pour {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponentiel
                else:
                    logger.error(f"Impossible de récupérer {url} après {retries} tentatives")
                    return None
    
    def parse_property_listing(self, soup):
        """Parse une page de listing pour extraire les informations des propriétés"""
        properties = []
        
        # Adapter ces sélecteurs selon la structure HTML réelle du site
        property_cards = soup.find_all('div', class_='property-card') or soup.find_all('article')
        
        if not property_cards:
            # Essayer d'autres sélecteurs communs
            property_cards = soup.find_all('div', class_=['listing-item', 'property-item', 'item'])
        
        for card in property_cards:
            try:
                property_data = self.extract_property_data(card)
                if property_data:
                    properties.append(property_data)
            except Exception as e:
                logger.warning(f"Erreur lors de l'extraction d'une propriété: {e}")
                continue
        
        return properties
    
    def extract_property_data(self, card):
        """Extrait les données d'une propriété depuis son élément HTML"""
        data = {}
        
        # Titre
        title_elem = (card.find(['h1', 'h2', 'h3', 'h4', 'h5']) or 
                     card.find('a', class_=['title', 'property-title', 'listing-title']) or
                     card.find(class_=['title', 'property-title', 'listing-title']))
        data['titre'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
        
        # Prix - recherche plus exhaustive
        price_elem = (card.find(class_=['price', 'prix', 'cost', 'amount', 'property-price']) or
                     card.find('span', string=lambda x: x and any(currency in str(x) for currency in ['FCFA', 'CFA', '€', '$'])) or
                     card.find(string=lambda x: x and any(currency in str(x) for currency in ['FCFA', 'CFA', '€', '$'])))
        if price_elem:
            if hasattr(price_elem, 'get_text'):
                data['prix'] = price_elem.get_text(strip=True)
            else:
                data['prix'] = str(price_elem).strip()
        else:
            data['prix'] = 'N/A'
        
        # Localisation/Adresse
        location_elem = (card.find(class_=['location', 'localisation', 'address', 'lieu', 'zone', 'quartier']) or
                        card.find('i', class_=['fa-map-marker', 'fa-location']) or
                        card.find(string=lambda x: x and any(loc in str(x).lower() for loc in ['dakar', 'pikine', 'guédiawaye', 'rufisque'])))
        if location_elem:
            if hasattr(location_elem, 'get_text'):
                data['localisation'] = location_elem.get_text(strip=True)
            elif hasattr(location_elem, 'parent'):
                data['localisation'] = location_elem.parent.get_text(strip=True)
            else:
                data['localisation'] = str(location_elem).strip()
        else:
            data['localisation'] = 'N/A'
        
        # Surface - recherche plus complète
        surface_patterns = ['m²', 'hectare', 'ha', 'are', 'superficie']
        surface_elem = None
        for pattern in surface_patterns:
            surface_elem = card.find(string=lambda x: x and pattern in str(x).lower())
            if surface_elem:
                break
        
        if not surface_elem:
            surface_elem = card.find(class_=['surface', 'area', 'size', 'superficie'])
        
        if surface_elem:
            if hasattr(surface_elem, 'get_text'):
                data['surface'] = surface_elem.get_text(strip=True)
            else:
                data['surface'] = str(surface_elem).strip()
        else:
            data['surface'] = 'N/A'
        
        # Lien vers la page détaillée
        link_elem = card.find('a', href=True)
        if link_elem:
            data['lien'] = urljoin(self.base_url, link_elem['href'])
        else:
            data['lien'] = 'N/A'
        
        # Description courte
        desc_elem = (card.find(class_=['description', 'excerpt', 'summary', 'content']) or
                    card.find('p'))
        data['description'] = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
        
        # ID de la propriété
        id_elem = card.get('id') or card.get('data-id')
        data['id_propriete'] = id_elem if id_elem else 'N/A'
        
        # Type de propriété
        type_elem = card.find(class_=['type', 'category', 'property-type'])
        data['type'] = type_elem.get_text(strip=True) if type_elem else 'Terrain'
        
        # Date de publication
        date_elem = (card.find(class_=['date', 'published', 'created']) or
                    card.find('time'))
        if date_elem:
            data['date_publication'] = date_elem.get_text(strip=True) or date_elem.get('datetime', 'N/A')
        else:
            data['date_publication'] = 'N/A'
        
        # Agent/Contact
        agent_elem = (card.find(class_=['agent', 'contact', 'seller', 'owner']) or
                     card.find(string=lambda x: x and 'agent' in str(x).lower()))
        if agent_elem:
            if hasattr(agent_elem, 'get_text'):
                data['agent'] = agent_elem.get_text(strip=True)
            else:
                data['agent'] = str(agent_elem).strip()
        else:
            data['agent'] = 'N/A'
        
        # Téléphone
        phone_elem = (card.find(class_=['phone', 'tel', 'telephone']) or
                     card.find('a', href=lambda x: x and x.startswith('tel:')) or
                     card.find(string=lambda x: x and any(char.isdigit() for char in str(x)) and len([c for c in str(x) if c.isdigit()]) >= 8))
        if phone_elem:
            if hasattr(phone_elem, 'get_text'):
                data['telephone'] = phone_elem.get_text(strip=True)
            elif hasattr(phone_elem, 'get'):
                data['telephone'] = phone_elem.get('href', '').replace('tel:', '')
            else:
                data['telephone'] = str(phone_elem).strip()
        else:
            data['telephone'] = 'N/A'
        
        # Images
        img_elems = card.find_all('img')
        images = []
        for img in img_elems:
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(urljoin(self.base_url, src))
        data['images'] = images if images else []
        data['nombre_images'] = len(images)
        
        # Caractéristiques supplémentaires
        features = []
        feature_keywords = ['clôturé', 'titre foncier', 'viabilisé', 'électricité', 'eau', 'égout', 'bitumé']
        for keyword in feature_keywords:
            if card.find(string=lambda x: x and keyword.lower() in str(x).lower()):
                features.append(keyword)
        data['caracteristiques'] = features
        
        # Statut (à vendre, vendu, etc.)
        status_elem = card.find(class_=['status', 'statut', 'badge'])
        data['statut'] = status_elem.get_text(strip=True) if status_elem else 'À vendre'
        
        return data if data['titre'] != 'N/A' else None
    
    def get_detailed_property_info(self, property_url):
        """Récupère les détails complets d'une propriété depuis sa page dédiée"""
        if property_url == 'N/A':
            return {}
        
        response = self.get_page(property_url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        details = {}
        
        # Description complète
        desc_elem = (soup.find(class_=['description', 'content', 'property-description', 'details']) or
                    soup.find('div', string=lambda x: x and len(str(x)) > 100))
        if desc_elem:
            details['description_complete'] = desc_elem.get_text(strip=True)
        
        # Prix détaillé
        price_elem = soup.find(class_=['price', 'prix', 'cost', 'property-price'])
        if price_elem:
            details['prix_detaille'] = price_elem.get_text(strip=True)
        
        # Caractéristiques détaillées
        characteristics = {}
        
        # Recherche dans les listes de caractéristiques
        feature_lists = soup.find_all(['ul', 'dl', 'div'], class_=['features', 'characteristics', 'details', 'specs'])
        for feature_list in feature_lists:
            items = feature_list.find_all(['li', 'dt', 'dd', 'span', 'div'])
            for item in items:
                text = item.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    characteristics[key.strip()] = value.strip()
                elif any(keyword in text.lower() for keyword in ['m²', 'hectare', 'superficie', 'surface']):
                    characteristics['surface_detaillee'] = text
                elif any(keyword in text.lower() for keyword in ['prix', 'coût', 'montant']):
                    characteristics['prix_info'] = text
        
        details['caracteristiques_detaillees'] = characteristics
        
        # Coordonnées GPS si disponibles
        map_elem = soup.find(['iframe', 'div'], src=lambda x: x and 'maps' in str(x)) or soup.find(attrs={'data-lat': True})
        if map_elem:
            lat = map_elem.get('data-lat') or 'N/A'
            lng = map_elem.get('data-lng') or 'N/A'
            details['coordonnees'] = {'latitude': lat, 'longitude': lng}
        
        # Galerie d'images complète
        img_gallery = soup.find(class_=['gallery', 'images', 'photos'])
        if img_gallery:
            images = []
            for img in img_gallery.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-original')
                if src:
                    images.append(urljoin(self.base_url, src))
            details['galerie_images'] = images
        
        # Informations de contact détaillées
        contact_section = soup.find(class_=['contact', 'agent-info', 'seller-info'])
        if contact_section:
            contact_info = {}
            
            # Nom de l'agent
            name_elem = contact_section.find(['h3', 'h4', 'span'], class_=['name', 'agent-name'])
            if name_elem:
                contact_info['nom_agent'] = name_elem.get_text(strip=True)
            
            # Téléphone
            phone_elem = contact_section.find('a', href=lambda x: x and x.startswith('tel:'))
            if phone_elem:
                contact_info['telephone_agent'] = phone_elem.get('href').replace('tel:', '')
            
            # Email
            email_elem = contact_section.find('a', href=lambda x: x and x.startswith('mailto:'))
            if email_elem:
                contact_info['email_agent'] = email_elem.get('href').replace('mailto:', '')
            
            details['contact_detaille'] = contact_info
        
        # Propriétés similaires ou recommandées
        similar_section = soup.find(class_=['similar', 'related', 'recommended'])
        if similar_section:
            similar_properties = []
            for prop in similar_section.find_all('a', href=True):
                similar_properties.append({
                    'titre': prop.get_text(strip=True),
                    'lien': urljoin(self.base_url, prop['href'])
                })
            details['proprietes_similaires'] = similar_properties[:5]  # Limiter à 5
        
        # Informations légales
        legal_info = {}
        legal_keywords = ['titre foncier', 'cadastre', 'permis', 'autorisation', 'zone']
        for keyword in legal_keywords:
            elem = soup.find(string=lambda x: x and keyword.lower() in str(x).lower())
            if elem:
                legal_info[keyword] = elem.strip()
        
        if legal_info:
            details['informations_legales'] = legal_info
        
        # Date de dernière mise à jour
        update_elem = soup.find(class_=['updated', 'modified', 'last-update'])
        if update_elem:
            details['derniere_mise_a_jour'] = update_elem.get_text(strip=True)
        
        return details
    
    def get_total_pages(self, soup):
        """Détermine le nombre total de pages"""
        pagination = soup.find(class_=['pagination', 'pager'])
        if pagination:
            page_links = pagination.find_all('a')
            if page_links:
                try:
                    return max([int(link.get_text()) for link in page_links if link.get_text().isdigit()])
                except ValueError:
                    pass
        return 1
    
    def scrape_all_pages(self, get_details=True):
        """Scrape toutes les pages de résultats avec option pour les détails complets"""
        logger.info(f"Début du scraping de {self.target_url}")
        
        # Première page pour déterminer le nombre total
        response = self.get_page(self.target_url)
        if not response:
            logger.error("Impossible de récupérer la première page")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire les propriétés de la première page
        properties = self.parse_property_listing(soup)
        self.properties.extend(properties)
        logger.info(f"Page 1: {len(properties)} propriétés trouvées")
        
        # Déterminer le nombre total de pages
        total_pages = self.get_total_pages(soup)
        logger.info(f"Nombre total de pages détecté: {total_pages}")
        
        # Scraper les pages suivantes
        for page_num in range(2, total_pages + 1):
            page_url = f"{self.target_url}?page={page_num}"
            logger.info(f"Scraping page {page_num}/{total_pages}")
            
            response = self.get_page(page_url)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                properties = self.parse_property_listing(soup)
                self.properties.extend(properties)
                logger.info(f"Page {page_num}: {len(properties)} propriétés trouvées")
            
            # Pause entre les requêtes pour être respectueux
            time.sleep(1)
        
        logger.info(f"Scraping des listes terminé. Total: {len(self.properties)} propriétés")
        
        # Récupérer les détails complets si demandé
        if get_details and self.properties:
            logger.info("Récupération des détails complets pour chaque propriété...")
            
            for i, property_data in enumerate(self.properties):
                logger.info(f"Détails {i+1}/{len(self.properties)}: {property_data.get('titre', 'N/A')}")
                
                # Récupérer les détails complets
                detailed_info = self.get_detailed_property_info(property_data.get('lien', 'N/A'))
                
                # Fusionner les détails avec les données existantes
                property_data.update(detailed_info)
                
                # Pause entre les requêtes détaillées
                time.sleep(2)
            
            logger.info("Récupération des détails terminée")
        
        logger.info(f"Scraping complet terminé. Total: {len(self.properties)} propriétés avec détails")
    
    def save_to_json(self, filename='keur_immo_terrains.json'):
        """Sauvegarde les données en JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.properties, f, ensure_ascii=False, indent=2)
        logger.info(f"Données sauvegardées dans {filename}")
    
    def save_to_csv(self, filename='keur_immo_terrains.csv'):
        """Sauvegarde les données en CSV"""
        if not self.properties:
            logger.warning("Aucune donnée à sauvegarder")
            return
        
        fieldnames = self.properties[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.properties)
        logger.info(f"Données sauvegardées dans {filename}")
    
    def analyze_data(self):
        """Analyse les données récupérées et affiche des statistiques"""
        if not self.properties:
            print("Aucune donnée à analyser")
            return
        
        print(f"\n=== ANALYSE DES DONNÉES ===")
        print(f"Nombre total de propriétés: {len(self.properties)}")
        
        # Analyse des prix
        prices = []
        for prop in self.properties:
            prix_text = prop.get('prix', 'N/A')
            if prix_text != 'N/A':
                # Extraire les chiffres du prix
                import re
                numbers = re.findall(r'[\d\s]+', prix_text.replace(',', '').replace('.', ''))
                if numbers:
                    try:
                        price = int(''.join(numbers[0].split()))
                        prices.append(price)
                    except ValueError:
                        pass
        
        if prices:
            print(f"\n--- Analyse des prix ---")
            print(f"Prix minimum: {min(prices):,} FCFA")
            print(f"Prix maximum: {max(prices):,} FCFA")
            print(f"Prix moyen: {sum(prices)//len(prices):,} FCFA")
        
        # Analyse des localisations
        locations = {}
        for prop in self.properties:
            loc = prop.get('localisation', 'N/A')
            if loc != 'N/A':
                locations[loc] = locations.get(loc, 0) + 1
        
        if locations:
            print(f"\n--- Top 10 des localisations ---")
            sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
            for loc, count in sorted_locations[:10]:
                print(f"{loc}: {count} propriétés")
        
        # Analyse des surfaces
        surfaces = []
        for prop in self.properties:
            surface_text = prop.get('surface', 'N/A')
            if surface_text != 'N/A':
                import re
                numbers = re.findall(r'\d+', surface_text)
                if numbers:
                    try:
                        surface = int(numbers[0])
                        surfaces.append(surface)
                    except ValueError:
                        pass
        
        if surfaces:
            print(f"\n--- Analyse des surfaces ---")
            print(f"Surface minimum: {min(surfaces)} m²")
            print(f"Surface maximum: {max(surfaces)} m²")
            print(f"Surface moyenne: {sum(surfaces)//len(surfaces)} m²")
        
        # Analyse des caractéristiques
        all_features = []
        for prop in self.properties:
            features = prop.get('caracteristiques', [])
            all_features.extend(features)
        
        if all_features:
            feature_counts = {}
            for feature in all_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            print(f"\n--- Caractéristiques les plus communes ---")
            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            for feature, count in sorted_features[:5]:
                print(f"{feature}: {count} propriétés")
        
        # Propriétés avec le plus d'images
        with_images = [prop for prop in self.properties if prop.get('nombre_images', 0) > 0]
        if with_images:
            print(f"\n--- Images ---")
            print(f"Propriétés avec images: {len(with_images)}")
            avg_images = sum(prop.get('nombre_images', 0) for prop in with_images) / len(with_images)
            print(f"Nombre moyen d'images: {avg_images:.1f}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scraper pour keur-immo.com')
    parser.add_argument('--no-details', action='store_true', 
                       help='Ne pas récupérer les détails complets (plus rapide)')
    parser.add_argument('--max-properties', type=int, default=None,
                       help='Nombre maximum de propriétés à scraper')
    
    args = parser.parse_args()
    
    scraper = KeurImmoScraper()
    
    # Scraper avec ou sans détails complets
    get_details = not args.no_details
    scraper.scrape_all_pages(get_details=get_details)
    
    # Limiter le nombre de propriétés si spécifié
    if args.max_properties and len(scraper.properties) > args.max_properties:
        scraper.properties = scraper.properties[:args.max_properties]
        logger.info(f"Limitation à {args.max_properties} propriétés")
    
    if scraper.properties:
        # Sauvegarder les données
        scraper.save_to_json()
        scraper.save_to_csv()
        
        # Analyser les données
        scraper.analyze_data()
        
        # Afficher quelques exemples détaillés
        print(f"\n=== EXEMPLES DÉTAILLÉS ===")
        for i, prop in enumerate(scraper.properties[:2]):
            print(f"\n--- Propriété {i+1} ---")
            for key, value in prop.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f"  {key}: {len(value)} éléments - {value[:3]}...")
                elif isinstance(value, dict):
                    print(f"  {key}: {len(value)} détails")
                    for sub_key, sub_value in list(value.items())[:3]:
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        
        print(f"\n=== FICHIERS GÉNÉRÉS ===")
        print(f"📄 keur_immo_terrains.json - Données complètes en JSON")
        print(f"📊 keur_immo_terrains.csv - Données tabulaires en CSV")
        print(f"📈 Total: {len(scraper.properties)} propriétés avec tous les détails")
        
    else:
        print("❌ Aucune donnée récupérée. Vérifiez la structure du site.")
        print("💡 Essayez d'abord: python test_scraper.py")

if __name__ == "__main__":
    main()