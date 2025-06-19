# Liste des imports nécessaires
from ortools.sat.python import cp_model
import json
import random
from tabulate import tabulate
import time
import copy
from collections import defaultdict
import os

# Afficher le chargement
avancement = 0
current_seed = None
fusion_choisie = None
resultats_choisis = None

# def transformer_interface_vers_config(path_interface="data/data_interface.json", path_config="data/config.json"):
#     """
#     Transforme le fichier de configuration brut de l'interface utilisateur (data_interface.json)
#     en un fichier de configuration allégé et structuré (config.json) pour le solveur.
#     Retourne également le dictionnaire résultant.
#     """
#     with open(path_interface, encoding="utf-8") as f:
#         interface = json.load(f)

#     config = {}

#     config["jours"] = interface["1_horaires"]["jours_classiques"]
#     config["jours_sans_apres_midi"] = interface["1_horaires"]["jours_particuliers"]
#     original_slots = interface["affichage"]["horaires_affichage"]
#     config["heures"] = []
#     for slot in original_slots:
#         start, end = slot.split(" - ")
#         h1, m1 = start.split(":")
#         h2, m2 = end.split(":")
#         # int(h1) retire tout zéro inutile en tête
#         config["heures"].append(f"{int(h1)}h{m1}-{int(h2)}h{m2}")

#         # 1) Matières « principales » (hors LV et options)
#     base_matieres = {
#         m
#         for matieres_niv in interface["affichage"]["volume_horaire_affichage"].values()
#         for m in matieres_niv
#     }

#     # 2) Matières des sous-groupes (langues vivantes et options)
#     sub_matieres = {
#         grp["MatiereGroupe"]
#         for grp in interface["3_ressources"]["classes"]
#         if grp["Dependances"]
#     }

#     # 3) Fusion et tri
#     config["matieres"] = sorted(base_matieres | sub_matieres)

#     config["sousGroupes_matieres"] = {
#         "Scientifique": ["Mathématiques", "SVT", "Physique-Chimie", "Technologie"],
#         "Langues": ["Français", "Anglais", "Espagnol", "Italien"],
#         "Artistique": ["Arts Plastiques", "Musique"]
#     }
#     config["niveaux"] = list(interface["affichage"]["volume_horaire_affichage"].keys())
#     config["volume_horaire"] = interface["affichage"]["volume_horaire_affichage"]

#     # Classes base
#     classes = interface["3_ressources"]["classes"]
#     config["classes_base"] = [c["Classe"] for c in classes if not c["Dependances"]]
#     # Capacités classes, avec suffixes pour les groupes (LV/options)
#     config["capacites_classes"] = {}
#     for c in classes:
#         eff = int(c["Effectif"])
#         if c["Dependances"]:
#             # c'est un sous-groupe : on génère le suffixe comme ailleurs
#             clean_mat = c["MatiereGroupe"]                     # ex. "Espagnol"
#             suffix = f"{c['Niveau'][0]}_{clean_mat[:3].lower()}"
#             # Écrase ou ajoute la capacité sous la clé suffixée
#             config["capacites_classes"][suffix] = eff
#         else:
#             # classe “pure” sans dépendances : clé = nom direct
#             config["capacites_classes"][c["Classe"]] = eff


#     # ——— Mapping brut → clé config des matières LV1/LV2 ———
#     matiere_to_config_key = {}
#     for grp in interface["3_ressources"]["classes"]:
#         raw = grp["MatiereGroupe"]  # ex. "Anglais", "Espagnol", "Latin", "Musique"…
#         # si un IDGroupe (p. ex. "LV1_Anglais" ou "LV2_Espagnol") est défini,
#         # on l’utilise ; sinon on fait TypeGroupe + "_" + MatiereGroupe
#         cible = grp.get("IDGroupe") or f"{grp.get('TypeGroupe')}_{raw}"
#         matiere_to_config_key[raw] = cible

#     # ——— Mapping brut → clé config des options ———
#     for niveau, opts in interface["options_par_niveau"].items():
#         for opt in opts:
#             raw = opt["Option"]             # ex. "Latin", "Escalade"
#             cible = f"Option_{raw}"         # ex. "Option_Latin"
#             matiere_to_config_key[raw] = cible

#     # ——— Mapping brut → clé config des LV1 explicite ———
#     # (au cas où certaines LV1 n’ont pas d’IDGroupe dans "classes")
#     for mat in config["matieres"]:
#         if mat.startswith("LV1_"):
#             # on récupère le raw : tout ce qui suit "LV1_"
#             raw = mat.split("_", 1)[1]
#             matiere_to_config_key[raw] = mat

#     # Professeurs
#     profs = interface["3_ressources"]["professeurs"]
#     config["professeurs"] = {}
#     for p in profs:
#         pNom = f"{p['Nom']} {p['Prenom']}"
#         raw_mat    = p.get("Matieres")  
#         varMatiere = matiere_to_config_key.get(raw_mat, raw_mat)
#         varNiveaux = p.get("Niveaux").split(",")
#         if varMatiere not in config["professeurs"]:
#             config["professeurs"][varMatiere] = {}
#         for pNiv in varNiveaux:
#             if pNiv not in config["professeurs"][varMatiere]:
#                 config["professeurs"][varMatiere][pNiv] = []
#             config["professeurs"][varMatiere][pNiv].append(pNom)
#     config["volume_par_professeur"] = {f"{p['Civilite']} {p['Nom']} {p['Prenom']}": int(p["Volume"]) for p in profs}

#     # Salles
#     salles = interface["3_ressources"]["salles"]
#     config["salles_generales"] = [s["Nom"] for s in salles]
#     config["capacites_salles"] = {s["Nom"]: int(s["Capacite"]) for s in salles}

#     config["preferences_profs"] = interface.get("contraintes", {}).get("profs", {}).get("indisponibilites_partielles", {})

#     config["preferences_salle_professeur"] = {
#         f"{p['Civilite']} {p['Nom']} {p['Prenom']}": p["SallePref"]
#         for p in profs
#         if p["SallePref"] != ""
#     }

#     # Indisponibilités
#     config["indisponibilites_profs"] = interface.get("contraintes", {}).get("profs", {}).get("indisponibilites_totales", {})
#     config["indisponibilites_salles"] = interface.get("contraintes", {}).get("salles", {}).get("indisponibilites_totales", {})

#     # === sous_groupes_config ===
#     config["sous_groupes_config"] = {}
#     for grp in interface["3_ressources"]["classes"]:
#         deps = grp.get("Dependances", "")
#         if not deps:
#             continue

#         # on récupère l'identifiant complet du groupe (ex. "LV2_Espagnol")
#         key = grp.get("IDGroupe") or grp.get("MatiereGroupe")

#         # nom de la matière sans préfixe, pour construire le suffixe
#         clean_mat = grp["MatiereGroupe"]  

#         # type : "LV" si TypeGroupe commence par "LV", "option" si "Option", sinon vide
#         type_grp = grp.get("TypeGroupe", "")
#         typ = "LV" if type_grp.startswith("LV") else "option" if type_grp.startswith("Option") else ""

#         entry = config["sous_groupes_config"].setdefault(
#             key,
#             {
#                 "niveaux": [],
#                 "suffixe": f"_{clean_mat[:3].lower()}",
#                 "groupes_dependants": [],
#                 "type": typ
#             }
#         )

#         # on ajoute le niveau (sans doublon)
#         niv = grp["Niveau"]
#         if niv not in entry["niveaux"]:
#             entry["niveaux"].append(niv)

#         # on ajoute chacun des groupes dépendants (sans doublon)
#         for g in deps.split(","):
#             if g and g not in entry["groupes_dependants"]:
#                 entry["groupes_dependants"].append(g)

#     # ——— Ajout des options dans sous_groupes_config ———
#     for niveau, opts in interface["options_par_niveau"].items():
#         for opt in opts:
#             clean_opt = opt["Option"]                        # ex. "Latin", "Escalade"
#             # ← clé identique à vos autres raw_mat, e.g. "Option_Latin"
#             key_opt = f"Option_{clean_opt}"

#             entry = config["sous_groupes_config"].setdefault(
#                 key_opt,
#                 {
#                     "niveaux": [],
#                     "suffixe": f"_{clean_opt[:3].lower()}",
#                     "groupes_dependants": [],
#                     "type": "option"
#                 }
#             )

#             # 1) niveaux
#             if niveau not in entry["niveaux"]:
#                 entry["niveaux"].append(niveau)

#             # 2) collecte des groupes dépendants déclarés
#             for grp in interface["3_ressources"]["classes"]:
#                 if (grp.get("MatiereGroupe") == key_opt  # on matche sur "Option_Latin"
#                         and grp.get("Dependances")):
#                     for g in grp["Dependances"].split(","):
#                         if g and g not in entry["groupes_dependants"]:
#                             entry["groupes_dependants"].append(g)

#             # 3) fallback : classes de base si pas de dépendances déclarées
#             if not entry["groupes_dependants"]:
#                 for grp in interface["3_ressources"]["classes"]:
#                     if not grp.get("Dependances") and grp["Niveau"] == niveau:
#                         cls = grp["Classe"]
#                         if cls not in entry["groupes_dependants"]:
#                             entry["groupes_dependants"].append(cls)

#     # (optionnel) trier pour cohérence
#     for v in config["sous_groupes_config"].values():
#         v["niveaux"].sort()
#         v["groupes_dependants"].sort()



#     # Affectations spécifiques
#     config["affectation_matiere_salle"] = {}
#     for salle in salles:
#         matiere = salle.get("Matieres")
#         if matiere not in ("", None):
#             if matiere not in config["affectation_matiere_salle"]:
#                 config["affectation_matiere_salle"][matiere] = salle["Nom"]
#             else:
#                 varSecur = config["affectation_matiere_salle"][matiere]
#                 if isinstance(varSecur, str):
#                     config["affectation_matiere_salle"][matiere] = [varSecur, salle["Nom"]]
#                 else:
#                     config["affectation_matiere_salle"][matiere].append(salle["Nom"])
            
#     config["permanence"] = {
#         "nom_salle": "Salle_Permanence",
#         "capacite": interface["contraintes_additionnelles"]["cantine_permanence"]["capacite_permanence"]
#     }

#     varCantine = config["heures"]
#     config["cantine"] = {
#         "capacite": interface["contraintes_additionnelles"]["cantine_permanence"]["capacite_cantine"],
#         "creneaux_dejeuner": [varCantine[3], varCantine[4]],
#         "assignation_niveaux": {
#             varCantine[3]: ["6e", "5e"],
#             varCantine[4]: ["4e", "3e"]
#         },
#         "proportion_demi_pensionnaire": interface["contraintes_additionnelles"]["cantine_permanence"]["taux_cantine"],
#         "priorite_active": (
#             interface["contraintes_additionnelles"]["cantine_permanence"]["fin_jeunes_plus_tot"].lower() == "oui"
#         )
#     }

#     # Poids et contraintes supplémentaires 
#     poidsNiveaux = interface["contraintes_additionnelles"]["poids_par_niveau"]

#     config["poids_matieres_par_niveau"] = {}
#     for niveau, matieres in poidsNiveaux.items():
#         if niveau not in config["poids_matieres_par_niveau"]:
#             config["poids_matieres_par_niveau"][niveau] = {}
#         for matiere, poids in matieres.items():
#             if matiere == "poids_max":
#                 continue
#             else:
#                 config["poids_matieres_par_niveau"][niveau].update({matiere: poids})

#     config["poids_cartable_max_somme_par_niveau"] = {
#         niveau: infos.get("poids_max", None)
#         for niveau, infos in poidsNiveaux.items()
#     }

#     varEnchainement = interface["contraintes_3_4"]["enchainement"]
#     config["mat_exclu_suite"] = []
#     for contrainte in varEnchainement:
#         if contrainte.get("Type") == "Interdiction":
#             entry = {
#                 "classes": contrainte.get("Qui"),
#                 "matiere1": contrainte.get("CoursA"),
#                 "matiere2": contrainte.get("CoursB"),
#                 "contrainte": "forte"
#             }
            
#             config["mat_exclu_suite"].append(entry)

#     config["mat_inclu_suite"] = []
#     for contrainte in varEnchainement:
#         if contrainte.get("Type") == "Obligation":
#             entry = {
#                 "classes": contrainte.get("Qui"),
#                 "matiere1": contrainte.get("CoursA"),
#                 "matiere2": contrainte.get("CoursB"),
#                 "nb_fois": 2,
#                 "contrainte": "moyenne"
#             }
#             config["mat_inclu_suite"].append(entry)

#     varPlanning = interface["contraintes_3_4"]["planning"]
#     # config["max_heures_par_etendue"] = interface["contraintes_3_4"]["planning"]
#     config["max_heures_par_etendue"] = []
#     for iPlan in varPlanning:
#         varEtendu = iPlan.get("Etendue")
#         if(varEtendu.find("1/2") != -1):
#             varEtendu = "demi-journee"
#         elif(varEtendu.find("jour") != -1):
#             varEtendu = "journee"
#         entry = {
#             "niveau": iPlan.get("Qui"),
#             "matiere": iPlan.get("Matiere"),
#             "max_heures": iPlan.get("Nb_heures"),
#             "etendue" : varEtendu
#         }            
#         config["max_heures_par_etendue"].append(entry)

#     varCoursPlanning = interface["contraintes_3_4"]["cours_planning"]
#     config["mat_horaire_donne_v2"] = []
#     for iCoursPlan in varCoursPlanning:
#         if iCoursPlan.get("Type") == "Obligation":
#             # on récupère la chaîne "HH:MM - HH:MM"
#             heure_str = iCoursPlan.get("Heure")  
#             # on splitte pour avoir ["HH:MM", "-", "HH:MM"]
#             start, _, end = heure_str.split()
#             # on découpe heures et minutes
#             h1, m1 = start.split(":")
#             h2, m2 = end.split(":")
#             # on forme "HhMM"
#             p_h_min = f"{int(h1)}h{m1}"
#             p_h_max = f"{int(h2)}h{m2}"
#             entry = {
#                 "classes":   iCoursPlan.get("Qui"),
#                 "matiere":   iCoursPlan.get("Matiere"),
#                 "jour":     iCoursPlan.get("Jour"),
#                 "horaire_min": p_h_min,
#                 "horaire_max": p_h_max,
#                 "nb_fois":    1
#             }
#             config["mat_horaire_donne_v2"].append(entry)
#     # Enregistre le résultat
#     with open(path_config, "w", encoding="utf-8") as f:
#         json.dump(config, f, indent=2, ensure_ascii=False)

#     return config


# transformer_interface_vers_config(
#     path_interface=os.path.join("data", "data_interface.json"),
#     path_config   =os.path.join("data", "config.json")
# )

# Fonction pour initialiser les données à partir du fichier de configuration JSON
def init_donnees(chemin_config="data/config.json"):
    """
    Charge la configuration JSON à partir du chemin spécifié et initialise
    l'ensemble des constantes pour la génération des emplois du temps.

    Arguments:
        chemin_config (str): Chemin vers le fichier JSON de configuration.

    Retourne:
        dict: Un dictionnaire contenant :
            - config: contenu brut du JSON
            - SEMAINES: liste des semaines ("Semaine A", "Semaine B")
            - JOURS: liste des jours de la semaine
            - HEURES: liste des créneaux horaires
            - MATIERES: liste des matières
            - PROFESSEURS: dictionnaire des professeurs par matière
            - VOLUME_HORAIRE: volumes horaires par niveau et matière
            - INDISPONIBILITES_PROFS: contraintes d'indisponibilité des profs
            - INDISPONIBILITES_SALLES: contraintes d'indisponibilité des salles
            - PREFERENCES_PROFS: préférences horaires des profs
            - SOUS_GROUPES_CONFIG: configuration des sous-groupes
            - NIVEAUX: niveaux d'enseignement (ex. "6e", "5e", etc.)
            - AFFECTATION_MATIERE_SALLE: mapping matière/prof → salle
            - SALLES_GENERALES: liste des salles communes
            - CLASSES_BASE: liste des classes de base (sans sous-groupes)
            - CAPACITES_SALLES: capacités des salles
            - CAPACITES_CLASSES: capacités des classes
            - MAX_HEURES_PAR_ETENDUE: règles pour nombre max d'heures par étendue
            - JOURS_SANS_APRES_MIDI: jours sans cours l'après-midi
            - PREFERENCES_SALLE_PROF: préférences de salle pour certains profs
            - MATIERES_SOUSGROUPES: dict des sous-groupes de matières
            - MATIERES_SCIENTIFIQUE / LANGUES / ARTISTIQUES: listes de matières par catégorie
            - SOUS_GROUPES: liste des noms complets de sous-groupes (classe + suffixe)
            - SOUS_GROUPES_SUFFIXES: mapping suffixe → nom de matière
            - CLASSES: toutes les classes, y compris sous-groupes
    """
    # 1) Charger le JSON
    with open(chemin_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 2) Constantes bihebdo
    MODE_BIHEBDO = True 
    SEMAINES = ["Semaine A", "Semaine B"]

    # 3) Extraire les principaux blocs depuis la config
    JOURS = config["jours"]
    HEURES = config["heures"]
    MATIERES = config["matieres"]
    PROFESSEURS = config["professeurs"]
    VOLUME_HORAIRE = config["volume_horaire"]
    INDISPONIBILITES_PROFS = config["indisponibilites_profs"]
    INDISPONIBILITES_SALLES = config["indisponibilites_salles"]
    PREFERENCES_PROFS = config["preferences_profs"]
    SOUS_GROUPES_CONFIG = config["sous_groupes_config"]
    NIVEAUX = config["niveaux"]
    AFFECTATION_MATIERE_SALLE = config.get("affectation_matiere_salle", {})
    SALLES_GENERALES = config.get("salles_generales", [])
    CLASSES_BASE = config["classes_base"]
    CAPACITES_SALLES = config.get("capacites_salles", {})
    CAPACITES_CLASSES = config.get("capacites_classes", {})
    MAX_HEURES_PAR_ETENDUE = config.get("max_heures_par_etendue", [])
    JOURS_SANS_APRES_MIDI = set(config.get("jours_sans_apres_midi", []))
    PREFERENCES_SALLE_PROF = config.get("preferences_salle_professeur", {})

    # 4) Sous-groupes de matières
    MATIERES_SOUSGROUPES = config["sousGroupes_matieres"]
    MATIERES_SCIENTIFIQUE = MATIERES_SOUSGROUPES["Scientifique"]
    MATIERES_LANGUES = MATIERES_SOUSGROUPES["Langues"]
    MATIERES_ARTISTIQUES = MATIERES_SOUSGROUPES["Artistique"]

    # 5) Recalculer SOUS_GROUPES et CLASSES
    # ── 5) Recalculer SOUS_GROUPES, SOUS_GROUPES_SUFFIXES et CLASSES ──
    SOUS_GROUPES = []
    SOUS_GROUPES_SUFFIXES = {}
    # on suppose que CLASSES_BASE et SOUS_GROUPES_CONFIG sont déjà chargés
    for matiere, cfg in SOUS_GROUPES_CONFIG.items():
        suffixe = cfg["suffixe"]
        # on mémorise la correspondance suffixe → matière
        SOUS_GROUPES_SUFFIXES[suffixe] = matiere
        # on récupère soit la liste explicite, soit le fallback par niveau
        dependants = cfg.get(
            "groupes_dependants",
            [cl for cl in CLASSES_BASE if cl[:2] in cfg["niveaux"]]
        )
        for classe in dependants:
            SOUS_GROUPES.append(f"{classe}{suffixe}")

    # map des suffixes vers leur type (par défaut "LV")
    SOUS_GROUPES_TYPES = {
        cfg["suffixe"]: cfg.get("type", "LV")
        for cfg in SOUS_GROUPES_CONFIG.values()
    }

    # on regénère la liste complète des classes (base + sous-groupes)
    CLASSES = CLASSES_BASE + SOUS_GROUPES

    # ── fin du bloc ──

    # 6) Retourner tout ce dont on aura besoin par la suite
    return {
        "config": config,  # contenu brut du JSON
        "SEMAINES": SEMAINES,
        "JOURS": JOURS,
        "HEURES": HEURES,
        "MATIERES": MATIERES,
        "PROFESSEURS": PROFESSEURS,
        "VOLUME_HORAIRE": VOLUME_HORAIRE,
        "INDISPONIBILITES_PROFS": INDISPONIBILITES_PROFS,
        "INDISPONIBILITES_SALLES": INDISPONIBILITES_SALLES,
        "PREFERENCES_PROFS": PREFERENCES_PROFS,
        "SOUS_GROUPES_CONFIG": SOUS_GROUPES_CONFIG,
        "NIVEAUX": NIVEAUX,
        "AFFECTATION_MATIERE_SALLE": AFFECTATION_MATIERE_SALLE,
        "SALLES_GENERALES": SALLES_GENERALES,
        "CLASSES_BASE": CLASSES_BASE,
        "CAPACITES_SALLES": CAPACITES_SALLES,
        "CAPACITES_CLASSES": CAPACITES_CLASSES,
        "MAX_HEURES_PAR_ETENDUE": MAX_HEURES_PAR_ETENDUE,
        "JOURS_SANS_APRES_MIDI": JOURS_SANS_APRES_MIDI,
        "PREFERENCES_SALLE_PROF": PREFERENCES_SALLE_PROF,
        "MATIERES_SOUSGROUPES": MATIERES_SOUSGROUPES,
        "MATIERES_SCIENTIFIQUE": MATIERES_SCIENTIFIQUE,
        "MATIERES_LANGUES": MATIERES_LANGUES,
        "MATIERES_ARTISTIQUES": MATIERES_ARTISTIQUES,
        "SOUS_GROUPES": SOUS_GROUPES,
        "SOUS_GROUPES_SUFFIXES": SOUS_GROUPES_SUFFIXES,
        "SOUS_GROUPES_TYPES": SOUS_GROUPES_TYPES,
        "CLASSES": CLASSES
    }

def initialiser_globals(chemin_config="data/config.json"):
    """
    Charge la configuration et extrait toutes les variables globales nécessaires.
    Retourne un tuple de (config, SEMAINES, JOURS, HEURES, MATIERES, PROFESSEURS,
    VOLUME_HORAIRE, INDISPONIBILITES_PROFS, INDISPONIBILITES_SALLES,
    PREFERENCES_PROFS, SOUS_GROUPES_CONFIG, NIVEAUX,
    AFFECTATION_MATIERE_SALLE, SALLES_GENERALES, CLASSES_BASE,
    CAPACITES_SALLES, CAPACITES_CLASSES, MAX_HEURES_PAR_ETENDUE,
    JOURS_SANS_APRES_MIDI, PREFERENCES_SALLE_PROF, MATIERES_SOUSGROUPES,
    MATIERES_SCIENTIFIQUE, MATIERES_LANGUES, MATIERES_ARTISTIQUES,
    SOUS_GROUPES, SOUS_GROUPES_SUFFIXES, SOUS_GROUPES_TYPES, CLASSES)
    """
    d = init_donnees(chemin_config)
    config                     = d["config"]
    SEMAINES                   = d["SEMAINES"]
    JOURS                      = d["JOURS"]
    HEURES                     = d["HEURES"]
    MATIERES                   = d["MATIERES"]
    PROFESSEURS                = d["PROFESSEURS"]
    VOLUME_HORAIRE             = d["VOLUME_HORAIRE"]
    INDISPONIBILITES_PROFS     = d["INDISPONIBILITES_PROFS"]
    INDISPONIBILITES_SALLES    = d["INDISPONIBILITES_SALLES"]
    PREFERENCES_PROFS          = d["PREFERENCES_PROFS"]
    SOUS_GROUPES_CONFIG        = d["SOUS_GROUPES_CONFIG"]
    NIVEAUX                    = d["NIVEAUX"]
    AFFECTATION_MATIERE_SALLE  = d["AFFECTATION_MATIERE_SALLE"]
    SALLES_GENERALES           = d["SALLES_GENERALES"]
    CLASSES_BASE               = d["CLASSES_BASE"]
    CAPACITES_SALLES           = d["CAPACITES_SALLES"]
    CAPACITES_CLASSES          = d["CAPACITES_CLASSES"]
    MAX_HEURES_PAR_ETENDUE     = d["MAX_HEURES_PAR_ETENDUE"]
    JOURS_SANS_APRES_MIDI      = d["JOURS_SANS_APRES_MIDI"]
    PREFERENCES_SALLE_PROF     = d["PREFERENCES_SALLE_PROF"]
    MATIERES_SOUSGROUPES       = d["MATIERES_SOUSGROUPES"]
    MATIERES_SCIENTIFIQUE      = d["MATIERES_SCIENTIFIQUE"]
    MATIERES_LANGUES           = d["MATIERES_LANGUES"]
    MATIERES_ARTISTIQUES       = d["MATIERES_ARTISTIQUES"]
    SOUS_GROUPES               = d["SOUS_GROUPES"]
    SOUS_GROUPES_SUFFIXES      = d["SOUS_GROUPES_SUFFIXES"]
    SOUS_GROUPES_TYPES         = d["SOUS_GROUPES_TYPES"]
    CLASSES                    = d["CLASSES"]

    return (
        config,
        SEMAINES,
        JOURS,
        HEURES,
        MATIERES,
        PROFESSEURS,
        VOLUME_HORAIRE,
        INDISPONIBILITES_PROFS,
        INDISPONIBILITES_SALLES,
        PREFERENCES_PROFS,
        SOUS_GROUPES_CONFIG,
        NIVEAUX,
        AFFECTATION_MATIERE_SALLE,
        SALLES_GENERALES,
        CLASSES_BASE,
        CAPACITES_SALLES,
        CAPACITES_CLASSES,
        MAX_HEURES_PAR_ETENDUE,
        JOURS_SANS_APRES_MIDI,
        PREFERENCES_SALLE_PROF,
        MATIERES_SOUSGROUPES,
        MATIERES_SCIENTIFIQUE,
        MATIERES_LANGUES,
        MATIERES_ARTISTIQUES,
        SOUS_GROUPES,
        SOUS_GROUPES_SUFFIXES,
        SOUS_GROUPES_TYPES,
        CLASSES
    )

