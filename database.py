"""
Module de gestion de la base de données pour l'agent LinkedIn automatisé.
"""
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# Créer une instance de moteur de base de données
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class ProfileInvitation(Base):
    """Modèle pour stocker les invitations envoyées."""

    __tablename__ = "profile_invitations"

    id = Column(Integer, primary_key=True)
    profile_id = Column(String(100), nullable=False, unique=True)
    profile_name = Column(String(255), nullable=False)
    profile_title = Column(String(255))
    profile_company = Column(String(255))
    profile_location = Column(String(255))
    profile_url = Column(String(500), nullable=False)
    invitation_sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    accepted = Column(Boolean, default=False)
    sector = Column(String(100))
    job_title = Column(String(100))
    search_location = Column(String(100))
    connection_level = Column(String(20))
    notes = Column(Text)

    def __repr__(self):
        return f"<ProfileInvitation(profile_name='{self.profile_name}', sent_at='{self.invitation_sent_at}')>"


class SessionStats(Base):
    """Modèle pour stocker les statistiques de session."""

    __tablename__ = "session_stats"

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    profiles_visited = Column(Integer, default=0)
    invitations_sent = Column(Integer, default=0)
    sector = Column(String(100))
    job_title = Column(String(100))
    location = Column(String(100))
    connection_level = Column(String(20))
    notes = Column(Text)

    def __repr__(self):
        return f"<SessionStats(start_time='{self.start_time}', invitations_sent={self.invitations_sent})>"


def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(engine)


def add_profile_invitation(
    profile_id, profile_name, profile_url, title="", company="", location="",
    sector="", job_title="", search_location="", connection_level=""
):
    """
    Ajoute une nouvelle invitation de profil à la base de données.
    
    Args:
        profile_id (str): Identifiant unique du profil LinkedIn
        profile_name (str): Nom du profil
        profile_url (str): URL du profil
        title (str, optional): Titre professionnel
        company (str, optional): Entreprise actuelle
        location (str, optional): Localisation du profil
        sector (str, optional): Secteur d'activité recherché
        job_title (str, optional): Fonction recherchée
        search_location (str, optional): Localisation recherchée
        connection_level (str, optional): Niveau de connexion
        
    Returns:
        ProfileInvitation: L'objet invitation créé
    """
    session = Session()
    profile_invitation = ProfileInvitation(
        profile_id=profile_id,
        profile_name=profile_name,
        profile_title=title,
        profile_company=company,
        profile_location=location,
        profile_url=profile_url,
        sector=sector,
        job_title=job_title,
        search_location=search_location,
        connection_level=connection_level,
    )
    
    try:
        session.add(profile_invitation)
        session.commit()
        return profile_invitation
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_invitations_sent_today():
    """
    Récupère le nombre d'invitations envoyées aujourd'hui.
    
    Returns:
        int: Nombre d'invitations envoyées aujourd'hui
    """
    session = Session()
    today = datetime.datetime.utcnow().date()
    try:
        count = session.query(ProfileInvitation).filter(
            ProfileInvitation.invitation_sent_at >= today
        ).count()
        return count
    finally:
        session.close()


def get_invitations_sent_this_week():
    """
    Récupère le nombre d'invitations envoyées cette semaine.
    
    Returns:
        int: Nombre d'invitations envoyées cette semaine
    """
    session = Session()
    today = datetime.datetime.utcnow().date()
    # Calcul du premier jour de la semaine (lundi)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    try:
        count = session.query(ProfileInvitation).filter(
            ProfileInvitation.invitation_sent_at >= start_of_week
        ).count()
        return count
    finally:
        session.close()


def start_new_session(sector="", job_title="", location="", connection_level=""):
    """
    Commence une nouvelle session de recherche.
    
    Args:
        sector (str): Secteur d'activité ciblé
        job_title (str): Fonction ciblée
        location (str): Localisation ciblée
        connection_level (str): Niveau de connexion ciblé
        
    Returns:
        SessionStats: L'objet session créé avec son ID
    """
    session = Session()
    new_session = SessionStats(
        sector=sector,
        job_title=job_title,
        location=location,
        connection_level=connection_level,
    )
    
    try:
        session.add(new_session)
        session.commit()
        return new_session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_session_stats(session_id, profiles_visited=0, invitations_sent=0, end_session=False):
    """
    Met à jour les statistiques d'une session.
    
    Args:
        session_id (int): ID de la session
        profiles_visited (int): Nombre de profils visités à ajouter
        invitations_sent (int): Nombre d'invitations envoyées à ajouter
        end_session (bool): Si True, marque la session comme terminée
        
    Returns:
        SessionStats: L'objet session mis à jour
    """
    db_session = Session()
    try:
        session_stats = db_session.query(SessionStats).filter_by(id=session_id).first()
        if not session_stats:
            return None
            
        session_stats.profiles_visited += profiles_visited
        session_stats.invitations_sent += invitations_sent
        
        if end_session:
            session_stats.end_time = datetime.datetime.utcnow()
            
        db_session.commit()
        return session_stats
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def get_recent_sessions(limit=10):
    """
    Récupère les sessions récentes.
    
    Args:
        limit (int): Nombre maximum de sessions à récupérer
        
    Returns:
        list: Liste des sessions récentes
    """
    session = Session()
    try:
        return session.query(SessionStats).order_by(
            SessionStats.start_time.desc()
        ).limit(limit).all()
    finally:
        session.close()


def get_recent_invitations(limit=100):
    """
    Récupère les invitations récentes.
    
    Args:
        limit (int): Nombre maximum d'invitations à récupérer
        
    Returns:
        list: Liste des invitations récentes
    """
    session = Session()
    try:
        return session.query(ProfileInvitation).order_by(
            ProfileInvitation.invitation_sent_at.desc()
        ).limit(limit).all()
    finally:
        session.close()


# Initialiser la base de données au démarrage
init_db()
