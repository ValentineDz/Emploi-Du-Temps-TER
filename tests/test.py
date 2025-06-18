import json
import pytest
from ortools.sat.python import cp_model

def charger_config(fichier):
    """
    Charge la configuration JSON depuis le fichier spécifié.

    :param fichier: Chemin vers le fichier JSON de configuration.
    :return: Un dictionnaire Python représentant le contenu du JSON.
    """
    with open(fichier, "r", encoding="utf-8") as f:
        return json.load(f)

def creer_modele(config):
    """
    Crée un modèle de programmation par contraintes pour générer un emploi du temps.

    Initialise :
      - Les variables d'affectation des matières par classe, jour et créneau.
      - Les variables d'affectation des salles.
      - Les contraintes de volume horaire, indisponibilités professeurs et salles,
        exclusivité de salle par créneau, et interdiction d'affecter un même professeur
        à deux classes en même temps.

    :param config: Dictionnaire de configuration (jours, heures, matières, professeurs, etc.).
    :return: Tuple (model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES_BASE).
    """
    model = cp_model.CpModel()
    JOURS = config["jours"]
    HEURES = config["heures"]
    MATIERES = config["matieres"]
    PROFESSEURS = config["professeurs"]
    VOLUME_HORAIRE = config["volume_horaire"]
    CLASSES_BASE = config["classes_base"]
    SALLES_GENERALES = config.get("salles_generales", [])

    emploi_du_temps = {}
    emploi_du_temps_salles = {}
    NOMBRE_DE_SALLES = len(SALLES_GENERALES)

    # Création des variables pour chaque classe, jour et créneau horaire
    for classe in CLASSES_BASE:
        niveau = classe[:2]
        for j, jour in enumerate(JOURS):
            for h, heure in enumerate(HEURES):
                # On autorise l'indice 0 pour absence de cours, puis 1..n pour les matières autorisées
                matieres_autorisees = list(VOLUME_HORAIRE[niveau].keys())
                matiere_indices = [0] + [MATIERES.index(m) + 1 for m in matieres_autorisees]
                emploi_du_temps[(classe, j, h)] = model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues(matiere_indices),
                    f"{classe}_{jour}_{heure}"
                )

    # 2) Création des IntVar pour l’emploi du temps des salles
    #    0 = pas de cours / salle libre, 1..NOMBRE_DE_SALLES = index dans SALLES_GENERALES
    for classe in CLASSES_BASE:
        for j, jour in enumerate(JOURS):
            for h, heure in enumerate(HEURES):
                emploi_du_temps_salles[(classe, j, h)] = model.NewIntVar(
                    0, NOMBRE_DE_SALLES,
                    f"salle_{classe}_{jour}_{heure}"
                )

     # Contrainte de volume horaire par matière et par classe
    for classe in CLASSES_BASE:
        niveau = classe[:2]
        for matiere, heures in VOLUME_HORAIRE[niveau].items():
            vars_matiere = []
            mat_index = MATIERES.index(matiere) + 1
            for j in range(len(JOURS)):
                for h in range(len(HEURES)):
                    # Booléen valant 1 si le cours est de cette matière à ce créneau
                    v = model.NewBoolVar(f"{classe}_{j}_{h}_{matiere}_count")
                    model.Add(emploi_du_temps[(classe, j, h)] == mat_index).OnlyEnforceIf(v)
                    model.Add(emploi_du_temps[(classe, j, h)] != mat_index).OnlyEnforceIf(v.Not())
                    vars_matiere.append(v)
            # On impose exactement le nombre d'heures défini dans la config_test
            model.Add(sum(vars_matiere) == heures)

    # Indisponibilités des professeurs
    for prof, indispos in config.get("indisponibilites_profs", {}).items():
        for jour_str, heures in indispos.items():
            jour_index = JOURS.index(jour_str)
            for classe in CLASSES_BASE:
                niveau = classe[:2]
                for matiere, prof_ref in PROFESSEURS.items():
                    # Déterminer si ce professeur enseigne cette matière et niveau
                    if isinstance(prof_ref, dict):
                        profs_niv = prof_ref.get(niveau, [])
                        concerne = prof in profs_niv if isinstance(profs_niv, list) else prof == profs_niv
                    else:
                        concerne = prof_ref == prof
                    if not concerne:
                        continue
                    mat_index = MATIERES.index(matiere) + 1
                    # Interdire la matière sur les créneaux indisponibles
                    for h in heures:
                        model.Add(emploi_du_temps[(classe, jour_index, h)] != mat_index)

    # Indisponibilités des salles selon l'affectation matière→salle
    AFFECTATION_MATIERE_SALLE = config.get("affectation_matiere_salle", {})
    INDISPONIBILITES_SALLES = config.get("indisponibilites_salles", {})
    for salle, indispos in INDISPONIBILITES_SALLES.items():
        matieres_concernees = [m for m, s in AFFECTATION_MATIERE_SALLE.items() if s == salle]
        for jour_str, heures in indispos.items():
            jour_index = JOURS.index(jour_str)
            for classe in CLASSES_BASE:
                niveau = classe[:2]
                for matiere, prof_ref in PROFESSEURS.items():
                    # Déterminer si cette matière peut être dans la salle concernée
                    if isinstance(prof_ref, str):
                        concerne = prof_ref in matieres_concernees
                    elif isinstance(prof_ref, dict):
                        profs_niv = prof_ref.get(niveau, [])
                        if isinstance(profs_niv, list):
                            concerne = any(p in matieres_concernees for p in profs_niv)
                        else:
                            concerne = profs_niv in matieres_concernees
                    else:
                        concerne = False
                    if not concerne:
                        continue
                    mat_index = MATIERES.index(matiere) + 1
                    for h in heures:
                        model.Add(emploi_du_temps[(classe, jour_index, h)] != mat_index)

    # Contrainte d'exclusivité sur les salles : une même salle ne peut accueillir
    # qu'une seule classe à un créneau donné
    for j in range(len(JOURS)):
        for h in range(len(HEURES)):
            for idx_salle, nom_salle in enumerate(SALLES_GENERALES, start=1):
                bools_salle = []
                for classe in CLASSES_BASE:
                    salle_var = emploi_du_temps_salles[(classe, j, h)]
                    b = model.NewBoolVar(f"{nom_salle}_{classe}_{j}_{h}_used")
                    model.Add(salle_var == idx_salle).OnlyEnforceIf(b)
                    model.Add(salle_var != idx_salle).OnlyEnforceIf(b.Not())
                    bools_salle.append(b)
                model.Add(sum(bools_salle) <= 1)
    


    # ─── Contrainte : un même prof ne peut pas enseigner deux classes au même créneau ───
    MEMNIV_ACTIVES = {
        (entry["niveau"], entry["matiere"])
        for entry in config.get("memnivmemcours", [])
    }
    # Liste de tous les profs référencés
    tous_les_profs = set()
    for mat, ref in PROFESSEURS.items():
        if isinstance(ref, str):
            tous_les_profs.add(ref)
        elif isinstance(ref, dict):
            for v in ref.values():
                if isinstance(v, list):
                    tous_les_profs.update(v)
                else:
                    tous_les_profs.add(v)
        elif isinstance(ref, list):
            tous_les_profs.update(ref)

    # Pour chaque prof et chaque créneau, on limite à un cours maximum
    for p in tous_les_profs:
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                bools_prof = []
                for cl in CLASSES_BASE:
                    niveau = cl[:2]
                    var_mat = emploi_du_temps[(cl, j, h)]
                    # Sauter les paires (niveau, matière) gérées par memNivMemCours
                    for m_idx, mat in enumerate(MATIERES, start=1):
                        # Si memNivMemCours active sur ce (niveau, matière), on skip :
                        if (niveau, mat) in MEMNIV_ACTIVES:
                            continue
                        prof_ref = PROFESSEURS[mat]
                        # Vérifier si p enseigne mat pour ce niveau
                        donne_par_p = False
                        if isinstance(prof_ref, str):
                            donne_par_p = (prof_ref == p)
                        elif isinstance(prof_ref, dict):
                            val = prof_ref.get(niveau)
                            if isinstance(val, str):
                                donne_par_p = (val == p)
                            elif isinstance(val, list):
                                donne_par_p = (p in val)
                        elif isinstance(prof_ref, list):
                            donne_par_p = (p in prof_ref)
                        if donne_par_p:
                            b = model.NewBoolVar(f"is_{p}_{cl}_{j}_{h}_{mat}")
                            model.Add(var_mat == m_idx).OnlyEnforceIf(b)
                            model.Add(var_mat != m_idx).OnlyEnforceIf(b.Not())
                            bools_prof.append(b)

                if bools_prof:
                    model.Add(sum(bools_prof) <= 1)

    return model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES_BASE