(
    config,
    SEMAINES,
    JOURS,
    HEURES,
    MATIERES,
    PROFESSEURS,
    VOLUME_HORAIRE,
    INDISPONIBILITES_PROFS,
    INDISPONIBILITES_SALLES,
    PREFERENCES_PROFS,
    SOUS_GROUPES_CONFIG,
    NIVEAUX,
    AFFECTATION_MATIERE_SALLE,
    SALLES_GENERALES,
    CLASSES_BASE,
    CAPACITES_SALLES,
    CAPACITES_CLASSES,
    MAX_HEURES_PAR_ETENDUE,
    JOURS_SANS_APRES_MIDI,
    PREFERENCES_SALLE_PROF,
    MATIERES_SOUSGROUPES,
    MATIERES_SCIENTIFIQUE,
    MATIERES_LANGUES,
    MATIERES_ARTISTIQUES,
    SOUS_GROUPES,
    SOUS_GROUPES_SUFFIXES,
    SOUS_GROUPES_TYPES,
    CLASSES
) = initialiser_globals()



def creer_modele():
    """
    Construit et retourne un modèle CP-SAT configuré pour générer un emploi du
    temps bihebdomadaire (Semaine A/B) respectant un ensemble de contraintes.

    Ce modèle comprend :
      - Attribution des salles pour chaque professeur n'ayant pas de salle dédiée.
      - Variables d'assignation des matières, des salles et des professeurs par créneau.
      - Contraintes de non-chevauchement de professeurs et de salles.
      - Tenue du volume horaire bihebdomadaire pour chaque classe / sous-groupe.
      - Gestion des jours sans après-midi, cantine, permanence, etc.
      - Objectif de minimisation des heures de permanence et des pénalités de préférence.
    
    Retourne:
        model (cp_model.CpModel): le modèle CP-SAT prêt à être résolu.
        emploi_du_temps (dict): dictionnaire de variables IntVar pour matières.
        emploi_du_temps_salles (dict): dictionnaire de variables IntVar pour salles.
        emploi_du_temps_profs (dict): dictionnaire de variables IntVar/BoolVar pour professeurs.
    """
    # On collecte d'abord la liste des professeurs qui n'ont pas de salle assignée
    professeurs_sans_salle = set()

    # Pour chaque matière, on identifie si le professeur référencé a déjà une salle
    for matiere, prof in PROFESSEURS.items():
        if isinstance(prof, dict):
            # Cas spécial : plusieurs profs selon niveau
            for niveau, profs in prof.items():
                if isinstance(profs, list):
                    for prof_nom in profs:
                        if prof_nom not in AFFECTATION_MATIERE_SALLE:
                            professeurs_sans_salle.add(prof_nom)
                else:
                    if profs not in AFFECTATION_MATIERE_SALLE:
                        professeurs_sans_salle.add(profs)
        else:
            # Un seul professeur pour toute la matière
            if prof not in AFFECTATION_MATIERE_SALLE:
                professeurs_sans_salle.add(prof)

    professeurs_sans_salle = list(professeurs_sans_salle)
    available_salles = SALLES_GENERALES.copy()

    # On assigne en priorité la salle préférée si le professeur en a indiqué une
    for prof in list(professeurs_sans_salle):  # itération sur une copie
        if prof in PREFERENCES_SALLE_PROF:
            salle_preferee = PREFERENCES_SALLE_PROF[prof]
            # On l'insère dans le mapping matière/prof → salle
            AFFECTATION_MATIERE_SALLE[prof] = salle_preferee
            # On retire cette salle du pool général
            if salle_preferee in available_salles:
                available_salles.remove(salle_preferee)
            # On le supprime également de la liste des sans-salle
            professeurs_sans_salle.remove(prof)

    # Pour chaque prof restant, on leur attribue une salle en round-robin
    for i, prof in enumerate(professeurs_sans_salle):
        if available_salles:
            salle_assignee = available_salles[i % len(available_salles)]
            AFFECTATION_MATIERE_SALLE[prof] = salle_assignee
        else:
            # Si on a épuisé available_salles, on recycle le listing original
            AFFECTATION_MATIERE_SALLE[prof] = SALLES_GENERALES[i % len(SALLES_GENERALES)]

    # Affichage de la répartition finale prof → salle
    print("Répartition des professeurs sur les salles :")
    for prof, salle in AFFECTATION_MATIERE_SALLE.items():
        print(f"{prof} → {salle}")


    # On calcule maintenant le volume horaire bihebdomadaire pour chaque niveau/matière
    VOLUME_HORAIRE_BIHEBDO = {}
    for niveau, matieres in VOLUME_HORAIRE.items():
        VOLUME_HORAIRE_BIHEBDO[niveau] = {}
        for matiere, volume in matieres.items():
            base = int(volume)
            # Si c'est un nombre entier, on répartit équitablement
            if volume % 1 == 0:
                A = B = volume
            else:
                # Sinon, on répartit la demi-heure aléatoirement entre A et B
                if random.choice([True, False]):
                    A, B = base + 1, base
                else:
                    A, B = base, base + 1
            VOLUME_HORAIRE_BIHEBDO[niveau][matiere] = {"Semaine A": A, "Semaine B": B}

    # Initialisation du modèle
    model = cp_model.CpModel()

    # Nombre fixe de salles : on numérote de 1 à N
    NOMBRE_DE_SALLES = 24

    # Dictionnaires pour stocker les variables du modèle
    emploi_du_temps = {semaine: {} for semaine in SEMAINES} # Dictionnaire pour les matières
    emploi_du_temps_salles = {semaine: {} for semaine in SEMAINES} # Dictionnaire pour les salles
    emploi_du_temps_profs = {semaine: {} for semaine in SEMAINES} # Dictionnaire pour les professeurs

    # Pour chaque classe (base et sous-groupes), chaque semaine, jour et heure :
    for classe in CLASSES:
        for semaine in SEMAINES:
            for j, jour in enumerate(JOURS):
                for h, heure in enumerate(HEURES):
                    niveau = classe[:2]

                    # Détermination des matières autorisées : 
                    # si c'est un sous-groupe, seule la langue correspondante
                    for suffixe, langue in SOUS_GROUPES_SUFFIXES.items():
                        if suffixe in classe:
                            matieres_autorisees = [langue]
                            break
                    else:
                        # sinon, toutes les matières générales hors sous-groupes
                        matieres_autorisees = [
                            m for m in VOLUME_HORAIRE[niveau].keys()
                            if m not in SOUS_GROUPES_SUFFIXES.values()
                        ]

                    # Indices admis pour la variable : 0 = pas de cours, 1..N = index matière
                    matiere_indices_autorises = [0] + [
                        MATIERES.index(m) + 1 for m in matieres_autorisees
                    ]

                    key = (classe, j, h)
                    # Variable IntVar pour la matière attribuée à ce créneau
                    emploi_du_temps[semaine][key] = model.NewIntVarFromDomain(
                        cp_model.Domain.FromValues(matiere_indices_autorises),
                        f"{classe}_{jour}_{heure}_{semaine.replace(' ', '_')}"
                    )
                    # Variable IntVar pour la salle (0 signifie pas de cours)
                    emploi_du_temps_salles[semaine][key] = model.NewIntVar(
                        0, NOMBRE_DE_SALLES,
                        f"salle_{classe}_{jour}_{heure}_{semaine.replace(' ', '_')}"
                    )

                    # Pour chaque matière autorisée, si plusieurs profs possibles, créer IntVar prof
                    for m in matieres_autorisees:
                        prof_ref = PROFESSEURS[m]
                        if isinstance(prof_ref, dict):
                            # Extraction de la liste de profs pour ce niveau
                            profs_niv = prof_ref.get(niveau, [])
                            if isinstance(profs_niv, list) and len(profs_niv) > 1:
                                key_prof = (classe, j, h, m, semaine)
                                emploi_du_temps_profs[semaine][key_prof] = model.NewIntVar(
                                    0, len(profs_niv) - 1,
                                    f"prof_{classe}_{j}_{h}_{m}_{semaine.replace(' ', '_')}"
                                )

    # Dictionnaire d'assignation prof/classe par matière ; utile dans certaines contraintes
    assignation_prof_classe = {}  # (classe, matiere, semaine) → bool ou indice

    # Pour chaque matière, on introduit les variables d'équité de répartition des profs
    for matiere, prof_ref in PROFESSEURS.items():
        # ─── Cas A : dictionnaire niveau → liste de profs (ex. Maths : {"6e": ["Dupont", ...], ...})
        if isinstance(prof_ref, dict):
            for niveau, liste_profs in prof_ref.items():
                # Si liste_profs n'est pas une liste ou a longueur ≤ 1, on skip
                if not isinstance(liste_profs, list) or len(liste_profs) <= 1:
                    continue

                # 1) Pour chaque créneau d'une classe de base de ce niveau, on crée un IntVar d'indice du prof
                for semaine in SEMAINES:
                    for cl in CLASSES_BASE:
                        if not cl.startswith(niveau):
                            continue
                        for j in range(len(JOURS)):
                            for h in range(len(HEURES)):
                                key_prof = (cl, j, h, matiere, semaine)
                                emploi_du_temps_profs[semaine][key_prof] = model.NewIntVar(
                                    0, len(liste_profs) - 1,
                                    f"prof_{cl}_{j}_{h}_{matiere}_{semaine.replace(' ', '_')}"
                                )

                # 2) Création de compteurs pour chaque prof (nombre d'heures attribuées)
                counts = []
                for prof in liste_profs:
                    var_count = model.NewIntVar(
                        0,
                        len(CLASSES_BASE) * len(JOURS) * len(HEURES),
                        f"nb_{matiere}_{niveau}_{prof.replace(' ', '_')}"
                    )
                    counts.append(var_count)

                # 3) Pour chaque prof d'indice i, créer les BoolVar indiquant "ce prof est choisi ici"
                for i, prof in enumerate(liste_profs):
                    occurrences = []
                    for semaine in SEMAINES:
                        for cl in CLASSES_BASE:
                            if not cl.startswith(niveau):
                                continue
                            for j in range(len(JOURS)):
                                for h in range(len(HEURES)):
                                    key_prof = (cl, j, h, matiere, semaine)
                                    if key_prof in emploi_du_temps_profs[semaine]:
                                        b = model.NewBoolVar(
                                            f"occur_{matiere}_{niveau}_{cl}_{j}_{h}_{prof.replace(' ', '_')}_{semaine.replace(' ', '_')}"
                                        )
                                        model.Add(
                                            emploi_du_temps_profs[semaine][key_prof] == i
                                        ).OnlyEnforceIf(b)
                                        model.Add(
                                            emploi_du_temps_profs[semaine][key_prof] != i
                                        ).OnlyEnforceIf(b.Not())
                                        occurrences.append(b)
                    # 4) Impose que le compteur = somme des occurrences pour ce prof
                    model.Add(counts[i] == sum(occurrences))

                # 5) Contrainte d'équité : pour tout couple (a,b), différence ≤ 1
                for a in range(len(liste_profs)):
                    for b in range(a + 1, len(liste_profs)):
                        model.Add(counts[a] - counts[b] <= 1)
                        model.Add(counts[b] - counts[a] <= 1)

        # ─── Cas B : liste globale de profs (ex. EPS : ["Richard", "X"])
        elif isinstance(prof_ref, list) and len(prof_ref) > 1:
            liste_profs = prof_ref

            # 1) Déterminer les classes concernées par cette matière
            classes_concernees = []
            for cl in CLASSES_BASE:
                niv = cl[:2]
                if matiere in VOLUME_HORAIRE.get(niv, {}):
                    classes_concernees.append(cl)

            # 2) Pour chaque créneau, créer IntVar pour choisir le prof (index dans liste_profs)
            for semaine in SEMAINES:
                for cl in classes_concernees:
                    for j in range(len(JOURS)):
                        for h in range(len(HEURES)):
                            key_prof = (cl, j, h, matiere, semaine)
                            emploi_du_temps_profs[semaine][key_prof] = model.NewIntVar(
                                0, len(liste_profs) - 1,
                                f"prof_{cl}_{j}_{h}_{matiere}_{semaine.replace(' ', '_')}"
                            )

            # 3) Création de compteurs pour chaque prof
            counts = []
            for prof in liste_profs:
                var_count = model.NewIntVar(
                    0,
                    len(CLASSES_BASE) * len(JOURS) * len(HEURES),
                    f"nb_{matiere}_{prof.replace(' ', '_')}"
                )
                counts.append(var_count)

            # 4) Pour chaque prof d'indice i, compter ses occurrences
            for i, prof in enumerate(liste_profs):
                occurrences = []
                for semaine in SEMAINES:
                    for cl in classes_concernees:
                        for j in range(len(JOURS)):
                            for h in range(len(HEURES)):
                                key_prof = (cl, j, h, matiere, semaine)
                                if key_prof in emploi_du_temps_profs[semaine]:
                                    b = model.NewBoolVar(
                                        f"occur_{matiere}_{cl}_{j}_{h}_{prof.replace(' ', '_')}_{semaine.replace(' ', '_')}"
                                    )
                                    model.Add(
                                        emploi_du_temps_profs[semaine][key_prof] == i
                                    ).OnlyEnforceIf(b)
                                    model.Add(
                                        emploi_du_temps_profs[semaine][key_prof] != i
                                    ).OnlyEnforceIf(b.Not())
                                    occurrences.append(b)
                model.Add(counts[i] == sum(occurrences))

            # 5) Contrainte d'équité
            for a in range(len(liste_profs)):
                for b in range(a + 1, len(liste_profs)):
                    model.Add(counts[a] - counts[b] <= 1)
                    model.Add(counts[b] - counts[a] <= 1)

        # ─── Cas C : exactement un prof (chaîne), rien à faire pour l'équité
        elif isinstance(prof_ref, str):
            pass

    # ─── Contrainte supplémentaire : même choix de prof entre Semaine A et B pour une classe donnée
    for (classe, matiere, semaine) in list(assignation_prof_classe.keys()):
        if semaine == "Semaine A":
            var_A = assignation_prof_classe[(classe, matiere, "Semaine A")]
            var_B = assignation_prof_classe.get((classe, matiere, "Semaine B"))
            if var_B is not None:
                model.Add(var_A == var_B)
                # On force la même attribution de prof pour A et B : attention aux cas où les profs diffèrent selon la config

    # ─── Contrainte : un même professeur ne peut pas enseigner deux classes différentes au même créneau
    # 1) Récupérer tous les noms de professeurs exploités    tous_les_profs = set()
    tous_les_profs = set()
    for mat, prof_ref in PROFESSEURS.items():
        if isinstance(prof_ref, str):
            tous_les_profs.add(prof_ref)
        elif isinstance(prof_ref, dict):
            for niv, val in prof_ref.items():
                if isinstance(val, str):
                    tous_les_profs.add(val)
                elif isinstance(val, list):
                    tous_les_profs.update(val)
        elif isinstance(prof_ref, list):
            tous_les_profs.update(prof_ref) 
            # On couvre ici tous les formats possibles (str, dict, list) pour consolider la liste des profs

    # MEMNIV_ACTIVES filtre les cours gérés dynamiquement : pense à vérifier la clé 'memnivmemcours' dans le JSON        
    MEMNIV_ACTIVES = {
        (entry["niveau"], entry["matiere"])
        for entry in config.get("memnivmemcours", [])
    }

   # 2) Pour chaque prof, semaine, créneau, on crée des BoolVar indiquant s'il donne cours dans chaque classe
    for p in tous_les_profs:
        for semaine in SEMAINES:
            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    bools_prof = []

                    # 2.a) Parcourir toutes les classes
                    for cl in CLASSES_BASE:
                        niveau_cl = cl[:2]

                        # 2.a.1) Cas où PROFESSEURS[mat] est une chaîne et égale à p
                        for m_idx, mat in enumerate(MATIERES, start=1):
                            if (niveau_cl, mat) in MEMNIV_ACTIVES:
                                continue
                            prof_ref = PROFESSEURS.get(mat)
                            if isinstance(prof_ref, str) and prof_ref == p:
                                b_cl_m = model.NewBoolVar(f"is_{p.replace(' ', '_')}_{cl}_{semaine}_{j}_{h}_matiere_{mat.replace(' ', '_')}")
                                var_mat = emploi_du_temps[semaine][(cl, j, h)]
                                model.Add(var_mat == m_idx).OnlyEnforceIf(b_cl_m)
                                model.Add(var_mat != m_idx).OnlyEnforceIf(b_cl_m.Not())
                                bools_prof.append(b_cl_m)

                        # 2.a.2) Cas où PROFESSEURS[mat] est un dict
                        for mat in MATIERES:
                            prof_ref = PROFESSEURS.get(mat)
                            mat_idx = MATIERES.index(mat) + 1

                            if isinstance(prof_ref, dict):
                                profs_niv = prof_ref.get(niveau_cl)
                                # a) Si c’est une chaîne de caractères
                                if isinstance(profs_niv, str) and profs_niv == p:
                                    b_cl_m = model.NewBoolVar(f"is_{p.replace(' ', '_')}_{cl}_{semaine}_{j}_{h}_matiere_{mat.replace(' ', '_')}")
                                    var_mat = emploi_du_temps[semaine][(cl, j, h)]
                                    model.Add(var_mat == mat_idx).OnlyEnforceIf(b_cl_m)
                                    model.Add(var_mat != mat_idx).OnlyEnforceIf(b_cl_m.Not())
                                    bools_prof.append(b_cl_m)

                                # b) Si c’est une liste
                                elif isinstance(profs_niv, list) and p in profs_niv:
                                    key_prof = (cl, j, h, mat, semaine)
                                    b_cl_m = model.NewBoolVar(f"is_{p.replace(' ', '_')}_{cl}_{semaine}_{j}_{h}_profIndex_{mat.replace(' ', '_')}")
                                    if key_prof in emploi_du_temps_profs[semaine]:
                                        idx_p = profs_niv.index(p)
                                        var_prof_index = emploi_du_temps_profs[semaine][key_prof]
                                        model.Add(var_prof_index == idx_p).OnlyEnforceIf(b_cl_m)
                                        model.Add(var_prof_index != idx_p).OnlyEnforceIf(b_cl_m.Not())
                                    else:
                                        var_mat = emploi_du_temps[semaine][(cl, j, h)]
                                        model.Add(var_mat == mat_idx).OnlyEnforceIf(b_cl_m)
                                        model.Add(var_mat != mat_idx).OnlyEnforceIf(b_cl_m.Not())
                                    bools_prof.append(b_cl_m)

                            # 2.a.3) Cas où PROFESSEURS[mat] est une liste simple [prof1, prof2, ...]
                            elif isinstance(prof_ref, list) and p in prof_ref:
                                key_prof = (cl, j, h, mat, semaine)
                                b_cl_m = model.NewBoolVar(f"is_{p.replace(' ', '_')}_{cl}_{semaine}_{j}_{h}_profIndex_{mat.replace(' ', '_')}")
                                if key_prof in emploi_du_temps_profs[semaine]:
                                    idx_p = prof_ref.index(p)
                                    var_prof_index = emploi_du_temps_profs[semaine][key_prof]
                                    model.Add(var_prof_index == idx_p).OnlyEnforceIf(b_cl_m)
                                    model.Add(var_prof_index != idx_p).OnlyEnforceIf(b_cl_m.Not())
                                else:
                                    var_mat = emploi_du_temps[semaine][(cl, j, h)]
                                    model.Add(var_mat == mat_idx).OnlyEnforceIf(b_cl_m)
                                    model.Add(var_mat != mat_idx).OnlyEnforceIf(b_cl_m.Not())
                                bools_prof.append(b_cl_m)

                    # 3) Enfin, on ajoute la contrainte : au plus un BoolVar de cette liste peut être à 1
                    if bools_prof:
                        model.Add(sum(bools_prof) <= 1) # Garantie qu’un prof n’est pas doublé sur le même créneau


    # ─── Contrainte : interdiction qu'une salle soit occupée par deux classes simultanément
    for semaine in SEMAINES:
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                for idx_salle, nom_salle in enumerate(SALLES_GENERALES, start=1):
                    bools_salle = []
                    for classe in CLASSES:
                        key = (classe, j, h)
                        salle_var = emploi_du_temps_salles[semaine][key]
                        b = model.NewBoolVar(f"{nom_salle}_{classe}_{j}_{h}_{semaine}_used")
                        model.Add(salle_var == idx_salle).OnlyEnforceIf(b)
                        model.Add(salle_var != idx_salle).OnlyEnforceIf(b.Not())
                        bools_salle.append(b)
                    model.Add(sum(bools_salle) <= 1)


    # ─── Contrainte : pas de cours les jours sans après-midi pour toutes les classes et sous-groupes
    for semaine in SEMAINES:
        for classe in CLASSES:
            for j, jour in enumerate(JOURS):
                if jour in JOURS_SANS_APRES_MIDI:
                    # On bloque tous les créneaux d'après-midi (index ≥ 5)
                    for h in range(5, len(HEURES)):
                        model.Add(emploi_du_temps[semaine][(classe, j, h)] == 0) # Bloque systématiquement l'après-midi pour les jours désignés 


    # ─── Contrainte : respecter le nombre maximal d'heures de chaque matière sur l'étendue journee/demi-journee
    for semaine in SEMAINES:
        for regle in MAX_HEURES_PAR_ETENDUE:
            niveau = regle["niveau"]
            matiere = regle["matiere"]
            matiere_index = MATIERES.index(matiere) + 1
            max_heures = regle["max_heures"]
            etendue = regle["etendue"]

            for classe in CLASSES_BASE:
                if not classe.startswith(niveau):
                    continue

                for j, jour in enumerate(JOURS):
                    # Si étendue = journée entière
                    if etendue == "journee":
                        heures_cibles = list(range(len(HEURES)))
                        vars_jour = []
                        for h in heures_cibles:
                            key = (classe, j, h)
                            if key in emploi_du_temps[semaine]:
                                v = model.NewBoolVar(f"{classe}_{semaine}_{j}_{h}_{matiere}_limit")
                                model.Add(emploi_du_temps[semaine][key] == matiere_index).OnlyEnforceIf(v)
                                model.Add(emploi_du_temps[semaine][key] != matiere_index).OnlyEnforceIf(v.Not())
                                vars_jour.append(v)
                        model.Add(sum(vars_jour) <= max_heures) # Respect du maximum d'heures sur la journée

                    # Si étendue = demi-journée (matin et après-midi séparés)
                    elif etendue == "demi-journee":
                        matin = list(range(4))
                        apres = list(range(5, len(HEURES)))

                        for label, heures in [("matin", matin), ("apres", apres)]:
                            vars_bloc = []
                            for h in heures:
                                key = (classe, j, h)
                                if key in emploi_du_temps[semaine]:
                                    v = model.NewBoolVar(f"{classe}_{semaine}_{j}_{label}_{h}_{matiere}_limit")
                                    model.Add(emploi_du_temps[semaine][key] == matiere_index).OnlyEnforceIf(v)
                                    model.Add(emploi_du_temps[semaine][key] != matiere_index).OnlyEnforceIf(v.Not())
                                    vars_bloc.append(v)
                            model.Add(sum(vars_bloc) <= max_heures) # Respect du maximum d'heures par demi-journée (matin/après-midi)


    """
    for niveau in NIVEAUX:
        classes_niveau = [classe for classe in CLASSES_BASE if classe.startswith(niveau)]

        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                for m in range(len(MATIERES)):
                    matiere_code = m + 1  # car 0 = trou

                    vars_matiere = []
                    for classe in classes_niveau:
                        var = model.NewBoolVar(f"{classe}_{j}_{h}_is_{matiere_code}")
                        model.Add(emploi_du_temps[(classe, j, h)] == matiere_code).OnlyEnforceIf(var)
                        model.Add(emploi_du_temps[(classe, j, h)] != matiere_code).OnlyEnforceIf(var.Not())
                        vars_matiere.append(var)

                    # Max 1 classe de ce niveau ne peut avoir cette matière à cette heure
                    model.Add(sum(vars_matiere) <= 1)
    """

    
    # ─── Contrainte : équilibre d'affectation des profs sur les matières (deuxième passe pour certains profils)
    # On cherche ici à répartir équitablement les heures entre tous les profs d’une même matière
    for matiere, prof_ref in PROFESSEURS.items():
        # a) Cas dict niveau → liste de profs (équité selon niveaux)
        if isinstance(prof_ref, dict):
            for niveau, liste_profs in prof_ref.items():
                if isinstance(liste_profs, list) and len(liste_profs) > 1:
                    # Création de compteurs "counts[p]" pour chaque prof
                    counts = []
                    for prof in liste_profs:
                        var_count = model.NewIntVar(
                            0,
                            len(CLASSES) * len(JOURS) * len(HEURES),
                            f"nb_{matiere}_{niveau}_{prof.replace(' ', '_')}"
                        )
                        counts.append(var_count)

                    # Pour chaque prof p, calcul des occurrences selon les variables d'index
                    for i, prof in enumerate(liste_profs):
                        occurrences = []
                        for semaine in SEMAINES:
                            for classe in CLASSES:
                                if not classe.startswith(niveau):
                                    continue
                                for j in range(len(JOURS)):
                                    for h in range(len(HEURES)):
                                        key_prof = (classe, j, h, matiere, semaine)
                                        if key_prof in emploi_du_temps_profs[semaine]:
                                            b = model.NewBoolVar(
                                                f"occur_{matiere}_{niveau}_{classe}_{j}_{h}_{prof.replace(' ', '_')}_{semaine.replace(' ', '_')}"
                                            )
                                            model.Add(
                                                emploi_du_temps_profs[semaine][key_prof] == i
                                            ).OnlyEnforceIf(b)
                                            model.Add(
                                                emploi_du_temps_profs[semaine][key_prof] != i
                                            ).OnlyEnforceIf(b.Not())
                                            occurrences.append(b)
                        model.Add(counts[i] == sum(occurrences)) # On associe chaque compteur à la somme des présences de p pour cette matière

                    # Contrainte d'équité
                    # Garantit que la charge horaire est équilibrée entre tous les profs listés
                    for a in range(len(liste_profs)):
                        for b in range(a + 1, len(liste_profs)):
                            model.Add(counts[a] - counts[b] <= 1)
                            model.Add(counts[b] - counts[a] <= 1)

        # b) Cas liste globale de profs
        elif isinstance(prof_ref, list) and len(prof_ref) > 1:
            counts = []
            for prof in prof_ref:
                var_count = model.NewIntVar(
                    0,
                    len(CLASSES) * len(JOURS) * len(HEURES),
                    f"nb_{matiere}_{prof.replace(' ', '_')}"
                )
                counts.append(var_count)

            for i, prof in enumerate(prof_ref):
                occurrences = []
                for semaine in SEMAINES:
                    for classe in CLASSES:
                        niveau = classe[:2]
                        if matiere not in VOLUME_HORAIRE.get(niveau, {}):
                            continue
                        for j in range(len(JOURS)):
                            for h in range(len(HEURES)):
                                key_prof = (classe, j, h, matiere, semaine)
                                if key_prof in emploi_du_temps_profs[semaine]:
                                    b = model.NewBoolVar(
                                        f"occur_{matiere}_{classe}_{j}_{h}_{prof.replace(' ', '_')}_{semaine.replace(' ', '_')}"
                                    )
                                    model.Add(
                                        emploi_du_temps_profs[semaine][key_prof] == i
                                    ).OnlyEnforceIf(b)
                                    model.Add(
                                        emploi_du_temps_profs[semaine][key_prof] != i
                                    ).OnlyEnforceIf(b.Not())
                                    occurrences.append(b)
                model.Add(counts[i] == sum(occurrences)) # Même principe de comptage pour une liste plate de profs

            # Egalisation de la distribution des cours pour tous les profs de la liste
            for a in range(len(prof_ref)):
                for b in range(a + 1, len(prof_ref)):
                    model.Add(counts[a] - counts[b] <= 1)
                    model.Add(counts[b] - counts[a] <= 1)

    # ─── Contrainte : les sous-groupes ne doivent pas chevaucher leur classe principale
    # On interdit aux sous-groupes LV/option d’avoir cours en même temps que la classe de base
    for semaine in SEMAINES:
        for sous_groupe in SOUS_GROUPES:
            suffixe     = next(s for s in SOUS_GROUPES_SUFFIXES if s in sous_groupe)
            classe_base = sous_groupe.replace(suffixe, "")
            sg_type     = SOUS_GROUPES_TYPES[suffixe]
            # on applique systématiquement aux options ET à toutes les LV
            if sg_type not in ("option", "LV"):
                continue

            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    var_sg = emploi_du_temps[semaine][(sous_groupe, j, h)]
                    var_cp = emploi_du_temps[semaine][(classe_base, j, h)]

                    # Bool pour « le sous-groupe a cours ici »
                    sg_has_cours = model.NewBoolVar(f"{sous_groupe}_has_cours_{j}_{h}_{semaine}")
                    model.Add(var_sg != 0).OnlyEnforceIf(sg_has_cours)
                    model.Add(var_sg == 0).OnlyEnforceIf(sg_has_cours.Not())

                    # interdiction : si le sous-groupe a cours, la classe principale doit être vide
                    model.Add(var_cp == 0).OnlyEnforceIf(sg_has_cours)


    # ─── Contrainte : deux sous-groupes LV/options d’une même classe ne peuvent pas se chevaucher,
    # sauf si la classe a 2 LV ou plus  ⇒ on les laisse alors courir en parallèle
    # Gestion spéciale : on autorise la superposition si plusieurs LV sont prévues
    for semaine in SEMAINES:
        for classe_base in CLASSES_BASE:
            # on récupère tous les suffixes de sous-groupes option ou LV pour cette classe
            sg_entries = [
                (sfx, f"{classe_base}{sfx}")
                for sfx, typ in SOUS_GROUPES_TYPES.items()
                if typ in ("option", "LV") and f"{classe_base}{sfx}" in CLASSES
            ]
            # s’il y en a moins de 2, rien à faire
            if len(sg_entries) < 2:
                continue

            # si c’est parce qu’il y a 2 (ou plus) LV pour cette classe, on tolère la superposition
            lv_entries = [e for e in sg_entries if SOUS_GROUPES_TYPES[e[0]] == "LV"]
            if len(lv_entries) > 1:
                # on saute complètement cette classe_base
                continue

            # sinon on interdit tout chevauchement entre **tous** ces sous-groupes
            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    bools_sg = []
                    for sfx, grp in sg_entries:
                        key = (grp, j, h)
                        b = model.NewBoolVar(f"{grp}_no_overlap_{j}_{h}_{semaine}")
                        model.Add(emploi_du_temps[semaine][key] != 0).OnlyEnforceIf(b)
                        model.Add(emploi_du_temps[semaine][key] == 0).OnlyEnforceIf(b.Not())
                        bools_sg.append(b)
                    model.Add(sum(bools_sg) <= 1) # Assure qu’au plus un sous-groupe en option/LV est actif par créneau

        # ─── Contrainte : synchronisation des LV entre classes dépendantes ───────────
        # Tous les sous-groupes LV listés doivent démarrer et finir leurs cours simultanément
        for semaine in SEMAINES:
            for mat_sg, cfg in SOUS_GROUPES_CONFIG.items():
                # Ne traiter que les LV
                if cfg.get("type") != "LV":
                    continue

                suffixe     = cfg["suffixe"]
                dependants  = cfg.get("groupes_dependants", [])
                # Il faut au moins deux classes pour synchroniser
                if len(dependants) < 2:
                    continue

                # Construire la liste des noms complets de sous-groupes (ex. "5e1_esp", "5e2_esp")
                lv_groupes = [cl_base + suffixe for cl_base in dependants]
                mat_index  = MATIERES.index(mat_sg) + 1

                for j in range(len(JOURS)):
                    for h in range(len(HEURES)):
                        bools = []
                        for grp in lv_groupes:
                            # BoolVar = 1 si ce groupe a cours de cette LV à (j,h)
                            b = model.NewBoolVar(f"sync_{mat_sg}_{grp}_{j}_{h}_{semaine}")
                            model.Add(emploi_du_temps[semaine][(grp, j, h)] == mat_index).OnlyEnforceIf(b)
                            model.Add(emploi_du_temps[semaine][(grp, j, h)] != mat_index).OnlyEnforceIf(b.Not())
                            bools.append(b)
                        # Imposer que tous ces booléens soient égaux deux à deux (tous ou aucun)
                        for i in range(len(bools)):
                            for k in range(i+1, len(bools)):
                                model.Add(bools[i] == bools[k])


    # Minimiser les heures de permanence
    # On définit une variable globale pour la somme des permanences (créneaux sans cours)
    total_permanence = model.NewIntVar(
        0,
        len(CLASSES) * len(JOURS) * len(HEURES) * len(SEMAINES),
        "total_permanence"
    )
    permanence_vars = []

    for semaine in SEMAINES:
        for classe in CLASSES:
            for j, jour in enumerate(JOURS):
                # On évite la première et la dernière heure de la journée
                for h in range(1, len(HEURES) - 1):
                    permanence = model.NewBoolVar(
                        f"permanence_{classe}_{jour}_{h}_{semaine.replace(' ', '_')}"
                    )
                    # Si la variable d’emploi du temps vaut 0 à ce créneau, c’est une permanence
                    model.Add(emploi_du_temps[semaine][(classe, j, h)] == 0).OnlyEnforceIf(permanence)
                    model.Add(emploi_du_temps[semaine][(classe, j, h)] != 0).OnlyEnforceIf(permanence.Not())
                    permanence_vars.append(permanence)

    model.Add(total_permanence == sum(permanence_vars))
    # Objectif partiel : réduire au maximum les permanences inutiles

    # ─── Contraintes d'indisponibilité pour tous les professeurs
    # On applique les indisponibilités listées dans la config pour bloquer les cours
    for prof, indispos in INDISPONIBILITES_PROFS.items():
        for jour_str, heures in indispos.items():
            if jour_str not in JOURS:
                continue
            jour_index = JOURS.index(jour_str)

            for classe in CLASSES:
                niveau_classe = classe[:2]
                # Vérifier si ce prof enseigne cette matière pour le niveau
                for matiere, prof_ref in PROFESSEURS.items():
                    est_concerne = False
                    if isinstance(prof_ref, str):
                        est_concerne = (prof_ref == prof)
                    elif isinstance(prof_ref, dict):
                        profs_niv = prof_ref.get(niveau_classe)
                        if isinstance(profs_niv, str):
                            est_concerne = (profs_niv == prof)
                        elif isinstance(profs_niv, list):
                            est_concerne = (prof in profs_niv)

                    if not est_concerne:
                        continue

                    matiere_index = MATIERES.index(matiere) + 1

                    # Pour chaque créneau interdit, on bloque l'affectation de la matière
                    for heure in heures:
                        clé = (classe, jour_index, heure)
                        for semaine in SEMAINES:
                            if clé in emploi_du_temps[semaine]:
                                model.Add(emploi_du_temps[semaine][clé] != matiere_index)
                                # On interdit la matière sur les heures non disponibles

    # ─── Contraintes de pénalités de préférence pour profs hors créneau préféré
    penalites_preferences = []
    # On crée des BoolVar pour chaque violation de préférence afin de les pénaliser
    for prof, prefs in PREFERENCES_PROFS.items():
        for jour_str, heures in prefs.items():
            if jour_str not in JOURS:
                continue
            jour_index = JOURS.index(jour_str)

            for classe in CLASSES:
                niveau_classe = classe[:2]

                for matiere, prof_ref in PROFESSEURS.items():
                    est_concerne = False
                    if isinstance(prof_ref, str):
                        est_concerne = (prof_ref == prof)
                    elif isinstance(prof_ref, dict):
                        profs_niveau = prof_ref.get(niveau_classe)
                        if isinstance(profs_niveau, str):
                            est_concerne = (profs_niveau == prof)
                        elif isinstance(profs_niveau, list):
                            est_concerne = (prof in profs_niveau)
                    if not est_concerne:
                        continue

                    mat_idx = MATIERES.index(matiere) + 1
                    for h in heures:
                        key = (classe, jour_index, h)
                        for semaine in SEMAINES:
                            if key not in emploi_du_temps[semaine]:
                                continue
                            violation = model.NewBoolVar(
                                f"pref_violation_{prof.replace(' ', '_')}_{classe}_{jour_index}_{h}_{semaine}"
                            )
                            model.Add(emploi_du_temps[semaine][key] == mat_idx).OnlyEnforceIf(violation)
                            model.Add(emploi_du_temps[semaine][key] != mat_idx).OnlyEnforceIf(violation.Not())
                            penalites_preferences.append(violation)


    poids_pref = 1  # Pondération assignée aux pénalités de préférence dans la fonction objectif

    # ─── Contraintes d'indisponibilité de salles (incl. salles spécialisées)
    matieres_specialisees = set(AFFECTATION_MATIERE_SALLE.keys())
    matieres_generales   = set(MATIERES) - matieres_specialisees

    for salle, indispos in INDISPONIBILITES_SALLES.items():
        # Déterminer quelles matières peuvent être données dans cette salle
        if salle in AFFECTATION_MATIERE_SALLE.values():
            # Salle spécialisée : seules les matières assignées à cette salle
            matieres_concernees = [
                m for m, s in AFFECTATION_MATIERE_SALLE.items()
                if s == salle
            ]
        else:
            # Salle générale : toutes les matières non spécialisées
            matieres_concernees = list(matieres_generales)

        for jour_str, heures in indispos.items():
            jour_index = JOURS.index(jour_str)
            for classe in CLASSES + [c for c in CAPACITES_CLASSES if c not in CLASSES]:
                niveau_classe = classe[:2]
                for matiere in matieres_concernees:
                    # Si la matière n'est pas enseignée à ce niveau, on skip
                    if niveau_classe not in VOLUME_HORAIRE or matiere not in VOLUME_HORAIRE[niveau_classe]:
                        continue
                    matiere_index = MATIERES.index(matiere) + 1
                    for h in heures:
                        cle = (classe, jour_index, h)
                        for semaine in SEMAINES:
                            if cle in emploi_du_temps[semaine]:
                                model.Add(emploi_du_temps[semaine][cle] != matiere_index)


    # ─── Attribution des salles en fonction des capacités (inclus salles spécialisées)
    for semaine in SEMAINES:
        for classe in CLASSES:
            # On détermine la classe de base si c'est un sous-groupe
            classe_base = classe
            for suffixe in SOUS_GROUPES_SUFFIXES:
                if classe.endswith(suffixe):
                    classe_base = classe.replace(suffixe, "")
                    break

            capacite_classe = CAPACITES_CLASSES.get(classe_base, 0)
            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    salle_var = emploi_du_temps_salles[semaine][(classe, j, h)]
                    # Sélection des salles valides par capacité
                    salles_valides = [
                        i
                        for i, nom in enumerate(SALLES_GENERALES, 1)
                        if CAPACITES_SALLES.get(nom, 0) >= capacite_classe
                    ]
                    # On ajoute aussi les salles spécialisées suffisantes
                    for nom_salle, cap in CAPACITES_SALLES.items():
                        if nom_salle not in SALLES_GENERALES and cap >= capacite_classe:
                            if nom_salle in AFFECTATION_MATIERE_SALLE.values():
                                try:
                                    index = SALLES_GENERALES.index(nom_salle) + 1
                                except ValueError:
                                    # Salle spécialisée non listée dans SALLES_GENERALES
                                    continue
                                salles_valides.append(index)
                    if not salles_valides:
                        # Si aucune salle dispos, on force la variable à 0 (pas de cours)
                        model.Add(salle_var == 0)
                    else:
                        # On autorise soit 0 (pas de cours) soit l'une des salles_valides
                        model.AddAllowedAssignments([salle_var], [[0]] + [[i] for i in salles_valides])

    # Respecter le volume horaire global bihebdo par classe et sous-groupe
    for niveau in ["6e", "5e", "4e", "3e"]:
        print(f"Vérification pour le niveau {niveau}:")
        print(f"→ Maths en {niveau} : {PROFESSEURS['Maths'][niveau]}")

    # ─── Respect du volume horaire global bihebdo (par classe et sous-groupe)
    # 1) Calcul du nombre de sous-groupes effectifs pour chaque (niveau, matière sous-groupe)
    nb_sousgroupes_par_niv_mat = {}
    for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
        for classe_base in CLASSES_BASE:
            niveau = classe_base[:2]
            sousg = classe_base + suffixe
            if sousg in CLASSES:
                clé = (niveau, mat_sg)
                nb_sousgroupes_par_niv_mat.setdefault(clé, 0)
                nb_sousgroupes_par_niv_mat[clé] += 1

    # 2) Boucle pour imposer le nombre exact d'heures pour chaque matière
    for classe in CLASSES:
        # Détermination du niveau :               # ex. "5e1_G2" → "5e"
        if "_G" in classe:
            niveau_classe = classe.split("e")[0] + "e"
        else:
            niveau_classe = classe[:2]

        # Déterminer la/les matières disponibles pour cette classe
        for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
            if suffixe in classe:
                matieres_disponibles = [mat_sg]
                break
        # Si pas de suffixe, on prend toutes les matières du niveau
        else:
            matieres_disponibles = [
                m for m in VOLUME_HORAIRE[niveau_classe]
                if m not in SOUS_GROUPES_SUFFIXES.values()
            ]

        # On parcourt les matières disponibles pour ce niveau
        for semaine in SEMAINES:
            for matiere in matieres_disponibles:
                # Si la matière n'existe pas dans le bihebdo pour ce niveau, on skip
                if matiere not in VOLUME_HORAIRE_BIHEBDO.get(niveau_classe, {}):
                    continue

                occurrences = []
                for j in range(len(JOURS)):
                    for h in range(len(HEURES)):
                        # On évite la pause déjeuner (h == 4) et le mercredi après-midi
                        if h == 4 or (JOURS[j] in JOURS_SANS_APRES_MIDI and h > 4):
                            continue
                        var = model.NewBoolVar(f"{classe}_{j}_{h}_{matiere}_{semaine}")
                        mat_idx = MATIERES.index(matiere) + 1
                        emploi = emploi_du_temps[semaine][(classe, j, h)]
                        model.Add(emploi == mat_idx).OnlyEnforceIf(var)
                        model.Add(emploi != mat_idx).OnlyEnforceIf(var.Not())
                        occurrences.append(var)

                # Volume cible pour ce niveau/matière/semaine
                volume_cible = VOLUME_HORAIRE_BIHEBDO[niveau_classe][matiere][semaine]
                # On impose que la somme des BoolVar = volume cible
                model.Add(sum(occurrences) == volume_cible)

    # ─── Contrainte : exclusion de matières
    def matExcluSuite(pMatiere1, pMatiere2, pContrainte="forte", pClasses=CLASSES_BASE):
        """
        Contrainte d'exclusion : la matière pMatiere2 ne peut pas suivre immédiatement
        pMatiere1 pour les classes spécifiées.

        Arguments:
            pMatiere1 (str): nom de la matière à exclure en premier.
            pMatiere2 (str): nom de la matière à exclure en second.
            pContrainte (str): "forte" ou "faible" pour le type de contrainte.
            pClasses (list ou str): liste de classes ou préfixe de classe.
        """
        matdex_1 = MATIERES.index(pMatiere1) + 1
        matdex_2 = MATIERES.index(pMatiere2) + 1
        print("-- Exclusion : " +
              "/" + pMatiere1 + "\\" +
              " suivi de " +
              "/" + pMatiere2 + "\\")

        # Sélection des classes à traiter
        if pClasses != CLASSES_BASE:
            choixClasse = [c for c in CLASSES_BASE if pClasses in c]
        else:
            choixClasse = pClasses

        # Pour chaque semaine, on applique la contrainte sur les bons IntVar
        for semaine in SEMAINES:
            for classe in choixClasse:
                for j in range(len(JOURS)):
                    for h in range(len(HEURES) - 1):
                        excluSuite_a = model.NewBoolVar(f"{classe}_{j}_{h}_excluA_{semaine}")
                        excluSuite_b = model.NewBoolVar(f"{classe}_{j}_{h+1}_excluB_{semaine}")

                        # On pointe maintenant explicitement sur emploi_du_temps[semaine]
                        varA = emploi_du_temps[semaine][(classe, j, h)]
                        varB = emploi_du_temps[semaine][(classe, j, h+1)]

                        model.Add(varA == matdex_1).OnlyEnforceIf(excluSuite_a)
                        model.Add(varA != matdex_1).OnlyEnforceIf(excluSuite_a.Not())
                        model.Add(varB == matdex_2).OnlyEnforceIf(excluSuite_b)
                        model.Add(varB != matdex_2).OnlyEnforceIf(excluSuite_b.Not())

                        if pContrainte == "faible":
                            model.AddBoolOr([excluSuite_a.Not(), excluSuite_b.Not()])
                        elif pContrainte == "forte":
                            model.AddImplication(excluSuite_a, excluSuite_b.Not())

    # ─── Contrainte : inclusion de matières
    def matIncluSuite(pMatiere1, pMatiere2, pContrainte, pNBFois=1, pClasses=CLASSES_BASE):
        """
        Contrainte d'inclusion : pMatiere1 doit être suivi immédiatement par pMatiere2 un
        certain nombre de fois (défini par pNBFois) selon la force de contrainte.

        Arguments:
            pMatiere1 (str): matière de départ.
            pMatiere2 (str): matière d'arrivée.
            pContrainte (str): "forte", "moyenne" ou "faible".
            pNBFois (int): nombre minimal/maximum d'occurrences selon pContrainte.
            pClasses (list ou str): classes concernées ou préfixe.
        """
        matdex_1 = MATIERES.index(pMatiere1) + 1
        matdex_2 = MATIERES.index(pMatiere2) + 1
        print("-- Inclusion : " + "/" + pMatiere1 + "\\" + " suivi de " + "/" + pMatiere2 + "\\")

        # Sélection des classes visées
        if pClasses != CLASSES_BASE:
            choixClasse = [c for c in CLASSES_BASE if pClasses in c]
        else:
            choixClasse = pClasses

        # Pour chaque semaine, on applique la contrainte sur les bons IntVar
        for semaine in SEMAINES:
            for classe in choixClasse:
                sequence_Suivi = []

                for j in range(len(JOURS)):
                    for h in range(len(HEURES) - 1):
                        # Booléen qui vaudra 1 si on a pMatiere1 à (j,h) ET pMatiere2 à (j,h+1)
                        suivi_var = model.NewBoolVar(f"{classe}_{j}_{h}_suivi_{pMatiere1}_{pMatiere2}_{semaine}")

                        # On crée deux BoolVar pour détecter la présence exacte de chaque matière
                        var_mat1 = model.NewBoolVar(f"{classe}_{j}_{h}_est_{pMatiere1}_{semaine}")
                        var_mat2 = model.NewBoolVar(f"{classe}_{j}_{h+1}_est_{pMatiere2}_{semaine}")

                        varA = emploi_du_temps[semaine][(classe, j, h)]
                        varB = emploi_du_temps[semaine][(classe, j, h + 1)]

                        # Si varA == matdex_1 alors var_mat1 = 1, sinon var_mat1 = 0
                        model.Add(varA == matdex_1).OnlyEnforceIf(var_mat1)
                        model.Add(varA != matdex_1).OnlyEnforceIf(var_mat1.Not())

                        # Si varB == matdex_2 alors var_mat2 = 1, sinon var_mat2 = 0
                        model.Add(varB == matdex_2).OnlyEnforceIf(var_mat2)
                        model.Add(varB != matdex_2).OnlyEnforceIf(var_mat2.Not())

                        # suivi_var = var_mat1 AND var_mat2
                        model.AddBoolAnd([var_mat1, var_mat2]).OnlyEnforceIf(suivi_var)
                        model.AddBoolOr([var_mat1.Not(), var_mat2.Not()]).OnlyEnforceIf(suivi_var.Not())

                        sequence_Suivi.append(suivi_var)

                        # Si contrainte forte, on force systématiquement le suivi mat1 → mat2
                        if pContrainte == "forte":
                            model.AddImplication(var_mat1, var_mat2)

                # Pour contrainte « moyenne », on exige au moins pNBFois suivis mat1→mat2 sur TOUTE la semaine
                if pContrainte == "moyenne":
                    model.Add(sum(sequence_Suivi) >= pNBFois)
                # Pour contrainte « faible », on impose au plus pNBFois
                elif pContrainte == "faible":
                    model.Add(sum(sequence_Suivi) <= pNBFois)


    #matIncluSuite("Français", "SVT", "moyenne", 1, "6e")



    ### Même Niveau, Même cours
    # /!\ Déactiver Contrainte lignes 162 à 178 pour que cela marche.

    # ─── Ensemble des (niveau, matière) pour lesquels memNivMemCours a été activé ───
    MEMNIV_ACTIVES = set()

    # Fonction pour ajouter la contrainte "Même Niveau, Même Cours"
    # (si elle n'est pas déjà active pour ce niveau/matière)
    def memNivMemCours(pNiveau, pMatiere):
        """
        Contrainte "Même Niveau, Même Cours" : si activée, impose que pour chaque créneau,
        toutes les classes d'un même niveau aient soit toutes pMatiere, soit aucune.

        Arguments:
            pNiveau (str): niveau ciblé (ex. "6e").
            pMatiere (str): matière concernée.
        """
        MEMNIV_ACTIVES.add((pNiveau, pMatiere))
        choixClasse = []
        matdex_p = MATIERES.index(pMatiere) + 1

        # Sélection des classes de ce niveau
        for c in CLASSES_BASE:
            if c.startswith(pNiveau):
                choixClasse.append(c)
        if not choixClasse:
            raise ValueError(f"{pNiveau} = Niveau Inexistant")

        # Pour chaque semaine, on impose « même créneau → même matière » et on totalise le nombre d’occurrences
        for semaine in SEMAINES:
            positionMatiere = []

            # on récupère l'objectif entier pour cette matière/ce niveau en cette semaine
            volume_cible = VOLUME_HORAIRE_BIHEBDO[pNiveau][pMatiere][semaine]

            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    var = model.NewBoolVar(f"{pMatiere}_{pNiveau}_{semaine}_{j}_{h}")
                    # Si TOUTES les classes du niveau ont pMatiere à (j,h), alors var = 1
                    for classe in choixClasse:
                        model.Add(emploi_du_temps[semaine][(classe, j, h)] == matdex_p).OnlyEnforceIf(var)
                        model.Add(emploi_du_temps[semaine][(classe, j, h)] != matdex_p).OnlyEnforceIf(var.Not())
                    positionMatiere.append(var)

            # On impose que la somme de tous ces indicateurs vaut exactement le volume entier
            model.Add(sum(positionMatiere) == volume_cible)

    # ─── Activation dynamique de la contrainte “Même Niveau, Même Cours”
    for entry in config.get("memnivmemcours", []):
        niveau  = entry["niveau"]    # ex. "6e"
        matiere = entry["matiere"]   # ex. "Maths"
        memNivMemCours(niveau, matiere)


    # ─── Empêcher deux classes du même niveau d'avoir la même matière au même créneau
    # (hors LV synchronisées par la contrainte dédiée)
    for semaine in SEMAINES:
        for niveau in NIVEAUX:
            classes_niveau = [cl for cl in CLASSES_BASE if cl.startswith(niveau)]
            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    for m_idx, mat in enumerate(MATIERES, start=1):
                        # si on a activé memNivMemCours(niveau, mat), on saute
                        if (niveau, mat) in MEMNIV_ACTIVES:
                            continue

                        # tolérance pour les LV :  
                        # si c'est un sous-groupe LV, on ne fait pas de mutual exclusion ici
                        cfg_sg = SOUS_GROUPES_CONFIG.get(mat)
                        if cfg_sg and cfg_sg.get("type") == "LV":
                            continue

                        # sinon, on impose qu'au plus 1 classe du niveau ait cette matière
                        bools_matiere = []
                        for cl in classes_niveau:
                            b = model.NewBoolVar(
                                f"{cl}_{semaine}_{j}_{h}_is_{mat.replace(' ', '_')}"
                            )
                            var_mat = emploi_du_temps[semaine][(cl, j, h)]
                            model.Add(var_mat == m_idx).OnlyEnforceIf(b)
                            model.Add(var_mat != m_idx).OnlyEnforceIf(b.Not())
                            bools_matiere.append(b)

                        model.Add(sum(bools_matiere) <= 1) # Au plus une classe du niveau a cette matière à ce créneau





    ### Cours Horaire Donnée v2 (Pour gérer les sous-groupes de matières)

    # ─── Contrainte : Cours Horaire Donnée v2 (pour gérer les sous-groupes de matières)
    def matHorairDonneV2(pClasses, pMatiere, pJour, pHorairMin, pHorairMax=None, pNBFois=None):
        """
        Contrainte pour imposer qu'une matière (ou liste de matières) apparaisse un
        certain nombre de fois dans un intervalle horaire donné pour des classes.

        Arguments:
            pClasses (str ou list): préfixe de niveau ou liste de classes.
            pMatiere (str ou list): matière unique, nom de sous-groupe ou liste de matières.
            pJour (str): jour ciblé (ex. "Jeudi").
            pHorairMin (str): horaire de début (ex. "13h").
            pHorairMax (str, optionnel): horaire de fin (ex. "17h").
            pNBFois (int, optionnel): nombre d'occurrences attendues.
        """
        jourdex_h = JOURS.index(pJour)
        HORAIRE_MIN, HORAIRE_MAX = pHorairMin, pHorairMax
        Hordex_Min, Hordex_Max = None, None

        # Préparation des classes ciblées
        if pClasses != CLASSES_BASE:
            choixClasse = [c for c in CLASSES_BASE if pClasses in c]
        else:
            choixClasse = list(CLASSES_BASE)

        if not choixClasse:
            raise ValueError(f"Classe(s) '{pClasses}' introuvable(s)")

        # Préparation des matières ciblées
        if isinstance(pMatiere, str):
            liste_matieres = [m for m in MATIERES if pMatiere in m]
        elif isinstance(pMatiere, list):
            liste_matieres = []
            for pm in pMatiere:
                liste_matieres += [m for m in MATIERES if pm in m]
            liste_matieres = list(set(liste_matieres))
        else:
            liste_matieres = []

        # Déterminer Hordex_Min et Hordex_Max
        for h, label in enumerate(HEURES):
            if label.startswith(HORAIRE_MIN):
                Hordex_Min = h
            if HORAIRE_MAX and label.endswith(HORAIRE_MAX):
                Hordex_Max = h
        if Hordex_Min is None:
            raise ValueError(f"Horaire min '{HORAIRE_MIN}' non trouvé dans HEURES")
        if Hordex_Max is None:
            Hordex_Max = Hordex_Min

        # Par défaut, nbFois = longueur de l'intervalle
        nbFois = (Hordex_Max - Hordex_Min + 1) if pNBFois is None else pNBFois

        # Boucler sur chaque classe et sur chaque semaine
        for classe in choixClasse:
            # Ajuster nbFois maximal selon volume horaire réel de pMatiere
            if isinstance(pMatiere, str):
                niveau = classe[:-1]  # ex. "6e1" -> "6e"
                if niveau in VOLUME_HORAIRE and pMatiere in VOLUME_HORAIRE[niveau]:
                    max_possible = VOLUME_HORAIRE[niveau][pMatiere]
                    if nbFois > max_possible:
                        nbFois = max_possible # Ajuster nbFois si nécessaire
            
            # Boucle pour chaque semaine
            # (on suppose que la contrainte s'applique à toutes les semaines)
            for semaine in SEMAINES:
                occMatHorair = [] # Liste pour stocker les BoolVar d'occurrence de matière à horaire donné
                # Pour chaque matière dans la liste, on crée les BoolVar
                for mat in liste_matieres:
                    matdex_h = MATIERES.index(mat) + 1
                    # Si on veut une seule heure fixe
                    if HORAIRE_MAX is None:
                        h = Hordex_Min
                        var = model.NewBoolVar(f"{classe}_{semaine}_{jourdex_h}_{h}_matiere_horaire")
                        model.Add(emploi_du_temps[semaine][(classe, jourdex_h, h)] == matdex_h).OnlyEnforceIf(var)
                        model.Add(emploi_du_temps[semaine][(classe, jourdex_h, h)] != matdex_h).OnlyEnforceIf(var.Not())
                        occMatHorair.append(var)
                    else:
                        # Si on a un intervalle [Hordex_Min..Hordex_Max]
                        for h in range(Hordex_Min, Hordex_Max + 1):
                            var = model.NewBoolVar(f"{classe}_{semaine}_{jourdex_h}_{h}_matiere_horaire")
                            model.Add(emploi_du_temps[semaine][(classe, jourdex_h, h)] == matdex_h).OnlyEnforceIf(var)
                            model.Add(emploi_du_temps[semaine][(classe, jourdex_h, h)] != matdex_h).OnlyEnforceIf(var.Not())
                            occMatHorair.append(var)

                # Imposer le nombre d'occurrences pour cette semaine
                model.Add(sum(occMatHorair) == nbFois) # Nombre exact de fois que la matière doit apparaître

    #matHorairDonneV2("6e", MATIERES_SCIENTIFIQUE, "Jeudi", "13h", "17h", 2)
    for entry in config.get("mat_horaire_donne_v2", []):
        pClasses    = entry["classes"]                            # ex. "6e"                   
        # On récupère la liste réelle de matières via le sous-groupe
        pMatiere    = entry["matiere"]     # ex. ["Maths","SVT","Physique","Techno"]
        pJour       = entry["jour"]                                # ex. "Jeudi"
        pHorairMin  = entry["horaire_min"]                         # ex. "13h"
        pHorairMax  = entry.get("horaire_max")                     # ex. "17h"
        pNBFois     = entry.get("nb_fois")                         # ex. 2

        matHorairDonneV2(pClasses, pMatiere, pJour, pHorairMin, pHorairMax, pNBFois)

    mat_exclu_entries = config.get("mat_exclu_suite", []) # Liste des exclusions de matières
    mat_inclu_entries = config.get("mat_inclu_suite", []) # Liste des inclusions de matières

    # (2) Boucle pour appeler matExcluSuite() selon la configuration JSON
    for entry in mat_exclu_entries:
        mat1 = entry["matiere1"]
        mat2 = entry["matiere2"]
        contrainte = entry.get("contrainte", "forte")
        classes_cible = entry.get("classes", "CLASSES_BASE")

        # Si classes_cible == "CLASSES_BASE", on envoie la liste python CLASSES_BASE
        if isinstance(classes_cible, str) and classes_cible == "CLASSES_BASE":
            matExcluSuite(mat1, mat2, contrainte, CLASSES_BASE)
        else:
            # Sinon, classes_cible peut être un préfixe (ex. "6e") ou une liste de classes
            matExcluSuite(mat1, mat2, contrainte, classes_cible)

    # (3) Boucle pour appeler matIncluSuite() selon la configuration JSON
    for entry in mat_inclu_entries:
        mat1 = entry["matiere1"]
        mat2 = entry["matiere2"]
        contrainte = entry.get("contrainte")
        nb_fois = entry.get("nb_fois", 1)
        classes_cible = entry.get("classes", "CLASSES_BASE")

        if isinstance(classes_cible, str) and classes_cible == "CLASSES_BASE":
            matIncluSuite(mat1, mat2, contrainte, nb_fois, CLASSES_BASE)
        else:
            matIncluSuite(mat1, mat2, contrainte, nb_fois, classes_cible)

    # ─── Contrainte : fusionner_groupes_vers_classes
    # (pour construire le dictionnaire fusion_data) 
    def fusionner_groupes_vers_classes(
        emploi_du_temps,
        emploi_du_temps_salles,
        emploi_du_temps_profs,
        solver,
        semaine
    ):
        """
        Construit un dictionnaire fusion_data[(classe, j, h)] → string décrivant
        le contenu du créneau (matière, prof, salle) pour chaque classe de base
        et leurs sous-groupes, pour la semaine donnée.

        Arguments:
            emploi_du_temps (dict): variables IntVar matières par créneau.
            emploi_du_temps_salles (dict): variables IntVar salles par créneau.
            emploi_du_temps_profs (dict): variables IntVar/BoolVar profs par créneau.
            solver (CpSolver): instance du solveur ayant résolu le modèle.
            semaine (str): "Semaine A" ou "Semaine B".

        Retourne:
            dict: fusion_data mapping clé (classe, j, h) → description texte du créneau.
        """
        # Dictionnaire pour stocker les données fusionnées
        fusion_data = {}

        # 1) D’abord, pour chaque classe de base
        for cl in CLASSES_BASE:
            for j, jour in enumerate(JOURS):
                for h, heure in enumerate(HEURES):
                    key = (cl, j, h)
                    contenu = []

                    # a) Cours de la classe principale
                    mat_idx = solver.Value(emploi_du_temps[semaine][key])
                    if mat_idx > 0:
                        mat = MATIERES[mat_idx - 1]
                        niv = cl[:2]
                        prof_ref = PROFESSEURS[mat]

                        # Sélection du professeur
                        if isinstance(prof_ref, dict):
                            profs_niv = prof_ref.get(niv, None)
                            key_prof = (cl, j, h, mat, semaine)

                            # Si on a une liste de profs pour ce niveau
                            if isinstance(profs_niv, list) and len(profs_niv) > 1:
                                if key_prof in emploi_du_temps_profs[semaine]:
                                    idx_prof = solver.Value(emploi_du_temps_profs[semaine][key_prof])
                                    prof_sel = profs_niv[idx_prof]
                                else:
                                    prof_sel = profs_niv[0]
                            # Si on a une chaîne (string) pour ce niveau, on l’utilise telle quelle
                            elif isinstance(profs_niv, str):
                                prof_sel = profs_niv
                            # Si c’est autre chose (ou None), on retombe sur prof_ref complet
                            else:
                                prof_sel = prof_ref
                        else:
                            # prof_ref est déjà une chaîne, un seul prof pour toute la matière
                            prof_sel = prof_ref

                        # Choix de la salle
                        salle = (
                            AFFECTATION_MATIERE_SALLE.get(mat)
                            or AFFECTATION_MATIERE_SALLE.get(prof_sel)
                        )
                        # Si pas de salle assignée, on prend l'index de la salle dans emploi_du_temps_salles pour cette semaine
                        idx_salle = solver.Value(emploi_du_temps_salles[semaine][key])
                        if not salle and 0 < idx_salle <= len(SALLES_GENERALES):
                            salle = SALLES_GENERALES[idx_salle - 1]

                        # Affichage de la salle avec sa capacité
                        cap_s = CAPACITES_SALLES.get(salle)
                        if cap_s is not None:
                            salle_aff = f"{salle} - {cap_s} places"
                        else:
                            salle_aff = f"{salle}"
                        contenu.append(f"{mat}\n{prof_sel}\n[{salle_aff}]")

                    # b) Sous-groupes de la même classe de base
                    for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
                        grp = f"{cl}{suffixe}"
                        if grp in CLASSES:
                            key_sg = (grp, j, h)
                            # On récupère l'index de la matière programmée pour ce sous-groupe
                            mat_idx_sg = solver.Value(emploi_du_temps[semaine][key_sg])
                            if mat_idx_sg > 0:
                                # On convertit l'index en nom de matière
                                mat2 = MATIERES[mat_idx_sg - 1]
                                # On récupère la référence au(x) professeur(s) pour cette matière
                                prof_ref2 = PROFESSEURS[mat2]

                                if isinstance(prof_ref2, dict):
                                    # Cas dict : plusieurs profs possibles selon le niveau (niv doit venir du contexte)
                                    profs2 = prof_ref2.get(niv, None)
                                    key_prof2 = (grp, j, h, mat2, semaine)

                                    if isinstance(profs2, list) and len(profs2) > 1:
                                        # Si liste de profs, on choisit l'index enregistré ou le premier par défaut
                                        if key_prof2 in emploi_du_temps_profs[semaine]:
                                            idx2 = solver.Value(emploi_du_temps_profs[semaine][key_prof2])
                                            prof2 = profs2[idx2]
                                        else:
                                            prof2 = profs2[0]
                                    elif isinstance(profs2, str):
                                        # ⚠️ Si unique prof sous forme de chaîne
                                        prof2 = profs2
                                    else:
                                        # ⚠️ Pas de donnée spécifique niveau : on garde la référence complète
                                        prof2 = prof_ref2
                                else:
                                    # ⚠️ Cas simple : prof_ref2 est déjà une chaîne ou liste
                                    prof2 = prof_ref2

                                # On récupère l'index de la salle pour ce sous-groupe
                                idx_sg = solver.Value(emploi_du_temps_salles[semaine][key_sg])
                                # On détermine la salle via le mapping matière→salle ou prof→salle
                                salle2 = (
                                    AFFECTATION_MATIERE_SALLE.get(mat2)
                                    or AFFECTATION_MATIERE_SALLE.get(prof2)
                                )
                                if not salle2 and 0 < idx_sg <= len(SALLES_GENERALES):
                                    # Si pas de mapping, on prend la salle générale correspondante
                                    salle2 = SALLES_GENERALES[idx_sg - 1]

                                # On récupère la capacité de la salle si disponible
                                cap_sg = CAPACITES_SALLES.get(salle2)
                                if cap_sg is not None:
                                    salle_aff2 = f"{salle2} - {cap_sg} places"
                                else:
                                    salle_aff2 = f"{salle2}"
                                # On construit la ligne de contenu pour le sous-groupe
                                contenu.append(f"{mat2} ({grp})\n{prof2}\n[{salle_aff2}]")

                    # On fusionne les contenus récupérés ou on place '---' si rien à afficher
                    fusion_data[key] = "\n\n".join(contenu) if contenu else "---"

        # 2) Optionnel : traiter chaque sous-groupe indépendamment
        for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
            for cl_base in CLASSES_BASE:
                grp = f"{cl_base}{suffixe}"
                if grp not in CLASSES:
                    continue
                for j, jour in enumerate(JOURS):
                    for h, heure in enumerate(HEURES):
                        key_sg = (grp, j, h)
                        contenu_sg = []
                        mat_idx_sg = solver.Value(emploi_du_temps[semaine][key_sg])
                        if mat_idx_sg > 0:
                            mat2 = MATIERES[mat_idx_sg - 1]
                            prof_ref2 = PROFESSEURS[mat2]

                            # ── Bloc corrigé pour la section “chaque sous-groupe isolément” ────
                            if isinstance(prof_ref2, dict):
                                # On déduit le niveau à partir de la classe de base
                                niv_b = cl_base[:2]
                                profs2 = prof_ref2.get(niv_b, None)
                                key_prof2 = (grp, j, h, mat2, semaine)

                                if isinstance(profs2, list) and len(profs2) > 1:
                                    # Choix du prof selon l'index ou par défaut le premier
                                    if key_prof2 in emploi_du_temps_profs[semaine]:
                                        idx2 = solver.Value(emploi_du_temps_profs[semaine][key_prof2])
                                        prof2 = profs2[idx2]
                                    else:
                                        prof2 = profs2[0]
                                elif isinstance(profs2, str):
                                    # Cas unique : prof est une chaîne
                                    prof2 = profs2
                                else:
                                    # Pas de donnée spécifique au niveau, on reprend la référence globale
                                    prof2 = prof_ref2
                            else:
                                # prof_ref2 n'est pas un dict → on l'utilise directement
                                prof2 = prof_ref2

                            # Récupération et détermination de la salle pour le sous-groupe
                            idx_s2 = solver.Value(emploi_du_temps_salles[semaine][key_sg])
                            salle2 = (
                                AFFECTATION_MATIERE_SALLE.get(mat2)
                                or AFFECTATION_MATIERE_SALLE.get(prof2)
                            )
                            if not salle2 and 0 < idx_s2 <= len(SALLES_GENERALES):
                                # Fallback sur la salle générale si pas de mapping trouvé
                                salle2 = SALLES_GENERALES[idx_s2 - 1]
                            cap_s2 = CAPACITES_SALLES.get(salle2)
                            if cap_s2 is not None:
                                salle_aff2 = f"{salle2} - {cap_s2} places"
                            else:
                                salle_aff2 = f"{salle2}"
                                # Assemblage du contenu pour ce sous-groupe isolé
                            contenu_sg.append(f"{mat2}\n{prof2}\n[{salle_aff2}]")

                        # ⚠️ On stocke le résultat, ou '---' si vide
                        fusion_data[key_sg] = "\n\n".join(contenu_sg) if contenu_sg else "---"

        return fusion_data

    # Synchroniser les créneaux pour chaque matière de sous-groupe
    # Assure que tous les sous-groupes d'une même matière démarrent et finissent leurs cours en même temps
    for suffixe, matiere in SOUS_GROUPES_SUFFIXES.items():
        groupes_matiere = [classe for classe in CLASSES if classe.endswith(suffixe)]

        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                bools = []

                for groupe in groupes_matiere:
                    if (groupe, j, h) in emploi_du_temps:
                        var = model.NewBoolVar(f"{matiere}_{groupe}_{j}_{h}")
                        # BoolVar = 1 <=> ce groupe a cours de cette matière à (j,h)
                        model.Add(emploi_du_temps[(groupe, j, h)] == MATIERES.index(matiere) + 1).OnlyEnforceIf(var)
                        model.Add(emploi_du_temps[(groupe, j, h)] != MATIERES.index(matiere) + 1).OnlyEnforceIf(var.Not())
                        bools.append(var)

                # Imposer la synchronisation : pour chaque paire, si l'un a cours, l'autre aussi
                for i in range(len(bools)):
                    for k in range(i + 1, len(bools)):
                        model.AddBoolOr([bools[i].Not(), bools[k]])
                        model.AddBoolOr([bools[k].Not(), bools[i]])


    # Lecture des paramètres cantine et mise en place des créneaux interdits
    cantine_config     = config.get("cantine", {})
    cap_cantine        = cantine_config.get("capacite", 200)
    ratio_demi         = cantine_config.get("proportion_demi_pensionnaire", 0.8)
    creneaux_dej       = cantine_config.get("creneaux_dejeuner", [])
    assignation_niveaux= cantine_config.get("assignation_niveaux", {})
    priorite_active    = cantine_config.get("priorite_active", True)

    # Vérification que tous les créneaux dejeuner figurent bien dans HEURES 
    for c in creneaux_dej:
        if c not in HEURES:
            raise ValueError(f"Créneau cantine '{c}' non reconnu dans HEURES.")

    # On recherche dynamiquement le créneau principal commençant par "12h"
    lunch_slot = next((slot for slot in HEURES if slot.startswith("12h")), None)
    if lunch_slot is None:
        raise ValueError("Aucun créneau HEURES ne commence par '12h'")
    h_dej = HEURES.index(lunch_slot)

    # Bloquer systématiquement ce créneau pour toutes les classes
    for semaine in SEMAINES:
        for classe in CLASSES:
            for j in range(len(JOURS)):
                model.Add(emploi_du_temps[semaine][(classe, j, h_dej)] == 0)

    # Allocation des créneaux déjeuner selon la capacité de la cantine
    if lunch_slot in creneaux_dej:
        total_eleves = sum(int(CAPACITES_CLASSES.get(cl, 0) * ratio_demi) for cl in CLASSES_BASE)
        if total_eleves <= cap_cantine:
            # Capacité suffisante
            classe_creneau_dej = {cl: h_dej for cl in CLASSES_BASE}
            print(f"✅ Tous les élèves peuvent déjeuner à {lunch_slot} (capacité suffisante)")
        else:
            if not priorite_active:
                # Répartition automatique sans priorité
                from itertools import cycle
                print("🔁 Capacité insuffisante : répartition automatique sans priorité")
                iter_slots = cycle([HEURES.index(c) for c in creneaux_dej])
                classe_creneau_dej = {cl: next(iter_slots) for cl in CLASSES_BASE}
            else:
                # Répartition par priorité de niveaux
                print(f"❌ Capacité insuffisante à {lunch_slot} : assignation par niveau")
                classe_creneau_dej = {}
                for cl in CLASSES_BASE:
                    niv = cl[:2]
                    for slot, niveaux in assignation_niveaux.items():
                        if niv in niveaux:
                            classe_creneau_dej[cl] = HEURES.index(slot)
                            break
                    else:
                        raise ValueError(f"Aucun créneau cantine défini pour le niveau '{niv}' (classe {cl}).")
    else:
        raise ValueError(f"Le créneau principal '{lunch_slot}' doit être inclus dans les créneaux possibles.")

    # Interdire tout cours pendant le créneau déjeuner assigné
    for semaine in SEMAINES:
        for cl, h_dej in classe_creneau_dej.items():
            for j in range(len(JOURS)):
                model.Add(emploi_du_temps[semaine][(cl, j, h_dej)] == 0)

    # Contrainte préférentielle : éviter les journées avec un cartable trop lourd (par niveau)
    # On pénalise les journées où la somme des "poids" des matières dépasse un seuil toléré
    penalites_surcharge_poids = []
    poids_matieres_par_niveau = config.get("poids_matieres_par_niveau", {})
    seuils_par_niveau = config.get("poids_cartable_max_somme_par_niveau", {})
    seuil_global = config.get("poids_cartable_max_somme", 6.0)

    for classe in CLASSES_BASE:
        niveau = classe[:2]
        poids_par_niveau = poids_matieres_par_niveau.get(niveau, {})
        seuil_max = seuils_par_niveau.get(niveau, seuil_global)
        if seuil_max <= 0:
            continue

        # On ajoute une marge de 5% puis on multiplie par 10 pour rester en IntVar
        seuil_tolerant_x10 = int(seuil_max * 1.05 * 10)

        for semaine in SEMAINES:
            for j, jour in enumerate(JOURS):
                poids_total_jour_vars = []

                for h in range(len(HEURES)):
                    # Si jour sans après-midi, on ignore les créneaux h > 4
                    if jour in JOURS_SANS_APRES_MIDI and h > 4:
                        continue

                    # On crée une liste de (BoolVar, poids)
                    poids_h_terms = []
                    mat_index = emploi_du_temps[semaine][(classe, j, h)]
                    # Pesée de chaque matière selon son poids configuré
                    for m, matiere in enumerate(MATIERES):
                        code_mat = m + 1
                        # Poids pour la matière au niveau courant
                        poids = poids_par_niveau.get(matiere, 0.0)

                        b = model.NewBoolVar(f"poids_{classe}_{j}_{h}_{matiere}_{semaine}")
                        model.Add(mat_index == code_mat).OnlyEnforceIf(b)
                        model.Add(mat_index != code_mat).OnlyEnforceIf(b.Not())
                        poids_h_terms.append((b, poids))

                    # Inclusion des sous-groupes dans le calcul de poids si présents
                    for suffixe in SOUS_GROUPES_SUFFIXES:
                        grp = f"{classe}{suffixe}"
                        if grp in CLASSES:
                            mat_index_sg = emploi_du_temps[semaine][(grp, j, h)]
                            for m, matiere in enumerate(MATIERES):
                                code_mat = m + 1
                                poids = poids_par_niveau.get(matiere, 0.0)

                                b_sg = model.NewBoolVar(f"poids_{grp}_{j}_{h}_{matiere}_{semaine}")
                                model.Add(mat_index_sg == code_mat).OnlyEnforceIf(b_sg)
                                model.Add(mat_index_sg != code_mat).OnlyEnforceIf(b_sg.Not())
                                poids_h_terms.append((b_sg, poids))

                    if poids_h_terms:
                        poids_total_h = model.NewIntVar(0, 1000, f"poids_total_{classe}_{j}_{h}_{semaine}")
                        # On convertit poids en entier (x10) pour la somme
                        model.Add(poids_total_h == sum(int(p * 10) * var for var, p in poids_h_terms))
                        poids_total_jour_vars.append(poids_total_h)

                if poids_total_jour_vars:
                    somme_poids_jour = model.NewIntVar(0, 10000, f"somme_poids_jour_{classe}_{j}_{semaine}")
                    model.Add(somme_poids_jour == sum(poids_total_jour_vars))

                    surcharge = model.NewIntVar(0, 10000, f"surcharge_poids_jour_{classe}_{j}_{semaine}")
                    # surcharge = max(somme_poids_jour – seuil_tolerant_x10, 0)
                    model.AddMaxEquality(surcharge, [somme_poids_jour - seuil_tolerant_x10, 0])
                    penalites_surcharge_poids.append(surcharge)

    # 🔁 On ajoute ces pénalités à l’objectif
    poids_surcharge = 5  # Pondération des pénalités de surcharge de cartable

    # # ─── Minimiser les différences entre Semaine A et Semaine B ─────────
    # diff_vars = []
    # for cl in CLASSES:
    #     for j in range(len(JOURS)):
    #         for h in range(len(HEURES)):
    #             # les deux variables IntVar pour le même créneau en A et B
    #             varA = emploi_du_temps["Semaine A"][(cl, j, h)]
    #             varB = emploi_du_temps["Semaine B"][(cl, j, h)]
    #             # booléen qui vaut 1 si varA != varB
    #             b = model.NewBoolVar(f"diff_{cl}_{j}_{h}")
    #             # b → varA != varB  et  ¬b → varA == varB
    #             model.Add(varA != varB).OnlyEnforceIf(b)
    #             model.Add(varA == varB).OnlyEnforceIf(b.Not())
    #             diff_vars.append(b)

    # poids_semaines = 1  # ajustez ce coefficient selon l'importance de la similarité



    model.Minimize(
        total_permanence
        + poids_pref * sum(penalites_preferences)
        + poids_surcharge * sum(penalites_surcharge_poids)
 #       + poids_semaines * sum(diff_vars)
    )


    return model, emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs


