"""
Interface utilisateur Streamlit pour l'agent LinkedIn automatisé.
"""
import os
import threading
import time
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

from linkedin_bot import LinkedInBot
import database as db
import config

# Configuration de la page Streamlit
st.set_page_config(
    page_title="LinkedIn Auto Connector",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning {
        color: #ff4b4b;
    }
    .success {
        color: #00c853;
    }
    .bot-running {
        background-color: #e6f4ea;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #00c853;
    }
    .bot-stopped {
        background-color: #fce8e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# Variables de session
if 'bot' not in st.session_state:
    st.session_state.bot = None
if 'bot_thread' not in st.session_state:
    st.session_state.bot_thread = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False


def start_bot_thread(sector, job_title, location, connection_level, headless_mode):
    """
    Démarre le bot LinkedIn dans un thread séparé.
    
    Args:
        sector (str): Secteur d'activité
        job_title (str): Fonction
        location (str): Localisation
        connection_level (str): Niveau de connexion
        headless_mode (bool): Mode headless
    """
    # Créer une nouvelle instance du bot
    st.session_state.bot = LinkedInBot(headless=headless_mode)
    
    # Définir l'état comme en cours d'exécution
    st.session_state.is_running = True
    
    # Démarrer le bot
    st.session_state.bot.start(
        sector=sector,
        job_title=job_title,
        location=location,
        connection_level=connection_level
    )
    
    # Mettre à jour l'état une fois terminé
    st.session_state.is_running = False


def stop_bot():
    """
    Arrête le bot LinkedIn.
    """
    if st.session_state.bot and st.session_state.is_running:
        st.session_state.bot.stop()
        
        # Attendre que le thread se termine
        if st.session_state.bot_thread and st.session_state.bot_thread.is_alive():
            st.session_state.bot_thread.join(timeout=10)
            
        st.session_state.is_running = False
        
        # Fermer le navigateur
        st.session_state.bot.close()
        st.session_state.bot = None


# En-tête principal
st.markdown('<div class="main-header">LinkedIn Auto Connector</div>', unsafe_allow_html=True)
st.markdown("""
Agent automatisé pour envoyer des invitations LinkedIn sans message.
""")

# Sidebar pour les paramètres et contrôles
st.sidebar.markdown('<div class="sub-header">Configuration</div>', unsafe_allow_html=True)

# Vérification des identifiants LinkedIn
email = config.LINKEDIN_EMAIL
if not email:
    email = st.sidebar.text_input("Email LinkedIn", type="default")
    
password = config.LINKEDIN_PASSWORD
if not password:
    password = st.sidebar.text_input("Mot de passe LinkedIn", type="password")
    
# Critères de recherche
st.sidebar.markdown('<div class="sub-header">Critères de recherche</div>', unsafe_allow_html=True)

sector = st.sidebar.text_input("Secteur d'activité", value=config.DEFAULT_SECTOR)
job_title = st.sidebar.text_input("Fonction", value=config.DEFAULT_JOB_TITLE)
location = st.sidebar.text_input("Localisation", value=config.DEFAULT_LOCATION)
connection_level = st.sidebar.selectbox("Niveau de connexion", 
                                      options=["2nd", "3rd"],
                                      index=0 if config.DEFAULT_CONNECTION_LEVEL == "2nd" else 1)

# Options avancées
st.sidebar.markdown('<div class="sub-header">Options avancées</div>', unsafe_allow_html=True)

headless_mode = st.sidebar.checkbox("Mode headless (sans interface graphique)", 
                                  value=config.HEADLESS_MODE)

max_invitations_per_day = st.sidebar.slider("Invitations max. par jour", 
                                          min_value=1, 
                                          max_value=50, 
                                          value=config.MAX_INVITATIONS_PER_DAY)

min_wait_time = st.sidebar.slider("Temps min. entre actions (sec)", 
                                min_value=5, 
                                max_value=30, 
                                value=config.MIN_WAIT_TIME)

max_wait_time = st.sidebar.slider("Temps max. entre actions (sec)", 
                                min_value=10, 
                                max_value=60, 
                                value=config.MAX_WAIT_TIME)

# Boutons d'action
st.sidebar.markdown('<div class="sub-header">Action</div>', unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("Démarrer", disabled=st.session_state.is_running, type="primary"):
        if not sector and not job_title and not location:
            st.sidebar.error("Veuillez spécifier au moins un critère de recherche.")
        elif not email or not password:
            st.sidebar.error("Veuillez fournir vos identifiants LinkedIn.")
        else:
            # Sauvegarder les paramètres dans les variables d'environnement temporaires
            os.environ["LINKEDIN_EMAIL"] = email
            os.environ["LINKEDIN_PASSWORD"] = password
            os.environ["MAX_INVITATIONS_PER_DAY"] = str(max_invitations_per_day)
            os.environ["MIN_WAIT_TIME"] = str(min_wait_time)
            os.environ["MAX_WAIT_TIME"] = str(max_wait_time)
            
            # Créer et démarrer le thread du bot
            st.session_state.bot_thread = threading.Thread(
                target=start_bot_thread,
                args=(sector, job_title, location, connection_level, headless_mode)
            )
            st.session_state.bot_thread.daemon = True
            st.session_state.bot_thread.start()
            
            st.sidebar.success("Bot démarré avec succès!")
            
with col2:
    if st.button("Arrêter", disabled=not st.session_state.is_running, type="secondary"):
        stop_bot()
        st.sidebar.warning("Bot arrêté!")

# Affichage du statut actuel
st.markdown('<div class="sub-header">État actuel</div>', unsafe_allow_html=True)

if st.session_state.is_running:
    st.markdown(f"""
    <div class="bot-running">
        <h3>🟢 Bot en cours d'exécution</h3>
        <p>Le bot est en train d'envoyer des invitations LinkedIn. Vous pouvez suivre son activité ci-dessous.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="bot-stopped">
        <h3>🔴 Bot arrêté</h3>
        <p>Le bot est actuellement arrêté. Configurez les critères de recherche et cliquez sur "Démarrer" pour commencer à envoyer des invitations.</p>
    </div>
    """, unsafe_allow_html=True)

# Tableau de bord avec des statistiques
st.markdown('<div class="sub-header">Tableau de bord</div>', unsafe_allow_html=True)

# Créer deux colonnes pour les statistiques
col1, col2, col3 = st.columns(3)

# Statistiques des invitations
with col1:
    st.markdown("<h3>Invitations</h3>", unsafe_allow_html=True)
    
    # Invitations aujourd'hui
    invitations_today = db.get_invitations_sent_today()
    
    # Invitations cette semaine
    invitations_this_week = db.get_invitations_sent_this_week()
    
    # Afficher les statistiques
    st.metric(label="Invitations aujourd'hui", 
              value=invitations_today,
              delta=f"Max. {max_invitations_per_day}")
    
    st.metric(label="Invitations cette semaine", 
              value=invitations_this_week,
              delta=f"Max. {config.MAX_INVITATIONS_PER_WEEK}")

# Statistiques des sessions
with col2:
    st.markdown("<h3>Sessions récentes</h3>", unsafe_allow_html=True)
    
    # Récupérer les sessions récentes
    recent_sessions = db.get_recent_sessions(limit=5)
    
    if recent_sessions:
        # Calculer le total des invitations envoyées
        total_invitations = sum(session.invitations_sent for session in recent_sessions)
        
        # Calculer le total des profils visités
        total_profiles = sum(session.profiles_visited for session in recent_sessions)
        
        # Afficher les statistiques
        st.metric(label="Total des invitations", value=total_invitations)
        st.metric(label="Total des profils visités", value=total_profiles)
    else:
        st.info("Aucune session récente trouvée")

# Paramètres de recherche actuels
with col3:
    st.markdown("<h3>Paramètres actuels</h3>", unsafe_allow_html=True)
    
    current_settings = {
        "Secteur": sector if sector else "Non spécifié",
        "Fonction": job_title if job_title else "Non spécifiée",
        "Localisation": location if location else "Non spécifiée",
        "Niveau de connexion": connection_level,
        "Mode headless": "Activé" if headless_mode else "Désactivé"
    }
    
    for key, value in current_settings.items():
        st.text(f"{key}: {value}")

# Historique des invitations
st.markdown('<div class="sub-header">Historique des invitations récentes</div>', unsafe_allow_html=True)

# Récupérer les invitations récentes
recent_invitations = db.get_recent_invitations(limit=50)

if recent_invitations:
    # Convertir en DataFrame pour un affichage plus propre
    invitations_data = []
    
    for invitation in recent_invitations:
        invitations_data.append({
            "Date": invitation.invitation_sent_at.strftime("%Y-%m-%d %H:%M"),
            "Nom": invitation.profile_name,
            "Titre": invitation.profile_title or "-",
            "Entreprise": invitation.profile_company or "-",
            "Localisation": invitation.profile_location or "-",
            "Critères": f"Secteur: {invitation.sector or '-'}, Fonction: {invitation.job_title or '-'}"
        })
    
    df_invitations = pd.DataFrame(invitations_data)
    st.dataframe(df_invitations)
else:
    st.info("Aucune invitation récente trouvée")

# Ajout d'un pied de page avec des informations importantes
st.markdown('<div class="sub-header">Informations importantes</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
<h4>⚠️ Avertissement</h4>
<p>Cet outil est conçu pour un usage personnel et éducatif. L'utilisation abusive peut entraîner des restrictions sur votre compte LinkedIn.</p>

<h4>🔒 Sécurité</h4>
<p>Vos identifiants LinkedIn sont uniquement stockés temporairement en mémoire et ne sont pas sauvegardés. L'utilisation des cookies permet d'éviter de saisir vos identifiants à chaque exécution.</p>

<h4>💡 Conseils d'utilisation</h4>
<ul>
<li>Limitez le nombre d'invitations à moins de 100 par semaine pour éviter les restrictions.</li>
<li>Variez vos critères de recherche pour diversifier votre réseau.</li>
<li>Assurez-vous que le bot ne tourne pas en continu pendant de longues périodes.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Fonction principale pour le mode développement
if __name__ == "__main__":
    # Cette section est exécutée uniquement si le script est exécuté directement
    pass