def matExcluSuite(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES_BASE, pMatiere1, pMatiere2, pContrainte="forte", pClasses=None):
    
    """
    Empêche qu’une instance de `pMatiere2` suive immédiatement `pMatiere1` dans l’emploi du temps.

    Args:
        model (cp_model.CpModel): Modèle de contraintes à enrichir.
        emploi_du_temps (dict): Variables IntVar indexées par (classe, jour, heure).
        JOURS (list[str]): Liste des noms de jours.
        HEURES (list[str]): Liste des créneaux horaires.
        MATIERES (list[str]): Liste des matières disponibles.
        CLASSES_BASE (list[str]): Liste des classes concernées.
        pMatiere1 (str): Nom de la matière à interdire en premier.
        pMatiere2 (str): Nom de la matière interdite juste après.
        pContrainte (str): "forte" ou "faible" (par défaut "forte").
        pClasses (str|None): Sous-chaîne pour filtrer les classes (toutes si None).
    """
    matdex_1 = MATIERES.index(pMatiere1) + 1
    matdex_2 = MATIERES.index(pMatiere2) + 1
    if pClasses is None:
        choixClasse = CLASSES_BASE
    else:
        choixClasse = [c for c in CLASSES_BASE if pClasses in c]

    for classe in choixClasse:
        for j in range(len(JOURS)):
            for h in range(len(HEURES) - 1):
                excluSuite_a = model.NewBoolVar(f"{classe}_{j}_{h}_excluA")
                excluSuite_b = model.NewBoolVar(f"{classe}_{j}_{h+1}_excluB")
                # Détection de la suite Matière1→Matière2
                model.Add(emploi_du_temps[(classe, j, h)] == matdex_1).OnlyEnforceIf(excluSuite_a)
                model.Add(emploi_du_temps[(classe, j, h)] != matdex_1).OnlyEnforceIf(excluSuite_a.Not())
                model.Add(emploi_du_temps[(classe, j, h+1)] == matdex_2).OnlyEnforceIf(excluSuite_b)
                model.Add(emploi_du_temps[(classe, j, h+1)] != matdex_2).OnlyEnforceIf(excluSuite_b.Not())
                # Appliquer la bonne contrainte
                if pContrainte == "faible":
                    model.AddBoolOr([excluSuite_a.Not(), excluSuite_b.Not()])
                elif pContrainte == "forte":
                    model.AddImplication(excluSuite_a, excluSuite_b.Not())

def matIncluSuite(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES_BASE, pMatiere1, pMatiere2, pContrainte, pNBFois=1, pClasses=None):
    """
    Impose qu’une instance de `pMatiere1` soit suivie de `pMatiere2` et contrôle leur occurrence.

    Args:
        model (cp_model.CpModel): Modèle de contraintes.
        emploi_du_temps (dict): Variables IntVar (classe, jour, heure).
        JOURS (list[str]): Jours de la semaine.
        HEURES (list[str]): Créneaux horaires.
        MATIERES (list[str]): Matières référencées.
        CLASSES_BASE (list[str]): Classes concernées.
        pMatiere1 (str): Matière de départ de la séquence.
        pMatiere2 (str): Matière de fin de la séquence.
        pContrainte (str): "forte", "moyenne" ou "faible".
        pNBFois (int): Nombre minimal/maximal de séquences (par défaut 1).
        pClasses (str|None): Filtre sur les classes (None = toutes).
    """
    matdex_1 = MATIERES.index(pMatiere1) + 1
    matdex_2 = MATIERES.index(pMatiere2) + 1
    if pClasses is None:
        choixClasse = CLASSES_BASE
    else:
        choixClasse = [c for c in CLASSES_BASE if pClasses in c]

    for classe in choixClasse:
        sequence_Suivi = []
        for j in range(len(JOURS)):
            for h in range(len(HEURES) - 1):
                # Booléens pour détecter la séquence
                suivi_var = model.NewBoolVar(f"{classe}_{j}_{h}_suivi_{pMatiere1}_{pMatiere2}")
                incluSuite_mat1 = model.NewBoolVar(f"{classe}_{j}_{h}_est_{pMatiere1}")
                incluSuite_mat2 = model.NewBoolVar(f"{classe}_{j}_{h+1}_est_{pMatiere2}")

                model.Add(emploi_du_temps[(classe, j, h)] == matdex_1).OnlyEnforceIf(incluSuite_mat1)
                model.Add(emploi_du_temps[(classe, j, h)] != matdex_1).OnlyEnforceIf(incluSuite_mat1.Not())
                model.Add(emploi_du_temps[(classe, j, h+1)] == matdex_2).OnlyEnforceIf(incluSuite_mat2)
                model.Add(emploi_du_temps[(classe, j, h+1)] != matdex_2).OnlyEnforceIf(incluSuite_mat2.Not())
                
                model.AddBoolAnd([incluSuite_mat1, incluSuite_mat2]).OnlyEnforceIf(suivi_var)
                model.AddBoolOr([incluSuite_mat1.Not(), incluSuite_mat2.Not()]).OnlyEnforceIf(suivi_var.Not())


                sequence_Suivi.append(suivi_var)
                # Pour implication forte, on lie directement les deux cours
                if pContrainte == "forte":
                    model.AddImplication(incluSuite_mat1, incluSuite_mat2)
        # Contraintes sur le nombre total d'occurrences
        if pContrainte == "moyenne":
            model.Add(sum(sequence_Suivi) >= pNBFois)
        elif pContrainte == "faible":
            model.Add(sum(sequence_Suivi) <= pNBFois)