def compter_volume_matiere_avec_sousgroupes(emploi_du_temps, solver):
    """
    Calcule le nombre d'heures planifiées par matière pour chaque classe de base,
    en incluant les contributions des sous-groupes **uniquement** si la classe de base
    est listée dans 'groupes_dependants' pour ce sous-groupe. Les volumes attendus
    ne contiennent pas les sous-groupes dont la classe de base n'est pas dépendante.
    """
    volumes = {}

    for classe in CLASSES:
        # On détecte si c'est un sous-groupe et on filtre selon 'groupes_dependants'
        suffixe = next((s for s in SOUS_GROUPES_SUFFIXES if classe.endswith(s)), None)
        if suffixe:
            mat_sg      = SOUS_GROUPES_SUFFIXES[suffixe]
            classe_base = classe[:-len(suffixe)]
            # on ignore les sous-groupes dont la classe de base n'est pas dépendante
            if classe_base not in SOUS_GROUPES_CONFIG[mat_sg].get("groupes_dependants", []):
                continue
        else:
            classe_base = classe

        niveau = classe_base[:2]

        # Initialisation du compteur et des attendus (filtrage des sous-groupes)
        if classe_base not in volumes:
            # On ne garde l’attendu de chaque matière que si :
            #  - c’est une matière “classique”
            #  - ou c’est un sous-groupe MAT pour lequel la classe_base est dépendante
            attendu = {}
            for mat, vol in VOLUME_HORAIRE.get(niveau, {}).items():
                if mat in SOUS_GROUPES_SUFFIXES.values():
                    # mat est un sous-groupe → inclure seulement si dépendante
                    if classe_base in SOUS_GROUPES_CONFIG[mat].get("groupes_dependants", []):
                        attendu[mat] = vol
                else:
                    attendu[mat] = vol

            volumes[classe_base] = {
                "par_matiere": {m: 0 for m in MATIERES},
                "attendus":    attendu
            }

        # Comptage heure par heure
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                key = (classe, j, h)
                if key in emploi_du_temps:
                    val = solver.Value(emploi_du_temps[key])
                    if val != 0:
                        matiere = MATIERES[val - 1]
                        volumes[classe_base]["par_matiere"][matiere] += 1

    # Affichage des écarts
    print("\n🚨 Écarts de volume horaire :")
    for classe_base, info in volumes.items():
        niveau = classe_base[:2]
        erreurs = []
        for matiere, nb_heures in info["par_matiere"].items():
            attendu = info["attendus"].get(matiere)
            if isinstance(attendu, int) and nb_heures != attendu:
                erreurs.append((matiere, nb_heures, attendu))

        if erreurs:
            print(f"\n❌ {classe_base} (niveau {niveau})")
            for matiere, nb, att in erreurs:
                print(f"   - {matiere:15}: {nb}h au lieu de {att}h ({nb - att:+})")
    return volumes

