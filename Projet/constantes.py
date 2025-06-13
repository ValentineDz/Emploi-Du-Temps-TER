"""
Fichier contenant toutes les constantes générales de l'application Dash pour le générateur d'emploi du temps.

Ce fichier centralise :
- Les niveaux scolaires utilisés (6e à 3e) ;
- Les jours de la semaine (étiquettes et ordre) ;
- Les plages horaires types configurables ;
- Les catégories d'options disponibles (langues, arts, sport, etc.) ;
- Des données par défaut pour l'interface :
    * Classes,
    * Professeurs,
    * Salles.

Il contient également trois DataFrames (`DF_CLASSES`, `DF_PROFS`, `DF_SALLES`) pré-remplis
pour servir de base ou d'exemple lors de l'import de données.

La fonction `initialiser_fichier_si_absent()` est appelée en fin de script pour garantir
la présence des fichiers nécessaires à l'exécution de l'application.
"""
import pandas as pd
from fonctions import initialiser_fichier_si_absent

NIVEAUX = ["6e", "5e", "4e", "3e"]

FICHIER_INTERFACE = "data/data_interface.json"

JOURS_SEMAINE = [
                        {'label': ' Lundi', 'value': 'Lundi'},
                        {'label': ' Mardi', 'value': 'Mardi'},
                        {'label': ' Mercredi', 'value': 'Mercredi'},
                        {'label': ' Jeudi', 'value': 'Jeudi'},
                        {'label': ' Vendredi', 'value': 'Vendredi'},
                    ]
ORDRE_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
# Données des horaires
HORAIRES_LABELS = [
    "Début de cours minimum",
    "Fin maximum des cours du matin",
    "Début minimum des cours de l'après-midi",
    "Fin de cours maximum"
]

# liste de choix des options
CATEGORIES_OPTIONS = {
    "Options langues régionales": [
        {"label": " Alsacien", "value": "Alsacien"},
        {"label": " Basque", "value": "Basque"},
        {"label": " Breton", "value": "Breton"},
        {"label": " Corse", "value": "Corse"},
        {"label": " Flamand", "value": "Flamand"}
    ],
    "Options langues anciennes": [
        {"label": " Latin", "value": "Latin"},
        {"label": " Grec ancien", "value": "Grec"}
    ],
    "Options artistiques": [
        {"label": " Arts plastiques", "value": "Arts_plastiques"},
        {"label": " Cinéma", "value": "Cinéma"},
        {"label": " Danse", "value": "Danse"},
        {"label": " Musique", "value": "Musique"},
        {"label": " Théâtre", "value": "Théâtre"}
    ],
    "Options sportives": [
        {"label": " Sports (global)", "value": "Sport"},
        {"label": " Athlétisme", "value": "Athletisme"},
        {"label": " Escalade", "value": "Escalade"},
        {"label": " Football", "value": "Football"},
        {"label": " Natation", "value": "Natation"}
    ],
    "Options de sciences et/ou technologie": [
        {"label": " Informatique", "value": "Informatique"},
        {"label": " Robotique", "value": "Robotique"}
    ]
}

OUI_NON = [{"label": " Oui", "value": "oui"}, {"label": " Non", "value": "non"}]

CLASSES_DEFAUT = [
                {"Classe": "5e1", "Niveau": "5e", "Effectif": "26", "Dependances": "", "MatiereGroupe": ""},
                {"Classe": "5e2", "Niveau": "5e", "Effectif": "30", "Dependances": "", "MatiereGroupe": ""},
                {"Classe": "5ESP1", "Niveau": "5e", "Effectif": "12", "Dependances": "5e1,5e2", "MatiereGroupe": "Espagnol", "TypeGroupe": "LV2"}
            ]

PROFS_DEFAUT = [
                {
                    "Civilite": "Mme", "Nom": "Durand", "Prenom": "Marie",
                    "Niveaux": "5e,4e", "Matieres": "Français", "Volume": 18,
                    "Duree": "1.5", "SallePref": ""
                },
                {
                    "Civilite": "M.", "Nom": "Dupont", "Prenom": "Paul",
                    "Niveaux": "6e,5e", "Matieres": "Mathématiques", "Volume": 20,
                    "Duree": "2", "SallePref": "A1"
                }
            ]

SALLES_DEFAUT = [{
            "Nom": "A1",
            "Matieres": "",
            "Capacite": 30
        },
        {
            "Nom": "B1",
            "Matieres": "Physique-chimie,SVT",
            "Capacite": 25
        }]

DF_CLASSES = pd.DataFrame({
        "Classe": ["6e1", "6e2", "6ESP1"],
        "Niveau": ["6e", "6e", "6e"],
        "Effectif": [25, 26, 12],
        "Dependances": ["", "", "6e1,6e2"],
        "MatiereGroupe": ["", "", "Espagnol"]
    })

DF_PROFS = pd.DataFrame([
        {
            "Civilite": "M.",
            "Nom": "Dupont",
            "Prenom": "Paul",
            "Niveaux": "6e,5e",
            "Matieres": "Mathématiques",
            "Volume": 20,
            "Duree": 2,
            "SallePref": "101"
        },
        {
            "Civilite": "Mme",
            "Nom": "Durand",
            "Prenom": "Marie",
            "Niveaux": "6e,5e,4e,3e",
            "Matieres": "Français",
            "Volume": 18,
            "Duree": 1,
            "SallePref": ""
        }
    ])

DF_SALLES = pd.DataFrame([
        {
            "Nom": "Salle Arts Plastiques",
            "Matieres": "Arts Plastiques",
            "Capacite": 35
        },
        {
            "Nom": "A1",
            "Matieres": "",
            "Capacite": 30
        }
    ])

INITIALISATION_FICHIER = initialiser_fichier_si_absent()


# Page de contraintes : 
CONSTRAINTS = {
    "Disponible": {
        "bg": "#90EE90",
        "color": "black"
    },
    "Indisponibilité partielle": {
        "bg": "#FFD580",
        "color": "black"
    },
    "Indisponibilité totale": {
        "bg": "#FF7F7F",
        "color": "white"
    }
}