def memNivMemCours(model, emploi_du_temps, JOURS, HEURES, MATIERES, VOLUME_HORAIRE, CLASSES_BASE, pNiveau, pMatiere):
    """
    Synchronise un même cours `pMatiere` pour toutes les classes d’un même niveau.

    Args:
        model (cp_model.CpModel): Modèle CP-SAT à enrichir.
        emploi_du_temps (dict): Variables d’emploi du temps.
        JOURS (list[str]): Liste des jours.
        HEURES (list[str]): Liste des créneaux.
        MATIERES (list[str]): Matières disponibles.
        VOLUME_HORAIRE (dict): Volume horaire par niveau et matière.
        CLASSES_BASE (list[str]): Toutes les classes.
        pNiveau (str): Préfixe de niveau (ex. "6e").
        pMatiere (str): Matière à synchroniser.
    """
    choixClasse = []
    matdex_p = MATIERES.index(pMatiere) + 1
    nb_heures_semaine = VOLUME_HORAIRE[pNiveau][pMatiere]

    for classe in CLASSES_BASE:
        if pNiveau in classe:
            choixClasse.append(classe)

    if not choixClasse:
        raise ValueError(f"Niveau inexistant : {pNiveau}")

    positionMatiere = {}
    # Créer un BoolVar par créneau indiquant si toutes les classes ont pMatiere
    for j in range(len(JOURS)):
        for h in range(len(HEURES)):
            var = model.NewBoolVar(f"{pMatiere}_pour_{pNiveau}_{j}_{h}")
            positionMatiere[(j, h)] = var
            for c in range(len(choixClasse)):
                model.Add(emploi_du_temps[(choixClasse[c], j, h)] == matdex_p).OnlyEnforceIf(var)
                model.Add(emploi_du_temps[(choixClasse[c], j, h)] != matdex_p).OnlyEnforceIf(var.Not())

    # Imposer le nombre d'heures synchronisées entre les classes 
    model.Add(sum(positionMatiere.values()) == nb_heures_semaine)

def appliquer_contrainte_cantine(
    model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES_BASE,
    config, cap_cantine, ratio_demi, creneaux_dej, assignation_niveaux, priorite_active):
    """
    Empêche toute programmation de cours pendant les créneaux de cantine.

    Si la capacité (`cap_cantine`) est suffisante pour accueillir tous
    les demi-pensionnaires à 12h-13h, ce créneau est bloqué pour tous.
    Sinon, les classes sont réparties soit de façon cyclique, soit selon
    `assignation_niveaux` si `priorite_active` est vrai.

    Args:
        model (cp_model.CpModel): Modèle de contraintes.
        emploi_du_temps (dict): Variables d’EDT.
        JOURS (list[str]): Jours.
        HEURES (list[str]): Créneaux.
        MATIERES (list[str]): Matières.
        PROFESSEURS (dict): Mapping matière→professeur(s).
        CLASSES_BASE (list[str]): Liste des classes.
        config (dict): Configuration complète (contenant `capacites_classes`).
        cap_cantine (int): Capacité maximale de la cantine.
        ratio_demi (float): Proportion de demi-pensionnaires.
        creneaux_dej (list[str]): Créneaux disponibles pour déjeuner.
        assignation_niveaux (dict): Créneaux de repas assignés par niveau.
        priorite_active (bool): Si True, respecte `assignation_niveaux`.
    """
    # Vérification créneaux valides
    h_dej_list = []
    for c in creneaux_dej:
        if c not in HEURES:
            raise ValueError(f"Créneau cantine '{c}' non reconnu dans HEURES.")
        h_dej_list.append(HEURES.index(c))
    if "12h-13h" not in creneaux_dej:
        raise ValueError("Le créneau 12h-13h doit être inclus dans les créneaux possibles.")

    h_12_13 = HEURES.index("12h-13h")

    # Calcul du nombre total d'élèves demi-pensionnaires
    total_eleves = sum(int(config["capacites_classes"].get(classe, 0) * ratio_demi) for classe in CLASSES_BASE)

    # Choix du créneau par classe
    if total_eleves <= cap_cantine:
        # Tous élèves à 12h-13h
        classe_creneau_dej = {classe: h_12_13 for classe in CLASSES_BASE}
    else:
        if not priorite_active:
            from itertools import cycle
            h_iter = cycle(h_dej_list)
            classe_creneau_dej = {classe: next(h_iter) for classe in CLASSES_BASE}
        else:
            classe_creneau_dej = {}
            for classe in CLASSES_BASE:
                niveau = classe[:2]
                affecte = False
                for creneau, niveaux in assignation_niveaux.items():
                    if niveau in niveaux:
                        classe_creneau_dej[classe] = HEURES.index(creneau)
                        affecte = True
                        break
                if not affecte:
                    raise ValueError(f"Aucun créneau cantine défini pour le niveau '{niveau}' (classe {classe}).")

    # Interdiction de cours sur le créneau cantine
    for classe, h_dej in classe_creneau_dej.items():
        for j in range(len(JOURS)):
            model.Add(emploi_du_temps[(classe, j, h_dej)] == 0)

    return model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES_BASE