# Vérification des volumes horaires par matière
def compter_volume_matiere_avec_sousgroupes(emploi_du_temps, solver):
    """
    Calcule le nombre d'heures planifiées par matière pour chaque classe de base,
    en incluant les contributions des sous-groupes **uniquement** si la classe de base
    est listée dans 'groupes_dependants' pour ce sous-groupe.
    (Version légère pour la vérification des contraintes.)
    """
    volumes = {}

    # On parcourt toutes les classes, y compris les sous-groupes
    # et on compte les heures planifiées par matière.
    for classe in CLASSES:
        suffixe = next((s for s in SOUS_GROUPES_SUFFIXES if classe.endswith(s)), None)
        if suffixe:
            mat_sg      = SOUS_GROUPES_SUFFIXES[suffixe]
            classe_base = classe[:-len(suffixe)]
            if classe_base not in SOUS_GROUPES_CONFIG[mat_sg].get("groupes_dependants", []):
                continue
        else:
            classe_base = classe

        # On extrait le niveau de la classe de base
        # (ex. "6e1" → "6e")
        niveau = classe_base[:2]

        # Initialisation du compteur et des attendus
        # On initialise le volume pour la classe de base si pas déjà fait
        if classe_base not in volumes:
            # même filtrage des attendus
            attendu = {}
            for mat, vol in VOLUME_HORAIRE.get(niveau, {}).items():
                # On inclut les matières classiques et les sous-groupes dont la classe de base est dépendante
                if mat in SOUS_GROUPES_SUFFIXES.values():
                    if classe_base in SOUS_GROUPES_CONFIG[mat].get("groupes_dependants", []):
                        attendu[mat] = vol
                else:
                    # Matière classique, on l'inclut
                    attendu[mat] = vol
            volumes[classe_base] = {
                "par_matiere": {m: 0 for m in MATIERES},
                "attendus":    attendu
            }

        # Comptage des heures assignées
        for j in range(len(JOURS)):
            # On parcourt les créneaux horaires
            for h in range(len(HEURES)):
                key = (classe, j, h)
                # On vérifie si la clé existe dans l'emploi du temps et on récupère la valeur assignée
                if key in emploi_du_temps:
                    val = solver.Value(emploi_du_temps[key])
                    # Si la valeur n'est pas 0, on incrémente le compteur pour la matière correspondante
                    # (val = 0 signifie pas de cours à ce créneau)
                    if val != 0:
                        mat = MATIERES[val - 1]
                        volumes[classe_base]["par_matiere"][mat] += 1
    
    return volumes # Retourne le dictionnaire des volumes par classe et matière

