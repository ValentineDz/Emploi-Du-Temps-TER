"""
Ce fichier regroupe l'ensemble des fonctions utilitaires liées à l'interface Dash de génération d'emplois du temps scolaires.
Il comprend des outils pour :

- Générer ou charger le fichier `data_interface.json` qui contient toutes les données de l'interface utilisateur.
- Mettre à jour dynamiquement des sections de ce fichier JSON.
- Générer les blocs nécessaires à l'affichage (professeurs, salles, horaires).
- Transformer les données de l'interface en configuration exploitable par le solveur OR-Tools.
- Charger les statistiques sur le respect des contraintes.

Ce module est central pour la gestion des données entre l'interface utilisateur et le solveur.
"""

# Bibliothèques
import os
import json
import pandas as pd
import dash
from dash import ctx, Input, Output, State, callback, dash_table, html, dcc, no_update, ALL, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from main_dash import app
from styles import *
from datetime import datetime, timedelta
from textes import *

import base64
import io
import re

from styles import style_liste_choix

import json
import math
import copy


from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape

jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
#################################################################################################################################################################
# Fonction pour générer le squelette JSON
def generer_squelette_json_interface():
    """
    Génère un squelette JSON structuré selon l'organisation réelle de l'interface utilisateur.
    """
    squelette = {
        "1_horaires": {
            "jours_classiques": [      
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi"
            ],
            "jours_particuliers": ["Mercredi"],
            "horaires_classiques": {},
            "duree_creneau": None,
            "recreations": None,
            "pause_meridienne": "00:00"
        },
        "2_langues_et_options": {
            "lv1": [],
            "lv2": [],
            "lv3_active": False,
            "lv3": [],
            "lv4_active": False,
            "lv4": [],
            "autres_langues": {
                "lv1": [],
                "lv2": [],
                "lv3": [],
                "lv4": []
            },
            "options": {
                "predefinies": [],
                "autres": [],
            }
        },
        "3_ressources": {
            "classes": [
                {"Classe": "6e1", "Niveau": "6e", "Effectif": "26", "Dependances": "", "MatiereGroupe": ""},
                {"Classe": "6e2", "Niveau": "6e", "Effectif": "30", "Dependances": "", "MatiereGroupe": ""},
                {"Classe": "6ESP1", "Niveau": "6e", "Effectif": "12", "Dependances": "6e1,6e2", "MatiereGroupe": "Espagnol"}
            ],
            "salles": [
                {"Nom": "A1", "Matieres": "", "Capacite": 30},
                {"Nom": "B1", "Matieres": "Physique-chimie,SVT", "Capacite": 25}
            ],
            "professeurs": [
                {"Civilite": "Mme", "Nom": "Durand", "Prenom": "Marie", "Niveaux": "5e,4e", "Matieres": "Français", "Volume": 18, "Duree": "1.5", "SallePref": ""},
                {"Civilite": "M.", "Nom": "Dupont", "Prenom": "Paul", "Niveaux": "6e,5e", "Matieres": "Mathématiques", "Volume": 20, "Duree": "2", "SallePref": "A1"}
            ]
        },
       "4_programme_national": {
            "6e": [
                {"Discipline": "Français", "VolumeHoraire": 4.5},
                {"Discipline": "Mathématiques", "VolumeHoraire": 4.5},
                {"Discipline": "Histoire-Géographie-EMC", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante", "VolumeHoraire": 4},
                {"Discipline": "Sciences (SVT et Physique-Chimie)", "VolumeHoraire": 3},
                {"Discipline": "EPS", "VolumeHoraire": 4},
                {"Discipline": "Arts plastiques", "VolumeHoraire": 1},
                {"Discipline": "Musique", "VolumeHoraire": 1},
            ],
            "5e": [
                {"Discipline": "Français", "VolumeHoraire": 4.5},
                {"Discipline": "Mathématiques", "VolumeHoraire": 3.5},
                {"Discipline": "Histoire-Géographie-EMC", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante 1", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante 2", "VolumeHoraire": 2.5},
                {"Discipline": "SVT", "VolumeHoraire": 1.5},
                {"Discipline": "Physique-Chimie", "VolumeHoraire": 1.5},
                {"Discipline": "Technologie", "VolumeHoraire": 1.5},
                {"Discipline": "EPS", "VolumeHoraire": 3},
                {"Discipline": "Arts plastiques", "VolumeHoraire": 1},
                {"Discipline": "Musique", "VolumeHoraire": 1},
            ],
            "4e": [
                {"Discipline": "Français", "VolumeHoraire": 4.5},
                {"Discipline": "Mathématiques", "VolumeHoraire": 3.5},
                {"Discipline": "Histoire-Géographie-EMC", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante 1", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante 2", "VolumeHoraire": 2.5},
                {"Discipline": "SVT", "VolumeHoraire": 1.5},
                {"Discipline": "Physique-Chimie", "VolumeHoraire": 1.5},
                {"Discipline": "Technologie", "VolumeHoraire": 1.5},
                {"Discipline": "EPS", "VolumeHoraire": 3},
                {"Discipline": "Arts plastiques", "VolumeHoraire": 1},
                {"Discipline": "Musique", "VolumeHoraire": 1},
            ],
            "3e": [
                {"Discipline": "Français", "VolumeHoraire": 4},
                {"Discipline": "Mathématiques", "VolumeHoraire": 3.5},
                {"Discipline": "Histoire-Géographie-EMC", "VolumeHoraire": 3.5},
                {"Discipline": "Langue vivante 1", "VolumeHoraire": 3},
                {"Discipline": "Langue vivante 2", "VolumeHoraire": 2.5},
                {"Discipline": "SVT", "VolumeHoraire": 1.5},
                {"Discipline": "Physique-Chimie", "VolumeHoraire": 1.5},
                {"Discipline": "Technologie", "VolumeHoraire": 1.5},
                {"Discipline": "EPS", "VolumeHoraire": 3},
                {"Discipline": "Arts plastiques", "VolumeHoraire": 1},
                {"Discipline": "Musique", "VolumeHoraire": 1},
            ],
            "emc": {
                "6e": { "inclus": "oui", "volume": None },
                "5e": { "inclus": "oui", "volume": None },
                "4e": { "inclus": "oui", "volume": None },
                "3e": { "inclus": "oui", "volume": None }
            }
        },
        "affichage": {
            "horaires_affichage": [],
            "professeurs_affichage": [],
            "volume_horaire_affichage": {},
            "salles_affichage": []
        },
        "contraintes": {
            "profs": {
                "indisponibilites_partielles": {},
                "indisponibilites_totales": {}
            },
            "groupes": {
                "indisponibilites_partielles": {},
                "indisponibilites_totales": {}
            },
            "salles": {
                "indisponibilites_partielles": {},
                "indisponibilites_totales": {}
            },
            "contraintes_3_4": {
            "planning": [],
            "cours_planning": [],
            "enchainement": []
            }
        },
        "contraintes_additionnelles": {
            "ordre_contraintes": [],
            "poids_par_niveau": {},
                "cantine_permanence": {
                "capacite_cantine": None,
                "taux_cantine": None,
                "capacite_permanence": None,
                "fin_jeunes_plus_tot": "non"
                },
            "fin_jeunes_plus_tot": False
        },
    }

    return squelette

FICHIER_INTERFACE = "data/data_interface.json"

def initialiser_fichier_si_absent():
    """
    Initialise le fichier `data_interface.json` s'il est absent, vide,
    ou invalide (structure manquante ou corrompue).
    """
    chemin = FICHIER_INTERFACE
    fichier_invalide = False

    if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = json.load(f)
            # Vérifie que les principales sections existent
            cles_essentielles = ["1_horaires", "2_langues_et_options", "3_ressources", "4_programme_national"]
            if not all(cle in contenu for cle in cles_essentielles):
                fichier_invalide = True
        except Exception:
            fichier_invalide = True
    else:
        fichier_invalide = True

    if fichier_invalide:
        # print("Fichier JSON absent, vide ou invalide : génération d'un squelette par défaut.")
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        donnees = generer_squelette_json_interface()
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)