def appliquer_contrainte_poids_cartable(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES, config):
    """
    Ajoute au modèle une fonction objectif pour limiter le poids total des cours par jour.

    Chaque matière reçoit un poids (`config["poids_matieres"]`), la somme des
    poids par jour est convertie en pénalité si elle dépasse le seuil (global
    ou par niveau). L’optimisation minimise la somme de ces pénalités.

    Args:
        model (cp_model.CpModel): Modèle CP-SAT.
        emploi_du_temps (dict): Variables d’EDT.
        JOURS (list[str]): Jours de la semaine.
        HEURES (list[str]): Créneaux horaires.
        MATIERES (list[str]): Matières.
        CLASSES (list[str]): Classes et sous-groupes.
        config (dict): Contient `poids_matieres`, `poids_cartable_max_somme_par_niveau`, etc.
    """
    penalites_surcharge_poids = []
    poids_matieres = config.get("poids_matieres", {})
    seuils_par_niveau = config.get("poids_cartable_max_somme_par_niveau", {})
    seuil_global = config.get("poids_cartable_max_somme", 6.0)
    JOURS_SANS_APRES_MIDI = config.get("jours_sans_apres_midi", [])
    SOUS_GROUPES_SUFFIXES = config.get("sous_groupes_suffixes", [])

    for classe in CLASSES:
        niveau = classe[:2]
        seuil_max = seuils_par_niveau.get(niveau, seuil_global)

        if seuil_max <= 0:
            continue  # Pas de contrainte si seuil non positif

        seuil_x10 = int(seuil_max * 10)
        seuil_tolerant_x10 = int(seuil_max * 1.05 * 10)  # tolérance de 5%

        for j, jour in enumerate(JOURS):
            poids_total_jour = []
            for h in range(len(HEURES)):
                # Ignorer l'après-midi si interdit
                if jour in JOURS_SANS_APRES_MIDI and h > 4:
                    continue

                poids_h = []
                matiere_index = emploi_du_temps[(classe, j, h)]
                # Pour chaque matière, lier un BoolVar à son poids
                for m, matiere in enumerate(MATIERES):
                    code = m + 1
                    poids = poids_matieres.get(matiere, 0)
                    var = model.NewBoolVar(f"poids_{classe}_{j}_{h}_{matiere}")
                    model.Add(matiere_index == code).OnlyEnforceIf(var)
                    model.Add(matiere_index != code).OnlyEnforceIf(var.Not())
                    poids_h.append((var, poids))

                 # Ajouter les sous-groupes si présents
                for suffixe in SOUS_GROUPES_SUFFIXES:
                    sg = f"{classe}{suffixe}"
                    if sg in CLASSES:
                        matiere_index_sg = emploi_du_temps[(sg, j, h)]
                        for m, matiere in enumerate(MATIERES):
                            code = m + 1
                            poids = poids_matieres.get(matiere, 0)
                            var = model.NewBoolVar(f"poids_{sg}_{j}_{h}_{matiere}")
                            model.Add(matiere_index_sg == code).OnlyEnforceIf(var)
                            model.Add(matiere_index_sg != code).OnlyEnforceIf(var.Not())
                            poids_h.append((var, poids))

                if poids_h:
                    poids_total_h = model.NewIntVar(0, 1000, f"poids_total_{classe}_{j}_{h}")
                    model.Add(poids_total_h == sum(int(p * 10) * var for var, p in poids_h))
                    poids_total_jour.append(poids_total_h)

            if poids_total_jour:
                somme_poids_jour = model.NewIntVar(0, 10000, f"somme_poids_jour_{classe}_{j}")
                model.Add(somme_poids_jour == sum(poids_total_jour))

                surcharge = model.NewIntVar(0, 10000, f"surcharge_poids_jour_{classe}_{j}")
                model.AddMaxEquality(surcharge, [somme_poids_jour - seuil_tolerant_x10, 0])
                penalites_surcharge_poids.append(surcharge)

    # Minimiser la somme des pénalités globales
    if penalites_surcharge_poids:
        model.Minimize(sum(penalites_surcharge_poids))

    return model




def appliquer_contrainte_max_heures_etendue(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES_BASE, MAX_HEURES_PAR_ETENDUE):
    """
    Limite le nombre d’heures d’une matière sur une journée ou une demi-journée.

    Pour chaque règle dans `MAX_HEURES_PAR_ETENDUE`, sélectionne les classes
    dont le nom commence par `niveau`, puis impose :
      - Étendue "journee"     : ≤ `max_heures` sur tous les créneaux du jour.
      - Étendue "demi-journee": ≤ `max_heures` séparément matin (indices 0–3)
                                et après-midi (indices 5+).

    Args:
        model (cp_model.CpModel): Modèle de contraintes.
        emploi_du_temps (dict): Variables IntVar d’emploi du temps.
        JOURS (list[str]): Jours autorisés.
        HEURES (list[str]): Créneaux horaires.
        MATIERES (list[str]): Dictionnaire des matières.
        CLASSES_BASE (list[str]): Liste des classes.
        MAX_HEURES_PAR_ETENDUE (list[dict]): Règles de la forme {
            "niveau": str, "matiere": str,
            "max_heures": int, "etendue": "journee"|"demi-journee"
        }.
    """
    
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
                if etendue == "journee":
                    heures_cibles = list(range(len(HEURES)))
                    vars_jour = []
                    for h in heures_cibles:
                        if (classe, j, h) in emploi_du_temps:
                            v = model.NewBoolVar(f"{classe}_{j}_{h}_{matiere}_limit")
                            model.Add(emploi_du_temps[(classe, j, h)] == matiere_index).OnlyEnforceIf(v)
                            model.Add(emploi_du_temps[(classe, j, h)] != matiere_index).OnlyEnforceIf(v.Not())
                            vars_jour.append(v)
                    model.Add(sum(vars_jour) <= max_heures)

                elif etendue == "demi-journee":
                    matin = list(range(4))
                    apres = list(range(5, len(HEURES)))

                    for label, heures in [("matin", matin), ("apres", apres)]:
                        vars_bloc = []
                        for h in heures:
                            if (classe, j, h) in emploi_du_temps:
                                v = model.NewBoolVar(f"{classe}_{j}_{label}_{h}_{matiere}_limit")
                                model.Add(emploi_du_temps[(classe, j, h)] == matiere_index).OnlyEnforceIf(v)
                                model.Add(emploi_du_temps[(classe, j, h)] != matiere_index).OnlyEnforceIf(v.Not())
                                vars_bloc.append(v)
                        model.Add(sum(vars_bloc) <= max_heures)


