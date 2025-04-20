"""
Configuration pour l'agent LinkedIn automatisé.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent

# Configurations LinkedIn
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
LINKEDIN_URL = "https://www.linkedin.com"
LINKEDIN_LOGIN_URL = f"{LINKEDIN_URL}/login"
LINKEDIN_SEARCH_URL = f"{LINKEDIN_URL}/search/results/people/"
COOKIES_FILE = os.path.join(BASE_DIR, "linkedin_cookies.pkl")

# Configurations de l'agent
MAX_INVITATIONS_PER_DAY = int(os.getenv("MAX_INVITATIONS_PER_DAY", "20"))
MAX_INVITATIONS_PER_WEEK = int(os.getenv("MAX_INVITATIONS_PER_WEEK", "100"))
MIN_WAIT_TIME = int(os.getenv("MIN_WAIT_TIME", "10"))  # En secondes
MAX_WAIT_TIME = int(os.getenv("MAX_WAIT_TIME", "30"))  # En secondes
SCROLL_PAUSE_TIME = 2  # Temps de pause entre les scrolls
MAX_PROFILES_TO_VISIT = 100  # Nombre maximum de profils à visiter par session

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/linkedin_bot.db")

# Configuration du navigateur
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

# Configuration de l'interface utilisateur
DEFAULT_SECTOR = os.getenv("DEFAULT_SECTOR", "")
DEFAULT_JOB_TITLE = os.getenv("DEFAULT_JOB_TITLE", "")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "")
DEFAULT_CONNECTION_LEVEL = os.getenv("DEFAULT_CONNECTION_LEVEL", "2nd")