def charger_donnees_interface():
    """
    Charge les données depuis le fichier JSON `data_interface.json`.
    Retourne un dictionnaire vide en cas d'erreur.
    """
    try:
        with open("data/data_interface.json", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    return data

def sauvegarder_donnees_interface(data, force=False):
    """
    Sauvegarde le fichier JSON complet. Par défaut, si les données semblent trop incomplètes,
    on empêche l'écrasement sauf si `force=True`.
    """
    if not isinstance(data, dict):
        return

    # Liste de clés essentielles attendues dans le fichier final
    cles_essentielles = ["1_horaires", "2_langues_et_options", "3_ressources", "4_programme_national"]
    if not force and not all(k in data for k in cles_essentielles):
        return

    os.makedirs("data", exist_ok=True)
    with open("data/data_interface.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_dicts(d1, d2):
    """
    Fusionne récursivement deux dictionnaires en conservant les clés de d1 et ajoutant/modifiant celles de d2.
    """
    for k, v in d2.items():
        if (
            k in d1
            and isinstance(d1[k], dict)
            and isinstance(v, dict)
        ):
            merge_dicts(d1[k], v)
        else:
            d1[k] = v
    return d1

def mettre_a_jour_section_interface(section, nouvelle_valeur):
    """
    Met à jour une section spécifique du fichier JSON interface sans écraser les autres données.
    La section peut être un chemin séparé par '.' pour sous-clés (ex : "4_programme_national.emc").
    """
    data = charger_donnees_interface()
    keys = section.split('.')
    d = data

    # Navigue jusqu'au dernier niveau
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]

    last_key = keys[-1]

    # Si la section existait déjà et que c'est un dict, on merge sinon on remplace
    if last_key in d and isinstance(d[last_key], dict) and isinstance(nouvelle_valeur, dict):
        d[last_key] = merge_dicts(d[last_key], nouvelle_valeur)
    else:
        d[last_key] = nouvelle_valeur

    sauvegarder_donnees_interface(data)

#################################################################################################################################################################

# Pour affichage du calendrier
def mois_de_x_n(x):
    """Renvoie le mois de x de l'année N pour focus_date"""
    annee = datetime.today().year
    return datetime(annee, x, 1)

def mois_de_x_n1(x):
    """Renvoie le mois de x de l'année N+1 pour focus_date"""
    annee = datetime.today().year + 1
    return datetime(annee, x, 1)

# Liste de choix des langues 
def generate_lang_selection(lang_id):
    """
    Génère un composant Dash contenant une checklist de langues et un espace pour les langues personnalisées.

    Paramètres :
    - lang_id (str) : identifiant unique pour les composants (permet différencier LV1, LV2, etc.).
    """
    options = [
        {'label': ' Allemand', 'value': 'Allemand'},
        {'label': ' Anglais', 'value': 'Anglais'},
        {'label': ' Arabe', 'value': 'Arabe'},
        {'label': ' Chinois', 'value': 'Chinois'},
        {'label': ' Espagnol', 'value': 'Espagnol'},
        {'label': ' Italien', 'value': 'Italien'},
    ]
    options.append({'label': ' Autre', 'value': 'Autre'}) 
    return html.Div([
        # Toutes les langues dans une seule checklist
        dcc.Checklist(
            id=f"langues-{lang_id}",
            options=options,
            value=[],
            inline=True,
            style=style_liste_choix
        ),
        html.Div(id=f"autre-langue-container-{lang_id}"),
        dcc.Store(id=f"nb-champs-{lang_id}", data=0)
    ])

# Fonction pour formater les options
def formater_options(options):
    """
    Formate une liste d'options pour affichage dans un composant Dash.
    Ajoute un style spécifique à chaque étiquette.

    Paramètres :
    - options (list[dict]) : liste de dictionnaires avec les clés 'label' et 'value'.
    """
    return [
        {
            'label': html.Span(opt['label'], style={
                'display': 'inline-block',
                'width': '150px',
                'marginLeft': '5px' 
            }),
            'value': opt['value']
        }
        for opt in options
    ]

def valider_format_horaire(horaire):
    """
    Vérifie si un horaire est au format HH:MM et le normalise.
    Retourne une chaîne vide si le format est incorrect.
    """
    try:
        if isinstance(horaire, str) and ":" in horaire:
            h, m = horaire.split(":")
            h, m = int(h), int(m)
            if 0 <= h <= 23 and 0 <= m <= 59:
                return f"{h:02d}:{m:02d}"
    except:
        pass
    return ""

def ajuster_date_fin(date_debut_str):
    """
    Ajoute 16 jours à la date de début, puis ajuste au lundi suivant.
    Retourne la date formatée (YYYY-MM-DD) ou None si erreur.
    """
    try:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        date_fin_provisoire = date_debut + timedelta(days=16)
        jours_a_ajouter = (7 - date_fin_provisoire.weekday()) % 7
        date_fin = date_fin_provisoire + timedelta(days=jours_a_ajouter)
        return date_fin.strftime("%Y-%m-%d")
    except Exception:
        return None

def maj_donnees_programme_par_niveau(data, niveau, table_data, emc_inclus, emc_volume):
    """
    Met à jour les données du programme national pour un niveau donné :
    - Disciplines et volumes horaires
    - Inclusion et volume de l'EMC

    Retourne le dictionnaire `data` modifié.
    """
    if "4_programme_national" not in data:
        data["4_programme_national"] = {}

    # Met à jour le tableau de disciplines pour le niveau
    data["4_programme_national"][niveau] = [
        d for d in table_data if "enseignement moral et civique" not in d.get("Discipline", "").lower()
    ]

    # Met à jour la section EMC sans toucher au reste
    if "emc" not in data["4_programme_national"]:
        data["4_programme_national"]["emc"] = {}

    try:
        volume = float(emc_volume) if emc_volume else None
    except Exception:
        volume = None

    data["4_programme_national"]["emc"][niveau] = {"inclus": emc_inclus, "volume": volume}

    return data

#################################################################################################################################################################

def calculer_horaires_affichage():
    """
    Calcule les horaires d'affichage avec :
    - Récréation de 15min après 2e créneau du matin
    - Récréation après la moitié des créneaux de l'après-midi (si >= 4)
    - Format : ["08:25 - 09:20", "09:20 - 10:15", "10:30 - 11:25", ...]
    """
    from datetime import datetime, timedelta

    data = charger_donnees_interface()
    horaires = data.get("1_horaires", {})
    horaires_cl = horaires.get("horaires_classiques", {})

    debut_matin = horaires_cl.get("Début de cours minimum", "")
    fin_matin = horaires_cl.get("Fin maximum des cours du matin", "")
    debut_apm = horaires_cl.get("Début minimum des cours de l'après-midi", "")
    fin_apm = horaires_cl.get("Fin de cours maximum", "")
    duree_creneau = horaires.get("duree_creneau", 55)
    duree_recre = horaires.get("recreations", 15)

    def parse(h):
        try:
            h, m = map(int, h.strip().split(":"))
            return datetime(2000, 1, 1, h, m)
        except:
            return None

    h_matin = parse(debut_matin)
    h_matin_fin = parse(fin_matin)
    h_apm = parse(debut_apm)
    h_apm_fin = parse(fin_apm)

    if not all([h_matin, h_matin_fin, h_apm, h_apm_fin]):
        # print("Données horaires incomplètes : pas de génération.")
        return

    horaires = []

    # ----- MATIN -----
    current = h_matin
    i = 0
    while True:
        start = current
        end = start + timedelta(minutes=duree_creneau)
        if end > h_matin_fin + timedelta(seconds=1):
            break
        horaires.append((start, end))
        current = end

        # Récré après 2e créneau
        i += 1
        if i == 2:
            current += timedelta(minutes=duree_recre)

    # ----- PAUSE MIDI -----
    if current < h_apm:
        horaires.append((current, h_apm))
    current = h_apm

    # ----- APRÈS-MIDI -----
    slots = []
    temp = current
    while temp + timedelta(minutes=duree_creneau) <= h_apm_fin:
        slots.append(temp)
        temp += timedelta(minutes=duree_creneau)

    mid = len(slots) // 2 if len(slots) >= 4 else -1

    i = 0
    while True:
        start = current
        end = start + timedelta(minutes=duree_creneau)
        if end > h_apm_fin + timedelta(seconds=1):
            break
        horaires.append((start, end))
        current = end

        i += 1
        if i == mid:
            current += timedelta(minutes=duree_recre)

    # Format final
    result = [f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}" for start, end in horaires]
    mettre_a_jour_section_interface("affichage.horaires_affichage", result)

def generer_professeurs_affichage():
    """
    Génère la liste des noms complets des professeurs pour affichage :
    "M. Dupont Alice", "Mme Martin Julie", ...
    """
    data = charger_donnees_interface()
    profs = data.get("3_ressources", {}).get("professeurs", [])
    if not profs:
        # print("Aucun professeur trouvé : génération annulée.")
        return

    liste_affichage = []
    for prof in profs:
        civilite = prof.get("Civilite", "").strip()
        nom = prof.get("Nom", "").strip()
        prenom = prof.get("Prenom", "").strip()
        if civilite or nom or prenom:
            ligne = f"{civilite} {nom} {prenom}".strip()
            liste_affichage.append(ligne)

    mettre_a_jour_section_interface("affichage.professeurs_affichage", liste_affichage)

def generer_volume_horaire():
    """
    Génère le bloc 'volume_horaire' avec :
    - Les matières du programme national (sans les mentions "Langue vivante*")
    - Les LV1/LV2 (sauf LV2 en 6e) avec volume associé
    - Les LV3/LV4 à 2h par défaut si activés
    - Les options par niveau
    """
    data = charger_donnees_interface()
    programme = data.get("4_programme_national", {})
    langues_data = data.get("2_langues_et_options", {})
    autres_langues = langues_data.get("autres_langues", {})
    options_par_niveau = data.get("options_par_niveau", {})

    lv_all = {
        "LV1": langues_data.get("lv1", []),
        "LV2": langues_data.get("lv2", []),
        "LV3": langues_data.get("lv3", []) if langues_data.get("lv3_active") else [],
        "LV4": langues_data.get("lv4", []) if langues_data.get("lv4_active") else []
    }

    autres_all = {
        "LV1": autres_langues.get("lv1", []),
        "LV2": autres_langues.get("lv2", []),
        "LV3": autres_langues.get("lv3", []),
        "LV4": autres_langues.get("lv4", [])
    }

    volume_par_niveau = {}

    for niveau in ["6e", "5e", "4e", "3e"]:
        bloc = {}

        matieres = programme.get(niveau, [])
        lv1_volume = None
        lv2_volume = None

        for mat in matieres:
            nom = mat.get("Discipline", "").strip()
            vol = mat.get("VolumeHoraire", None)
            if not nom or not isinstance(vol, (int, float)):
                continue

            if nom in ["Langue vivante", "Langue vivante 1"]:
                lv1_volume = vol
            elif nom == "Langue vivante 2":
                lv2_volume = vol
            else:
                bloc[nom] = vol

        # Langues LV1 et LV2
        for lv in ["LV1", "LV2"]:
            if niveau == "6e" and lv == "LV2":
                continue  # Pas de LV2 en 6e

            vol_ref = lv1_volume if lv == "LV1" else lv2_volume
            langues = lv_all.get(lv, [])
            autres = autres_all.get(lv, [])
            for langue in langues:
                if langue.lower().strip() == "autre":
                    for alt in autres:
                        if alt.strip():
                            bloc[f"{lv}_{alt.strip()}"] = vol_ref if vol_ref else 2
                elif langue.strip():
                    bloc[f"{lv}_{langue.strip()}"] = vol_ref if vol_ref else 2

        # LV3 et LV4 à 2h si activés
        if niveau in ["4e", "3e"]:
            for langue in lv_all["LV3"]:
                if langue.lower().strip() == "autre":
                    for alt in autres_all["LV3"]:
                        if alt.strip():
                            bloc[f"LV3_{alt.strip()}"] = 2
                elif langue.strip():
                    bloc[f"LV3_{langue.strip()}"] = 2

        if niveau == "3e":
            for langue in lv_all["LV4"]:
                if langue.lower().strip() == "autre":
                    for alt in autres_all["LV4"]:
                        if alt.strip():
                            bloc[f"LV4_{alt.strip()}"] = 2
                elif langue.strip():
                    bloc[f"LV4_{langue.strip()}"] = 2


        # Options personnalisées
        options = options_par_niveau.get(niveau, [])
        for opt in options:
            nom = opt.get("Option", "").strip()
            vol = opt.get("Volume", None)
            if nom and isinstance(vol, (int, float)):
                bloc[f"Option_{nom}"] = vol

        # EMC séparé si non inclus
        emc_bloc = data.get("4_programme_national", {}).get("emc", {}).get(niveau, {})
        if emc_bloc.get("inclus") == "non":
            vol = emc_bloc.get("volume", None)
            if isinstance(vol, (int, float)):
                bloc["EMC"] = vol

        volume_par_niveau[niveau] = bloc

    mettre_a_jour_section_interface("affichage.volume_horaire_affichage", volume_par_niveau)

def generer_salles_affichage():
    """
    Génère la liste des noms de salles pour affichage simple.
    Exemple : ["Salle A", "Salle B", "Salle Physique"]
    """
    data = charger_donnees_interface()
    salles = data.get("3_ressources", {}).get("salles", [])
    if not salles:
        # print("Aucune salle trouvée, génération annulée.")
        return

    noms_salles = []
    for salle in salles:
        nom = salle.get("Nom", "").strip()
        if nom:
            noms_salles.append(nom)

    mettre_a_jour_section_interface("affichage.salles_affichage", noms_salles)

def transformer_interface_vers_config(path_interface="data/data_interface.json", path_config="data/config.json"):
    """
    Transforme le fichier de configuration brut de l'interface utilisateur (data_interface.json)
    en un fichier de configuration allégé et structuré (config.json) pour le solveur.
    Retourne également le dictionnaire résultant.
    """
    with open(path_interface, encoding="utf-8") as f:
        interface = json.load(f)

    config = {}

    config["jours"] = interface["1_horaires"]["jours_classiques"]
    config["heures"] = interface["affichage"]["horaires_affichage"]

    config["matieres"] = sorted({m for niveau in interface["affichage"]["volume_horaire_affichage"].values() for m in niveau})
    config["niveaux"] = list(interface["affichage"]["volume_horaire_affichage"].keys())
    config["volume_horaire"] = interface["affichage"]["volume_horaire_affichage"]

    # Classes base
    classes = interface["3_ressources"]["classes"]
    config["classes_base"] = [c["Classe"] for c in classes if not c["Dependances"]]
    config["capacites_classes"] = {c["Classe"]: int(c["Effectif"]) for c in classes}

    # Professeurs
    profs = interface["3_ressources"]["professeurs"]
    config["professeurs"] = {}  
    config["volume_par_professeur"] = {f"{p['Civilite']} {p['Nom']} {p['Prenom']}": int(p["Volume"]) for p in profs}

    # Salles
    salles = interface["3_ressources"]["salles"]
    config["capacites_salles"] = {s["Nom"]: int(s["Capacite"]) for s in salles}

    # Indisponibilités
    config["indisponibilites_profs"] = interface.get("contraintes", {}).get("profs", {}).get("indisponibilites_totales", {})
    config["indisponibilites_salles"] = interface.get("contraintes", {}).get("salles", {}).get("indisponibilites_totales", {})

    # Sous-groupes
    config["sous_groupes_config"] = {}
    for groupe in interface["3_ressources"]["classes"]:
        if groupe["Dependances"]:
            matiere = groupe["MatiereGroupe"]
            niveau = groupe["Niveau"]
            suffixe = "_" + groupe["Classe"].split("_")[-1] if "_" in groupe["Classe"] else "_" + matiere[:2]
            if matiere not in config["sous_groupes_config"]:
                config["sous_groupes_config"][matiere] = {"niveaux": [], "suffixe": suffixe}
            if niveau not in config["sous_groupes_config"][matiere]["niveaux"]:
                config["sous_groupes_config"][matiere]["niveaux"].append(niveau)

    # Affectations spécifiques
    config["affectation_matiere_salle"] = interface.get("affectation_matiere_salle", {})

    # Poids et contraintes supplémentaires 
    config["poids_matieres"] = interface.get("poids_matieres", {})
    config["poids_cartable_max_somme_par_niveau"] = interface.get("poids_cartable_max_somme_par_niveau", {})

    # Enregistre le résultat
    with open(path_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return config


def charger_statistiques_contraintes(path="data/tous_rapports_contraintes.json"):
    """
    Charge les statistiques depuis le JSON et retourne :
    - pourcentage global
    - table_data pour Dash
    - violations (set)
    - détails groupés par contrainte
    - stats : volume_horaire %, obligatoires %, optionnelles %
    """

    CORRECTIONS_ACCENTS = {
        "Volume horaire": "Volume horaire",
        "Volume par professeur": "Volume par professeur",
        "Indisponibilites profs": "Indisponibilités profs",
        "Indisponibilites salles": "Indisponibilités salles",
        "Double affectation profs": "Double affectation profs",
        "Double affectation salles": "Double affectation salles",
        "Jours sans apres midi": "Jours sans après-midi",
        "Mat exclu suite": "Matière exclue en suite",
        "Mat inclu suite": "Matière incluse en suite",
        "Mat horaire donne v2": "Horaire imposé pour groupe de matières",
        "Max heures par etendue": "Maximum heures par étendue",
        "Mem niveau cours": "Cours synchronisés par niveau",
        "Cantine": "Réfectoire",
        "Permanence": "Permanence",
        "Poids cartable": "Poids du cartable",
        "Preferences salle professeur": "Préférences de salle (professeurs)"
    }

    with open(path, encoding="utf-8") as f:
        data_stats = json.load(f)

    stats = data_stats["0"]
    pourcentage_global = data_stats.get("pourcentage_global", 0)

    table_data = []
    violations = set()
    details_violations_grouped = {}

    # Compteurs pour statistiques
    total_obl, respectees_obl = 0, 0
    total_opt, respectees_opt = 0, 0
    volume_horaire_pct = None

    for key, val in stats.items():
        total = val["total"]
        respectees = val["respectees"]
        statut = val.get("statut", "optionnelle")
        details = val.get("details", [])
        nom_brut = key.replace("_", " ").capitalize()
        nom_affiche = CORRECTIONS_ACCENTS.get(nom_brut, nom_brut)

        if total == 0:
            taux = "-"
        else:
            taux = f"{round(respectees / total * 100, 1)}%"
            if respectees < total:
                violations.add(key)
                if details:
                    details_violations_grouped[nom_affiche] = list(set(details))

        # Ajouter à table
        table_data.append({
            "contrainte": nom_affiche,
            "statut": statut.capitalize(),
            "respectees": respectees,
            "total": total,
            "taux": taux
        })

        # Compter pour stats
        if statut == "obligatoire":
            total_obl += total
            respectees_obl += respectees
        else:
            total_opt += total
            respectees_opt += respectees

        if key == "volume_horaire":
            volume_horaire_pct = f"{round((respectees / total) * 100, 1)}%" if total > 0 else "-"

    # Pourcentages synthétiques
    taux_obligatoire = f"{round((respectees_obl / total_obl) * 100, 1)}%" if total_obl else "-"
    taux_optionnel = f"{round((respectees_opt / total_opt) * 100, 1)}%" if total_opt else "-"

    stats_globales = {
        "volume_horaire": volume_horaire_pct,
        "contraintes_obligatoires": taux_obligatoire,
        "contraintes_optionnelles": taux_optionnel
    }

    return pourcentage_global, table_data, violations, details_violations_grouped, stats_globales

# Page de contraintes 
def charger_config():
    """
    Charge la configuration complète de l'application à partir du fichier JSON principal.

    Returns:
        dict: Le contenu du fichier de configuration `data_interface.json`.
    """
    with open("data/data_interface.json", encoding="utf-8") as f:
        return json.load(f)


def charger_contraintes_interface(entite: str) -> dict:
    """
    Charge les contraintes horaires (partielles et totales) d'une entité (prof, groupe, salle).

    Args:
        entite (str): Nom de l'entité ciblée ("profs", "groupes", ou "salles").

    Returns:
        dict: Dictionnaire des contraintes avec pour chaque nom les cases marquées.
    """
    fichier = "data/data_interface.json"
    if not os.path.exists(fichier):
        return {}

    with open(fichier, encoding="utf-8") as f:
        data = json.load(f)

    entite_data = data.get("contraintes", {}).get(entite, {})
    part = entite_data.get("indisponibilites_partielles", {})
    tot  = entite_data.get("indisponibilites_totales", {})

    contraintes = {}
    for nom in set(part) | set(tot):
        contraintes[nom] = {}
        for jour, lignes in part.get(nom, {}).items():
            for ligne in lignes:
                contraintes[nom][f"{ligne}|{jour}"] = "Indisponibilité partielle"
        for jour, lignes in tot.get(nom, {}).items():
            for ligne in lignes:
                contraintes[nom][f"{ligne}|{jour}"] = "Indisponibilité totale"
    return contraintes


def build_styles(cell_constraints):
    """
    Construit les styles CSS conditionnels pour un tableau Dash en fonction des contraintes par cellule.

    Args:
        cell_constraints (dict): Dictionnaire des contraintes de type {"row|col": "type"}.

    Returns:
        list: Liste de dictionnaires de styles Dash pour le tableau.
    """
    styles = []
    for key, constraint in cell_constraints.items():
        row_s, col = key.split("|")
        row = int(row_s)

        if constraint == "Indisponibilité partielle":
            styles.append({
                "if": {"row_index": row, "column_id": col},
                "backgroundImage": f"url('{app.get_asset_url('indisponibilite_partielle_mini.png')}')",
                "backgroundRepeat": "no-repeat",
                "backgroundPosition": "center",
                "backgroundSize": "0.6rem 0.6rem",
                "backgroundColor": "#FFD580",
                "color": "transparent"
            })

        elif constraint == "Indisponibilité totale":
            styles.append({
                "if": {"row_index": row, "column_id": col},
                "backgroundImage": f"url('{app.get_asset_url('indisponible_totale_mini.png')}')",
                "backgroundRepeat": "no-repeat",
                "backgroundPosition": "center",
                "backgroundSize": "0.6rem 0.6rem",
                "backgroundColor": "#FF7F7F",
                "color": "transparent"
            })

        elif constraint == "Disponible":
            styles.append({
                "if": {"row_index": row, "column_id": col},
                "backgroundColor": "#90EE90",
                "color": "black"
            })

    return styles


def save_constraints_interface(entite: str, contraintes: dict):
    """
    Sauvegarde les contraintes dans le fichier JSON pour une entité donnée.

    Args:
        entite (str): Nom de l'entité ("profs", "groupes", "salles").
        contraintes (dict): Dictionnaire des contraintes marquées.
    """
    fichier = "data/data_interface.json"
    if os.path.exists(fichier):
        with open(fichier, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    if "contraintes" not in data:
        data["contraintes"] = {}

    part = {}
    tot = {}

    for nom, mapping in contraintes.items():
        for key, val in mapping.items():
            if val == "Disponible":
                continue  # ne pas sauvegarder les cases disponibles
            ligne, jour = key.split("|")
            ligne = int(ligne)
            cible = part if val == "Indisponibilité partielle" else tot
            cible.setdefault(nom, {}).setdefault(jour, []).append(ligne)


    data["contraintes"][entite] = {
        "indisponibilites_partielles": part,
        "indisponibilites_totales": tot
    }

    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



def construire_recapitulatif(depuis_store_data, heures):
    """
    Construit un tableau récapitulatif des contraintes pour affichage.

    Args:
        depuis_store_data (dict): Dictionnaire des contraintes par entité.
        heures (list): Liste des heures affichées en ligne.

    Returns:
        list: Liste de dictionnaires avec les colonnes "Concerne", "Jour", "Heure", "Contrainte".
    """
    recap = []
    for nom, mapping in depuis_store_data.items():
        for key, contrainte in mapping.items():
            if contrainte == "Disponible":
                continue
            ligne, jour = key.split("|")
            ligne_index = int(ligne)
            heure = heures[ligne_index] if ligne_index < len(heures) else f"Créneau {ligne_index}"
            recap.append({
                "Concerne": nom,
                "Jour": jour,
                "Heure": heure,
                "Contrainte": contrainte
            })
    return recap


def charger_contraintes_3_4(cle: str) -> list:
    """
    Charge une contrainte de type 3.4 depuis le fichier JSON.

    Args:
        cle (str): Clé dans la section "contraintes_3_4".

    Returns:
        list: Liste des contraintes enregistrées pour cette clé.
    """
    with open("data/data_interface.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("contraintes_3_4", {}).get(cle, [])

def enregistrer_contraintes_3_4(cle: str, contenu: list):
    """
    Enregistre la contrainte dans la section "contraintes_3_4.<cle>" du fichier JSON.

    Args:
        cle (str): Nom de la contrainte (ex : "planning").
        contenu (list): Liste d'entrées à enregistrer.
    """
    mettre_a_jour_section_interface(f"contraintes_3_4.{cle}", contenu)


def creer_table_edt(jours, heures):
    """
    Crée un DataFrame représentant un emploi du temps vide avec colonnes jours et lignes heures.

    Args:
        jours (list): Liste des jours de la semaine.
        heures (list): Liste des horaires.

    Returns:
        pd.DataFrame: Tableau EDT initialisé avec des cellules vides.
    """
    return pd.DataFrame([{"Heure": h, **{j: "" for j in jours}} for h in heures])

def make_section_contraintes(
    section_id: str,
    titre: str,
    options_dropdown: list[str],
    data_store: dict,
    data_recap: list[dict],
    jours, 
    heures
) ->dbc.AccordionItem:
    """ 
    Crée un AccordionItem pour la section de saisie de contraintes.
    - section_id       : 'profs', 'groupes' ou 'salles'
    - titre            : "Contraintes des professeurs", etc.
    - options_dropdown : liste des options pour le premier dropdown
    - data_store       : données initiales pour dcc.Store
    - data_recap       : données pour le tableau récapitulatif
    """
    # Construction du contenu interne 
    children = html.Div([
        html.H5(f"Sélectionner une ou plusieurs {titre.lower()}"),
        dcc.Dropdown(
            id=f"select-{section_id}",
            options=[{"label": o, "value": o} for o in options_dropdown],
            multi=True,
            placeholder=f"Sélectionner les {titre.lower()}",
            style=style_dropdown_center
        ),
        html.Br(),
        html.P(
            "Cliquez sur les boutons ci-dessous pour définir la disponibilité, puis utilisez le panneau pour appliquer.",
            className="text-center"
        ),
        html.Div([
            dbc.Button([
                        html.I(className="bi bi-check-circle me-2"),
                        "Disponible"
                        ],id=f"btn-vert-{section_id}", style=style_btn_dispnobible, className="me-2"),
                        dbc.Button(
    [
        html.Img(
            src=app.get_asset_url("tilde-icon-white-thick.png"),
            style={
                "width":         "1.2rem",
                "height":        "1.2rem",
                "marginRight":   "0.5rem",
                "verticalAlign": "middle",
            },
            alt="tilde"
        ),
        "Indisponibilité partielle"
    ],
    id=f"btn-orange-{section_id}",
    style=style_btn_indisponible,
    className="me-2"
),

            dbc.Button([
                        html.I(className="bi bi-x-circle me-2"),
                        "Indisponibilité totale"
                        ],id=f"btn-rouge-{section_id}", style=style_btn_totale, className="me-2"),
            dbc.Button([
                        html.I(className="bi bi-arrow-counterclockwise me-2"),
                        "Réinitialiser"
                        ],id=f"btn-reset-{section_id}", style=style_btn_reset, className="me-2"),
        ], className="mb-3 text-center"),
        html.Div(id=f"message-{section_id}", style=style_message),

        html.Div(
            style=style_flex_space_between,
            children=[
                # Tableau emploi du temps
                html.Div([
                    dash_table.DataTable(
                        id=f"table-edt-{section_id}",
                        columns=[{"name": "Heure", "id": "Heure"}] +
                                [{"name": j, "id": j} for j in jours],
                        data=creer_table_edt(jours, heures).to_dict("records"),
                        style_table=style_table_container,
                        style_cell={
        "textAlign": "center",
        "padding": "0",
        "height": "2rem",
        "lineHeight": "2rem"
    },
                        style_data_conditional=[],
                        style_header=style_header,
                    )
                ], style=style_content_left),
                # Panneau d'ajout de contrainte
                html.Div([
                    html.H5("Ajouter une contrainte"),
                    html.Label("Jour :"),
                    dcc.Dropdown(
                        id=f"dropdown-jours-{section_id}",
                        options=[{"label": j, "value": j} for j in jours],
                        multi=True,
                        placeholder="Sélectionner les jours"
                    ),
                    html.Label("Plages horaires :", style=style_label_margin_top),
                    dcc.Dropdown(
                        id=f"dropdown-plages-{section_id}",
                        options=[{"label": h, "value": h} for h in heures],
                        multi=True,
                        placeholder="Sélectionner les plages horaires"
                    ),
                    html.Div("Type de contrainte :", style=style_label_margin_top),
                    dcc.Dropdown(
                        id=f"dropdown-contraintes-{section_id}",
                        options=[
                            {"label": "Disponible", "value": "Disponible"},
                            {"label": "Indisponibilité partielle", "value": "Indisponibilité partielle"},
                            {"label": "Indisponibilité totale", "value": "Indisponibilité totale"}
                        ],
                        placeholder="Choisir un type",
                        clearable=False
                    ),
                    html.Button(
                        "Appliquer",
                        id=f"btn-appliquer-{section_id}",
                        n_clicks=0,
                        style=style_btn_apply
                    )
                ], style=style_apply_panel)
            ]
        ),

        html.Br(),
        html.H5("Récapitulatif des contraintes", style=style_recap_title),
        dash_table.DataTable(
            id=f"table-recap-{section_id}",
            columns=[
                {"name": "Concerné(e)", "id": "Concerne"},
                {"name": "Jour",        "id": "Jour"},
                {"name": "Heure",       "id": "Heure"},
                {"name": "Contrainte",  "id": "Contrainte"},
            ],
            page_size=6,
            page_action='native',
            data=data_recap,
            row_deletable = True,
            style_table=style_table_container,
            style_cell=style_cell,
            style_header=style_header,
        ),

        # Stores
        dcc.Store(id=f"store-cell-colors-{section_id}",      data={}),
        dcc.Store(id=f"store-recap-{section_id}",             data=data_recap),
        dcc.Store(id=f"store-couleur-active-{section_id}",    data=""),
        dcc.Store(id=f"store-{section_id}-data",              data=data_store)
    ], style={"padding": "1rem"})

    index = ['profs', 'groupes', 'salles'].index(section_id) + 1
    numero = f"3.{index}"

    return dbc.AccordionItem(
        children,
        title=html.Span(f"{numero} {titre}", style=titre_accordion_h4),
        item_id=f"contraintes-{section_id}"
    )
def maj_contrainte_nb_heures(n_clicks, qui, matiere, nb_heures, etendue, store_data, volume_horaire):
    if not n_clicks:
        raise PreventUpdate

    if not etendue:
        raise PreventUpdate  # Étendue obligatoire
    
    planning = list(store_data) if store_data else []

    etendue_str = etendue.replace("_", " ")

    final_tuples = []
    if qui and matiere:
        qui_list = [qui] if isinstance(qui, str) else qui
        mat_list = [matiere] if isinstance(matiere, str) else matiere
        final_tuples = [(q, m) for q in qui_list for m in mat_list]
    elif matiere:
        mat_list = [matiere] if isinstance(matiere, str) else matiere
        final_tuples = [
            (q, m)
            for q, vols in volume_horaire.items()
            for m in mat_list
            if m in vols
        ]
    elif qui:
        qui_list = [qui] if isinstance(qui, str) else qui
        final_tuples = [
            (q, m)
            for q in qui_list
            for m in volume_horaire.get(q, {})
        ]
    else:
        # Rien à faire si ni classe ni matière
        raise PreventUpdate

    # 2) Déterminer nb_list_finales
    if isinstance(nb_heures, list):
        nb_list_user = nb_heures
    else:
        nb_list_user = [nb_heures] if nb_heures is not None else []

    new_entries = []
    for q, m in final_tuples:
        if nb_list_user:
            nb_list_finales = nb_list_user
        else:
            val = volume_horaire.get(q, {}).get(m)
            if isinstance(val, int):
                nb_list_finales = [val]
            elif isinstance(val, list):
                nb_list_finales = [max(val)]
            else:
                nb_list_finales = []

        for nb in nb_list_finales:
            new_entries.append({
                "Qui":       q,
                "Matiere":   m,
                "Nb_heures": nb,    
                "Etendue":   etendue_str
            })

    # 3) Fusionner : on ajoute chaque nouvelle ligne si elle n’existe pas déjà
    for entry in new_entries:
        if entry not in planning:
            planning.append(entry)

    # 4) Sauvegarde 
    enregistrer_contraintes_3_4("planning", planning)
    return planning, planning



#######################Page resultat ########################
def charger_donnees_edt():
    """
    Charge les données d'emploi du temps depuis le fichier JSON principal.

    Ouvre le fichier 'data/emploi_du_temps_global.json', charge son contenu sous forme de dictionnaire
    et extrait la liste triée de tous les horaires présents dans l'emploi du temps (pour les deux semaines).

    Returns:
        tuple: Un tuple (edt_global, heures) où :
            - edt_global (dict) : Données globales de l'emploi du temps, ou dictionnaire vide si erreur.
            - heures (list) : Liste triée de tous les horaires trouvés dans l'emploi du temps.
    """
    try:
        with open("data/emploi_du_temps_global.json", encoding="utf-8") as f:
            edt_global = json.load(f)
    except Exception:
        edt_global = {}
        return edt_global, []

    # Extraction dynamique des heures
    heures_set = set()
    for semaine in ["Semaine A", "Semaine B"]:
        for classe in edt_global.get("edt_classe", {}).get(semaine, {}).values():
            for jour in classe.values():
                heures_set.update(jour.keys())
    heures = sorted(heures_set, key=lambda h: int(h.replace("h", "")) if h.replace("h", "").isdigit() else 99)
    return edt_global, heures

def sauvegarder_edt_global(edt_global):
    """
    Sauvegarde l'emploi du temps global dans le fichier JSON principal.

    Prend en entrée les données d'emploi du temps et les enregistre dans
    'data/emploi_du_temps_global.json' au format JSON (UTF-8, indenté).

    Args:
        edt_global (dict): Données globales de l'emploi du temps à sauvegarder.

    Returns:
        None
    """
    try:
        with open("data/emploi_du_temps_global.json", "w", encoding="utf-8") as f:
            json.dump(edt_global, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print("Erreur lors de la sauvegarde :", e)

def get_entites(edt, vue):
    """
    Retourne la liste triée de toutes les entités présentes pour une vue donnée.

    Combine et trie l'ensemble des entités présentes pour la vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle')
    sur les deux semaines (A et B).

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').

    Returns:
        list: Liste triée des noms d'entités présents pour la vue donnée.
    """
    entitesA = set(edt[vue]["Semaine A"].keys())
    entitesB = set(edt[vue]["Semaine B"].keys())
    return sorted(entitesA | entitesB)

def fmt(cell, vue):
    """
    Formate le contenu d'une cellule de l'emploi du temps pour affichage HTML.

    Selon la vue sélectionnée, retourne une chaîne HTML contenant les informations principales
    (matière, professeur(s), salle, classe) du créneau, présentées différemment selon la vue.

    Args:
        cell (dict or None): Dictionnaire contenant les données du créneau (ou None si vide).
        vue (str): Vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').

    Returns:
        str: Chaîne HTML formatée pour affichage dans le tableau (ou chaîne vide si cellule vide).
    """
    if not cell:
        return ""
    mat = ", ".join(cell.get("matiere", []))
    prof = ", ".join(cell.get("professeurs", []) or cell.get("prof", []))
    salle = ", ".join(cell.get("salle", []))
    classe = ", ".join(cell.get("classe", []))
    if vue == "edt_classe":
        return f"<b>{mat}</b><br><span style='{sous_style}'>{prof}<br>{salle}</span>"
    elif vue == "edt_prof":
        return f"<b>{mat}</b><br><span style='{sous_style}'>{classe}<br>{salle}</span>"
    elif vue == "edt_salle":
        return f"<b>{mat}</b><br><span style='{sous_style}'>{classe}<br>{prof}</span>"
    return ""

def fmt_cours_simple(cell):
    """
    Formate simplement le nom de la ou des matières d'un créneau.

    Renvoie le nom de la matière (ou la liste concaténée des matières séparées par "/").
    Si la cellule est vide, renvoie 'vide'.

    Args:
        cell (dict or None): Dictionnaire du créneau.

    Returns:
        str: Nom de la matière, ou 'vide' si la cellule est vide.
    """
    if not cell:
        return "vide"
    return f"{'/'.join(cell.get('matiere', []))}"

def is_cours_plein(edt, vue, entite, jour, heure):
    """
    Vérifie si le créneau donné est un cours « plein » (identique sur les deux semaines).

    Un créneau est considéré « plein » si la matière, le(s) professeur(s) et la salle sont identiques
    pour la semaine A et la semaine B.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).
        jour (str): Jour concerné.
        heure (str): Horaire concerné.

    Returns:
        bool: True si le créneau est identique sur les deux semaines, sinon False.
    """
    cell_a = edt[vue]["Semaine A"].get(entite, {}).get(jour, {}).get(heure, None)
    cell_b = edt[vue]["Semaine B"].get(entite, {}).get(jour, {}).get(heure, None)
    if cell_a is None or cell_b is None:
        return False
    return (cell_a.get('matiere') == cell_b.get('matiere') and 
            cell_a.get('professeurs', cell_a.get('prof', [])) == cell_b.get('professeurs', cell_b.get('prof', [])) and 
            cell_a.get('salle') == cell_b.get('salle'))

def has_content(edt, vue, entite, jour, heure):
    """
    Indique si un créneau donné contient au moins un cours (semaine A ou B).

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).
        jour (str): Jour concerné.
        heure (str): Horaire concerné.

    Returns:
        bool: True si le créneau est occupé en semaine A ou B, sinon False.
    """
    cell_a = edt[vue]["Semaine A"].get(entite, {}).get(jour, {}).get(heure, None)
    cell_b = edt[vue]["Semaine B"].get(entite, {}).get(jour, {}).get(heure, None)
    return cell_a is not None or cell_b is not None

def get_cours_type(edt, vue, entite, jour, heure):
    """
    Détermine le type de cours pour un créneau donné.

    Retourne :
      - 'vide' si aucune information sur les deux semaines,
      - 'plein' si le cours est identique sur les deux semaines,
      - 'demi' si les cours diffèrent entre A et B.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).
        jour (str): Jour concerné.
        heure (str): Horaire concerné.

    Returns:
        str: 'vide', 'plein' ou 'demi' selon le cas.
    """
    cell_a = edt[vue]["Semaine A"].get(entite, {}).get(jour, {}).get(heure, None)
    cell_b = edt[vue]["Semaine B"].get(entite, {}).get(jour, {}).get(heure, None)
    if cell_a is None and cell_b is None:
        return "vide"
    elif is_cours_plein(edt, vue, entite, jour, heure):
        return "plein"
    else:
        return "demi"


def apply_transformation(edt, vue, entite, source, dest, action):
    """
    Applique une transformation sur l'emploi du temps (déplacement, échange ou fusion de cours).

    Cette fonction prend en entrée une action de transformation (déplacement, échange, fusion...)
    entre deux créneaux, et retourne un nouvel emploi du temps après application de l’action.
    L’ensemble des cas (swap, overwrite, merge, split, move…) est géré selon la valeur de `action`.

    Args:
        edt (dict): Données globales de l'emploi du temps (sera copié).
        vue (str): Vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').
        entite (str): Nom de l'entité (classe, prof, salle).
        source (dict): Dictionnaire décrivant le créneau source (avec clés 'jour' et 'heure').
        dest (dict): Dictionnaire décrivant le créneau destination (avec clés 'jour' et 'heure').
        action (str): Nom de l'action à appliquer (ex. 'swap_plein', 'move_plein_to_vide'...).

    Returns:
        dict: Nouveau dictionnaire de l'emploi du temps après transformation.
    """
    edt_new = copy.deepcopy(edt)
    cell_src_a = edt[vue]["Semaine A"].get(entite, {}).get(source["jour"], {}).get(source["heure"], None)
    cell_src_b = edt[vue]["Semaine B"].get(entite, {}).get(source["jour"], {}).get(source["heure"], None)
    cell_dest_a = edt[vue]["Semaine A"].get(entite, {}).get(dest["jour"], {}).get(dest["heure"], None)
    cell_dest_b = edt[vue]["Semaine B"].get(entite, {}).get(dest["jour"], {}).get(dest["heure"], None)

    if action == "swap_plein":
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_a)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_b)
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)

    elif action == "swap_demi":
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_a)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_b)
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)

    elif action == "swap_plein_demi":
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_a)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = copy.deepcopy(cell_dest_b)
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)

    elif action == "overwrite_plein":
        # Remplacer la destination par le cours plein source (A sur les deux semaines) et vider la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "plein_to_demi_split":
        # Mettre le cours plein source en B de la destination, garder A destination, vider la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_dest_a or cell_dest_b)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "demi_to_plein_split":
        # Mettre le demi source en B de la destination, garder A destination, vider la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_dest_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a or cell_src_b)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "overwrite_demi_a":
        # Mettre le demi-cours A source en A destination, B destination à None, vider la source A
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = None
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "overwrite_demi_b":
        # Mettre le demi-cours B source en B destination, A destination à None, vider la source B
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = None
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "move_plein_to_vide":
        # Déplacer le cours plein source vers la destination vide, effacer la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "move_demi_to_vide":
        # Déplacer le demi-cours source vers la destination vide, effacer la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_a_to_b":
        # Remplace semaine B de dest par semaine A de source, laisse A inchangé
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_b_to_a":
        # Remplace semaine A de dest par semaine B de source, laisse B inchangé
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_a_to_a":
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_b_to_b":
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "overwrite_any":
        # Remplacer la destination par la source (A et B), et vider la source
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_plein_a_dest":
        # Remplace Semaine A de dest par Semaine A de source (cours plein), sans toucher à B
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_plein_b_dest":
        # Remplace Semaine B de dest par Semaine A de source (cours plein), sans toucher à A
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_a_plein_dest":
        # Mettre Semaine A source à la place d'un cours plein (A et B identiques) -> remplacer A, laisser B
        edt_new[vue]["Semaine A"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_a)
        edt_new[vue]["Semaine A"][entite][source["jour"]][source["heure"]] = None

    elif action == "merge_b_plein_dest":
        # Mettre Semaine B source à la place d'un cours plein (A et B identiques) -> remplacer B, laisser A
        edt_new[vue]["Semaine B"][entite][dest["jour"]][dest["heure"]] = copy.deepcopy(cell_src_b)
        edt_new[vue]["Semaine B"][entite][source["jour"]][source["heure"]] = None

    return edt_new


