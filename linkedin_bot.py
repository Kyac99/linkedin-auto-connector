"""
Agent automatisé pour envoyer des invitations LinkedIn sans message.
"""
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

import config
from utils.helpers import (
    random_sleep, 
    save_cookies, 
    load_cookies, 
    extract_profile_id,
    format_search_url
)
import database as db

# Configuration du logging
logger = logging.getLogger("linkedin_bot")


class LinkedInBot:
    """
    Agent automatisé pour envoyer des invitations sur LinkedIn.
    """

    def __init__(self, headless=False):
        """
        Initialise l'agent LinkedIn.
        
        Args:
            headless (bool): Si True, le navigateur sera exécuté en mode headless
        """
        self.driver = None
        self.headless = headless
        self.session_id = None
        self.profiles_visited = 0
        self.invitations_sent = 0
        self.is_running = False

    def setup_driver(self):
        """
        Configure et initialise le navigateur Chrome.
        
        Returns:
            bool: True si le navigateur a été initialisé avec succès, False sinon
        """
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
                
            # Options pour éviter la détection comme un bot
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={config.USER_AGENT}")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Initialiser le service Chrome
            if config.CHROME_DRIVER_PATH:
                service = Service(config.CHROME_DRIVER_PATH)
            else:
                service = Service(ChromeDriverManager().install())
                
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Définir une taille d'écran standard
            self.driver.set_window_size(1920, 1080)
            
            # Contourner la détection du bot
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("Navigateur initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du navigateur: {e}")
            return False

    def login(self, email=None, password=None, use_cookies=True):
        """
        Se connecte à LinkedIn.
        
        Args:
            email (str, optional): Adresse email LinkedIn
            password (str, optional): Mot de passe LinkedIn
            use_cookies (bool): Si True, essaie d'utiliser les cookies enregistrés
            
        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        if not self.driver:
            if not self.setup_driver():
                return False
                
        try:
            # Aller sur LinkedIn
            self.driver.get(config.LINKEDIN_URL)
            random_sleep(2, 5)
            
            # Essayer d'utiliser les cookies si demandé
            if use_cookies and load_cookies(self.driver, config.COOKIES_FILE):
                # Rafraîchir après chargement des cookies
                self.driver.get(config.LINKEDIN_URL)
                random_sleep(3, 6)
                
                # Vérifier si nous sommes connectés
                if self._is_logged_in():
                    logger.info("Connexion réussie via les cookies")
                    return True
                else:
                    logger.warning("Cookies invalides ou expirés, tentative de connexion manuelle")
            
            # Si nous ne sommes pas connectés, procéder à la connexion manuelle
            email = email or config.LINKEDIN_EMAIL
            password = password or config.LINKEDIN_PASSWORD
            
            if not email or not password:
                logger.error("Identifiants LinkedIn manquants")
                return False
                
            # Aller à la page de connexion
            self.driver.get(config.LINKEDIN_LOGIN_URL)
            random_sleep(2, 5)
            
            # Trouver et remplir le champ email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Trouver et remplir le champ mot de passe
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Cliquer sur le bouton de connexion
            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()
            
            # Attendre que la page se charge
            random_sleep(5, 10)
            
            # Vérifier si nous sommes connectés
            if self._is_logged_in():
                logger.info("Connexion réussie")
                
                # Sauvegarder les cookies pour les prochaines sessions
                save_cookies(self.driver, config.COOKIES_FILE)
                return True
            else:
                logger.error("Échec de la connexion")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False

    def _is_logged_in(self):
        """
        Vérifie si l'utilisateur est connecté à LinkedIn.
        
        Returns:
            bool: True si connecté, False sinon
        """
        try:
            # Attendre que le menu de navigation soit chargé (élément qui n'existe que pour les utilisateurs connectés)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav__me"))
            )
            return True
        except TimeoutException:
            return False

    def search_profiles(self, sector="", job_title="", location="", connection_level="2nd"):
        """
        Recherche des profils LinkedIn selon les critères spécifiés.
        
        Args:
            sector (str): Secteur d'activité
            job_title (str): Fonction
            location (str): Localisation
            connection_level (str): Niveau de connexion (2nd, 3rd)
            
        Returns:
            bool: True si la recherche a été effectuée avec succès, False sinon
        """
        try:
            # Formatage de l'URL de recherche
            search_url = format_search_url(
                config.LINKEDIN_SEARCH_URL,
                sector=sector,
                job_title=job_title,
                location=location,
                connection_level=connection_level
            )
            
            logger.info(f"URL de recherche: {search_url}")
            
            # Accéder à l'URL de recherche
            self.driver.get(search_url)
            random_sleep(3, 6)
            
            # Vérifier si la recherche a renvoyé des résultats
            try:
                # Chercher un élément qui indique l'absence de résultats
                no_results = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Aucun résultat')]")
                if no_results:
                    logger.warning("Aucun résultat trouvé pour cette recherche")
                    return False
                    
                # Vérifier le nombre de résultats
                results_count_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container"))
                )
                logger.info("Résultats de recherche chargés avec succès")
                return True
                
            except TimeoutException:
                logger.warning("Impossible de charger les résultats de recherche")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return False

    def extract_profile_info(self, profile_element):
        """
        Extrait les informations d'un profil à partir d'un élément HTML.
        
        Args:
            profile_element: Élément WebElement du profil
            
        Returns:
            dict: Dictionnaire contenant les informations du profil
        """
        try:
            # Extraire le nom et l'URL du profil
            name_element = profile_element.find_element(By.CSS_SELECTOR, ".entity-result__title a")
            profile_name = name_element.text.strip()
            profile_url = name_element.get_attribute("href").split("?")[0]  # Supprimer les paramètres d'URL
            
            # Extraire l'ID du profil à partir de l'URL
            profile_id = extract_profile_id(profile_url)
            
            # Tenter d'extraire le titre (poste actuel)
            try:
                title_element = profile_element.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                profile_title = title_element.text.strip()
            except NoSuchElementException:
                profile_title = ""
                
            # Tenter d'extraire l'entreprise actuelle
            try:
                company_element = profile_element.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                profile_company = company_element.text.strip()
            except NoSuchElementException:
                profile_company = ""
                
            # Tenter d'extraire la localisation
            try:
                location_element = profile_element.find_element(By.CSS_SELECTOR, ".entity-result__tertiary-subtitle")
                profile_location = location_element.text.strip()
            except NoSuchElementException:
                profile_location = ""
                
            return {
                "id": profile_id,
                "name": profile_name,
                "url": profile_url,
                "title": profile_title,
                "company": profile_company,
                "location": profile_location
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations du profil: {e}")
            return None

    def send_invitation(self, profile_element, sector="", job_title="", location="", connection_level=""):
        """
        Envoie une invitation de connexion à un profil.
        
        Args:
            profile_element: Élément WebElement du profil
            sector (str): Secteur d'activité recherché
            job_title (str): Fonction recherchée
            location (str): Localisation recherchée
            connection_level (str): Niveau de connexion
            
        Returns:
            bool: True si l'invitation a été envoyée avec succès, False sinon
        """
        try:
            # Vérifier les limites d'invitations
            daily_invitations = db.get_invitations_sent_today()
            weekly_invitations = db.get_invitations_sent_this_week()
            
            if daily_invitations >= config.MAX_INVITATIONS_PER_DAY:
                logger.warning(f"Limite quotidienne d'invitations atteinte ({daily_invitations})")
                return False
                
            if weekly_invitations >= config.MAX_INVITATIONS_PER_WEEK:
                logger.warning(f"Limite hebdomadaire d'invitations atteinte ({weekly_invitations})")
                return False
                
            # Extraire les informations du profil
            profile_info = self.extract_profile_info(profile_element)
            if not profile_info:
                return False
                
            # Chercher le bouton "Se connecter" ou "Suivre" dans le profil
            connect_button = None
            buttons = profile_element.find_elements(By.CSS_SELECTOR, ".artdeco-button")
            
            for button in buttons:
                button_text = button.text.strip().lower()
                if "connecter" in button_text or "connect" in button_text:
                    connect_button = button
                    break
                    
            if not connect_button:
                logger.info(f"Aucun bouton de connexion trouvé pour {profile_info['name']}")
                return False
                
            # Cliquer sur le bouton "Se connecter"
            connect_button.click()
            random_sleep(1, 3)
            
            # Sur certaines versions de LinkedIn, une modale peut apparaître pour ajouter un message
            # Nous allons simplement cliquer sur le bouton "Envoyer" sans ajouter de message
            try:
                # Rechercher le bouton "Envoyer" dans la modale
                send_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.artdeco-button--primary"))
                )
                
                # Simuler un délai avant de cliquer (comportement humain)
                random_sleep(1, 3)
                
                # Cliquer sur "Envoyer"
                send_button.click()
                random_sleep(1, 3)
                
            except TimeoutException:
                # Pas de modale, l'invitation a probablement déjà été envoyée
                logger.info("Invitation envoyée directement (sans modale)")
                
            # Enregistrer l'invitation dans la base de données
            db.add_profile_invitation(
                profile_id=profile_info["id"],
                profile_name=profile_info["name"],
                profile_url=profile_info["url"],
                title=profile_info["title"],
                company=profile_info["company"],
                location=profile_info["location"],
                sector=sector,
                job_title=job_title,
                search_location=location,
                connection_level=connection_level
            )
            
            logger.info(f"Invitation envoyée avec succès à {profile_info['name']}")
            
            # Mettre à jour les compteurs
            self.invitations_sent += 1
            
            # Mettre à jour les statistiques de session
            if self.session_id:
                db.update_session_stats(self.session_id, invitations_sent=1)
                
            return True
            
        except ElementClickInterceptedException:
            logger.warning("Le bouton est masqué par un autre élément")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'invitation: {e}")
            return False

    def scroll_down(self, count=1):
        """
        Fait défiler la page vers le bas.
        
        Args:
            count (int): Nombre de fois à défiler
        """
        for _ in range(count):
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(config.SCROLL_PAUSE_TIME)

    def process_search_results(self, sector="", job_title="", location="", connection_level=""):
        """
        Traite les résultats de recherche et envoie des invitations.
        
        Args:
            sector (str): Secteur d'activité
            job_title (str): Fonction
            location (str): Localisation
            connection_level (str): Niveau de connexion
            
        Returns:
            tuple: (profils visités, invitations envoyées)
        """
        visited_profiles = 0
        sent_invitations = 0
        page = 1
        
        while self.is_running and visited_profiles < config.MAX_PROFILES_TO_VISIT:
            try:
                # Attendre que les résultats de recherche se chargent
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".entity-result__item"))
                )
                
                # Trouver tous les profils sur la page actuelle
                profile_elements = self.driver.find_elements(By.CSS_SELECTOR, ".entity-result__item")
                logger.info(f"Page {page}: {len(profile_elements)} profils trouvés")
                
                # Traiter chaque profil
                for profile_element in profile_elements:
                    if not self.is_running:
                        break
                        
                    visited_profiles += 1
                    self.profiles_visited += 1
                    
                    # Mettre à jour les statistiques de session
                    if self.session_id:
                        db.update_session_stats(self.session_id, profiles_visited=1)
                        
                    # Envoyer une invitation
                    if self.send_invitation(profile_element, sector, job_title, location, connection_level):
                        sent_invitations += 1
                        
                    # Pause aléatoire entre les profils
                    random_sleep(config.MIN_WAIT_TIME, config.MAX_WAIT_TIME)
                    
                    # Vérifier si la limite a été atteinte
                    if visited_profiles >= config.MAX_PROFILES_TO_VISIT:
                        logger.info(f"Limite de profils atteinte ({visited_profiles})")
                        break
                        
                # Vérifier s'il y a une page suivante
                try:
                    next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Suivant']")
                    if "disabled" in next_button.get_attribute("class"):
                        logger.info("Dernière page atteinte")
                        break
                        
                    next_button.click()
                    page += 1
                    random_sleep(3, 6)
                    
                except NoSuchElementException:
                    logger.info("Pas de bouton 'Suivant' trouvé")
                    break
                    
            except TimeoutException:
                logger.warning("Impossible de charger les résultats de recherche")
                break
            except Exception as e:
                logger.error(f"Erreur lors du traitement des résultats: {e}")
                break
                
        return visited_profiles, sent_invitations

    def start(self, sector="", job_title="", location="", connection_level="2nd"):
        """
        Démarre le bot pour envoyer des invitations.
        
        Args:
            sector (str): Secteur d'activité
            job_title (str): Fonction
            location (str): Localisation
            connection_level (str): Niveau de connexion
            
        Returns:
            bool: True si le bot a démarré avec succès, False sinon
        """
        try:
            # Vérifier si le bot est déjà en cours d'exécution
            if self.is_running:
                logger.warning("Le bot est déjà en cours d'exécution")
                return False
                
            self.is_running = True
            self.profiles_visited = 0
            self.invitations_sent = 0
            
            # Se connecter à LinkedIn
            if not self._is_logged_in():
                if not self.login():
                    logger.error("Impossible de se connecter à LinkedIn")
                    self.is_running = False
                    return False
            
            # Créer une nouvelle session
            session = db.start_new_session(
                sector=sector,
                job_title=job_title,
                location=location,
                connection_level=connection_level
            )
            self.session_id = session.id
            
            # Rechercher des profils
            if not self.search_profiles(sector, job_title, location, connection_level):
                logger.error("Échec de la recherche de profils")
                db.update_session_stats(self.session_id, end_session=True)
                self.is_running = False
                return False
                
            # Traiter les résultats de recherche
            visited, sent = self.process_search_results(sector, job_title, location, connection_level)
            
            # Terminer la session
            db.update_session_stats(self.session_id, end_session=True)
            
            logger.info(f"Session terminée. Profils visités: {visited}, Invitations envoyées: {sent}")
            self.is_running = False
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du bot: {e}")
            if self.session_id:
                db.update_session_stats(self.session_id, end_session=True)
            self.is_running = False
            return False

    def stop(self):
        """
        Arrête le bot.
        """
        logger.info("Arrêt du bot en cours...")
        self.is_running = False
        if self.session_id:
            db.update_session_stats(self.session_id, end_session=True)

    def close(self):
        """
        Ferme le navigateur et libère les ressources.
        """
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Navigateur fermé")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture du navigateur: {e}")