# Vérification des permanences
def verifier_permanence(solver, emploi_un_semaine, capacite_perm):
    """
    Vérifie la gestion des permanences pour une semaine donnée en excluant
    dynamiquement les créneaux déjeuner selon la capacité de la cantine.
    """
    global avancement
    res = resultats_contraintes["permanence"]
    # Initialisation des résultats
    res["total"] = 0
    res["respectees"] = 0
    res["details"].clear()

    # 1) pré-calculs habituels
    nb_heures = len(HEURES)
    try:
        h_dej = HEURES.index("12h-13h")
    except ValueError:
        raise ValueError("Le créneau '12h-13h' doit être présent dans HEURES")

    # 2) récupération de la config cantine
    cant_cfg = config.get("cantine", {})
    creneaux_dej = cant_cfg.get("creneaux_dejeuner", ["12h-13h"])
    ratio = cant_cfg.get("proportion_demi_pensionnaire", 1.0)
    cap_cantine = cant_cfg.get("capacite", 0)

    # 3) calcul du nombre total d'élèves demi-pensionnaires
    total_eleves = sum(
        int(CAPACITES_CLASSES.get(cl, 0) * ratio)
        for cl in CLASSES_BASE
    )

    # 4) on détermine la liste des indices horaires à ignorer
    if total_eleves > cap_cantine:
        # capacité insuffisante → on bloque **tous** les créneaux déjeuner
        ignored = {
            HEURES.index(c) for c in creneaux_dej
            if c in HEURES
        }
    else:
        # capacité suffisante → on ne bloque que 12h-13h
        ignored = {h_dej}

    # 5) boucle de vérification
    for j, jour in enumerate(JOURS):
        for h in range(nb_heures):
            # on saute : première, dernière, créneaux déjeuner dynamiques,
            # et le pm interdit si applicable
            if (
                h == 0
                or h == nb_heures - 1
                or h in ignored
                or (jour in JOURS_SANS_APRES_MIDI and h > h_dej)
            ):
                continue
            
            # on vérifie les classes de base et leurs sous-groupes
            # pour chaque classe de base, on regarde les sous-groupes
            libres = []
            for cl in CLASSES_BASE:
                groupes = [cl] + [
                    f"{cl}{sfx}"
                    for sfx in SOUS_GROUPES_SUFFIXES
                    if f"{cl}{sfx}" in CLASSES
                ]
                if all(solver.Value(emploi_un_semaine[(g, j, h)]) == 0 for g in groupes):
                    libres.append((cl, CAPACITES_CLASSES.get(cl, 0)))

            if not libres: # aucune classe libre à ce créneau
                continue
            
            # on calcule le nombre total d'élèves libres
            # et on compare à la capacité de permanence
            total_libres = sum(cap for _, cap in libres)
            res["total"] += 1

            # on vérifie si le total respecte la capacité de permanence
            # (capacite_perm est un paramètre de la fonction)
            if total_libres <= capacite_perm:
                res["respectees"] += 1
                avancement += 1
                #print(f"[Run {current_seed}] Progression (verifier_permanence) : {avancement}")
            else:
                clist = ", ".join(f"{cl}({cap}p)" for cl, cap in libres)
                res["details"].append(
                    f"{jour} {HEURES[h]} : {total_libres} élèves en perm (max {capacite_perm}) — {clist}"
                )

# Vérification du volume horaire planifié par classe
def verifier_volume_horaire(emploi_du_temps, solver):
    """
    Vérifie que le volume horaire planifié par classe correspond aux volumes attendus.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (pour une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
    """

    global avancement
    # On initialise le compteur global d'avancement et les résultats de cette contrainte
    res = resultats_contraintes["volume_horaire"]
    # Calcul des volumes planifiés en incluant les sous-groupes si pertinents 
    volumes = compter_volume_matiere_avec_sousgroupes(emploi_du_temps, solver)

    # Parcours de chaque classe et de ses informations de volume
    for classe, info in volumes.items():
        # Extraction du niveau (ex. "6e", "5e") pour contextualiser les données
        niveau = classe[:2]
        # Pour chaque matière, comparer heures planifiées vs attendues
        for matiere, nb_heures in info["par_matiere"].items():
            # Récupération du volume attendu pour cette matière
            attendu = info["attendus"].get(matiere)
            # Ne traiter que les matières dont l'attendu est un entier défini
            if isinstance(attendu, int):
                # Incrément du nombre total de contrôles effectués
                res["total"] += 1
                if nb_heures == attendu:
                    # Si le volume correspond, on marque comme respecté
                    res["respectees"] += 1
                    avancement += 1
                    # Affichage de l'avancement pour le suivi
                    #print(f"[Run {current_seed}] Progression (verifier_volume_horaire) : {avancement}")
                else:
                    # Si le volume ne correspond pas, on enregistre l'erreur dans les détails pour un rapport ultérieur
                    res["details"].append(f"{classe} - {matiere} : {nb_heures}h au lieu de {attendu}h")

# Vérification des jours sans après-midi
def verifier_jours_sans_apres_midi(emploi_du_temps, solver, jours_sans_apres_midi):
    """
    Vérifie que pour tous les jours sans après-midi, aucun cours n'est planifié
    à partir du créneau d'indice 5 (13h-14h et suivants).

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        jours_sans_apres_midi (list): liste des jours interdits l'après-midi.
    """
    global avancement
    # On récupère le conteneur de résultats pour cette contrainte
    res = resultats_contraintes["jours_sans_apres_midi"]
    for classe in CLASSES:
        # Boucle sur chaque jour pour la classe
        for j, jour in enumerate(JOURS):
            if jour not in jours_sans_apres_midi:
                # Si le jour n'est pas interdit l'après-midi, on passe au suivant
                continue
            # Vérification des créneaux de 13h (index 5) à la fin
            for h in range(5, len(HEURES)):
                # Lecture de la matière effective au créneau
                mat_index = solver.Value(emploi_du_temps[(classe, j, h)])
                res["total"] += 1  # On compte cette vérification
                if mat_index == 0:
                    # Pas de cours → contrainte respectée
                    res["respectees"] += 1
                    avancement += 1
                    #print(f"[Run {current_seed}] Progression (verifier_jour_sans_apres_midi) : {avancement}")
                else:
                    # Violation détectée : on note la matière interdite
                    mat = MATIERES[mat_index-1]
                    res["details"].append(f"{classe} - {jour} {HEURES[h]} : Cours interdit ({mat})")


def verifier_indisponibilites_profs(emploi_un_semaine, solver, indispos_profs):
    """
    Vérifie que pour chaque prof, aucun cours n'est planifié aux créneaux où il est indisponible.

    Arguments:
        emploi_un_semaine (dict): variables IntVar matières par créneau (pour cette semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        indispos_profs (dict): mapping professeur → jours → liste d'heures interdites.
    """
    global avancement
    # On récupère le conteneur de résultats pour cette contrainte
    res = resultats_contraintes["indisponibilites_profs"]

    # Pour chaque professeur et sa liste d'indisponibilités
    for prof, indispos in indispos_profs.items():
        for jour_str, heures in indispos.items():
            if jour_str not in JOURS:
                # Ignorer si le jour n'existe pas dans la liste
                continue
            jour_index = JOURS.index(jour_str)

            for classe in CLASSES:
                niveau_classe = classe[:2]
                # On vérifie si ce prof peut enseigner cette matière/niveau
                for matiere, prof_ref in PROFESSEURS.items():
                    est_concerne = False
                    if isinstance(prof_ref, str):
                        est_concerne = (prof_ref == prof)
                    elif isinstance(prof_ref, dict):
                        profs_niv = prof_ref.get(niveau_classe)
                        if isinstance(profs_niv, str):
                            est_concerne = (profs_niv == prof)
                        elif isinstance(profs_niv, list):
                            est_concerne = (prof in profs_niv)

                    if not est_concerne:
                        continue  # Si le prof n'enseigne pas ici, on passe

                    mat_idx = MATIERES.index(matiere) + 1
                    # On teste chaque créneau où le prof est indisponible
                    for h in heures:
                        key = (classe, jour_index, h)
                        if key not in emploi_un_semaine:
                            # Créneau non concerné par ce planning
                            continue

                        res["total"] += 1  # On compte cette vérification
                        val_creneau = solver.Value(emploi_un_semaine[key])
                        if val_creneau != mat_idx:
                            # Aucune matière planifiée → contrainte respectée
                            res["respectees"] += 1
                            avancement += 1
                            #print(f"[Run {current_seed}] Progression (verifier_indisponibilite_prof) : {avancement}")
                        else:
                            # Violation : le cours du prof est planifié alors qu'il est indisponible
                            res["details"].append(
                                f"{classe} - {jour_str} {HEURES[h]} : "
                                f"{matiere} planifié(e) alors que {prof} est indisponible"
                            )

# Vérification du volume maximal de cours par professeur
def verifier_volume_par_professeur(emploi_du_temps, solver, volume_par_prof):
    """
    Vérifie que chaque professeur n'excède pas le nombre maximal de cours
    qui lui est assigné (volume_par_prof).

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        volume_par_prof (dict): mapping prof → volume max.
    """
    global avancement
    # Initialisation du résultat pour cette contrainte
    res = resultats_contraintes["volume_par_professeur"]
    # Préparation d'un compteur par professeur concerné
    compteur = {prof: 0 for prof in volume_par_prof}

    # Parcours de chaque classe de base uniquement
    for classe in CLASSES_BASE:
        niveau = classe[:2]
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                matiere_index = solver.Value(emploi_du_temps[(classe, j, h)])
                if matiere_index == 0:
                    # Pas de cours → on passe
                    continue
                matiere = MATIERES[matiere_index - 1]
                prof_ref = PROFESSEURS[matiere]

                # Détermination du professeur référent pour cette matière/niveau
                if isinstance(prof_ref, dict):
                    profs = prof_ref.get(niveau, [])
                    if isinstance(profs, list) and profs:
                        prof = profs[0]  # Choix du premier prof de la liste
                    elif isinstance(profs, str):
                        prof = profs    # Chaîne unique → on l'utilise directement
                    else:
                        prof = None     # Pas de prof disponible pour ce niveau
                else:
                    prof = prof_ref     # Cas simple : prof_ref est une chaîne ou liste

                if prof in compteur:
                    # Incrément du nombre de cours planifiés pour ce prof
                    compteur[prof] += 1

    # Vérification finale : comparaison avec les volumes maximaux
    for prof, nb_cours in compteur.items():
        res["total"] += 1  # On compte cette validation
        if nb_cours <= volume_par_prof.get(prof, float('inf')):
            res["respectees"] += 1
            avancement += 1
            #print(f"[Run {current_seed}] Progression (verifier_volume_par_professeur) : {avancement}")
        else:
            # Violation : le prof a plus de cours que le volume autorisé
            res["details"].append(f"{prof} a {nb_cours} cours (max {volume_par_prof.get(prof)})")

# Vérification de la capacité de la cantine
def verifier_cantine(classe_creneau_dej, cap_cantine, ratio_demi, capacites_classes):
    """
    Vérifie que la capacité de la cantine n'est pas dépassée sur les créneaux
    attribués pour le déjeuner.

    Arguments:
        classe_creneau_dej (dict): mapping classe → indice créneau déjeuner.
        cap_cantine (int): capacité maximale de la cantine.
        ratio_demi (float): proportion de demi-pensionnaires.
        capacites_classes (dict): mapping classe → nombre d'élèves.
    """
    global avancement
    # Récupération du conteneur de résultats pour la cantine
    res = resultats_contraintes["cantine"]
    
    from collections import defaultdict
    # Comptage total d’élèves demi-pensionnaires par créneau
    eleves_par_creneau = defaultdict(int)

    for classe, h in classe_creneau_dej.items():
        nb_eleves = int(capacites_classes.get(classe, 0) * ratio_demi)
        eleves_par_creneau[h] += nb_eleves
        res["total"] += 1  # On compte cette vérification

    # Vérification de la capacité pour chaque créneau
    surcharge_detectee = False
    for h, total_eleves in eleves_par_creneau.items():
        if total_eleves > cap_cantine:
            surcharge_detectee = True
            # Capacité dépassée → enregistrement du détail
            res["details"].append(
                f"Créneau {HEURES[h]} : capacité cantine insuffisante ({total_eleves} élèves pour {cap_cantine} places)"
            )
        else:
            # Capacité respectée → incrément du compteur
            res["respectees"] += 1
            avancement += 1
            #print(f"[Run {current_seed}] Progression (verifier_cantine) : {avancement}")

    # Si aucun dépassement, toutes les vérifications sont considérées respectées
    if not surcharge_detectee:
        res["respectees"] = res["total"]

# Vérification du poids du cartable par jour
def verifier_poids_cartable(
    emploi_du_temps,
    solver,
    poids_matieres_par_niveau,
    seuils_par_niveau,
    seuil_global,
    jours_sans_apres_midi,
    pSemaine
):
    """
    Vérifie, pour chaque classe de base et pour chaque jour, si la somme des poids
    (pour les matières planifiées) dépasse le seuil toléré pour la journée.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        poids_matieres_par_niveau (dict): mapping niveau → mapping matière → poids.
        seuils_par_niveau (dict): mapping niveau → seuil max toléré.
        seuil_global (float): seuil global si niveau non spécifié.
        jours_sans_apres_midi (list): jours interdits l'après-midi.
        pSemaine (str): nom de la semaine ("Semaine A" ou "Semaine B").
    """
    global avancement
    # Récupération du conteneur de résultats pour la surcharge de cartable
    res = resultats_contraintes["poids_cartable"]

    for classe in CLASSES_BASE:
        niveau = classe[:2]
        # Obtenir les poids pour ce niveau ou utiliser le seuil global
        poids_par_niveau = poids_matieres_par_niveau.get(niveau, {})
        seuil_max = seuils_par_niveau.get(niveau, seuil_global)
        if seuil_max <= 0:
            # Aucun seuil à appliquer pour ce niveau
            continue

        # Ajout d'une marge de 5 % sur le seuil
        seuil_tolerance = seuil_max * 1.05

        for j, jour in enumerate(JOURS):
            poids_total_jour = 0.0

            for h, heure in enumerate(HEURES):
                # Ignorer l'après-midi si le jour est interdit
                if jour in jours_sans_apres_midi and h > 4:
                    continue

                matiere_index = solver.Value(emploi_du_temps[(classe, j, h)])
                if matiere_index > 0:
                    matiere = MATIERES[matiere_index - 1]
                    poids = poids_par_niveau.get(matiere, 0.0)
                    # Accumulation du poids total pour la journée
                    poids_total_jour += poids

            # Validation et comptage de cette journée
            res["total"] += 1
            if poids_total_jour <= seuil_tolerance:
                res["respectees"] += 1
                avancement += 1
                #print(f"[Run {current_seed}] Progression (verifier_poids_cartable {pSemaine}) : {avancement}")
            else:
                # Surcharge détectée → ajout du détail avec valeurs précises
                res["details"].append(
                    f"{classe} - {pSemaine} - {jour} : poids {poids_total_jour:.2f}kg "
                    f"> tolérance {seuil_tolerance:.2f}kg"
                )

# Vérification des indisponibilités de salles
def verifier_indisponibilites_salles(emploi_du_temps, solver, indispos_salles, affectation_matiere_salle):
    """
    Vérifie qu'aucune salle indisponible n'est utilisée pour une matière qui y est assignée.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        indispos_salles (dict): mapping salle → jours → liste d'heures interdites.
        affectation_matiere_salle (dict): mapping matière/prof → salle assignée.
    """
    global avancement
    # On récupère le conteneur de résultats pour cette contrainte
    res = resultats_contraintes["indisponibilites_salles"]

    for salle, indispos in indispos_salles.items():
        # Pour chaque salle et ses indisponibilités
        for jour_str, heures in indispos.items():
            if jour_str not in JOURS:
                # Ignorer les jours non définis dans JOURS
                continue
            jour_index = JOURS.index(jour_str)

            # Filtrer uniquement les matières réellement assignées à cette salle
            matieres_concernees = [
                m for m in affectation_matiere_salle
                if m in MATIERES and affectation_matiere_salle[m] == salle
            ]

            for classe in CLASSES:
                niveau = classe[:2]
                # Pour chaque matière concernée, vérifier chaque créneau interdit
                for matiere in matieres_concernees:
                    mat_index = MATIERES.index(matiere) + 1
                    for h in heures:
                        # Comptage de la vérification
                        res["total"] += 1
                        val = solver.Value(emploi_du_temps[(classe, jour_index, h)])
                        if val == mat_index:
                            # Violation : cours planifié dans une salle indisponible
                            res["details"].append(
                                f"{classe} - {jour_str} {HEURES[h]} : Cours interdit en salle indisponible ({matiere} en {salle})"
                            )
                        else:
                            # Contrainte respectée pour ce créneau
                            res["respectees"] += 1
                            avancement += 1
                            #print(f"[Run {current_seed}] Progression (verifier_indisponibilites_salles) : {avancement}")

# Vérification de l'exclusion de séquence de matières
def verifier_matExcluSuite(emploi_du_temps, solver, pMatiere1, pMatiere2, pClasses=CLASSES_BASE):
    """
    Vérifie l'absence de la séquence pMatiere1 → pMatiere2 dans l'emploi du temps des classes.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        pMatiere1 (str): matière 1 (ne doit pas être suivie de pMatiere2).
        pMatiere2 (str): matière 2.
        pClasses (list ou str): classes concernées ou préfixe.
    """
    global avancement
    # On initialise les compteurs de violations et totaux
    res = resultats_contraintes["mat_exclu_suite"]
    matdex_1 = MATIERES.index(pMatiere1) + 1
    matdex_2 = MATIERES.index(pMatiere2) + 1

    choixClasse = []
    if pClasses != CLASSES_BASE:
        # Filtrer les classes par préfixe si besoin
        for c in CLASSES_BASE:
            if pClasses in c:
                choixClasse.append(c)
    else:
        choixClasse = pClasses

    violations = 0
    total_possibles = 0

    for classe in choixClasse:
        for j in range(len(JOURS)):
            for h in range(len(HEURES) - 1):
                total_possibles += 1
                # Lecture des matières consécutives
                val_actuel = solver.Value(emploi_du_temps[(classe, j, h)])
                val_suivant = solver.Value(emploi_du_temps[(classe, j, h + 1)])
                if val_actuel == matdex_1 and val_suivant == matdex_2:
                    # Violation détectée
                    violations += 1
                    res["details"].append(
                        f"{classe} - {JOURS[j]} {HEURES[h]} suivi de {HEURES[h+1]} : {pMatiere1} → {pMatiere2}"
                    )

    # Mise à jour des compteurs globaux
    res["total"] += total_possibles
    if violations == 0:
        # Si aucune violation, on compte toutes les opportunités comme respectées
        res["respectees"] += total_possibles
        avancement += 1
        #print(f"[Run {current_seed}] Progression (verifier_matExcluSuite) : {avancement}")
    return violations == 0

# Vérification de l'inclusion de séquence de matières
def verifier_matIncluSuite(emploi_du_temps, solver, pMatiere1, pMatiere2, pContrainte, pNBFois=1, pClasses=CLASSES_BASE):
    """
    Vérifie la contrainte d'inclusion pMatiere1 → pMatiere2 selon le type de contrainte.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau.
        solver (CpSolver): solveur ayant résolu le modèle.
        pMatiere1 (str): matière de départ.
        pMatiere2 (str): matière d'arrivée.
        pContrainte (str): "forte", "moyenne" ou "faible".
        pNBFois (int): nombre d'occurrences attendu si "moyenne" ou "faible".
        pClasses (list ou str): classes concernées ou préfixe.
    """
    global avancement
    # Initialisation des compteurs
    res = resultats_contraintes["mat_inclu_suite"]
    matdex_1 = MATIERES.index(pMatiere1) + 1
    matdex_2 = MATIERES.index(pMatiere2) + 1

    choixClasse = []
    if pClasses != CLASSES_BASE:
        # Filtrer les classes par préfixe
        for c in CLASSES_BASE:
            if pClasses in c:
                choixClasse.append(c)
    else:
        choixClasse = pClasses

    total_possibles = 0
    total_suivi = 0

    for classe in choixClasse:
        occurences_classe = 0
        for j in range(len(JOURS)):
            for h in range(len(HEURES) - 1):
                total_possibles += 1
                # Lecture des matières consécutives
                val_actuel = solver.Value(emploi_du_temps[(classe, j, h)])
                val_suivant = solver.Value(emploi_du_temps[(classe, j, h + 1)])
                if val_actuel == matdex_1 and val_suivant == matdex_2:
                    # Compte de l'occurrence
                    occurences_classe += 1
                    total_suivi += 1
        if occurences_classe > 0:
            # Enregistrement des détails par classe
            res["details"].append(f"{classe} : {occurences_classe} occurrences de {pMatiere1} → {pMatiere2}")

    res["total"] += total_possibles

    # Évaluation selon le type de contrainte
    if pContrainte == "forte":
        respect = (total_suivi > 0)
    elif pContrainte == "moyenne":
        respect = (total_suivi >= pNBFois)
    else:  # "faible"
        respect = (total_suivi <= pNBFois)

    if respect:
        # Si la contrainte est respectée, on compte tous les cas possibles
        res["respectees"] += total_possibles
        avancement += 1
        #print(f"[Run {current_seed}] Progression (verifier_matIncluSuite) : {avancement}")
    else:
        # Violation de la contrainte
        res["details"].append(
            f"Contrainte {pContrainte} non respectée : {total_suivi} occurrences (attendu {pNBFois})"
        )
    return respect

