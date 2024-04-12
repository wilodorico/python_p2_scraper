# Script Scraper de données de livres

Ce projet est un script scraper de livres pour le site [Book to Scrape](http://books.toscrape.com).

Le script récupère les informations sur tous les livres de chaque catégorie et télécharge leur image.

Données récupérées :
- l'URL du livre
- le titre
- la description
- la catégorie
- l'UPC (code produit universel)
- le prix hors taxe
- le prix avec taxe
- la quantité disponible
- le classement du livre par étoiles
- l'URL de l'image du livre

 
Les données sont écrites dans un fichier CSV nommé de la catégorie du livre + la date du jour.

Les images et le fichier CSV sont stockés dans un dossier nommé de leur catégorie.

Chaque dossier catégorie est stocké dans le dossier **bookscrap_files**

## Comment installer le projet
1. Ouvrer un terminal
2. Placer vous dans le dossier où vous voulez cloner le projet
3. Cloner le projet avec la commande : `https://github.com/wilodorico/python_p2_scraper.git`

## Créer et activer l'environnement virtuel
1. Placer vous sur le projet
2. Créer l'environnement virtuel avec la commande : `python -m env venv`
3. Activer l'environnement virtuel :
- Pour Windows : `env\Scripts\activate`
- Pour MacOS et linux :  `source env/bin/activate`

## Installation des packages
Une fois que vous avez activé l'environnement virtuel, installez les packages à l'aide du fichier `requirements.txt` 

Exécuter la commande : `pip install -r requirements.txt`

## Comment lancer le script
1. S'assurer d'être dans le bon répertoire du projet via le terminal
2. Activer l'environnement virtuel
3. Exécuter le script `main.py` avec la commande : `python main.py`

Une fois exécuté le script va scraper les données des livres et télécharger les images