def fmt_pdf(cell, vue, semaine=None):
    """
    Formate le contenu d'une cellule de l'emploi du temps pour affichage PDF.

    Produit une chaîne HTML adaptée à l’export PDF (mise en forme avec balises HTML/Font),
    selon la vue sélectionnée et la semaine si précisée.

    Args:
        cell (dict or None): Dictionnaire du créneau (ou None).
        vue (str): Vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').
        semaine (str, optional): Semaine concernée (A ou B, par défaut None).

    Returns:
        str: Chaîne HTML formatée pour le PDF.
    """
    if not cell:
        return ""
    mat = ", ".join(cell.get("matiere", []))
    prof = ", ".join(cell.get("professeurs", []) or cell.get("prof", []))
    salle = ", ".join(cell.get("salle", []))
    classe = ", ".join(cell.get("classe", []))
    if vue == "edt_classe":
          return f"<b>{mat}</b><br/><font size='6'>{prof}<br/>{salle}</font>"
    elif vue == "edt_prof":
        return f"<b>{mat}</b><br/><font size='6'>{classe}<br/>{salle}</font>"
    elif vue == "edt_salle":
        return f"<b>{mat}</b><br/><font size='6'>{classe}<br/>{prof}</font>"
    return "" 


def make_pdf(title, table_data_and_types):
    """
    Génère un fichier PDF à partir d'un tableau d'emploi du temps.

    Construit le document PDF : ajoute un titre, génère un tableau stylisé à partir des données fournies,
    colore les cellules selon leur type (plein, demi, pause), et retourne le contenu du PDF sous forme binaire.

    Args:
        title (str): Titre du document.
        table_data_and_types (tuple): Tuple (table_data, cell_types), où table_data contient les cellules du tableau
                                      et cell_types les types de chaque cellule (plein/demi/pause).

    Returns:
        bytes: Contenu binaire du fichier PDF prêt à être téléchargé.
    """
    table_data, cell_types = table_data_and_types
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20
    )
    elements = []
    # Titre
    style_title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=18, alignment=1, spaceAfter=18)
    elements.append(Paragraph(title, style_title))

    # Tableau principal
    data = [["Heure"] + jours] + table_data
    t = Table(data, colWidths=[60] + [105] * len(jours), rowHeights=40)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (0, -1), 10),
        ('LINEBEFORE', (1, 0), (-1, -1), 2, colors.HexColor('#343a40')),
        ('LINEABOVE', (0, 1), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#343a40')),
        ('INNERGRID', (1, 1), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (1, 1), (-1, -1), colors.HexColor('#222')),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (1, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    # Couleurs de fond selon le type de cellule
    for i, row_types in enumerate(cell_types, start=1):
        for j, typ in enumerate(row_types[1:], start=1):
            if typ == "plein":
                t.setStyle(TableStyle([('BACKGROUND', (j, i), (j, i), colors.HexColor('#d4edda'))]))
                t.setStyle(TableStyle([('BOX', (j, i), (j, i), 2, colors.HexColor('#28a745'))]))
            elif typ == "demi":
                t.setStyle(TableStyle([('BACKGROUND', (j, i), (j, i), colors.white)]))
                t.setStyle(TableStyle([('BOX', (j, i), (j, i), 1, colors.HexColor('#dee2e6'))]))
            elif typ == "pause":
                t.setStyle(TableStyle([('BACKGROUND', (j, i), (j, i), colors.HexColor('#f7f7f7'))]))
                t.setStyle(TableStyle([('BOX', (j, i), (j, i), 1, colors.HexColor('#999'))]))
    # Pause déjeuner en italique
    for i, row in enumerate(data[1:], start=1):
        for j, cell in enumerate(row[1:], start=1):
            if hasattr(cell, "getPlainText"):
                plain = cell.getPlainText()
                if plain and "pause déjeuner" in plain.lower():
                    t.setStyle(TableStyle([
                        ('TEXTCOLOR', (j, i), (j, i), colors.HexColor('#888')),
                        ('FONTNAME', (j, i), (j, i), 'Helvetica-Oblique'),
                        ('FONTSIZE', (j, i), (j, i), 10),
                    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def safe_join(val):
    """
    Formate de façon sûre une valeur pour affichage ou édition.

    Si la valeur est une liste, retourne une chaîne avec les éléments séparés par virgule.
    Si c’est déjà une chaîne, la retourne. Sinon, retourne une chaîne vide.

    Args:
        val (list or str or None): Valeur à formater.

    Returns:
        str: Valeur formatée pour affichage.
    """
    if isinstance(val, list):
        return ", ".join(val)
    elif isinstance(val, str):
        return val
    return ""


def generate_cell_content(cell_a, cell_b, is_plein, is_selected=False, is_source=False, vue="edt_classe"):
    """
    Génère le contenu Dash d'une cellule d'emploi du temps (plein ou demi).

    Selon que la cellule est un cours plein ou demi (cours différents A/B), construit le composant visuel
    (markdown, labels A/B, mise en forme spéciale si sélectionnée ou source d’un déplacement).

    Args:
        cell_a (dict or None): Données de la cellule Semaine A.
        cell_b (dict or None): Données de la cellule Semaine B.
        is_plein (bool): Indique si le créneau est un cours plein (identique sur A et B).
        is_selected (bool): Indique si la cellule est actuellement sélectionnée (pour l’affichage).
        is_source (bool or dict): Indique si la cellule est la source d’un déplacement, ou un dict pour détails.
        vue (str): Vue courante de l’emploi du temps.

    Returns:
        html.Div: Composant Dash représentant la cellule.
    """
    border_style = {"border": "3px solid #dc3545"} if is_source else {}
    if is_plein:
        return html.Div(
            dcc.Markdown(fmt(cell_a, vue), dangerously_allow_html=True),
            style={**cell_plein_style, **border_style} if not is_source else {**cell_plein_source_style, **border_style}
        )
    else:
        content_a = fmt(cell_a, vue) if cell_a else "<em>Libre</em>"
        content_b = fmt(cell_b, vue) if cell_b else "<em>Libre</em>"
        return html.Div([
            html.Div([
                html.Div("A", style=label_a_style),
                dcc.Markdown(content_a, dangerously_allow_html=True, style=markdown_demi_style)
            ], style={**(border_style if is_source and is_source.get("semaine") == "A" else {}), **cell_demi_a_style}),
            html.Div([
                html.Div("B", style=label_b_style),
                dcc.Markdown(content_b, dangerously_allow_html=True, style=markdown_demi_style)
            ], style={**(border_style if is_source and is_source.get("semaine") == "B" else {}), **cell_demi_b_style})
        ], style=cell_demi_container_style if not is_selected else cell_demi_container_selected_style)

def build_split_table(edt, vue, entite, mode, move_source, edit_source=None):
    """
    Construit le tableau principal de l’emploi du temps pour une entité.

    Affiche l’ensemble des créneaux horaires sous forme de tableau, en stylant chaque cellule selon son type
    (plein, demi, source de déplacement, cellule éditée…), avec gestion de l’état interactif (mode édition/déplacement).

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).
        mode (str): Mode d'affichage ("edit", "move", etc.).
        move_source (dict or None): Créneau source du déplacement en cours (ou None).
        edit_source (dict or None, optional): Créneau en cours d'édition (ou None).

    Returns:
        html.Table: Composant Dash représentant le tableau.
    """
    _ , heures = charger_donnees_edt()
    headers = [
        html.Th("Heure", style=header_style),
        *[html.Th(jour, style=header_style) for jour in jours]
    ]
    rows = [html.Tr(headers)]
    
    for heure in heures:
        cells = [html.Td(heure, style=heure_cell_style)]
        for jour in jours:
            cell_a = edt[vue].get("Semaine A", {}).get(entite, {}).get(jour, {}).get(heure, None)
            cell_b = edt[vue].get("Semaine B", {}).get(entite, {}).get(jour, {}).get(heure, None)
            is_plein = is_cours_plein(edt, vue, entite, jour, heure)
            is_source = move_source and (
                move_source["vue"] == vue and
                move_source["entite"] == entite and
                move_source["jour"] == jour and
                move_source["heure"] == heure
            )
            is_edit_selected = False
            if mode == "edit" and edit_source:
                is_edit_selected = (
                    edit_source["vue"] == vue and
                    edit_source["entite"] == entite and
                    edit_source["jour"] == jour and
                    edit_source["heure"] == heure
                )
            cell_style = (
                cours_cell_source_style if (is_source or is_edit_selected) else
                cours_cell_plein_style if is_plein else
                cours_cell_midi_style if heure.startswith("12") else
                {**cours_cell_style, "cursor": "pointer" if (mode in ["edit", "move"] and has_content(edt, vue, entite, jour, heure)) else "default"}
            )
            cell_id = {
                "type": "cellule",
                "vue": vue,
                "entite": entite,
                "jour": jour,
                "heure": heure,
                "semaine": "A" if is_plein else (move_source["semaine"] if is_source and move_source and "semaine" in move_source else "A")
            }
            cell = html.Td(
                generate_cell_content(cell_a, cell_b, is_plein, is_source, move_source if is_source else None, vue),
                id=cell_id,
                n_clicks=0,
                style=cell_style
            )
            cells.append(cell)
        rows.append(html.Tr(cells))
    
    return html.Table(rows, style=table_style)

def get_configuration_options(edt, vue, entite, source, dest):
    """
    Génère les options de transformation disponibles entre deux créneaux.

    Selon le type de chaque créneau (plein, demi, vide), retourne la liste des actions autorisées
    (ex : swap, overwrite, move…), avec label, description et identifiant d’action pour affichage dans l’UI.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité.
        source (dict): Créneau source.
        dest (dict): Créneau destination.

    Returns:
        list: Liste de dictionnaires représentant chaque option de transformation possible.
    """
    type_src = get_cours_type(edt, vue, entite, source["jour"], source["heure"])
    type_dest = get_cours_type(edt, vue, entite, dest["jour"], dest["heure"])

    cell_src_a = edt[vue]["Semaine A"].get(entite, {}).get(source["jour"], {}).get(source["heure"], None)
    cell_src_b = edt[vue]["Semaine B"].get(entite, {}).get(source["jour"], {}).get(source["heure"], None)
    cell_dest_a = edt[vue]["Semaine A"].get(entite, {}).get(dest["jour"], {}).get(dest["heure"], None)
    cell_dest_b = edt[vue]["Semaine B"].get(entite, {}).get(dest["jour"], {}).get(dest["heure"], None)

    options = []

    if type_src == "plein" and type_dest == "plein":
        options.append({
            "id": "swap_plein",
            "label": "Échanger les cours pleins",
            "description": f"{fmt_cours_simple(cell_src_a)} ↔ {fmt_cours_simple(cell_dest_a)}",
            "action": "swap_plein"
        })
    elif type_src == "demi" and type_dest == "demi":
        options.append({
            "id": "swap_demi",
            "label": "Échanger les demi-cours",
            "description": f"A:{fmt_cours_simple(cell_src_a)} B:{fmt_cours_simple(cell_src_b)} ↔ A:{fmt_cours_simple(cell_dest_a)} B:{fmt_cours_simple(cell_dest_b)}",
            "action": "swap_demi"
        })
        if cell_src_a:
            options.append({
                "id": "merge_a_to_a",
                "label": "Déplacer uniquement le cours semaine A",
                "action": "merge_a_to_a"
            })
        if cell_src_b:
            options.append({
                "id": "merge_b_to_b",
                "label": "Déplacer uniquement le cours semaine B",

                "action": "merge_b_to_b"
            })
    elif (type_src == "plein" and type_dest == "demi") or (type_src == "demi" and type_dest == "plein"):
        options.append({
            "id": "swap_plein_demi",
            "label": "Échanger les cours",
            "action": "swap_plein_demi"
        })
        if type_src == "plein":
            options.append({
                "id": "merge_plein_a_dest",
                "label": "Déplacer uniquement le cours semaine A",
                "action": "merge_b_to_a"
            })
            options.append({
                "id": "merge_plein_b_dest",
                "label": "Déplacer uniquement le cours semaine B",
                "action": "merge_a_to_b"
            })
        else:
            options.append({
                "id": "merge_a_plein_dest",
                "label": "Déplacer uniquement le cours semaine A",
                "action": "merge_a_plein_dest"
            })
            options.append({
                "id": "merge_b_plein_dest",
                "label": "Déplacer uniquement le cours semaine B",
                "action": "merge_b_plein_dest"
            })
    elif type_dest == "vide":
        if type_src == "plein":
            options.append({
                "id": "move_plein_to_vide",
                "label": "Déplacer cours plein",
                "action": "move_plein_to_vide"
            })
        elif type_src == "demi":
            options.append({
                "id": "move_demi_to_vide",
                "label": "Échanger les demi-cours",
                "action": "move_demi_to_vide"
            })
    # Toujours proposer "overwrite_any" si les deux ne sont pas vides
    if type_src != "vide" and type_dest != "vide":
        options.append({
            "id": "overwrite_any",
            "label": "Remplacer la destination par la source",
            "action": "overwrite_any"
        })
    return options


def build_option_preview_dash(edt, vue, entite, source, dest, action):
    """
    Génère une prévisualisation Dash d'une transformation entre deux créneaux.

    Applique virtuellement l'action de transformation, puis affiche un tableau compact montrant
    le résultat potentiel (aperçu avant validation).

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité.
        source (dict): Créneau source.
        dest (dict): Créneau destination.
        action (str): Action de transformation à prévisualiser.

    Returns:
        html.Div: Composant Dash contenant la prévisualisation (mini-tableau de résultat).
    """
    # Applique virtuellement la transformation
    edt_preview = apply_transformation(copy.deepcopy(edt), vue, entite, source, dest, action)
    return html.Div([
        build_preview_table(edt_preview, vue, entite)
    ], style=preview_container_style)

def get_table_matrix_pdf(edt, vue, entite):
    """
    Génère la matrice de données et types de cellules pour l’export PDF.

    Produit une liste de lignes et une liste associée de types de cellules (plein/demi/pause)
    pour chaque créneau de l’entité et de la vue demandée, au format adapté à ReportLab.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).

    Returns:
        tuple: (rows, cell_types), où rows contient les objets Paragraph/Table pour le PDF,
               et cell_types la structure des types de chaque cellule.
    """
    _ , heures = charger_donnees_edt()
    base_style = ParagraphStyle(
        "cell",
        fontName="Helvetica",
        fontSize=7.5,
        alignment=1,
        leading=8,
        spaceBefore=0,
        spaceAfter=0,
        leftIndent=0,
        rightIndent=0,
        borderPadding=0
    )
    rows = []
    cell_types = []  # Pour stocker le type de chaque cellule
    for heure in heures:
        row = [Paragraph(f"<b>{heure}</b>", base_style)]
        row_types = ["heure"]
        for jour in jours:
            cA = edt[vue].get("Semaine A", {}).get(entite, {}).get(jour, {}).get(heure, None)
            cB = edt[vue].get("Semaine B", {}).get(entite, {}).get(jour, {}).get(heure, None)
            if heure.startswith("12") and not (cA or cB):
                cell = Paragraph("<i>Pause déjeuner</i>", base_style)
                row.append(cell)  
                row_types.append("pause")
            elif is_cours_plein(edt, vue, entite, jour, heure):
                txt = fmt_pdf(cA, vue)
                cell = Paragraph(txt.replace("\n", "<br/>"), base_style) if txt else ""
                row.append(cell)  
                row_types.append("plein")
            else:
                txtA = fmt_pdf(cA, vue, semaine="A")
                txtB = fmt_pdf(cB, vue, semaine="B")
                # Style pour le label A/B
                label_style = ParagraphStyle(
                    "label",
                    fontName="Helvetica-Bold",
                    fontSize=5.5,
                    alignment=0,  
                    leading=6,
                    spaceAfter=1,
                    leftIndent=0,
                    rightIndent=0,
                    borderPadding=0
                )
                # Style pour le contenu du cours
                cours_style = ParagraphStyle(
                    "cours",
                    fontName="Helvetica",
                    fontSize=5.0,
                    alignment=0,  
                    leading=6,
                    spaceAfter=0,
                    leftIndent=0,
                    rightIndent=0,
                    borderPadding=0,
                    wordWrap='CJK'
                )
                # Demi-cellule A
                cellA = Table([
                        [Paragraph(txtA.replace("\n", "<br/>"), cours_style)]
                    ], colWidths=[53], rowHeights=[22])
                # Demi-cellule B
                cellB = Table([
                     [Paragraph(txtB.replace("\n", "<br/>"), cours_style)]
                    ], colWidths=[53], rowHeights=[22])
                # Table 1 ligne, 2 colonnes
                split = Table([[cellA, cellB]], colWidths=[49, 49], rowHeights=[22])
                split.setStyle(TableStyle([
                    ('LINEAFTER', (0,0), (0,0), 1, colors.HexColor('#888')),
                    ('VALIGN', (0,0), (-1,-1), "MID"),
                    ('ALIGN', (0,0), (-1,-1), "LEFT"),
                    ('LEFTPADDING', (0,0), (-1,-1), 1),
                    ('RIGHTPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                cell = split
                row.append(cell)  
                row_types.append("demi")
        rows.append(row)
        cell_types.append(row_types)
    return rows, cell_types

def build_preview_table(edt, vue, entite):
    """
    Génère un mini-tableau Dash compact pour prévisualisation rapide.

    Construit un tableau affichant les créneaux horaires d'une entité, avec un style compact et
    une distinction visuelle entre cours plein et demi.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Vue sélectionnée.
        entite (str): Nom de l'entité (classe, prof, salle).

    Returns:
        html.Table: Composant Dash représentant le mini-tableau de preview.
    """
    _ , heures = charger_donnees_edt()
    # Génère un tableau Dash compact pour la preview (mini EDT)
    headers = [
        html.Th("Heure", style=preview_header_style),
        *[html.Th(j, style=preview_header_style) for j in jours]
    ]
    rows = [html.Tr(headers)]
    for heure in heures:
        cells = [html.Td(heure, style=preview_heure_cell_style)]
        for jour in jours:
            cell_a = edt[vue].get("Semaine A", {}).get(entite, {}).get(jour, {}).get(heure, None)
            cell_b = edt[vue].get("Semaine B", {}).get(entite, {}).get(jour, {}).get(heure, None)
            is_plein = is_cours_plein(edt, vue, entite, jour, heure)
            style = preview_cours_cell_plein_style if is_plein else preview_cours_cell_style
            if is_plein:
                content = dcc.Markdown(fmt(cell_a, vue), dangerously_allow_html=True, style=preview_markdown_plein_style)
            else:
                content = html.Div([
                    html.Div(dcc.Markdown(fmt(cell_a, vue), dangerously_allow_html=True, style=preview_markdown_demi_style), style=preview_demi_a_style),
                    html.Div(dcc.Markdown(fmt(cell_b, vue), dangerously_allow_html=True, style=preview_markdown_demi_style), style=preview_demi_b_style)
                ], style=preview_demi_container_style)
            cells.append(html.Td(content, style=style))
        rows.append(html.Tr(cells))
    return html.Table(rows, style={
         **preview_table_style
    }
)

def build_edit_panel(cell, vue, semaine="A"):
    """
    Construit le panneau d'édition pour un créneau horaire donné.

    Ce panneau affiche des champs d'entrée pour modifier les informations d'un cours (matière, professeur, salle, classe)
    en fonction du type de vue sélectionnée (classe, professeur, salle). Les champs affichés varient selon la vue pour
    refléter les informations pertinentes.

    Args:
        cell (dict): Données du créneau horaire (matière, professeurs, salle, classe).
        vue (str): Type de vue sélectionnée ("edt_classe", "edt_prof", "edt_salle").
        semaine (str, optional): Semaine concernée ("A" ou "B"). Par défaut, "A".

    Returns:
        html.Div: Composant contenant les champs d'édition pour le créneau horaire.
    """
    mat_val = safe_join(cell.get("matiere", []))
    prof_val = safe_join(cell.get("professeurs", []) or cell.get("prof", []))
    salle_val = safe_join(cell.get("salle", []))
    classe_val = safe_join(cell.get("classe", []))
    items = [
        dbc.Label("Matière"), dbc.Input(id=f"input-matiere-{semaine}-visible", type="text", value=mat_val or "", key=f"mat-{semaine}-{mat_val}"),
    ]
    if vue == "edt_classe":
        items += [
            dbc.Label("Professeur"), dbc.Input(id=f"input-prof-{semaine}-visible", type="text", value=prof_val or "", key=f"prof-{semaine}-{prof_val}"),
            dbc.Label("Salle"), dbc.Input(id=f"input-salle-{semaine}-visible", type="text", value=salle_val or "", key=f"salle-{semaine}-{salle_val}"),
        ]
    elif vue == "edt_prof":
        items += [
            dbc.Label("Classe"), dbc.Input(id=f"input-classe-{semaine}-visible", type="text", value=classe_val or "", key=f"classe-{semaine}-{classe_val}"),
            dbc.Label("Salle"), dbc.Input(id=f"input-salle-{semaine}-visible", type="text", value=salle_val or "", key=f"salle-{semaine}-{salle_val}"),
        ]
    elif vue == "edt_salle":
        items += [
            dbc.Label("Classe"), dbc.Input(id=f"input-classe-{semaine}-visible", type="text", value=classe_val or "", key=f"classe-{semaine}-{classe_val}"),
            dbc.Label("Professeur"), dbc.Input(id=f"input-prof-{semaine}-visible", type="text", value=prof_val or "", key=f"prof-{semaine}-{prof_val}"),
        ]
    return html.Div(items)



def transformer_interface_vers_config(path_interface="data/data_interface.json", path_config="data/config.json"):
    """
    Transforme le fichier de configuration brut de l'interface utilisateur (data_interface.json)
    en un fichier de configuration allégé et structuré (config.json) pour le solveur.
    Retourne également le dictionnaire résultant.
    """
    with open(path_interface, encoding="utf-8") as f:
        interface = json.load(f)

    config = {}

    config["jours"] = interface["1_horaires"]["jours_classiques"]
    config["heures"] = interface["affichage"]["horaires_affichage"]

    config["matieres"] = sorted({m for niveau in interface["affichage"]["volume_horaire_affichage"].values() for m in niveau})
    config["niveaux"] = list(interface["affichage"]["volume_horaire_affichage"].keys())
    config["volume_horaire"] = interface["affichage"]["volume_horaire_affichage"]

    # Classes base
    classes = interface["3_ressources"]["classes"]
    config["classes_base"] = [c["Classe"] for c in classes if not c["Dependances"]]
    config["capacites_classes"] = {c["Classe"]: int(c["Effectif"]) for c in classes}

    # Professeurs
    profs = interface["3_ressources"]["professeurs"]
    config["professeurs"] = {}  
    config["volume_par_professeur"] = {f"{p['Civilite']} {p['Nom']} {p['Prenom']}": int(p["Volume"]) for p in profs}

    # Salles
    salles = interface["3_ressources"]["salles"]
    config["capacites_salles"] = {s["Nom"]: int(s["Capacite"]) for s in salles}

    # Indisponibilités
    config["indisponibilites_profs"] = interface.get("contraintes", {}).get("profs", {}).get("indisponibilites_totales", {})
    config["indisponibilites_salles"] = interface.get("contraintes", {}).get("salles", {}).get("indisponibilites_totales", {})

    # Sous-groupes
    config["sous_groupes_config"] = {}
    for groupe in interface["3_ressources"]["classes"]:
        if groupe["Dependances"]:
            matiere = groupe["MatiereGroupe"]
            niveau = groupe["Niveau"]
            suffixe = "_" + groupe["Classe"].split("_")[-1] if "_" in groupe["Classe"] else "_" + matiere[:2]
            if matiere not in config["sous_groupes_config"]:
                config["sous_groupes_config"][matiere] = {"niveaux": [], "suffixe": suffixe}
            if niveau not in config["sous_groupes_config"][matiere]["niveaux"]:
                config["sous_groupes_config"][matiere]["niveaux"].append(niveau)

    # Affectations spécifiques
    config["affectation_matiere_salle"] = interface.get("affectation_matiere_salle", {})

    # Poids et contraintes supplémentaires 
    config["poids_matieres"] = interface.get("poids_matieres", {})
    config["poids_cartable_max_somme_par_niveau"] = interface.get("poids_cartable_max_somme_par_niveau", {})

    # Enregistre le résultat
    with open(path_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return config

def charger_data_interface_et_modeles():
    """
    Transforme data_interface.json en config utilisable,
    puis retourne tous les objets nécessaires au solveur executer_runs.
    """
    config = transformer_interface_vers_config()

    # Placeholder pour les objets non encore calculés
    model = {}
    emploi_du_temps = {}
    emploi_du_temps_salles = {}
    emploi_du_temps_profs = {}

    # Élémentaires
    JOURS = config["jours"]
    HEURES = config["heures"]
    MATIERES = config["matieres"]
    CLASSES_BASE = config["classes_base"]
    CLASSES = list(config["capacites_classes"].keys())
    CAPACITES_CLASSES = config["capacites_classes"]
    INDISPONIBILITES_PROFS = config.get("indisponibilites_profs", {})
    INDISPONIBILITES_SALLES = config.get("indisponibilites_salles", {})

    # Professeurs (liste)
    PROFESSEURS = list(config.get("volume_par_professeur", {}).keys())

    # Sous-groupes
    sous_groupes_config = config.get("sous_groupes_config", {})
    SOUS_GROUPES_SUFFIXES = {matiere: val["suffixe"] for matiere, val in sous_groupes_config.items()}

    # Autres éléments
    AFFECTATION_MATIERE_SALLE = config.get("affectation_matiere_salle", {})
    fusionner_groupes_vers_classes = None  
    solve_et_verifie = None 

    return (
        model,
        emploi_du_temps,
        emploi_du_temps_salles,
        emploi_du_temps_profs,
        JOURS,
        HEURES,
        MATIERES,
        PROFESSEURS,
        SOUS_GROUPES_SUFFIXES,
        CLASSES,
        CLASSES_BASE,
        CAPACITES_CLASSES,
        INDISPONIBILITES_PROFS,
        INDISPONIBILITES_SALLES,
        config,
        AFFECTATION_MATIERE_SALLE,
        fusionner_groupes_vers_classes,
        solve_et_verifie
    )

def charger_statistiques_contraintes(path="data/tous_rapports_contraintes.json"):
    """
    Charge les statistiques depuis le JSON et retourne :
    - pourcentage global
    - table_data pour Dash
    - violations (set)
    - détails groupés par contrainte
    - stats : volume_horaire %, obligatoires %, optionnelles %
    """

    CORRECTIONS_ACCENTS = {
        "Volume horaire": "Volume horaire",
        "Volume par professeur": "Volume par professeur",
        "Indisponibilites profs": "Indisponibilités profs",
        "Indisponibilites salles": "Indisponibilités salles",
        "Double affectation profs": "Double affectation profs",
        "Double affectation salles": "Double affectation salles",
        "Jours sans apres midi": "Jours sans après-midi",
        "Mat exclu suite": "Matière exclue en suite",
        "Mat inclu suite": "Matière incluse en suite",
        "Mat horaire donne v2": "Horaire imposé pour groupe de matières",
        "Max heures par etendue": "Maximum heures par étendue",
        "Mem niveau cours": "Cours synchronisés par niveau",
        "Cantine": "Réfectoire",
        "Permanence": "Permanence",
        "Poids cartable": "Poids du cartable",
        "Preferences salle professeur": "Préférences de salle (professeurs)"
    }

    with open(path, encoding="utf-8") as f:
        data_stats = json.load(f)

    stats = data_stats["0"]
    pourcentage_global = data_stats.get("pourcentage_global", 0)

    table_data = []
    violations = set()
    details_violations_grouped = {}

    # Compteurs pour statistiques
    total_obl, respectees_obl = 0, 0
    total_opt, respectees_opt = 0, 0
    volume_horaire_pct = None

    for key, val in stats.items():
        total = val["total"]
        respectees = val["respectees"]
        statut = val.get("statut", "optionnelle")
        details = val.get("details", [])
        nom_brut = key.replace("_", " ").capitalize()
        nom_affiche = CORRECTIONS_ACCENTS.get(nom_brut, nom_brut)

        if total == 0:
            taux = "-"
        else:
            taux = f"{round(respectees / total * 100, 1)}%"
            if respectees < total:
                violations.add(key)
                if details:
                    details_violations_grouped[nom_affiche] = list(set(details))

        # Ajouter à table
        table_data.append({
            "contrainte": nom_affiche,
            "statut": statut.capitalize(),
            "respectees": respectees,
            "total": total,
            "taux": taux
        })

        # Compter pour stats
        if statut == "obligatoire":
            total_obl += total
            respectees_obl += respectees
        else:
            total_opt += total
            respectees_opt += respectees

        if key == "volume_horaire":
            volume_horaire_pct = f"{round((respectees / total) * 100, 1)}%" if total > 0 else "-"

    # Pourcentages synthétiques
    taux_obligatoire = f"{round((respectees_obl / total_obl) * 100, 1)}%" if total_obl else "-"
    taux_optionnel = f"{round((respectees_opt / total_opt) * 100, 1)}%" if total_opt else "-"

    stats_globales = {
        "volume_horaire": volume_horaire_pct,
        "contraintes_obligatoires": taux_obligatoire,
        "contraintes_optionnelles": taux_optionnel
    }

    return pourcentage_global, table_data, violations, details_violations_grouped, stats_globales