# Vérification de la contrainte "Même Niveau, Même Cours"
def verifier_memNivMemCours(emploi_du_temps, solver, pNiveau, pMatiere):
    """
    Vérifie la contrainte "Même Niveau, Même Cours" pour une matière donnée.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau.
        solver (CpSolver): solveur ayant résolu le modèle.
        pNiveau (str): niveau ciblé (ex. "6e").
        pMatiere (str): matière concernée.
    Retourne:
        bool: True si la contrainte est respectée, False sinon.
    """
    global avancement
    # Récupération du conteneur de résultats pour cette contrainte
    res = resultats_contraintes["mem_niveau_cours"]
    # Conversion de la matière en son index pour comparaison
    matdex_p = MATIERES.index(pMatiere) + 1

    # Récupération des classes correspondant au niveau
    choixClasse = [c for c in CLASSES_BASE if pNiveau in c]
    if not choixClasse:
        # Niveau inconnu : on enregistre l’erreur et on sort
        res["details"].append(f"Niveau inconnu : {pNiveau}")
        return False

    res["total"] += 1  # une contrainte globale
    violations = []

    # Pour chaque créneau, vérifier si la matière est présente pour toutes les classes ou aucune
    for j in range(len(JOURS)):
        for h in range(len(HEURES)):
            presences = []
            for c in choixClasse:
                val = solver.Value(emploi_du_temps[(c, j, h)])
                presences.append(val == matdex_p)
            # Détection de la violation si certains ont la matière et d’autres non
            if any(presences) and not all(presences):
                viol_classes = [choixClasse[i] for i, present in enumerate(presences) if present]
                non_viol_classes = [choixClasse[i] for i, present in enumerate(presences) if not present]
                violations.append(
                    f"{JOURS[j]} {HEURES[h]} : {pMatiere} donné dans {viol_classes} "
                    f"mais pas dans {non_viol_classes}"
                )

    if not violations:
        # Pas de violation → contrainte respectée
        res["respectees"] += 1
        avancement += 1
        #print(f"[Run {current_seed}] Progression (verifier_memNIvMemCours) : {avancement}")
        return True
    else:
        # Enregistrement des détails des violations
        res["details"].extend(violations)
        return False


# Vérification des limites d'heures par étendue (journée ou demi-journée)
def verifier_max_heures_par_etendue(emploi_du_temps, solver, max_heures_par_etendue):
    """
    Vérifie les contraintes de nombre maximal d'heures par étendue (journée ou demi-journée)
    définies dans max_heures_par_etendue.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        max_heures_par_etendue (list): liste de règles avec "niveau", "matiere", "max_heures", "etendue"
    """
    global avancement
    # Récupération du conteneur de résultats pour cette contrainte
    res = resultats_contraintes["max_heures_par_etendue"]

    for regle in max_heures_par_etendue:
        niveau = regle["niveau"]
        matiere = regle["matiere"]
        # Conversion de la matière en index
        matiere_index = MATIERES.index(matiere) + 1
        max_heures = regle["max_heures"]
        etendue = regle["etendue"]

        for classe in CLASSES_BASE:
            if not classe.startswith(niveau):
                continue  # Ignore les classes d'un autre niveau

            for j, jour in enumerate(JOURS):
                if etendue == "journee":
                    heures_cibles = range(len(HEURES))
                    compteur = 0
                    for h in heures_cibles:
                        if (classe, j, h) in emploi_du_temps:
                            if solver.Value(emploi_du_temps[(classe, j, h)]) == matiere_index:
                                compteur += 1
                    res["total"] += 1
                    if compteur <= max_heures:
                        # Limite journalière respectée
                        res["respectees"] += 1
                        avancement += 1
                        #print(f"[Run {current_seed}] Progression (verifier_max_heures_par_etendue) : {avancement}")
                    else:
                        # Dépassement de la limite journalière
                        res["details"].append(
                            f"{classe} - {jour} : {compteur}h de {matiere} (max {max_heures})"
                        )

                elif etendue == "demi-journee":
                    matin = range(4)
                    apres = range(5, len(HEURES))
                    for label, heures in [("matin", matin), ("apres", apres)]:
                        compteur = 0
                        for h in heures:
                            if (classe, j, h) in emploi_du_temps:
                                if solver.Value(emploi_du_temps[(classe, j, h)]) == matiere_index:
                                    compteur += 1
                        res["total"] += 1
                        if compteur <= max_heures:
                            # Limite demi-journée respectée
                            res["respectees"] += 1
                            avancement += 1
                            #print(f"[Run {current_seed}] Progression (verifier_max_heures_par_etendue) : {avancement}")
                        else:
                            # Dépassement de la limite demi-journée
                            res["details"].append(
                                f"{classe} - {jour} ({label}) : {compteur}h de {matiere} (max {max_heures})"
                            )


# Vérification de la contrainte matHorairDonneV2
def verifier_matHorairDonneV2(
    emploi_du_temps,
    solver,
    pClasses,
    pMatiere,
    pJour,
    pHorairMin,
    pHorairMax=None,
    pNBFois=None
):
    """
    Vérifie la contrainte matHorairDonneV2 : 
    impose qu'une matière apparaisse un certain nombre de fois dans un horaire donné.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        pClasses (str ou list): préfixe ou liste de classes.
        pMatiere (str, list ou sous-groupe): matière ou liste de matières ou clé de sous-groupe.
        pJour (str): jour ciblé (ex. "Jeudi").
        pHorairMin (str): horaire de début (ex. "13h").
        pHorairMax (str ou None): horaire de fin (ex. "17h").
        pNBFois (int ou None): nombre de fois attendu.
    """
    global avancement
    # Récupération du conteneur de résultats pour cette contrainte
    res = resultats_contraintes["mat_horaire_donne_v2"]

    # 1) Traduction du jour en index
    jourdex_h = JOURS.index(pJour)
    HORAIRE_MIN, HORAIRE_MAX = pHorairMin, pHorairMax
    Hordex_Min, Hordex_Max = None, None

    # 2) Préparation des classes ciblées
    choixClasse = []
    if pClasses != CLASSES_BASE:
        for c in CLASSES_BASE:
            if pClasses in c:
                choixClasse.append(c)
    else:
        choixClasse = list(CLASSES_BASE)
    if not choixClasse:
        # Aucune classe trouvée selon le critère
        res["details"].append(f"Classes {pClasses} non trouvées")
        return

    # 3) Préparation de la liste de matières à rechercher
    if isinstance(pMatiere, str) and pMatiere in MATIERES_SOUSGROUPES:
        liste_matieres = MATIERES_SOUSGROUPES[pMatiere]
    elif isinstance(pMatiere, list):
        liste_matieres = list({m for pm in pMatiere for m in MATIERES if pm in m})
    elif isinstance(pMatiere, str):
        liste_matieres = [m for m in MATIERES if pMatiere in m]
    else:
        liste_matieres = []
    # Liste des matières ciblées constituée

    # 4) Repérage des indices horaires min et max
    for idx, h in enumerate(HEURES):
        if h.startswith(HORAIRE_MIN):
            Hordex_Min = idx
        if HORAIRE_MAX and h.endswith(HORAIRE_MAX):
            Hordex_Max = idx
    if Hordex_Min is None:
        # Horaire de début non trouvé
        res["details"].append(f"Horaire min '{HORAIRE_MIN}' non trouvé")
        return
    if Hordex_Max is None:
        # Pas de fin spécifiée : on prend seulement le créneau de départ
        Hordex_Max = Hordex_Min

    # 5) Calcul du nombre attendu de cases
    nbFois = pNBFois if pNBFois is not None else (Hordex_Max - Hordex_Min + 1)
    # Nombre d'occurrences attendu calculé

    # 6) Comptage et comparaison pour chaque classe
    for classe in choixClasse:
        if isinstance(pMatiere, str) and pMatiere in VOLUME_HORAIRE.get(classe[:-1], {}):
            max_possible = VOLUME_HORAIRE[classe[:-1]][pMatiere]
            nbFois = min(nbFois, max_possible)  # Ajustement si nécessaire

        compteur = 0
        for h in range(Hordex_Min, Hordex_Max + 1):
            key = (classe, jourdex_h, h)
            if key in emploi_du_temps:
                val = solver.Value(emploi_du_temps[key])
                if val > 0:
                    mat = MATIERES[val - 1]
                    if mat in liste_matieres:
                        compteur += 1

        res["total"] += 1
        if compteur == nbFois:
            # Contrainte respectée pour cette classe et ce jour
            res["respectees"] += 1
            avancement += 1
            #print(f"[Run {current_seed}] Progression (verifier_matHoraireDonneV2) : {avancement}")
        else:
            # Violation : nombre d'occurrences différent de l'attendu
            res["details"].append(
                f"{classe} - {pJour} ({HORAIRE_MIN}-{HORAIRE_MAX or HORAIRE_MIN}) : "
                f"{compteur}h de {liste_matieres} (attendu {nbFois})"
            )

# Vérification des préférences de salle des professeurs
def verifier_preferences_salle_professeur(solver,emploi_du_temps, emploi_du_temps_profs,JOURS,HEURES,MATIERES, PROFESSEURS, PREFERENCES_SALLE_PROF,):
    """
    Vérifie que, lorsque un professeur ayant une préférence de salle donne cours,
    il est bien dans sa salle préférée (ou la salle assignée).

    Arguments:
        solver (CpSolver): solveur ayant résolu le modèle.
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        emploi_du_temps_profs (dict): variables IntVar/BoolVar profs par créneau.
        JOURS (list): liste des jours.
        HEURES (list): liste des créneaux horaires.
        MATIERES (list): liste des matières.
        PROFESSEURS (dict): mapping matière → prof ou liste/dict de profs.
        PREFERENCES_SALLE_PROF (dict): mapping prof → salle préférée.
    """

    global avancement
    res = resultats_contraintes["preferences_salle_professeur"]

    # 1) Réinitialiser les compteurs et vider les détails
    res["total"] = 0
    res["respectees"] = 0
    res["details"].clear()

    # 2) Parcourir chaque classe, chaque jour et chaque heure
    for classe in CLASSES:
        niveau_classe = classe[:2]

        for j, jour in enumerate(JOURS):
            for h, heure in enumerate(HEURES):
                # a) Obtenir l'index de la matière (0 = pas de cours)
                mat_index = solver.Value(emploi_du_temps[(classe, j, h)])
                if mat_index == 0:
                    # Pas de cours à ce créneau → rien à vérifier
                    continue

                # b) Déterminer le nom de la matière et du professeur effectif
                mat = MATIERES[mat_index - 1]
                prof_ref = PROFESSEURS.get(mat)

                # c) Trouver le professeur qui enseigne réellement ce créneau
                if isinstance(prof_ref, str):
                    # Contrainte simple : la matière est donnée par un seul prof
                    prof_enseigne = prof_ref
                else:
                    # prof_ref est un dict {niveau → liste ou chaîne}
                    profs_niv = prof_ref.get(niveau_classe)
                    if isinstance(profs_niv, list):
                        # Plusieurs profs possibles : on regarde la variable emploi_du_temps_profs
                        key_prof = (classe, j, h, mat)
                        if key_prof in emploi_du_temps_profs:
                            idx = solver.Value(emploi_du_temps_profs[key_prof])
                            prof_enseigne = profs_niv[idx]
                        else:
                            # Si aucune variable n'a été créée, on prend le premier de la liste
                            prof_enseigne = profs_niv[0]
                    else:
                        # profs_niv est directement une chaîne
                        prof_enseigne = profs_niv

                # d) Si ce prof n'a pas de préférence de salle, on passe au suivant
                if prof_enseigne not in PREFERENCES_SALLE_PROF:
                    continue

                salle_preferee = PREFERENCES_SALLE_PROF[prof_enseigne]

                # e) Incrémenter le total de cas à vérifier
                res["total"] += 1

                # f) Récupérer la salle « logique » de ce professeur dans AFFECTATION_MATIERE_SALLE
                actual_salle = AFFECTATION_MATIERE_SALLE.get(prof_enseigne)

                # g) Comparer : si la salle affichée correspond bien à la préférence
                if actual_salle == salle_preferee:
                    res["respectees"] += 1
                    avancement += 1
                    #print(f"[Run {current_seed}] Progression (verifier_preferences_salle_professeur) : {avancement}")
                else:
                    # Si la clé n'existe pas dans AFFECTATION_MATIERE_SALLE, actual_salle sera None
                    res["details"].append(
                        f"{classe} - {jour} {heure} : {prof_enseigne} en {actual_salle} "
                        f"(préféré : {salle_preferee})"
                    )

# Vérification de la double affectation des salles
def verifier_double_affectation_salles(emploi_du_temps, emploi_du_temps_salles, solver, SALLES_GENERALES, CLASSES):
    """
    Vérifie qu'aucune salle n'est attribuée à plus d'une classe au même créneau.

    Arguments:
        emploi_du_temps (dict): variables IntVar matières par créneau (une semaine).
        emploi_du_temps_salles (dict): variables IntVar salles par créneau (une semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        SALLES_GENERALES (list): liste des salles communes.
        CLASSES (list): liste de toutes les classes (base + sous-groupes).
    """
    global avancement
    res = resultats_contraintes["double_affectation_salles"]

    # Pour chaque jour j, chaque heure h, on compte combien de classes sont dans chaque salle.
    for j in range(len(JOURS)):
        for h in range(len(HEURES)):
            # Construire un compteur {nom_salle: [liste_classes_occupant]}
            classes_par_salle = {salle: [] for salle in SALLES_GENERALES}
            # Pour chaque classe, on récupère la valeur de l’IntVar salle
            for classe in CLASSES:
                clé = (classe, j, h)
                salle_idx = solver.Value(emploi_du_temps_salles[clé])
                if salle_idx > 0 and salle_idx <= len(SALLES_GENERALES):
                    nom_salle = SALLES_GENERALES[salle_idx - 1]
                    classes_par_salle[nom_salle].append(classe)

            # Pour chaque salle, on incrémente 'total' et on regarde s’il y a au plus une classe
            for salle, liste_classes in classes_par_salle.items():
                res["total"] += 1
                if len(liste_classes) <= 1:
                    res["respectees"] += 1
                    avancement += 1
                    #print(f"[Run {current_seed}] Progression (verifier_double_affectation_salles) : {avancement}")
                else:
                    # Violation : plusieurs classes dans la même salle
                    clist = ", ".join(liste_classes)
                    res["details"].append(
                        f"{JOURS[j]} {HEURES[h]} – Salle '{salle}' occupée par {clist}"
                    )

# Vérification de la double affectation des professeurs
def verifier_double_affectation_profs(
    emploi_du_temps_semaine,
    emploi_du_temps_profs_semaine,
    solver,
    PROFESSEURS,
    CLASSES,
    JOURS,
    HEURES,
    resultats_contraintes,
    semaine  # ← nouveau paramètre
):
    """
    Vérifie qu'aucun professeur n'est assigné à deux classes différentes au même créneau
    pour la semaine spécifiée.

    Arguments:
        emploi_du_temps_semaine (dict): variables IntVar matières par créneau (cette semaine).
        emploi_du_temps_profs_semaine (dict): variables IntVar/BoolVar profs par créneau (cette semaine).
        solver (CpSolver): solveur ayant résolu le modèle.
        PROFESSEURS (dict): mapping matière → prof(s).
        CLASSES (list): liste de toutes les classes.
        JOURS (list): liste des jours.
        HEURES (list): liste des horaires.
        resultats_contraintes (dict): dictionnaire pour stocker résultats des vérifications.
        semaine (str): "Semaine A" ou "Semaine B".
    """
    from collections import defaultdict

    global avancement
    # Récupération de l’espace de résultats pour la contrainte
    res = resultats_contraintes["double_affectation_profs"]

    # Construction de l’ensemble des (niveau, matière) à ignorer selon memnivmemcours
    memniv_active = {
        (entry["niveau"], entry["matiere"])
        for entry in config.get("memnivmemcours", [])
    }

    # Parcours par jour et par créneau horaire
    for j in range(len(JOURS)):
        for h in range(len(HEURES)):
            # Initialisation du compteur prof → liste de classes
            prof_count = defaultdict(list)

            # Parcours des classes de base pour identifier quel prof enseigne
            for cl in CLASSES_BASE:
                # Détermination du niveau de la classe (ex. "6e")
                niveau_cl = cl[:2]

                key_cl = (cl, j, h)
                if key_cl not in emploi_du_temps_semaine:
                    continue
                mat_idx = solver.Value(emploi_du_temps_semaine[key_cl])
                if mat_idx == 0:
                    continue  # Pas de cours planifié

                # Conversion de l’index en nom de matière
                mat = MATIERES[mat_idx - 1]

                # Ignorer si la matière est gérée dynamiquement par memnivmemcours
                if (niveau_cl, mat) in memniv_active:
                    continue

                prof_ref = PROFESSEURS[mat]

                # 🔍 Détermination du professeur effectif à ce créneau
                if isinstance(prof_ref, str):
                    # Cas simple : chaîne unique
                    prof_sel = prof_ref

                elif isinstance(prof_ref, dict):
                    # Cas dict : choisir selon niveau et variable profs_semaine
                    profs_niv = prof_ref.get(niveau_cl)
                    if isinstance(profs_niv, str):
                        prof_sel = profs_niv
                    elif isinstance(profs_niv, list) and profs_niv:
                        prof_sel = profs_niv[0]
                        for key_prof, var in emploi_du_temps_profs_semaine.items():
                            cl_k, j_k, h_k, mat_k, sem_k = key_prof
                            if (cl_k, j_k, h_k, mat_k) == (cl, j, h, mat):
                                idx = solver.Value(var)
                                prof_sel = profs_niv[idx]
                                break
                    else:
                        prof_sel = None

                elif isinstance(prof_ref, list) and prof_ref:
                    # Cas liste globale de profs
                    profs_niv = prof_ref
                    prof_sel = profs_niv[0]
                    for key_prof, var in emploi_du_temps_profs_semaine.items():
                        cl_k, j_k, h_k, mat_k, sem_k = key_prof
                        if (cl_k, j_k, h_k, mat_k) == (cl, j, h, mat):
                            idx = solver.Value(var)
                            prof_sel = profs_niv[idx]
                            break

                else:
                    prof_sel = None

                if prof_sel:
                    # Ajout de la classe à la liste du prof pour ce créneau
                    prof_count[prof_sel].append(cl)

            # Vérification finale : un prof ne doit pas avoir plus d’une classe simultanée
            for prof, classes in prof_count.items():
                res["total"] += 1  # Comptage de cette vérification
                if len(classes) <= 1:
                    # Contrainte respectée pour ce prof
                    res["respectees"] += 1
                    avancement += 1
                    #print(f"[Run {current_seed}] Progression (verifier_double_affectation_profs) : {avancement}")
                else:
                    # Violation détectée : le prof est assigné à plusieurs classes simultanément
                    clist = ", ".join(classes)
                    res["details"].append(
                        f"{semaine} – {JOURS[j]} {HEURES[h]} : Prof '{prof}' en double dans {clist}"
                    )


# Initialisation du dictionnaire global de résultats
resultats_contraintes = {
    "volume_horaire":         {"total": 0, "respectees": 0, "details": []},
    "indisponibilites_profs": {"total": 0, "respectees": 0, "details": []},
    "jours_sans_apres_midi":  {"total": 0, "respectees": 0, "details": []},
    "volume_par_professeur":  {"total": 0, "respectees": 0, "details": []},
    "cantine":                {"total": 0, "respectees": 0, "details": []},
    "permanence":             {"total": 0, "respectees": 0, "details": []},
    "poids_cartable":         {"total": 0, "respectees": 0, "details": []},
    "indisponibilites_salles":{"total": 0, "respectees": 0, "details": []},
    "double_affectation_salles": {"total": 0, "respectees": 0, "details": []},
    "double_affectation_profs": {"total": 0, "respectees": 0, "details": []},
    "mat_exclu_suite":        {"total": 0, "respectees": 0, "details": []},
    "mat_inclu_suite":        {"total": 0, "respectees": 0, "details": []},
    "mem_niveau_cours":       {"total": 0, "respectees": 0, "details": []},
    "max_heures_par_etendue": {"total": 0, "respectees": 0, "details": []},
    "mat_horaire_donne_v2":   {"total": 0, "respectees": 0, "details": []},
    "preferences_salle_professeur": {"total": 0, "respectees": 0, "details": []}
}

# Vérifie et résout le modèle CP-SAT, puis vérifie les contraintes
def solve_et_verifie(
    model,
    emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs,
    JOURS, HEURES, MATIERES, PROFESSEURS,
    SOUS_GROUPES_SUFFIXES, CLASSES, CLASSES_BASE,
    CAPACITES_CLASSES, INDISPONIBILITES_PROFS, INDISPONIBILITES_SALLES,
    config, AFFECTATION_MATIERE_SALLE,
    fusionner_groupes_vers_classes,
    seed
):
    """
    Résout le modèle CP-SAT avec la graine donnée, puis vérifie toutes les contraintes
    configurées dans 'config'. Les vérifications sont faites pour la Semaine A et B.

    Arguments:
        model (CpModel): le modèle CP-SAT à résoudre.
        emploi_du_temps (dict): variables IntVar matières par créneau.
        emploi_du_temps_salles (dict): variables IntVar salles par créneau.
        emploi_du_temps_profs (dict): variables IntVar/BoolVar profs par créneau.
        JOURS (list): liste des jours.
        HEURES (list): liste des horaires.
        MATIERES (list): liste des matières.
        PROFESSEURS (dict): mapping matière → prof(s).
        SOUS_GROUPES_SUFFIXES (dict): mapping suffixe → matière sous-groupe.
        CLASSES (list): toutes les classes (base + sous-groupes).
        CLASSES_BASE (list): classes de base.
        CAPACITES_CLASSES (dict): mapping classe → capacité d'élèves.
        INDISPONIBILITES_PROFS (dict): mapping prof → indisponibilités.
        INDISPONIBILITES_SALLES (dict): mapping salle → indisponibilités.
        config (dict): contenu cru du JSON de configuration.
        AFFECTATION_MATIERE_SALLE (dict): mapping matière/prof → salle assignée.
        fusionner_groupes_vers_classes (func): fonction pour fusionner groupes → texte.
        seed (int): graine aléatoire pour le solveur.

    Retourne:
        tuple:
            - emplois (dict): {"Semaine A": fusion_A, "Semaine B": fusion_B}
            - taux (float): pourcentage de contraintes respectées (0.0 à 1.0).
            - resultats_contraintes (dict): détails des vérifications pour chaque catégorie.
    """
    # Réinitialiser le dict resultats_contraintes…
    for cat in resultats_contraintes:
        resultats_contraintes[cat]["total"] = 0
        resultats_contraintes[cat]["respectees"] = 0
        resultats_contraintes[cat]["details"].clear()

    # Lancer le solveur
    solver = cp_model.CpSolver()
    solver.parameters.random_seed = seed
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, 0.0, None

    # Fusionner les emplois du temps pour chaque semaine
    fusion_A = fusionner_groupes_vers_classes(
        emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs, solver, "Semaine A"
    )
    fusion_B = fusionner_groupes_vers_classes(
        emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs, solver, "Semaine B"
    )

    global current_seed
    current_seed = seed

    # ─── VÉRIFICATIONS POUR CHAQUE SEMAINE ────────────────────────────────────
    for semaine in SEMAINES:
        # 1) verifier_volume_horaire  ← si on a défini "volume_horaire" dans config
        if "volume_horaire" in config:
            verifier_volume_horaire(emploi_du_temps[semaine], solver)

        # 2) verifier_jours_sans_apres_midi ← si "jours_sans_apres_midi" défini et non vide
        jours_sans_ap = config.get("jours_sans_apres_midi", [])
        if jours_sans_ap:
            verifier_jours_sans_apres_midi(
                emploi_du_temps[semaine], solver, jours_sans_ap
            )

        # 3) verifier_indisponibilites_profs ← si "indisponibilites_profs" existe
        if config.get("indisponibilites_profs"):
            verifier_indisponibilites_profs(
                emploi_du_temps[semaine], solver, INDISPONIBILITES_PROFS
            )

        # 4) verifier_volume_par_professeur ← si "volume_par_professeur" existe
        vol_par_prof = config.get("volume_par_professeur", {})
        if vol_par_prof:
            verifier_volume_par_professeur(
                emploi_du_temps[semaine], solver, vol_par_prof
            )

        # 5) verifier_indisponibilites_salles ← si "indisponibilites_salles" existe
        if config.get("indisponibilites_salles"):
            verifier_indisponibilites_salles(
                emploi_du_temps[semaine],
                solver,
                INDISPONIBILITES_SALLES,
                AFFECTATION_MATIERE_SALLE
            )

        # 6) verifier_double_affectation_salles ← on appelle systématiquement si on a défini SALLES_GENERALES
        if SALLES_GENERALES:
            verifier_double_affectation_salles(
                emploi_du_temps[semaine],
                emploi_du_temps_salles[semaine],
                solver,
                SALLES_GENERALES,
                CLASSES
            )

        # 7) verifier_double_affectation_profs ← on l’appelle toujours, 
        #    mais on peut vérifier la présence de PROFESSEURS et CLASSES
        if PROFESSEURS and CLASSES:
            verifier_double_affectation_profs(
                emploi_du_temps[semaine],
                emploi_du_temps_profs[semaine],
                solver,
                PROFESSEURS,
                CLASSES,
                JOURS,
                HEURES,
                resultats_contraintes,
                semaine
            )

        # 8) verifier_cantine ← si "cantine" existe dans config
        if "cantine" in config:
            cant_cfg = config["cantine"]
            verifier_cantine(
                classe_creneau_dej,
                cant_cfg.get("capacite", 0),
                cant_cfg.get("proportion_demi_pensionnaire", 0),
                CAPACITES_CLASSES
            )

        # 9) verifier_permanence ← si "permanence" existe ET qu’on a configuré une capacité
        perm_cfg = config.get("permanence", {})
        if perm_cfg and perm_cfg.get("capacite", 0) > 0:
            # récupérer h_dej une seule fois
            verifier_permanence(
                solver,
                emploi_du_temps[semaine],
                perm_cfg["capacite"]
            )


        # 10) verifier_poids_cartable ← si "poids_matieres" existe
        if config.get("poids_matieres_par_niveau"):
            verifier_poids_cartable(
                emploi_du_temps[semaine],
                solver,
                config.get("poids_matieres_par_niveau", {}),
                config.get("poids_cartable_max_somme_par_niveau", {}),
                config.get("poids_cartable_max_somme", 0.0),
                config.get("jours_sans_apres_midi", []),
                semaine
            )

        # 11) verifier_matExcluSuite ← si "mat_exclu_suite" existe et non vide
        entries_exclu = config.get("mat_exclu_suite", [])
        if entries_exclu:
            for entry in entries_exclu:
                m1 = entry["matiere1"]
                m2 = entry["matiere2"]
                contra = entry.get("contrainte", "forte")
                classes_cible = entry.get("classes", "CLASSES_BASE")
                # si "CLASSES_BASE" dans JSON, on renvoie la constante Python CLASSES_BASE
                if isinstance(classes_cible, str) and classes_cible == "CLASSES_BASE":
                    verifier_matExcluSuite(
                        emploi_du_temps[semaine], solver, m1, m2, CLASSES_BASE
                    )
                else:
                    verifier_matExcluSuite(
                        emploi_du_temps[semaine], solver, m1, m2, classes_cible
                    )

        # 12) verifier_matIncluSuite ← si "mat_inclu_suite" existe
        entries_inclu = config.get("mat_inclu_suite", [])
        if entries_inclu:
            for entry in entries_inclu:
                m1 = entry["matiere1"]
                m2 = entry["matiere2"]
                contra = entry.get("contrainte", "moyenne")
                nb_fois = entry.get("nb_fois", 1)
                classes_cible = entry.get("classes", "CLASSES_BASE")
                if isinstance(classes_cible, str) and classes_cible == "CLASSES_BASE":
                    verifier_matIncluSuite(
                        emploi_du_temps[semaine],
                        solver,
                        m1, m2, contra, nb_fois, CLASSES_BASE
                    )
                else:
                    verifier_matIncluSuite(
                        emploi_du_temps[semaine],
                        solver,
                        m1, m2, contra, nb_fois, classes_cible
                    )

        # 13) verifier_memNivMemCours ← si on a configuré expressément une matière à vérifier
        if config.get("memnivmemcours"):
            for entry in config.get("memnivmemcours", []):
                niveau  = entry["niveau"]    # ex. "6e"
                matiere = entry["matiere"]   # ex. "Maths"
                for semaine in SEMAINES:
                    verifier_memNivMemCours(
                        emploi_du_temps[semaine],
                        solver,
                        niveau,
                        matiere
                    )


        # 14) verifier_matHorairDonneV2 ← si on a défini la clé correspondante dans JSON
        mat_horaire_entries = config.get("mat_horaire_donne_v2", [])
        if mat_horaire_entries:
            for entry in mat_horaire_entries:
                classes_cible = entry["classes"]
                matieres_cible = entry["matiere"]  
                jour_cible = entry["jour"]
                horaire_min = entry["horaire_min"]
                horaire_max = entry.get("horaire_max")
                nb_fois = entry.get("nb_fois")
                verifier_matHorairDonneV2(
                    emploi_du_temps[semaine],
                    solver,
                    classes_cible,
                    matieres_cible,
                    jour_cible,
                    horaire_min,
                    horaire_max,
                    nb_fois
                )

        # 15) verifier_preferences_salle_professeur ← si "preferences_salle_professeur" existe
        if config.get("preferences_salle_professeur"):
            verifier_preferences_salle_professeur(
                solver,
                emploi_du_temps[semaine],
                emploi_du_temps_profs[semaine],
                JOURS, HEURES, MATIERES, PROFESSEURS,
                config.get("preferences_salle_professeur", {})
            )

        # 16) verifier_max_heures_par_etendue ← si "max_heures_par_etendue" existe
        if config.get("max_heures_par_etendue"):
            verifier_max_heures_par_etendue(
                emploi_du_temps[semaine],
                solver,
                config.get("max_heures_par_etendue", [])
            )

    # ─── Calcule le taux global de contraintes respectées (Semaine A + Semaine B) ──
    total_c = sum(stats["total"] for stats in resultats_contraintes.values())
    total_r = sum(stats["respectees"] for stats in resultats_contraintes.values())
    taux = (total_r / total_c) if total_c > 0 else 1.0

    # Affichage du rapport détaillé des contraintes
    return {"Semaine A": fusion_A, "Semaine B": fusion_B}, taux, resultats_contraintes


