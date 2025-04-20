"""
Fonctions utilitaires pour l'agent LinkedIn automatisé.
"""
import random
import time
import pickle
import logging
import re
from pathlib import Path
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("linkedin_bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("linkedin_bot")


def random_sleep(min_seconds=10, max_seconds=30):
    """
    Pause aléatoire pour simuler un comportement humain.
    
    Args:
        min_seconds (int): Durée minimum en secondes
        max_seconds (int): Durée maximum en secondes
    """
    seconds = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Pause de {seconds:.2f} secondes")
    time.sleep(seconds)


def extract_profile_id(url):
    """
    Extrait l'identifiant de profil LinkedIn à partir de l'URL.
    
    Args:
        url (str): URL du profil LinkedIn
        
    Returns:
        str: Identifiant du profil ou None si non trouvé
    """
    # Extraction de l'ID à partir de /in/username/ ou /in/username-12345/
    match = re.search(r"/in/([^/]+)/?", url)
    if match:
        return match.group(1)
    return None


def save_cookies(driver, filename):
    """
    Sauvegarde les cookies de session dans un fichier.
    
    Args:
        driver: Instance du navigateur Selenium
        filename (str): Chemin du fichier pour sauvegarder les cookies
    """
    try:
        cookies = driver.get_cookies()
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "wb") as file:
            pickle.dump(cookies, file)
        logger.info(f"Cookies sauvegardés dans {filename}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des cookies: {e}")
        return False


def load_cookies(driver, filename):
    """
    Charge les cookies de session depuis un fichier.
    
    Args:
        driver: Instance du navigateur Selenium
        filename (str): Chemin du fichier contenant les cookies
        
    Returns:
        bool: True si les cookies ont été chargés avec succès, False sinon
    """
    try:
        if not Path(filename).exists():
            logger.warning(f"Fichier de cookies introuvable: {filename}")
            return False
            
        with open(filename, "rb") as file:
            cookies = pickle.load(file)
            
        for cookie in cookies:
            # Certains navigateurs peuvent avoir des problèmes avec les cookies sameSite
            if "sameSite" in cookie:
                del cookie["sameSite"]
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Impossible d'ajouter le cookie: {e}")
                
        logger.info(f"Cookies chargés depuis {filename}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du chargement des cookies: {e}")
        return False


def format_search_url(base_url, sector="", job_title="", location="", connection_level=""):
    """
    Formate l'URL de recherche LinkedIn avec les paramètres spécifiés.
    
    Args:
        base_url (str): URL de base pour la recherche LinkedIn
        sector (str): Secteur d'activité
        job_title (str): Fonction
        location (str): Localisation
        connection_level (str): Niveau de connexion (2nd, 3rd)
        
    Returns:
        str: URL de recherche formatée
    """
    params = []
    
    if sector:
        params.append(f"industry=%5B%22{sector}%22%5D")
        
    if job_title:
        params.append(f"title=%5B%22{job_title}%22%5D")
        
    if location:
        params.append(f"geoUrn=%5B%22{location}%22%5D")
        
    if connection_level:
        if connection_level == "2nd":
            params.append("network=%5B%22S%22%5D")
        elif connection_level == "3rd":
            params.append("network=%5B%22O%22%5D")
            
    # Ajout de paramètres par défaut pour le tri
    params.append("origin=FACETED_SEARCH")
    params.append("sortBy=RELEVANCE")
    
    # Construction de l'URL finale
    if params:
        return f"{base_url}?{'&'.join(params)}"
    return base_url


def get_current_timestamp():
    """
    Retourne un horodatage formaté pour la journalisation.
    
    Returns:
        str: Horodatage formaté
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_init_file():
    """Crée un fichier __init__.py vide dans le dossier courant."""
    with open("__init__.py", "w") as f:
        pass
