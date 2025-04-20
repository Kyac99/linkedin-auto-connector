# LinkedIn Auto Connector

Un agent automatisé pour LinkedIn qui envoie des invitations de connexion sans message à des profils ciblés.

## Objectif

Cet outil permet de :
- Se connecter automatiquement à un compte LinkedIn
- Identifier et cibler des profils selon des critères définis (secteur, métier, localisation, etc.)
- Envoyer des invitations sans message d'accompagnement

## Fonctionnalités

1. **Connexion LinkedIn automatisée**
   - Via navigateur simulé (Selenium)
   - Option d'utiliser les cookies de session

2. **Définition de la cible**
   - Filtrage par secteur d'activité
   - Filtrage par fonction
   - Filtrage par localisation géographique
   - Filtrage par niveau de connexion

3. **Automatisation des invitations**
   - Parcours automatique des résultats de recherche
   - Envoi d'invitations sans message
   - Respect des limites LinkedIn (configurable)
   - Comportement humanisé (temps d'attente aléatoire)

4. **Dashboard minimal**
   - Suivi des invitations envoyées
   - Historique des profils contactés
   - Configuration des critères de ciblage
   - Contrôles pour lancer/arrêter l'agent

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/Kyac99/linkedin-auto-connector.git
cd linkedin-auto-connector
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configuration :
   - Créez un fichier `.env` basé sur le modèle `.env.example`
   - Ajoutez vos identifiants LinkedIn

## Utilisation

1. Lancez l'interface web :
```bash
python app.py
```

2. Accédez à l'interface via votre navigateur à l'adresse `http://localhost:8501`

3. Configurez vos critères de recherche et lancez l'agent

## Sécurité

- L'outil introduit des délais aléatoires entre les actions pour imiter un comportement humain
- Le nombre d'invitations est limité et configurable
- Pause automatique lorsque la limite est atteinte

## Avertissement

Cet outil est destiné à un usage personnel et éducatif. L'utilisation abusive peut entraîner des restrictions sur votre compte LinkedIn. Utilisez-le de manière responsable et respectez les conditions d'utilisation de LinkedIn.

## Stack Technique

- Python
- Selenium
- Streamlit (interface utilisateur)
- SQLite (stockage des données)