# Fonction utilitaire pour calculer le pourcentage global à partir de resultats_contraintes
def calculer_pourcentage_global(resultats):
    """
    Calcule le pourcentage global de contraintes respectées à partir du dictionnaire
    resultats_contraintes.

    Arguments:
        resultats (dict): mapping catégorie → {"total": int, "respectees": int, ...}

    Retourne:
        float: pourcentage (0-100).
    """
    total_g = 0
    resp_g = 0
    for stats in resultats.values():
        total_g += stats["total"]
        resp_g += stats["respectees"]
    if total_g == 0:
        return 100.0
    return (resp_g / total_g) * 100.0

# Fonction d'affichage du rapport détaillé des contraintes
def afficher_rapport_contraintes(resultats_contraintes):
    """
    Affiche, pour chaque catégorie de contrainte, le nombre de cas vérifiés,
    le nombre de cas respectés, le pourcentage, et les détails des violations.
    
    Arguments:
        resultats_contraintes (dict): mapping catégorie → {"total": int, "respectees": int, "details": list}
    """
    # En-tête du rapport pour la lisibilité
    print("\n##############################")
    print("Rapport de vérification des contraintes")
    print("##############################\n")
    total_global = 0  # Compteur du total global de vérifications
    respect_global = 0  # Compteur du total global de cas respectés

    for categorie, stats in resultats_contraintes.items():
        total = stats["total"]
        resp = stats["respectees"]
        details = stats["details"]
        total_global += total # Mise à jour du total global
        respect_global += resp # Mise à jour du total global

        # Calcul du pourcentage de respect pour chaque catégorie
        taux_cat = (resp / total * 100) if total > 0 else 100.0

        print(f"→ Contrainte '{categorie}':")
        print(f"   • Total de cas vérifiés : {total}")
        print(f"   • Cas respectés         : {resp} ({taux_cat:.1f} %)")
        if total - resp > 0:
            # Affichage des violations
            print(f"   • Violations détectées  : {total - resp}")
        else:
            print("   • Aucune violation détectée")

        if details:
            # Affichage des détails des violations
            print("   Détails :")
            for viol in details:
                print(f"      - {viol}")
        print()
    
    # Calcul et affichage de la synthès globale
    if total_global > 0:
        taux_global = respect_global / total_global * 100
    else:
        taux_global = 100.0
    print("##############################")
    print("Synthèse globale :")
    print(f"   • Total général de vérifications   : {total_global}")
    print(f"   • Total général de cas respectés   : {respect_global} ({taux_global:.1f} %)")
    print("##############################\n")

# Fonction de configuration de la cantine
def configurer_cantine(
    model,
    emploi_du_temps,
    SEMAINES,
    JOURS,
    HEURES,
    CLASSES_BASE,
    CAPACITES_CLASSES,
    config
):
    """
    Applique au modèle :
      1. La lecture des paramètres de cantine (capacité, créneaux, priorités).
      2. Le calcul de l’indice horaire de déjeuner pour chaque classe.
      3. L’interdiction de cours à ces créneaux dans le modèle CP-SAT.

    Arguments :
        model (CpModel)                        : le modèle CP-SAT à enrichir.
        emploi_du_temps (dict)                : variables IntVar matières par créneau.
        SEMAINES (list[str])                  : ["Semaine A","Semaine B"].
        JOURS (list[str])                     : liste des jours.
        HEURES (list[str])                    : liste des créneaux (ex. "12h-13h").
        CLASSES_BASE (list[str])              : classes de base (sans sous-groupes).
        CAPACITES_CLASSES (dict[str,int])     : effectifs par classe de base.
        config (dict)                         : contenu brut du JSON, doit contenir "cantine".

    Retourne :
        dict[str,int] : mapping classe → indice du créneau déjeuner.
    """
    cantine_config     = config.get("cantine", {})
    cap_cantine        = cantine_config.get("capacite", 200)
    ratio_demi         = cantine_config.get("proportion_demi_pensionnaire", 0.8)
    creneaux_dej       = cantine_config.get("creneaux_dejeuner", [])
    assignation_niveaux= cantine_config.get("assignation_niveaux", {})
    priorite_active    = cantine_config.get("priorite_active", True)

    # Vérification que tous les créneaux dejeuner figurent bien dans HEURES 
    for c in creneaux_dej:
        if c not in HEURES:
            raise ValueError(f"Créneau cantine '{c}' non reconnu dans HEURES.")

    # On recherche dynamiquement le créneau principal commençant par "12h"
    lunch_slot = next((slot for slot in HEURES if slot.startswith("12h")), None)
    if lunch_slot is None:
        raise ValueError("Aucun créneau HEURES ne commence par '12h'")
    h_dej = HEURES.index(lunch_slot)

    # Bloquer systématiquement ce créneau pour toutes les classes
    for semaine in SEMAINES:
        for classe in CLASSES:
            for j in range(len(JOURS)):
                model.Add(emploi_du_temps[semaine][(classe, j, h_dej)] == 0)

    # Allocation des créneaux déjeuner selon la capacité de la cantine
    if lunch_slot in creneaux_dej:
        total_eleves = sum(int(CAPACITES_CLASSES.get(cl, 0) * ratio_demi) for cl in CLASSES_BASE)
        if total_eleves <= cap_cantine:
            # Capacité suffisante
            classe_creneau_dej = {cl: h_dej for cl in CLASSES_BASE}
            print(f"✅ Tous les élèves peuvent déjeuner à {lunch_slot} (capacité suffisante)")
        else:
            if not priorite_active:
                # Répartition automatique sans priorité
                from itertools import cycle
                print("🔁 Capacité insuffisante : répartition automatique sans priorité")
                iter_slots = cycle([HEURES.index(c) for c in creneaux_dej])
                classe_creneau_dej = {cl: next(iter_slots) for cl in CLASSES_BASE}
            else:
                # Répartition par priorité de niveaux
                print(f"❌ Capacité insuffisante à {lunch_slot} : assignation par niveau")
                classe_creneau_dej = {}
                for cl in CLASSES_BASE:
                    niv = cl[:2]
                    for slot, niveaux in assignation_niveaux.items():
                        if niv in niveaux:
                            classe_creneau_dej[cl] = HEURES.index(slot)
                            break
                    else:
                        raise ValueError(f"Aucun créneau cantine défini pour le niveau '{niv}' (classe {cl}).")
    else:
        raise ValueError(f"Le créneau principal '{lunch_slot}' doit être inclus dans les créneaux possibles.")

    # 6) Interdire les cours à ces créneaux
    for sem in SEMAINES:
        for cl, h_dej in classe_creneau_dej.items():
            for j in range(len(JOURS)):
                model.Add(emploi_du_temps[sem][(cl, j, h_dej)] == 0)

    return classe_creneau_dej

# Création du modèle et des variables
model, emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs = creer_modele()

# Configuration de la cantine (et blocage des créneaux déjeuner)
classe_creneau_dej = configurer_cantine(
    model,
    emploi_du_temps,
    SEMAINES,
    JOURS,
    HEURES,
    CLASSES_BASE,
    CAPACITES_CLASSES,
    config
)

# Synchronisation des sous-groupes
def synchroniser_sous_groupes(
    model,
    emploi_du_temps,
    SOUS_GROUPES_SUFFIXES,
    CLASSES,
    JOURS,
    HEURES,
    MATIERES
):
    """
    Pour chaque suffixe de sous-groupe, crée des BoolVar indiquant
    si cette matière de sous-groupe est planifiée, puis synchronise
    tous ces BoolVar entre eux (tous ou aucun).

    Arguments :
        model (CpModel)                : votre modèle CP-SAT.
        emploi_du_temps (dict)         : IntVar matières par créneau.
        SOUS_GROUPES_SUFFIXES (dict)   : suffixe → nom de matière.
        CLASSES (list[str])            : toutes les classes (base + sous-groupes).
        JOURS (list[str])              : liste des jours.
        HEURES (list[str])             : liste des créneaux (ex. "8h-9h").
        MATIERES (list[str])           : liste des matières.
    """
    for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
        groupes_matiere = [cls for cls in CLASSES if cls.endswith(suffixe)]
        idx_mat = MATIERES.index(mat_sg) + 1
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                bools = []
                for grp in groupes_matiere:
                    key = (grp, j, h)
                    if key in emploi_du_temps:
                        v = model.NewBoolVar(f"{mat_sg}_{grp}_{j}_{h}")
                        model.Add(emploi_du_temps[key] == idx_mat).OnlyEnforceIf(v)
                        model.Add(emploi_du_temps[key] != idx_mat).OnlyEnforceIf(v.Not())
                        bools.append(v)
                # Synchroniser : si un v est vrai, tous doivent l’être
                for i in range(len(bools)):
                    for k in range(i + 1, len(bools)):
                        model.AddBoolOr([bools[i].Not(), bools[k]])
                        model.AddBoolOr([bools[k].Not(), bools[i]])

# Synchronisation des sous-groupes
synchroniser_sous_groupes(
    model,
    emploi_du_temps,
    SOUS_GROUPES_SUFFIXES,
    CLASSES,
    JOURS,
    HEURES,
    MATIERES
)

def preparer_mappings_affichage(PROFESSEURS, AFFECTATION_MATIERE_SALLE):
    """
    Initialise deux dictionnaires :
      - dictProfs  : pour stocker l’EDT de chaque prof (avec clé "emploiTemps" initialisée à une liste vide)
      - dictSalles : pour stocker l’EDT de chaque salle (avec clé "emploiTemps" initialisée à une liste vide)
    """
    dictProfs = {}
    for mat, nomProf in PROFESSEURS.items():
        if isinstance(nomProf, dict):
            for niv, val in nomProf.items():
                if isinstance(val, list):
                    for prof in val:
                        dictProfs.setdefault(prof, {"matiere": mat, "emploiTemps": []})
                else:
                    dictProfs.setdefault(val,  {"matiere": mat, "emploiTemps": []})
        else:
            dictProfs.setdefault(nomProf, {"matiere": mat, "emploiTemps": []})

    dictSalles = {}
    for salle_entry in AFFECTATION_MATIERE_SALLE.values():
        if isinstance(salle_entry, list):
            for s in salle_entry:
                dictSalles.setdefault(s, {"emploiTemps": []})
        else:
            dictSalles.setdefault(salle_entry, {"emploiTemps": []})

    return dictProfs, dictSalles



# Préparation des mappings pour l'affichage (avant d'utiliser attributProfsCours etc.)
dictProfs, dictSalles = preparer_mappings_affichage(
    PROFESSEURS,
    AFFECTATION_MATIERE_SALLE
)


for prof in dictProfs:
    dictProfs[prof]["emploiTemps"] = [
        [JOURS[i]] + ["---"] * len(HEURES)
        for i in range(len(JOURS))
    ]
for salle in dictSalles:
    dictSalles[salle]["emploiTemps"] = [
        [JOURS[i]] + ["---"] * len(HEURES)
        for i in range(len(JOURS))
    ]

# Fonction pour attribuer l'emploi du temps des professeurs à partir du tableau d'une classe
def attributProfsCours(pTable, pClasse):
    """
    Met à jour dictProfs en ajoutant l'emploi du temps d'un professeur à partir
    du tableau pTable d'une classe donnée.

    Arguments:
        pTable (list): tableau 2D représentant l'emploi du temps d'une classe.
        pClasse (str): nom de la classe correspondante.
    """
    for prof in dictProfs:
        # Initialisation de la table temporaire pour ce professeur
        profTable = []
        # Récupère l'ancien emploi du temps pour fusionner en cas de double appel
        profSecond = dictProfs[prof].get("emploiTemps", [])
        for row_idx in range(len(pTable)):
            row = []
            for col_idx in range(len(pTable[row_idx])):
                if col_idx == 0:
                    # Colonne 0 contient le jour, on l’affiche directement
                    row.append(f"{JOURS[row_idx]}")
                else:
                    cell = pTable[row_idx][col_idx]
                    if cell.find(prof) != -1:
                        # Si la cellule contient le nom du prof, on extrait la salle
                        affichSalle = cell[cell.find("Salle"):]
                        row.append(f"{prof}\n{pClasse}\n[{affichSalle}]")
                    elif profSecond and profSecond[row_idx][col_idx] != "---":
                        # Sinon, on conserve l’ancienne valeur si elle n’est pas vide
                        row.append(profSecond[row_idx][col_idx])
                    else:
                        # Aucun cours → on met un placeholder
                        row.append("---")
            profTable.append(row)
        # Mise à jour de l’emploi du temps du prof dans le dictionnaire global
        dictProfs[prof]["emploiTemps"] = profTable

# Fonction pour afficher l'emploi du temps des professeurs
def affichCoursProfs():
    """
    Affiche l'emploi du temps de chaque professeur stocké dans dictProfs.
    """
    headers = ["Jour/Heure"] + HEURES
    for prof in dictProfs:
        print("Cours pour " + prof)
        # Utilisation de tabulate pour un rendu en grille
        #print(tabulate(dictProfs[prof]["emploiTemps"], headers, tablefmt="grid"))

# Fonction pour attribuer l'emploi du temps des salles à partir du tableau d'une classe
def attributEDTSalles(pTable, pClasse):
    """
    Met à jour dictSalles en ajoutant l'emploi du temps d'une salle à partir
    du tableau pTable d'une classe donnée.

    Arguments:
        pTable (list): tableau 2D représentant l'emploi du temps d'une classe.
        pClasse (str): nom de la classe correspondante.
    """
    for salle in dictSalles:
        # Initialisation de la table temporaire pour cette salle
        salleTable = []
        # Récupère l'ancien emploi du temps pour fusion éventuelle
        salleSecond = dictSalles[salle].get("emploiTemps", [])
        for row_idx in range(len(pTable)):
            row = []
            for col_idx in range(len(pTable[row_idx])):
                if col_idx == 0:
                    # Première colonne → jour
                    row.append(f"{JOURS[row_idx]}")
                else:
                    cell = pTable[row_idx][col_idx]
                    if cell.find(salle) != -1:
                        # Si la cellule contient le nom de la salle, on cherche le prof associé
                        leProf = ""
                        for prof in dictProfs:
                            if cell.find(prof) != -1:
                                leProf = prof
                                break
                        row.append(f"{leProf}\n{pClasse}\n[{salle}]")
                    elif salleSecond and salleSecond[row_idx][col_idx] != "---":
                        # Conserve l’ancien contenu si existant
                        row.append(salleSecond[row_idx][col_idx])
                    else:
                        # Pas de cours → placeholder
                        row.append("---")
            salleTable.append(row)
        # Mise à jour de l’emploi du temps de la salle
        dictSalles[salle]["emploiTemps"] = salleTable

# Fonction pour afficher l'emploi du temps des salles
def affichEDTSalles():
    """
    Affiche l'emploi du temps de chaque salle stocké dans dictSalles.
    """
    headers = ["Jour/Heure"] + HEURES
    for salle in dictSalles:
        print("Cours en " + salle)
        # Affichage en grille via tabulate
        #print(tabulate(dictSalles[salle]["emploiTemps"], headers, tablefmt="grid"))

# Fonction pour fusionner les groupes vers les classes (texte pour affichage)
def fusionner_groupes_vers_classes(emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs, solver, semaine):
    """
    Construit un dictionnaire fusion_data[(classe, j, h)] → string décrivant le contenu
    du créneau pour chaque classe de base et sous-groupe, pour la semaine donnée.
    Identique à la version interne, mais utile pour génération d'EDT final.
    """
    # Initialisation du dictionnaire pour stocker les données fusionnées
    fusion_data = {}

    # 1) D’abord, pour chaque classe de base
    for cl in CLASSES_BASE:
        for j, jour in enumerate(JOURS):
            for h, heure in enumerate(HEURES):
                key = (cl, j, h)
                contenu = []

                # a) Cours de la classe principale
                mat_idx = solver.Value(emploi_du_temps[semaine][key])
                if mat_idx > 0:
                    # Convertir l'index en matière
                    mat = MATIERES[mat_idx - 1]
                    niv = cl[:2]
                    prof_ref = PROFESSEURS[mat]

                    # Choix du prof
                    if isinstance(prof_ref, dict):
                        # Sélection du professeur selon le niveau et variable d'emploi du temps
                        profs_niv = prof_ref.get(niv, [])
                        key_prof = (cl, j, h, mat, semaine)
                        if key_prof in emploi_du_temps_profs[semaine]:
                            prof_sel = profs_niv[solver.Value(emploi_du_temps_profs[semaine][key_prof])]
                        else:
                            prof_sel = profs_niv[0] if profs_niv else prof_ref
                    else:
                        # Professeur est une chaîne unique
                        prof_sel = prof_ref

                    # Choix de la salle
                    salle = (
                        AFFECTATION_MATIERE_SALLE.get(mat)
                        or AFFECTATION_MATIERE_SALLE.get(prof_sel)
                    )
                    idx_salle = solver.Value(emploi_du_temps_salles[semaine][key])
                    if not salle and 0 < idx_salle <= len(SALLES_GENERALES):
                        # Si pas de salle assignée, on utilise la salle générale
                        salle = SALLES_GENERALES[idx_salle - 1]

                    cap_s = CAPACITES_SALLES.get(salle)
                    if cap_s is not None:
                        salle_aff = f"{salle} - {cap_s} places"
                    else:
                        # Si pas de capacité définie, on affiche juste le nom de la salle
                        salle_aff = f"{salle}"
                    contenu.append(f"{mat}\n{prof_sel}\n[{salle_aff}]")

                # b) Sous-groupes de la même classe de base
                for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
                    grp = f"{cl}{suffixe}"
                    if grp in CLASSES:
                        key_sg = (grp, j, h)
                        mat_idx_sg = solver.Value(emploi_du_temps[semaine][key_sg])
                        if mat_idx_sg > 0:
                            # Convertir l'index en matière pour le sous-groupe
                            mat2 = MATIERES[mat_idx_sg - 1]
                            prof_ref2 = PROFESSEURS[mat2]

                            if isinstance(prof_ref2, dict):
                                profs2 = prof_ref2.get(niv, [])
                                key_prof2 = (grp, j, h, mat2, semaine)
                                if key_prof2 in emploi_du_temps_profs[semaine]:
                                    prof2 = profs2[solver.Value(emploi_du_temps_profs[semaine][key_prof2])]
                                else:
                                    prof2 = profs2[0] if profs2 else prof_ref2
                            else:
                                # Professeur est une chaîne unique
                                prof2 = prof_ref2

                            idx_sg = solver.Value(emploi_du_temps_salles[semaine][key_sg])
                            salle2 = (
                                AFFECTATION_MATIERE_SALLE.get(mat2)
                                or AFFECTATION_MATIERE_SALLE.get(prof2)
                            )
                            if not salle2 and 0 < idx_sg <= len(SALLES_GENERALES):
                                salle2 = SALLES_GENERALES[idx_sg - 1]

                            cap_sg = CAPACITES_SALLES.get(salle2)
                            if cap_sg is not None:
                                salle_aff2 = f"{salle2} - {cap_sg} places"
                            else:
                                # Si pas de capacité définie, on affiche juste le nom de la salle
                                salle_aff2 = f"{salle2}"
                            contenu.append(f"{mat2} ({grp})\n{prof2}\n[{salle_aff2}]")

                # Fusion du contenu
                fusion_data[key] = "\n\n".join(contenu) if contenu else "---"

    # 2) Optionnel : traiter chaque sous-groupe indépendamment
    for suffixe, mat_sg in SOUS_GROUPES_SUFFIXES.items():
        for cl_base in CLASSES_BASE:
            grp = f"{cl_base}{suffixe}"
            if grp not in CLASSES:
                continue
            for j, jour in enumerate(JOURS):
                for h, heure in enumerate(HEURES):
                    key_sg = (grp, j, h)
                    contenu_sg = []
                    mat_idx_sg = solver.Value(emploi_du_temps[semaine][key_sg])
                    if mat_idx_sg > 0:
                        # Construction du bloc d'affichage pour le sous-groupe
                        mat2 = MATIERES[mat_idx_sg - 1]
                        prof_ref2 = PROFESSEURS[mat2]

                        if isinstance(prof_ref2, dict):
                            niv_b = cl_base[:2]
                            profs2 = prof_ref2.get(niv_b, [])
                            key_prof2 = (grp, j, h, mat2, semaine)
                            if key_prof2 in emploi_du_temps_profs[semaine]:
                                prof2 = profs2[solver.Value(emploi_du_temps_profs[semaine][key_prof2])]
                            else:
                                prof2 = profs2[0] if profs2 else prof_ref2
                        else:
                            prof2 = prof_ref2

                        idx_s2 = solver.Value(emploi_du_temps_salles[semaine][key_sg])
                        salle2 = (
                            AFFECTATION_MATIERE_SALLE.get(mat2)
                            or AFFECTATION_MATIERE_SALLE.get(prof2)
                        )
                        if not salle2 and 0 < idx_s2 <= len(SALLES_GENERALES):
                            salle2 = SALLES_GENERALES[idx_s2 - 1]
                        cap_s2 = CAPACITES_SALLES.get(salle2)
                        if cap_s2 is not None:
                            salle_aff2 = f"{salle2} - {cap_s2} places"
                        else:
                            salle_aff2 = f"{salle2}"
                        contenu_sg.append(f"{mat2}\n{prof2}\n[{salle_aff2}]")

                    fusion_data[key_sg] = "\n\n".join(contenu_sg) if contenu_sg else "---"

    return fusion_data


def afficher_resultat_si_disponible():
    global fusion_choisie
    if fusion_choisie:
        print("Résultat final :", fusion_choisie)

# Fonction pour choisir la fusion et les résultats correspondant à la meilleure graine
def choisir_run(fusions_par_run, meilleur_seed):
    """
    Sélectionne dans fusions_par_run la fusion et les résultats
    correspondant à la meilleure graine.
    Retourne (fusion_choisie, resultats_choisis).
    """
    fusion_choisie = None
    resultats_choisis = None
    for seed_i, fusion_i, resultats_i in fusions_par_run:
        if seed_i == meilleur_seed:
            fusion_choisie = fusion_i
            resultats_choisis = resultats_i
            break
    if fusion_choisie is None:
        print(f"Aucun run trouvé pour le seed {meilleur_seed}.")
    else:
        print(f"\n--- Emploi du temps pour la meilleure run (seed = {meilleur_seed}) ---\n")
    return fusion_choisie, resultats_choisis