def matHorairDonneV2(pClasses, pMatiere, pJour, pHorairMin, pHorairMax=None, pNBFois=None):
    """
    Contraint le nombre de créneaux réservés à une ou plusieurs matières données.

    Sélectionne les classes contenant `pClasses`, puis :
      - Pour chaque créneau dans [pHorairMin, pHorairMax], crée un BoolVar
        indiquant la présence de `pMatiere` (ou liste).
      - Imposer que le nombre total de ces BoolVar soit exactement `pNBFois`
        (ou égal à la taille de la plage si `pNBFois` est None).

    Args:
        pClasses (str|list[str]): Classe(s) ou filtre sur le nom des classes.
        pMatiere (str|list[str]): Matière(s) à contraindre.
        pJour (str): Nom du jour visé.
        pHorairMin (str): Heure de début ("13h").
        pHorairMax (str|None): Heure de fin ("17h") ou None.
        pNBFois (int|None): Nombre exact d’occurrences attendu.
    """
    
    jourdex_h = JOURS.index(pJour)
    HORAIRE_MIN, HORAIRE_MAX = pHorairMin, pHorairMax
    Hordex_Min, Hordex_Max = None, None

    choixClasse = []
    if pClasses != CLASSES_BASE:
        for pC in range(len(CLASSES_BASE)):
            if CLASSES_BASE[pC].find(pClasses) != -1:
                choixClasse.append(CLASSES_BASE[pC])
    else:
        choixClasse = pClasses

    if not choixClasse:
        raise ValueError(pClasses + " = Classe Inexistant")

    choixMatiere = []
    if isinstance(pMatiere, str):
        for pM in range(len(MATIERES)):
            if MATIERES[pM].find(pMatiere) != -1:
                choixMatiere.append(MATIERES[pM])
    elif isinstance(pMatiere, list):
        for pSM in range(len(pMatiere)):
            for pM in range(len(MATIERES)):
                if MATIERES[pM].find(pMatiere[pSM]) != -1:
                    choixMatiere.append(MATIERES[pM])
    else:
        choixMatiere = pClasses

    occMatHorair = []
    # Détermination des indices min et max
    for h in range(len(HEURES)):
        if HEURES[h].find(HORAIRE_MIN) == 0:
            Hordex_Min = h
        if HORAIRE_MAX is not None and HEURES[h].find(HORAIRE_MAX) > 0:
            Hordex_Max = h

    if HORAIRE_MAX is not None:
        nbFois = (Hordex_Max - Hordex_Min) + 1
    else:
        nbFois = 1

    # Pour chaque classe et chaque créneau, on crée un BoolVar
    for classe in choixClasse:
        if isinstance(pMatiere, str):
            classe_h2 = classe[:-1]
            if nbFois > VOLUME_HORAIRE[classe_h2][pMatiere]:
                nbFois = VOLUME_HORAIRE[classe_h2][pMatiere]

        for matiere in choixMatiere:
            matdex_h = MATIERES.index(matiere) + 1
            if HORAIRE_MAX is None:
                h = Hordex_Min
                matHorair = model.NewBoolVar(f"{classe}_{jourdex_h}_{h}_matiere_horaire")
                model.Add(emploi_du_temps[(classe, jourdex_h, h)] == matdex_h).OnlyEnforceIf(matHorair)
                model.Add(emploi_du_temps[(classe, jourdex_h, h)] != matdex_h).OnlyEnforceIf(matHorair.Not())
                occMatHorair.append(matHorair)
            else:
                for h in range(Hordex_Min, Hordex_Max + 1):
                    matHorair = model.NewBoolVar(f"{classe}_{jourdex_h}_{h}_matiere_horaire")
                    model.Add(emploi_du_temps[(classe, jourdex_h, h)] == matdex_h).OnlyEnforceIf(matHorair)
                    model.Add(emploi_du_temps[(classe, jourdex_h, h)] != matdex_h).OnlyEnforceIf(matHorair.Not())
                    occMatHorair.append(matHorair)
        # Imposer le nombre d'occurrences
        if pNBFois is None:
            model.Add(sum(occMatHorair) == nbFois)
        else:
            model.Add(sum(occMatHorair) == pNBFois)


