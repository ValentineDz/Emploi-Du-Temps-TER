# Emploi du Temps - TER : Conception d'un outil d'expérimentation de scénarios et de génération d'emploi du temps

## Présentation
Ce projet a été développé dans le cadre d’un TER (Travail d’Étude et de Recherche)  de Master 1 MIASHS parcours Informatique et Cognition de l’Université Grenoble Alpes. Il propose une application de génération automatique d’emplois du temps pour les établissements scolaires de type collège.

L’objectif est de fournir une solution, capable de gérer un grand nombre de contraintes pédagogiques, matérielles et organisationnelles, tout en restant modulaire et adaptée aux besoins des utilisateurs. L’application met l’accent sur la lisibilité des résultats, l’ergonomie de l’interface et la transparence dans le traitement des contraintes.

## Objectifs du projet
- Proposer une solution locale, autonome, et simple à utiliser pour la création d’emplois du temps.
- Intégrer des contraintes telles que : disponibilités, volumes horaires, gestion des salles, sous-groupes, enchaînements de cours, poids du cartable.
- Permettre à l’utilisateur de visualiser les résultats, de comprendre pourquoi une contrainte n’a pas pu être respectée, et d’exporter les emplois du temps générés.
- Assurer une séparation claire entre l’interface (saisie, affichage) et le solveur (résolution de contraintes).
- Permettre une adaptation facile à d’autres établissements ou contextes pédagogiques.


## Architecture du projet
Le projet repose sur deux composants principaux :

- **Interface utilisateur** : développée avec le framework [Dash](https://dash.plotly.com/) (Python), elle permet de renseigner, visualiser et exporter les données (saisies, contraintes, résultats).
- **Solveur de contraintes** : développé avec [Google OR-Tools](https://developers.google.com/optimization), il transforme le problème d’emploi du temps en un problème d’optimisation à contraintes.

Les données sont échangées entre ces deux modules via des fichiers JSON structurés.


## Technologies utilisées
- Langage principal : **Python 3.10+**
- Interface : **Dash**, **dash-mantine-components**
- Solveur : **OR-Tools**
- Formats d’échange : **JSON** pour les données, **PDF** pour l’export
- Environnement : **local uniquement** (pas de base de données, ni de serveur distant)


## Installation
### 1. Prérequis
- Système d’exploitation : Windows, macOS, ou Linux
- Python 3.10 ou supérieur installé (avec `pip`)
- Navigateur web à jour (Chrome, Firefox, Edge...)

### 2. Cloner le dépôt
Ouvrir un terminal et exécuter :
```bash
git clone https://github.com/ValentineDz/Emploi-Du-Temps-TER.git
cd Emploi-Du-Temps-TER
```

### 3. Installer les dépendances
Dans le dossier du projet, exécuter :
```bash
pip install -r requirements.txt
```

### 4. Lancer l’application
Dans le dossier du projet, lancer :
```bash
python app.py
```
Puis ouvrir un navigateur à l’adresse suivante : [http://127.0.0.1:8050](http://127.0.0.1:8050)


## Utilisation
Une fois l’application lancée :
- L’utilisateur peut **saisir ou importer** les données nécessaires : enseignants, classes, matières, salles, options, langues, calendrier...
- Il peut ensuite **générer un emploi du temps** à l’aide du bouton prévu à cet effet.
- Les **résultats** sont consultables directement via l’interface : affichage visuel des emplois du temps par classe, salle ou professeur.
- Il est possible d’**exporter les emplois du temps** en **PDF**.
- Toutes les saisies et modifications sont **enregistrées automatiquement** dans les fichiers JSON (données stockées localement).


## Procédure de mise à jour
Pour mettre à jour l’application tout en conservant les données :
1. **Arrêter l’application** avec `CTRL + C` dans le terminal.
2. **Sauvegarder** le fichier `data/data_interface.json` si nécessaire.
3. Mettre à jour le projet :
    - Si cloné avec Git :
    ```bash
    git pull
    ```
    - Sinon, télécharger la dernière archive ZIP depuis GitHub.
4. Réinstaller les dépendances si le fichier `requirements.txt` a été modifié :
```bash
pip install -r requirements.txt
```
5. Relancer l’application :
```bash
python app.py
```


## Licence
Ce projet a été réalisé à des fins pédagogiques dans le cadre d’un TER à l’Université Grenoble Alpes.
Il peut être utilisé, modifié ou adapté à des fins non commerciales. 


## Auteurs
Projet développé par six étudiants du Master MIASHS – Université Grenoble Alpes : 
- M. Arbaut Jean-Baptiste
- M. Deschamps Kylian
- Mme Duez-Faurie Valentine
- M. Eramil Kadir
- M. Pilloud Aubry
- Mme Tropel Célia

Maître d’ouvrage : 
- Mme Landry Aurélie


## Documentation
La documentation complète, incluant le manuel d’installation, est disponible dans le dossier "Documents".
L'ensemble des documents du premier et du second semestre sont sur le [Google Drive du projet](https://drive.google.com/drive/folders/1gjVmAVPBoRPbrPL_emGiR3nooUzGTV3G?usp=sharing)