# Fonction pour détecter les salles surchargées
def detecter_salles_surchargees(fusion, CLASSES, SOUS_GROUPES_SUFFIXES,
                                CAPACITES_CLASSES, SALLES_GENERALES,
                                SEMAINES, JOURS, HEURES):
    """
    Parcourt la fusion pour repérer les salles où le nombre total d'élèves
    dépasse la capacité. Renvoie un set de tuples (semaine, j, h, nom_salle).
    """
    from collections import defaultdict
    taille_par_classe = {}
    for cl in CLASSES:
        base = cl
        for sfx in SOUS_GROUPES_SUFFIXES:
            if cl.endswith(sfx):
                base = cl[:-len(sfx)]
                break
        taille_par_classe[cl] = CAPACITES_CLASSES.get(base, 0)

    surchargees = set()
    for sem in SEMAINES:
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                compte = defaultdict(int)
                for cl in CLASSES:
                    contenu = fusion[sem].get((cl, j, h), "")
                    if "[" in contenu and "]" in contenu:
                        salle = contenu.split("[",1)[1].split("]",1)[0].split(" - ")[0].strip()
                        compte[salle] += taille_par_classe[cl]
                for salle, total in compte.items():
                    cap = CAPACITES_CLASSES.get(salle, 0)
                    if total > cap:
                        surchargees.add((sem, j, h, salle))
    return surchargees

# Fonction pour afficher les emplois du temps des élèves
def afficher_edts_elèves(fusion, CLASSES, SEMAINES, JOURS, HEURES):
    """
    Affiche dans la console, pour chaque classe et chaque semaine,
    son emploi du temps sous forme de tableau.
    """
    from tabulate import tabulate
    headers = ["Jour/Heure"] + HEURES
    for sem in SEMAINES:
        print(f"\n=== EMPLOIS DU TEMPS Élèves ({sem}) ===\n")
        for cl in CLASSES:
            print(f"\nClasse {cl} — {sem}")
            table = []
            for j, jour in enumerate(JOURS):
                row = [jour] + [
                    fusion[sem].get((cl, j, h), "---")
                    for h in range(len(HEURES))
                ]
                table.append(row)
            #print(tabulate(table, headers, tablefmt="grid"))

# Fonction pour afficher les emplois du temps des professeurs et des salles
def afficher_edts_profs_salles(fusion, SEMAINES, CLASSES, JOURS, HEURES,
                               dictProfs, dictSalles,
                               attributProfsCours, attributEDTSalles,
                               affichCoursProfs, affichEDTSalles):
    """
    Pour chaque semaine, reconstruit pTable pour chaque classe, met à jour
    dictProfs/dictSalles via attributProfsCours/attributEDTSalles, puis affiche.
    """
    # Remise à zéro
    for prof in dictProfs:
        dictProfs[prof]["emploiTemps"] = []
    for salle in dictSalles:
        dictSalles[salle]["emploiTemps"] = []

    for sem in SEMAINES:
        print(f"\n##### Professeurs — {sem} #####\n")
        for cl in CLASSES:
            pTable = [
                [JOURS[j]] + [
                    fusion[sem].get((cl, j, h), "---") or "---"
                    for h in range(len(HEURES))
                ]
                for j in range(len(JOURS))
            ]
            attributProfsCours(pTable, cl)
            attributEDTSalles(pTable, cl)
        affichCoursProfs()
        print(f"\n##### Salles — {sem} #####\n")
        affichEDTSalles()
        # reset pour la semaine suivante
        for prof in dictProfs:
            dictProfs[prof]["emploiTemps"] = []
        for salle in dictSalles:
            dictSalles[salle]["emploiTemps"] = []

def generer_json_edt(fusion, SEMAINES, CLASSES_BASE, JOURS, HEURES, MATIERES):
    """
    Génère et écrit "emploi_du_temps_global.json" contenant
    edt_classe, edt_prof et edt_salle structurés comme dans l'exemple fourni.
    """
    import json

    # 1. Construire 'edt_classe'
    edt_classe = {}
    for semaine in SEMAINES:
        edt_classe[semaine] = {}
        for cl in CLASSES_BASE:
            edt_classe[semaine][cl] = {}
            for j, jour in enumerate(JOURS):
                edt_classe[semaine][cl][jour] = {}
                for h, heure in enumerate(HEURES):
                    clé = (cl, j, h)
                    contenu = meilleure_fusion[semaine].get(clé, "")
                    if not contenu or contenu.strip() == "---":
                        continue

                    # ne garder que la partie avant "-" (ex. "8h30" à partir de "8h30-9h20")
                    heure_simple = heure.split("-", 1)[0]

                    # extraction des blocs (sous-groupes éventuels)
                    blocs = contenu.split("\n\n")
                    matieres_liste = []
                    profs_liste    = []
                    salles_liste   = []

                    for bloc in blocs:
                        lignes = bloc.split("\n")
                        if len(lignes) < 3:
                            continue
                        mat   = lignes[0].strip()
                        prof  = lignes[1].strip()
                        salle_brute = lignes[2].strip()
                        if salle_brute.startswith("[") and "]" in salle_brute:
                            sauv = salle_brute.lstrip("[").rstrip("]")
                            salle_extr = sauv.split(" -")[0]
                        else:
                            salle_extr = salle_brute.strip("[]")
                        matieres_liste.append(mat)
                        profs_liste.append(prof)
                        salles_liste.append(salle_extr)

                    edt_classe[semaine][cl][jour][heure_simple] = {
                        "matiere":     matieres_liste,
                        "professeurs": profs_liste,
                        "salle":       salles_liste
                    }

    # 2. Construire 'edt_profs'
    edt_profs = {}
    for semaine in SEMAINES:
        edt_profs[semaine] = {}
        # première passe : collecte de tous les profs
        profs_tous = set()
        for (cl, j, h), contenu in meilleure_fusion[semaine].items():
            if not contenu or contenu.strip() == "---":
                continue
            for bloc in contenu.split("\n\n"):
                lignes = bloc.split("\n")
                if len(lignes) < 3:
                    continue
                profs_tous.add(lignes[1].strip())

        for prof in profs_tous:
            edt_profs[semaine][prof] = {jour: {} for jour in JOURS}

        # deuxième passe : remplissage
        for (cl, j, h), contenu in meilleure_fusion[semaine].items():
            if not contenu or contenu.strip() == "---":
                continue
            jour = JOURS[j]
            heure = HEURES[h]

            # ne garder que la partie avant "-" (ex. "8h30")
            heure_simple = heure.split("-", 1)[0]

            for bloc in contenu.split("\n\n"):
                lignes = bloc.split("\n")
                if len(lignes) < 3:
                    continue
                mat         = lignes[0].strip()
                prof        = lignes[1].strip()
                salle_brute = lignes[2].strip()
                if salle_brute.startswith("[") and "]" in salle_brute:
                    sauv       = salle_brute.lstrip("[").rstrip("]")
                    salle_extr = sauv.split(" -")[0]
                else:
                    salle_extr = salle_brute.strip("[]")

                if prof not in edt_profs[semaine]:
                    edt_profs[semaine][prof] = {jour2: {} for jour2 in JOURS}

                edt_profs[semaine][prof][jour][heure_simple] = {
                    "classe":  [cl],
                    "matiere": [mat],
                    "salle":   [salle_extr]
                }


    # 3. Construire 'edt_salles'
    edt_salles = {}
    for semaine in SEMAINES:
        edt_salles[semaine] = {}
        salles_toutes = set()
        for contenu in meilleure_fusion[semaine].values():
            if not contenu or contenu.strip() == "---":
                continue
            for bloc in contenu.split("\n\n"):
                lignes = bloc.split("\n")
                if len(lignes) < 3:
                    continue
                salle_brute = lignes[2].strip()
                if salle_brute.startswith("[") and "]" in salle_brute:
                    sauv       = salle_brute.lstrip("[").rstrip("]")
                    salle_extr = sauv.split(" -")[0]
                else:
                    salle_extr = salle_brute.strip("[]")
                salles_toutes.add(salle_extr)

        for salle_extr in salles_toutes:
            edt_salles[semaine][salle_extr] = {jour: {} for jour in JOURS}

        for (cl, j, h), contenu in meilleure_fusion[semaine].items():
            if not contenu or contenu.strip() == "---":
                continue
            jour  = JOURS[j]
            heure = HEURES[h]

            # ne garder que la partie avant "-" (ex. "8h30")
            heure_simple = heure.split("-", 1)[0]

            for bloc in contenu.split("\n\n"):
                lignes      = bloc.split("\n")
                if len(lignes) < 3:
                    continue
                mat         = lignes[0].strip()
                prof        = lignes[1].strip()
                salle_brute = lignes[2].strip()
                if salle_brute.startswith("[") and "]" in salle_brute:
                    sauv       = salle_brute.lstrip("[").rstrip("]")
                    salle_extr = sauv.split(" -")[0]
                else:
                    salle_extr = salle_brute.strip("[]")

                if salle_extr not in edt_salles[semaine]:
                    edt_salles[semaine][salle_extr] = {jour2: {} for jour2 in JOURS}

                edt_salles[semaine][salle_extr][jour][heure_simple] = {
                    "classe":      [cl],
                    "matiere":     [mat],
                    "professeurs": [prof]
                }

    # 4. Écrire le JSON final
    final_output = {
        "edt_classe": edt_classe,
        "edt_prof":   edt_profs,
        "edt_salle":  edt_salles
    }
    with open("data/emploi_du_temps_global.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

    print("→ Fichier JSON généré : data/emploi_du_temps_global.json")


constraint_status = {
    # Définition du statut (obligatoire/optionnelle) pour chaque type de contrainte
    "volume_horaire":                "obligatoire",
    "indisponibilites_profs":        "optionnelle",
    "jours_sans_apres_midi":         "obligatoire",
    "volume_par_professeur":         "optionnelle",
    "cantine":                       "obligatoire",
    "permanence":                    "optionnelle",
    "poids_cartable":                "optionnelle",
    "indisponibilites_salles":       "optionnelle",
    "double_affectation_salles":     "obligatoire",
    "double_affectation_profs":      "obligatoire",
    "mat_exclu_suite":               "optionnelle",
    "mat_inclu_suite":               "optionnelle",
    "mem_niveau_cours":              "optionnelle",
    "max_heures_par_etendue":        "optionnelle",
    "mat_horaire_donne_v2":          "optionnelle",
    "preferences_salle_professeur":  "optionnelle"
}

# Fonction pour générer le fichier JSON des rapports de contraintes
def generer_json_rapports(fusions_par_run, constraint_status):
    """
    Génère et écrit "tous_rapports_contraintes.json" à partir de fusions_par_run
    et du mapping constraint_status.
    """
    import json
    tous = {}
    for seed_i, _, resultats_i in fusions_par_run:
        statuts = {}
        for cat, stats in resultats_i.items():
            statuts[cat] = {
                "statut": constraint_status.get(cat, "non renseigné"),
                "total": stats["total"],
                "respectees": stats["respectees"],
                "details": stats["details"]
            }
        tous[str(seed_i)] = statuts
    total, resp = 0, 0
    for run in tous.values():
        for s in run.values():
            total += s["total"]; resp += s["respectees"]
    tous["pourcentage_global"] = round((resp/total)*100,2) if total else 100.0
    with open("data/tous_rapports_contraintes.json", "w", encoding="utf-8") as f:
        json.dump(tous, f, ensure_ascii=False, indent=4)
    print(f"→ Tous les rapports écrits (global {tous['pourcentage_global']}%)")

if fusion_choisie:
    surchargees = detecter_salles_surchargees(
        fusion_choisie, CLASSES, SOUS_GROUPES_SUFFIXES,
        CAPACITES_CLASSES, SALLES_GENERALES,
        SEMAINES, JOURS, HEURES
    )
    afficher_edts_elèves(fusion_choisie, CLASSES, SEMAINES, JOURS, HEURES)
    afficher_edts_profs_salles(
        fusion_choisie, SEMAINES, CLASSES, JOURS, HEURES,
        dictProfs, dictSalles,
        attributProfsCours, attributEDTSalles,
        affichCoursProfs, affichEDTSalles
    )
    # (optionnel) afficher surchargees
    generer_json_edt(fusion_choisie, SEMAINES, CLASSES_BASE, JOURS, HEURES, MATIERES)
    generer_json_rapports(fusions_par_run, constraint_status)
    if resultats_choisis:
        afficher_rapport_contraintes(resultats_choisis)


avancement_global = {
    "run_actuel": 0,
    "total_runs": 0,
    "temps_debut": 0,
    "temps_moyen_par_run": 0,
    "temps_estime_restant": 0,
    "meilleur_taux": 0,
    "en_cours": False,
    "termine": False,
    "seed_actuelle": None,
    "taux_actuel": 0,
    "derniere_maj": 0,
    "phase_actuelle": "Initialisation",
    "etape_actuelle": ""
}

def lancer_depuis_interface(nombre_runs):
    global fusions_par_run, taux_par_run, meilleur_seed, meilleure_fusion, meilleur_resultats, fusion_choisie
    global avancement_global
    
    # Initialisation du suivi
    avancement_global.update({
        "run_actuel": 0,
        "total_runs": nombre_runs,
        "temps_debut": time.time(),
        "temps_moyen_par_run": 0,
        "temps_estime_restant": 0,
        "meilleur_taux": 0,
        "en_cours": True,
        "termine": False,
        "seed_actuelle": None,
        "taux_actuel": 0,
        "derniere_maj": time.time(),
        "phase_actuelle": "Préparation",
        "etape_actuelle": "Création du modèle..."
    })

    try:
        # 1) Création du modèle et des emplois du temps
        avancement_global["etape_actuelle"] = "Création du modèle CP-SAT..."
        avancement_global["derniere_maj"] = time.time()
        
        model, emploi_du_temps, emploi_du_temps_salles, emploi_du_temps_profs = creer_modele()
        
        # 2) Exécution des runs avec suivi
        avancement_global["phase_actuelle"] = "Calcul des emplois du temps"
        avancement_global["etape_actuelle"] = f"Lancement de {nombre_runs} runs..."
        avancement_global["derniere_maj"] = time.time()
        
        fusions_par_run, \
        taux_par_run, \
        meilleur_seed, \
        meilleure_fusion, \
        meilleur_resultats = executer_runs_avec_suivi(
            nombre_runs,
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

        # 3) Sélection de la meilleure fusion
        avancement_global["phase_actuelle"] = "Finalisation"
        avancement_global["etape_actuelle"] = "Sélection de la meilleure solution..."
        avancement_global["derniere_maj"] = time.time()
        
        fusion_choisie, resultats_choisis = choisir_run(fusions_par_run, meilleur_seed)

        # 4) Affichage à l'écran + génération des JSON
        if fusion_choisie:
            avancement_global["etape_actuelle"] = "Génération des emplois du temps..."
            avancement_global["derniere_maj"] = time.time()
            
            # a) Affichage des EDT élèves
            afficher_edts_elèves(fusion_choisie, CLASSES, SEMAINES, JOURS, HEURES)

            avancement_global["etape_actuelle"] = "Génération des emplois du temps professeurs..."
            avancement_global["derniere_maj"] = time.time()
            
            # b) Affichage des EDT profs et des salles
            affichCoursProfs()
            affichEDTSalles()

            avancement_global["etape_actuelle"] = "Génération des fichiers JSON..."
            avancement_global["derniere_maj"] = time.time()
            
            # c) Génération du fichier JSON global
            generer_json_edt(fusion_choisie, SEMAINES, CLASSES_BASE, JOURS, HEURES, MATIERES)

            # d) Génération de tous les rapports de contraintes
            generer_json_rapports(fusions_par_run, constraint_status)

            avancement_global["etape_actuelle"] = "Terminé avec succès !"
            print("✅ Emplois du temps générés avec succès !")
        else:
            avancement_global["etape_actuelle"] = "Aucune solution valide trouvée"
            print("❌ Aucune solution valide n'a pu être choisie.")

    except Exception as e:
        avancement_global["etape_actuelle"] = f"Erreur : {str(e)}"
        avancement_global["en_cours"] = False
        avancement_global["termine"] = True
        print(f"❌ Erreur durant le calcul : {e}")
        raise
    
    finally:
        # Finalisation du suivi
        avancement_global["en_cours"] = False
        avancement_global["termine"] = True
        avancement_global["derniere_maj"] = time.time()


def executer_runs_avec_suivi(
    NOMBRE_DE_RUNS,
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
):
    """

    Exécute plusieurs runs d'optimisation d'emploi du temps avec suivi en temps réel.
    
    Met à jour les variables globales pour permettre le suivi en temps réel dans l'interface Dash.
    Cette fonction exécute plusieurs optimisations avec des seeds différents et retourne les résultats
    bruts sans formatage de présentation.
    
    Args:
        NOMBRE_DE_RUNS (int): Nombre total de runs d'optimisation à exécuter
        model: Modèle d'optimisation à utiliser
        emploi_du_temps: Structure de données de l'emploi du temps principal
        emploi_du_temps_salles: Emploi du temps spécifique aux salles
        emploi_du_temps_profs: Emploi du temps spécifique aux professeurs
        JOURS (list): Liste des jours de la semaine
        HEURES (list): Liste des créneaux horaires
        MATIERES (list): Liste des matières enseignées
        PROFESSEURS (list): Liste des professeurs
        SOUS_GROUPES_SUFFIXES (list): Suffixes pour les sous-groupes
        CLASSES (list): Liste de toutes les classes
        CLASSES_BASE (list): Liste des classes de base
        CAPACITES_CLASSES (dict): Capacités d'accueil par classe
        INDISPONIBILITES_PROFS (dict): Indisponibilités des professeurs
        INDISPONIBILITES_SALLES (dict): Indisponibilités des salles
        config (dict): Configuration générale du système
        AFFECTATION_MATIERE_SALLE (dict): Affectation des matières aux salles
        fusionner_groupes_vers_classes (function): Fonction de fusion des groupes
        solve_et_verifie (function): Fonction de résolution et vérification
    
    Returns:
        tuple: Un tuple contenant :
            - fusions_par_run (list): Liste des résultats de fusion pour chaque run réussi
            - taux_par_run (list): Liste des taux de réussite pour chaque run
            - meilleur_seed (int): Seed ayant donné le meilleur résultat
            - meilleure_fusion (dict): Meilleure fusion obtenue
            - meilleur_resultats (dict): Meilleurs résultats détaillés
    
    Side Effects:
        Met à jour la variable globale `avancement_global` avec les informations
        de progression en temps réel (pourcentage, temps estimé, etc.)
    
    Note:
        Cette fonction utilise des variables globales pour le suivi en temps réel
        et est conçue pour être utilisée avec une interface Dash.

    """
    global avancement_global
    
    # Initialisation correcte des variables de suivi
    avancement_global.update({
        "total_runs": NOMBRE_DE_RUNS,
        "run_actuel": 0,
        "en_cours": True,
        "termine": False,
        "temps_debut": time.time(),
        "heure_fin_estimee": None,  
        "phase_actuelle": "calcul",
        "etape_actuelle": "preparation",
        "temps_moyen_par_run": 0,
        "temps_estime_restant": 0,
        "meilleur_taux": 0,
        "taux_actuel": 0,
        "seed_actuelle": None,
        "derniere_maj": time.time()
    })
    
    # Initialisation des variables pour stocker les meilleurs résultats
    meilleur_taux_global = -1.0
    meilleure_fusion = None
    meilleur_seed = None
    meilleur_resultats = None

    # Listes pour stocker les résultats de chaque run
    fusions_par_run = []
    taux_par_run = []

    # Boucle principale sur les runs
    for idx_run, seed in enumerate(range(NOMBRE_DE_RUNS), start=1):
        # Mise à jour AVANT de commencer le run
        avancement_global["run_actuel"] = idx_run
        avancement_global["seed_actuelle"] = seed
        avancement_global["etape_actuelle"] = "en_cours"
        avancement_global["derniere_maj"] = time.time()
        avancement_global["taux_actuel"] = 0
        
        # Marquer le début du run pour le calcul du temps
        debut_run = time.time()
        
        # Appel à la fonction de résolution et vérification
        fusion_par_semaine, taux_i, resultats_i = solve_et_verifie(
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
            seed
        )
        
        # Calcul du temps de ce run
        fin_run = time.time()
        duree_run = fin_run - debut_run

        if fusion_par_semaine is None:
            avancement_global["taux_actuel"] = 0
        else:
            # Si une solution a été trouvée, on stocke les résultats
            fusions_par_run.append((seed, fusion_par_semaine, resultats_i))
            taux_par_run.append((seed, taux_i))
            
            avancement_global["taux_actuel"] = taux_i

            # Mise à jour du meilleur résultat si nécessaire
            if taux_i > meilleur_taux_global:
                meilleur_taux_global = taux_i
                meilleure_fusion = copy.deepcopy(fusion_par_semaine)
                meilleur_seed = seed
                meilleur_resultats = resultats_i
                avancement_global["meilleur_taux"] = taux_i

        # Calcul de l'estimation du temps restant pour plusieurs runs
        if NOMBRE_DE_RUNS > 1:
            elapsed_total = time.time() - avancement_global["temps_debut"]
            runs_effectues = idx_run
            avg_time_per_run = elapsed_total / runs_effectues
            runs_restants = NOMBRE_DE_RUNS - runs_effectues
            est_remaining = avg_time_per_run * runs_restants

            # CORRECTION : Calcul de l'heure de fin SEULEMENT si elle n'existe pas encore
            # ou si l'estimation a significativement changé (pour éviter les fluctuations)
            if (avancement_global["heure_fin_estimee"] is None or 
                abs(est_remaining - avancement_global["temps_estime_restant"]) > 30):  # Plus de 30s de différence
                import datetime
                avancement_global["heure_fin_estimee"] = datetime.datetime.now() + datetime.timedelta(seconds=est_remaining)

            # Mise à jour des statistiques temporelles
            avancement_global["temps_moyen_par_run"] = avg_time_per_run
            avancement_global["temps_estime_restant"] = est_remaining
            avancement_global["derniere_maj"] = time.time()

    # Marquer comme terminé
    avancement_global["termine"] = True
    avancement_global["en_cours"] = False
    avancement_global["etape_actuelle"] = "termine"
    
    return fusions_par_run, taux_par_run, meilleur_seed, meilleure_fusion, meilleur_resultats

def get_avancement_info():
    """
    Récupère les informations d'avancement de l'optimisation en cours.
    
    Cette fonction permet d'obtenir l'état actuel de progression des
    runs d'optimisation depuis l'interface Dash. Elle retourne des données
    brutes.
    
    Returns:
        dict: Dictionnaire contenant les informations d'avancement :
            - pourcentage (int): Pourcentage de progression (0-100)
            - phase (str): Phase actuelle ('attente', 'calcul', 'finalisation')
            - etape (str): Étape détaillée dans la phase
            - run_actuel (int): Numéro du run en cours
            - total_runs (int): Nombre total de runs à effectuer
            - temps_debut (float): Timestamp du début de l'exécution
            - temps_estime_restant (float): Temps estimé restant en secondes
            - heure_fin_estimee (datetime): Heure estimée de fin
            - temps_moyen_par_run (float): Temps moyen par run en secondes
            - meilleur_taux (float): Meilleur taux obtenu jusqu'à présent
            - taux_actuel (float): Taux du run en cours
            - seed_actuelle (int): Seed du run en cours
            - termine (bool): True si l'exécution est terminée
    
    Note:
        Utilise la variable globale `avancement_global` pour récupérer les
        informations de progression en temps réel.
    """
    global avancement_global
    
    if not avancement_global["en_cours"] and not avancement_global["termine"]:
        return {
            "pourcentage": 0,
            "phase": "attente",
            "etape": "pret",
            "run_actuel": 0,
            "total_runs": 0,
            "temps_debut": 0,
            "temps_estime_restant": 0,
            "heure_fin_estimee": None,
            "temps_moyen_par_run": 0,
            "meilleur_taux": 0,
            "taux_actuel": 0,
            "seed_actuelle": None,
            "termine": False
        }
    
    # Calcul du pourcentage global
    if avancement_global["phase_actuelle"] == "preparation":
        pourcentage = 5
    elif avancement_global["phase_actuelle"] == "calcul":
        total_runs = avancement_global["total_runs"]
        run_actuel = avancement_global["run_actuel"]
        
        if total_runs > 0:
            runs_completes = max(0, run_actuel - 1)
            progress_runs = runs_completes / total_runs
            
            if total_runs == 1:
                if avancement_global["temps_debut"] > 0:
                    temps_ecoule = time.time() - avancement_global["temps_debut"]
                    progress_temporelle = min(0.8, temps_ecoule / 120)
                    pourcentage = 5 + (85 * progress_temporelle)
                else:
                    pourcentage = 10
            else:
                pourcentage = 5 + (85 * progress_runs)
        else:
            pourcentage = 10
    elif avancement_global["phase_actuelle"] == "finalisation":
        pourcentage = 95
    else:
        pourcentage = 10
    
    if avancement_global["termine"]:
        pourcentage = 100
    
    return {
        "pourcentage": int(pourcentage),
        "phase": avancement_global["phase_actuelle"],
        "etape": avancement_global["etape_actuelle"],
        "run_actuel": avancement_global["run_actuel"],
        "total_runs": avancement_global["total_runs"],
        "temps_debut": avancement_global["temps_debut"],
        "temps_estime_restant": avancement_global["temps_estime_restant"],
        "heure_fin_estimee": avancement_global["heure_fin_estimee"],
        "temps_moyen_par_run": avancement_global["temps_moyen_par_run"],
        "meilleur_taux": avancement_global["meilleur_taux"],
        "taux_actuel": avancement_global["taux_actuel"],
        "seed_actuelle": avancement_global["seed_actuelle"],
        "termine": avancement_global["termine"]
    }

def reset_avancement():
    """
    Réinitialise les variables de suivi de l'avancement.
    
    Cette fonction remet à zéro toutes les variables globales utilisées pour
    le suivi de la progression des runs d'optimisation. Elle doit être appelée
    avant de démarrer une nouvelle série de runs ou pour nettoyer l'état
    après une exécution terminée.
    
    Side Effects:
        Remet à zéro la variable globale `avancement_global` avec les valeurs
        par défaut pour tous les champs de suivi.
        
    Note:
        Cette fonction est particulièrement utile pour s'assurer que l'interface
        Dash affiche un état propre entre différentes exécutions.
    """
    global avancement_global
    avancement_global.update({
        "run_actuel": 0,
        "total_runs": 0,
        "temps_debut": 0,
        "heure_fin_estimee": None,
        "temps_moyen_par_run": 0,
        "temps_estime_restant": 0,
        "meilleur_taux": 0,
        "en_cours": False,
        "termine": False,
        "seed_actuelle": None,
        "taux_actuel": 0,
        "derniere_maj": 0,
        "phase_actuelle": "initialisation",
        "etape_actuelle": ""
    })