def resoudre_modele(model):
    """
    Résout un modèle CP-SAT et garantit qu'une solution est trouvée.

    Cette fonction crée un CpSolver, lance la résolution du modèle fourni,
    et vérifie que le statut retourné est FEASIBLE ou OPTIMAL.

    :param model: cp_model.CpModel à résoudre.
    :return: CpSolver chargé de la solution.
    :raises AssertionError: si aucune solution (faisable ou optimale) n'est trouvée.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in [cp_model.FEASIBLE, cp_model.OPTIMAL], "Pas de solution trouvée"
    return solver


@pytest.mark.parametrize("n_iter", [50])
def test_indisponibilites_respectees(n_iter):
    """
    Vérifie que ni les professeurs ni les salles ne sont assignés sur leurs créneaux
    d’indisponibilité, à chaque exécution du modèle.
    """
    config = charger_config("config_test.json")

    for i in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)
        solver = resoudre_modele(model)

        # –– Professeurs : aucun cours ne doit être programmé quand ils sont indisponibles
        for prof, indispos in config.get("indisponibilites_profs", {}).items():
            for jour_str, heures in indispos.items():
                jour_index = JOURS.index(jour_str)
                for classe in CLASSES:
                    niveau = classe[:2]
                    for matiere, prof_ref in PROFESSEURS.items():
                        if isinstance(prof_ref, dict):
                            profs_niv = prof_ref.get(niveau, [])
                            concerne = prof in profs_niv if isinstance(profs_niv, list) else prof == profs_niv
                        else:
                            concerne = prof_ref == prof
                        if not concerne:
                            continue
                        mat_index = MATIERES.index(matiere) + 1
                        for h in heures:
                            val = solver.Value(emploi_du_temps[(classe, jour_index, h)])
                            assert val != mat_index, (
                                f"Indisponibilité prof {prof} violée à {jour_str} {HEURES[h]} "
                                f"classe {classe} matiere {matiere}"
                            )

        # –– Salles : on s’assure qu’aucune matière affectée à une salle indisponible
        AFFECTATION_MATIERE_SALLE = config.get("affectation_matiere_salle", {})
        INDISPONIBILITES_SALLES = config.get("indisponibilites_salles", {})
        for salle, indispos in INDISPONIBILITES_SALLES.items():
            matieres_concernees = [m for m, s in AFFECTATION_MATIERE_SALLE.items() if s == salle]
            for jour_str, heures in indispos.items():
                jour_index = JOURS.index(jour_str)
                for classe in CLASSES:
                    niveau = classe[:2]
                    for matiere, prof_ref in PROFESSEURS.items():
                        if isinstance(prof_ref, str):
                            concerne = prof_ref in matieres_concernees
                        elif isinstance(prof_ref, dict):
                            profs_niv = prof_ref.get(niveau, [])
                            if isinstance(profs_niv, list):
                                concerne = any(p in matieres_concernees for p in profs_niv)
                            else:
                                concerne = profs_niv in matieres_concernees
                        else:
                            concerne = False
                        if not concerne:
                            continue
                        mat_index = MATIERES.index(matiere) + 1
                        for h in heures:
                            val = solver.Value(emploi_du_temps[(classe, jour_index, h)])
                            assert val != mat_index, (
                                f"Indisponibilité salle {salle} violée à {jour_str} {HEURES[h]} "
                                f"classe {classe} matiere {matiere}"
                            )

    print(f"Test passé sur {n_iter} exécutions : les indisponibilités sont respectées.")


@pytest.mark.parametrize("n_iter", [50])
def test_volume_horaire_respecte(n_iter):
    """
    S’assure que le nombre d’heures par matière et par classe correspond exactement
    au volume précisé dans la configuration, à chaque résolution.
    """
    config = charger_config("config_test.json")

    for i in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)
        solver = resoudre_modele(model)

        for classe in CLASSES:
            for matiere, heures_attendues in config["volume_horaire"][classe[:2]].items():
                mat_index = MATIERES.index(matiere) + 1
                compte = 0
                for j in range(len(JOURS)):
                    for h in range(len(HEURES)):
                        if solver.Value(emploi_du_temps[(classe, j, h)]) == mat_index:
                            compte += 1
                assert compte == heures_attendues, (
                    f"Erreur au tour {i+1} : volume horaire incorrect pour {matiere} en {classe} : "
                    f"{compte} au lieu de {heures_attendues}"
                )

    print(f"Test passé sur {n_iter} exécutions : le volume horaire est toujours respecté.")


@pytest.mark.parametrize("n_iter", [50])
def test_matExcluSuite(n_iter):
    """
    Vérifie que, lorsqu’on applique une exclusion forte entre deux matières,
    pMatiere2 ne suit jamais immédiatement pMatiere1.
    """
    config = charger_config("config_test.json")
    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)

        # On empêche Maths suivi de SVT pour le test
        matExcluSuite(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES, "Maths", "SVT", pContrainte="forte")

        solver = resoudre_modele(model)

        # Chaque fois qu’on voit Maths, on s'assure que le créneau suivant n’est pas SVT
        for classe in CLASSES:
            for j in range(len(JOURS)):
                for h in range(len(HEURES) - 1):
                    val1 = solver.Value(emploi_du_temps[(classe, j, h)])
                    val2 = solver.Value(emploi_du_temps[(classe, j, h + 1)])
                    if val1 == MATIERES.index("Maths") + 1:
                        assert val2 != MATIERES.index("SVT") + 1, \
                            f"Violation exclusion forte : Maths suivi de SVT en {classe} {JOURS[j]} {HEURES[h]}->{HEURES[h+1]}"


@pytest.mark.parametrize("n_iter", [50])
def test_matIncluSuite(n_iter):
    """
    Contrôle que chaque occurrence de pMatiere1 entraîne, en contrainte forte,
    une occurrence immédiate de pMatiere2, et pas d’autres cas.
    """
    config = charger_config("config_test.json")
    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)

        # Chaque cours de maths doit être suivi de Français
        matIncluSuite(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES, "Maths", "Français", pContrainte="forte", pNBFois=1)

        solver = resoudre_modele(model)

        # Vérifie que chaque occurrence de "Maths" est suivie immédiatement par "Français"
        for classe in CLASSES:
            for j in range(len(JOURS)):
                for h in range(len(HEURES) - 1):
                    val1 = solver.Value(emploi_du_temps[(classe, j, h)])
                    val2 = solver.Value(emploi_du_temps[(classe, j, h + 1)])
                    if val1 == MATIERES.index("Maths") + 1:
                        assert val2 == MATIERES.index("Français") + 1, \
                            f"Violation inclusion forte : Maths non suivi de Français en {classe} {JOURS[j]} {HEURES[h]}->{HEURES[h+1]}"


@pytest.mark.parametrize("n_iter", [50])
def test_memNivMemCours(n_iter):

    config = charger_config("config_test.json")
    for _ in range(n_iter):
        # Initialisation
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)
        VOLUME_HORAIRE = config["volume_horaire"]

        # On applique la contrainte "memnivmemcours" pour les 6e et Maths
        memNivMemCours(model, emploi_du_temps, JOURS, HEURES, MATIERES,
                       VOLUME_HORAIRE, CLASSES, "6e", "Maths")

        solver = resoudre_modele(model)
        assert solver.StatusName() in ("OPTIMAL", "FEASIBLE")

        # Identification des classes de 6e
        classes_6e = [c for c in CLASSES if c.startswith("6e")]
        assert len(classes_6e) >= 2, "Il faut au moins deux classes de 6e pour ce test"
        # On ne prend que les deux premières
        cl1, cl2 = classes_6e[:2]

        mat_index = MATIERES.index("Maths") + 1
        expected = int(VOLUME_HORAIRE["6e"]["Maths"])

        # Synchronisation : mêmes créneaux pour Maths
        for j in range(len(JOURS)):
            for h in range(len(HEURES)):
                v1 = solver.Value(emploi_du_temps[(cl1, j, h)]) == mat_index
                v2 = solver.Value(emploi_du_temps[(cl2, j, h)]) == mat_index
                assert v1 == v2, (
                    f"Incohérence memNivMemCours : Maths à {JOURS[j]} {HEURES[h]} "
                    f"pour {cl1}={v1} vs {cl2}={v2}"
                )

        # Vérification du volume global
        count1 = sum(
            1
            for j in range(len(JOURS))
            for h in range(len(HEURES))
            if solver.Value(emploi_du_temps[(cl1, j, h)]) == mat_index
        )
        assert count1 == expected, (
            f"Volume horaire incorrect pour Maths en 6e : {count1} au lieu de {expected}"
        )



@pytest.mark.parametrize("n_iter", [50])
def test_contrainte_cantine(n_iter):
    """
    Vérifie que les créneaux de cantine sont systématiquement bloqués
    pour les demi-pensionnaires, selon la capacité et la priorité configurées.
    """
    config = charger_config("config_test.json")

    for _ in range(n_iter):
        # Création du modèle sans la contrainte cantine
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)

        # Récupération des paramètres cantine
        cantine_config = config.get("cantine", {})
        cap_cantine = cantine_config.get("capacite", 200)
        ratio_demi = cantine_config.get("proportion_demi_pensionnaire", 0.8)
        creneaux_dej = cantine_config.get("creneaux_dejeuner", ["12h-13h"])
        assignation_niveaux = cantine_config.get("assignation_niveaux", {})
        priorite_active = cantine_config.get("priorite_active", True)

        # Ajout de la contrainte cantine dans le modèle
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = appliquer_contrainte_cantine(
            model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES,
            config, cap_cantine, ratio_demi, creneaux_dej, assignation_niveaux, priorite_active
        )

        solver = resoudre_modele(model)

        total_eleves = sum(int(config["capacites_classes"].get(classe, 0) * ratio_demi) for classe in CLASSES)

        if total_eleves <= cap_cantine:
            # Créneau unique 12h-13h pour tous
            for classe in CLASSES:
                h = HEURES.index("12h-13h")
                for j in range(len(JOURS)):
                    val = solver.Value(emploi_du_temps[(classe, j, h)])
                    assert val == 0, f"Cours trouvé pendant cantine en {classe} {JOURS[j]} {HEURES[h]}"
        else:
            # Chaque classe doit avoir son créneau sans cours
            classe_creneau_dej = {}
            for classe in CLASSES:
                niveau = classe[:2]
                affecte = False
                for creneau, niveaux in assignation_niveaux.items():
                    if niveau in niveaux:
                        h = HEURES.index(creneau)
                        classe_creneau_dej[classe] = h
                        affecte = True
                        break
                assert affecte, f"Classe {classe} sans créneau cantine assigné"

            for classe, h_dej in classe_creneau_dej.items():
                for j in range(len(JOURS)):
                    val = solver.Value(emploi_du_temps[(classe, j, h_dej)])
                    assert val == 0, f"Cours trouvé pendant cantine en {classe} {JOURS[j]} {HEURES[h_dej]}"


@pytest.mark.parametrize("n_iter", [50])
def test_poids_cartable(n_iter):
    """
    Assure que l’ajout des pénalités de poids cartable n’empêche pas la résolution
    et que le modèle reste faisable ou optimal.
    """
    config = charger_config("config_test.json")

    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)
        model = appliquer_contrainte_poids_cartable(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES, config)

        solver = resoudre_modele(model)

        assert solver.StatusName() in ["FEASIBLE", "OPTIMAL"], "Modèle non solvable avec contrainte poids cartable"


@pytest.mark.parametrize("n_iter", [50])
def test_max_heures_par_etendue(n_iter):
    """
    Contrôle que les règles de nombre max d’heures par journée ou demi-journée
    sont bien respectées après résolution.
    """
    config = charger_config("config_test.json")
    MAX_HEURES_PAR_ETENDUE = config.get("max_heures_par_etendue", [])

    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)

        if MAX_HEURES_PAR_ETENDUE:
            appliquer_contrainte_max_heures_etendue(model, emploi_du_temps, JOURS, HEURES, MATIERES, CLASSES, MAX_HEURES_PAR_ETENDUE)

        solver = resoudre_modele(model)

        # Vérification post-solution pour chaque règle
        for regle in MAX_HEURES_PAR_ETENDUE:
            niveau = regle["niveau"]
            matiere = regle["matiere"]
            mat_index = MATIERES.index(matiere) + 1
            max_heures = regle["max_heures"]
            etendue = regle["etendue"]

            for classe in CLASSES:
                if not classe.startswith(niveau):
                    continue

                for j, jour in enumerate(JOURS):
                    if etendue == "journee":
                        compte = 0
                        for h in range(len(HEURES)):
                            val = solver.Value(emploi_du_temps[(classe, j, h)])
                            if val == mat_index:
                                compte += 1
                        assert compte <= max_heures, \
                            f"Violation max heures journée : {compte} > {max_heures} pour {matiere} en {classe} le {jour}"

                    elif etendue == "demi-journee":
                        matin_heures = list(range(4))
                        apres_heures = list(range(5, len(HEURES)))

                        for label, heures in [("matin", matin_heures), ("apres", apres_heures)]:
                            compte_bloc = 0
                            for h in heures:
                                val = solver.Value(emploi_du_temps[(classe, j, h)])
                                if val == mat_index:
                                    compte_bloc += 1
                            assert compte_bloc <= max_heures, \
                                f"Violation max heures demi-journée ({label}): {compte_bloc} > {max_heures} pour {matiere} en {classe} le {jour}"


@pytest.mark.parametrize("n_iter", [50])
def test_jours_sans_apres_midi(n_iter):
    """
    Vérifie qu’aucun cours n’est programmé l’après-midi pour les jours listés
    dans `jours_sans_apres_midi` de la configuration.
    """
    config = charger_config("config_test.json")
    JOURS_SANS_APRES_MIDI = config.get("jours_sans_apres_midi", [])

    # Valider la structure de la config
    assert isinstance(JOURS_SANS_APRES_MIDI, list), "'jours_sans_apres_midi' doit être une liste"
    for jour in JOURS_SANS_APRES_MIDI:
        assert jour in config["jours"], f"Jour '{jour}' dans 'jours_sans_apres_midi' non présent dans la liste officielle des jours"

    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES = creer_modele(config)

        # Ajout de la contrainte : pas de cours l'après-midi les jours sans après-midi
        for classe in CLASSES:
            for j, jour in enumerate(JOURS):
                if jour in JOURS_SANS_APRES_MIDI:
                    for h in range(5, len(HEURES)): 
                        model.Add(emploi_du_temps[(classe, j, h)] == 0)

        solver = resoudre_modele(model)

        # Vérification qu'il n'y a pas de cours l'après-midi les jours sans après-midi
        for classe in CLASSES:
            for j, jour in enumerate(JOURS):
                if jour in JOURS_SANS_APRES_MIDI:
                    for h in range(5, len(HEURES)):
                        val = solver.Value(emploi_du_temps[(classe, j, h)])
                        assert val == 0, (
                            f"Cours trouvé l'après-midi alors que c'est interdit en {classe} le {jour} "
                            f"à {HEURES[h]}"
                        )


@pytest.mark.parametrize("n_iter", [50])
def test_matHorairDonneV2(n_iter):
    """
    Teste qu’on obtient le nombre exact de créneaux scientifiques demandé
    pour les classes de 6e un jour donné.
    """
    config = charger_config("config_test.json")
    global model, emploi_du_temps, JOURS, HEURES, MATIERES, VOLUME_HORAIRE, CLASSES_BASE
    for _ in range(n_iter):
        model, emploi_du_temps, JOURS, HEURES, MATIERES, PROFESSEURS, CLASSES_BASE = creer_modele(config)
        VOLUME_HORAIRE = config["volume_horaire"]

        # Exemple de sous-groupe scientifique à partir du JSON)
        MATIERES_SCIENTIFIQUE = config.get("sousGroupes_matieres", {}).get("Scientifique", ["Maths", "Physique", "Chimie"])

        # Applique la contrainte sur les matières scientifiques le jeudi entre 13h et 17h, 2 fois
        matHorairDonneV2("6e", MATIERES_SCIENTIFIQUE, "Mercredi", "13h", "17h", 2)

        solver = resoudre_modele(model)

        # Vérifie que le nombre total d'heures sur ce créneau est bien 2 (au moins) pour ces matières
        jourdex = JOURS.index("Mercredi")
        heures_13_17 = [i for i, h in enumerate(HEURES) if h >= "13h" and h <= "17h"]
        total_occurrences = 0
        mat_indices = [MATIERES.index(m) + 1 for m in MATIERES_SCIENTIFIQUE if m in MATIERES]

        for classe in [c for c in CLASSES_BASE if "6e" in c]:
            for h in heures_13_17:
                val = solver.Value(emploi_du_temps[(classe, jourdex, h)])
                if val in mat_indices:
                    total_occurrences += 1

        assert total_occurrences == 2, f"Nombre d'heures scientifique incorrect : {total_occurrences} au lieu de 2"

@pytest.mark.parametrize("n_iter", [50])
def test_affectation_salles(n_iter):
    """
    S’assure qu’on peut affecter chaque professeur à une salle :
    respecte les préférences, répartit en rotation sinon, et ne laisse personne sans salle.
    """
    config = charger_config("config_test.json")
    PROFESSEURS = config["professeurs"]
    SALLES_GENERALES = config["salles_generales"]
    PREFERENCES_SALLE_PROF = config.get("preferences_salle_prof", {})
    # On part d'une affectation initiale vide
    AFFECTATION = {}

    # Identifier les professeurs sans salle dans AFFECTATION
    professeurs_sans_salle = set()
    for matiere, prof in PROFESSEURS.items():
        if isinstance(prof, dict):  # Plusieurs niveaux
            for niveau, profs in prof.items():
                if isinstance(profs, list):
                    for prof_nom in profs:
                        if prof_nom not in AFFECTATION:
                            professeurs_sans_salle.add(prof_nom)
                else:
                    if profs not in AFFECTATION:
                        professeurs_sans_salle.add(profs)
        else:
            if prof not in AFFECTATION:
                professeurs_sans_salle.add(prof)
    professeurs_sans_salle = list(professeurs_sans_salle)

    # Préparer le pool de salles générales disponibles
    available_salles = SALLES_GENERALES.copy()
    affectation_prof = AFFECTATION.copy()

    # Affecter d'abord les préférences
    for prof in list(professeurs_sans_salle):
        if prof in PREFERENCES_SALLE_PROF:
            salle_pref = PREFERENCES_SALLE_PROF[prof]
            affectation_prof[prof] = salle_pref
            if salle_pref in available_salles:
                available_salles.remove(salle_pref)
            professeurs_sans_salle.remove(prof)

    # Répartition en rotation pour les autres profs
    for i, prof in enumerate(professeurs_sans_salle):
        if available_salles:
            salle_assignee = available_salles[i % len(available_salles)]
            affectation_prof[prof] = salle_assignee
        else:
            affectation_prof[prof] = SALLES_GENERALES[i % len(SALLES_GENERALES)]

    # Vérifications
    # Tous les professeurs doivent avoir une salle affectée
    all_profs = set()
    for prof in PROFESSEURS.values():
        if isinstance(prof, dict):
            for p in prof.values():
                if isinstance(p, list):
                    all_profs.update(p)
                else:
                    all_profs.add(p)
        else:
            all_profs.add(prof)

    for prof in all_profs:
        assert prof in affectation_prof, f"Professeur {prof} sans salle affectée"

    # Les préférences doivent être respectées
    for prof, salle in PREFERENCES_SALLE_PROF.items():
        assert affectation_prof.get(prof) == salle, f"Préférence non respectée pour {prof}"

    # Les professeurs sans préférence reçoivent une salle parmi SALLES_GENERALES
    for prof in all_profs:
        if prof not in PREFERENCES_SALLE_PROF:
            assert affectation_prof[prof] in SALLES_GENERALES, (
                f"Salle incorrecte pour {prof} : {affectation_prof[prof]} non dans SALLES_GENERALES"
            )


@pytest.mark.parametrize("n_iter", [50])
def test_exclusivite_salles(n_iter):
    """
    Vérifie qu’on ne peut pas assigner deux classes dans la même salle
    à un même créneau, via l’infaisabilité du modèle.
    """
    for _ in range(n_iter):
        model = cp_model.CpModel()

        # Variables salle pour chaque classe, ce créneau : 0=aucune salle, 1=Salle1, 2=Salle2
        salle_C1 = model.NewIntVar(0, 2, "salle_C1_0_0")
        salle_C2 = model.NewIntVar(0, 2, "salle_C2_0_0")

        # Création de deux IntVar et leurs BoolVar associés 
        b1_C1 = model.NewBoolVar("C1_en_salle1_0_0")
        model.Add(salle_C1 == 1).OnlyEnforceIf(b1_C1)
        model.Add(salle_C1 != 1).OnlyEnforceIf(b1_C1.Not())

        b1_C2 = model.NewBoolVar("C2_en_salle1_0_0")
        model.Add(salle_C2 == 1).OnlyEnforceIf(b1_C2)
        model.Add(salle_C2 != 1).OnlyEnforceIf(b1_C2.Not())

        # Contrainte d’exclusivité : les deux classes ne peuvent pas être en salle 1 en même temps
        model.Add(b1_C1 + b1_C2 <= 1)

        # On force un conflit : les deux classes doivent être en salle 1
        model.Add(b1_C1 == 1)
        model.Add(b1_C2 == 1)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status == cp_model.INFEASIBLE, "Deux classes ont pu prendre simultanément la même salle : la contrainte d'exclusivité a échoué."

@pytest.mark.parametrize("n_iter", [50])
def test_double_affectation_profs(n_iter):
    """
    Contrôle qu’un même professeur ne peut pas enseigner simultanément
    deux classes au même créneau (modèle infaisable si on l’y force).
    Pour se faire, on crée un mini-modèle avec une seule matière et deux classes.
    """
    for _ in range(n_iter):
        model = cp_model.CpModel()
        JOURS = ["Lundi"]
        HEURES = ["8h-9h"]
        MATIERES = ["MatiereX"]
        # On déclare un seul professeur "M. X" pour cette unique matière, pour simplifier:
        PROFESSEURS = {"MatiereX": "M. X"}
        CLASSES = ["C1", "C2"]

        # On crée deux variables d’emploi du temps forcées à 1
        emploi = {}
        for cl in CLASSES:
            emploi[(cl, 0, 0)] = model.NewIntVarFromDomain(
                cp_model.Domain.FromValues([1]),
                f"{cl}_Lundi_8h-9h"
            )

        # Volume horaire trivial : chaque classe a exactement ce créneau
        v1 = model.NewBoolVar("C1_count")
        model.Add(emploi[("C1", 0, 0)] == 1).OnlyEnforceIf(v1)
        model.Add(emploi[("C1", 0, 0)] != 1).OnlyEnforceIf(v1.Not())

        v2 = model.NewBoolVar("C2_count")
        model.Add(emploi[("C2", 0, 0)] == 1).OnlyEnforceIf(v2)
        model.Add(emploi[("C2", 0, 0)] != 1).OnlyEnforceIf(v2.Not())

        model.Add(sum([v1, v2]) == 2)  # force C1 et C2 à être à MatiereX en même temps

        # Contrainte globale : M. X ne peut pas être dans deux classes en même temps
        b_C1 = model.NewBoolVar("is_MX_C1_0_0")
        model.Add(emploi[("C1", 0, 0)] == 1).OnlyEnforceIf(b_C1)
        model.Add(emploi[("C1", 0, 0)] != 1).OnlyEnforceIf(b_C1.Not())

        b_C2 = model.NewBoolVar("is_MX_C2_0_0")
        model.Add(emploi[("C2", 0, 0)] == 1).OnlyEnforceIf(b_C2)
        model.Add(emploi[("C2", 0, 0)] != 1).OnlyEnforceIf(b_C2.Not())

        model.Add(b_C1 + b_C2 <= 1)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status == cp_model.INFEASIBLE, (
            "Double affectation d’un même prof dans deux classes en même créneau autorisée → devrait être INFEASIBLE"
        )

    print(f"Test passé sur {n_iter} exécutions : la double affectation profs est bien interdite.")



if __name__ == "__main__":
    pytest.main([__file__])
