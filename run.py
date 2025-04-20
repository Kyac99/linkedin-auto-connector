"""
Script d'entrée pour démarrer l'application LinkedIn Auto Connector.
"""
import os
import subprocess
import sys

def main():
    """
    Point d'entrée principal de l'application.
    Vérifie les dépendances et lance l'interface Streamlit.
    """
    print("Démarrage de LinkedIn Auto Connector...")
    
    # Vérifier si les dépendances sont installées
    try:
        import streamlit
        import selenium
        import webdriver_manager
    except ImportError:
        print("Installation des dépendances requises...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Lancement de l'application Streamlit
    print("Lancement de l'interface utilisateur...")
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
