from ortools.sat.python import cp_model
import csv
import random
from tabulate import tabulate

# 1) LECTURE DES CSV
# ==================

# Lecture du volume horaire (par niveau et matière)
volume_horaire = {}
with open("volume_horaire.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # On lit les en-têtes : Niveau, Matiere, Heures
    for row in reader:
        niveau = row["Niveau"]       # ex. "6e"
        matiere = row["Matiere"]     # ex. "Maths"
        heures = int(row["Heures"])  # ex. 5

        if niveau not in volume_horaire:
            volume_horaire[niveau] = {}
        volume_horaire[niveau][matiere] = heures

# Lecture des profs (un prof par matière/niveau, ou "*" pour tous les niveaux)
profs = {}
with open("profs.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # Colonnes : Matiere, Niveau, Professeur
    for row in reader:
        matiere = row["Matiere"]       # ex: "Maths"
        niveau = row["Niveau"]         # ex: "6e" ou "*"
        professeur = row["Professeur"] # ex: "M. Dupont"

        if matiere not in profs:
            profs[matiere] = {}

        if niveau == "*":
            profs[matiere]["defaut"] = professeur
        else:
            profs[matiere][niveau] = professeur

# 2) AUTRES CONSTANTES
# ====================
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
HEURES = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h"]

# On conserve la liste de toutes les matières pour l'indexation
# (si tu veux qu'elle soit aussi dynamique, tu pourrais la lire d'un CSV).
MATIERES = [
    "Maths", "Français", "Histoire", "SVT", "Anglais",
    "Physique", "Techno", "EPS", "Arts Plastiques", "Musique"
]

NIVEAUX = ["6e", "5e", "4e", "3e"]
CLASSES = [f"{niveau}{i+1}" for niveau in NIVEAUX for i in range(2)]

# Affectation manuelle des salles spécialisées
AFFECTATION_PROF_SALLE = {
    "Mme Lefebvre": "Salle_Musique",
    "Mme Richard": "Gymnase",
    "M. Morel": "Salle_Arts",
    "Mme Petit": "Laboratoire",
}

SALLES_GENERALES = ["Salle_1", "Salle_2", "Salle_3", "Salle_4"]

# Répartition des professeurs qui n'ont pas de salle dédiée dans les salles générales
professeurs_sans_salle = set()

# On parcourt les profs
for matiere, contenu in profs.items():
    # contenu peut être un dict { "6e":"M. Dupont", "5e":"..." } ou { "defaut":"Mme Bernard" }
    # On récupère toutes les valeurs (noms de profs) :
    all_profs = []
    for key, val in contenu.items():
        if key == "defaut":
            all_profs.append(val)
        else:
            all_profs.append(val)

    # on ajoute ces profs dans un set
    for prof_nom in all_profs:
        # s'ils n'ont pas de salle spécialisée, on les met dans professeurs_sans_salle
        if prof_nom not in AFFECTATION_PROF_SALLE:
            professeurs_sans_salle.add(prof_nom)

professeurs_sans_salle = list(professeurs_sans_salle)  # Convertir en liste
for i, prof in enumerate(professeurs_sans_salle):
    AFFECTATION_PROF_SALLE[prof] = SALLES_GENERALES[i % len(SALLES_GENERALES)]

print("Répartition des professeurs sur les salles :")
for prof, salle in AFFECTATION_PROF_SALLE.items():
    print(f"{prof} → {salle}")

# 3) MODELE OR-TOOLS
# ==================
model = cp_model.CpModel()

NOMBRE_DE_SALLES = 10  # ex. 10 salles disponibles

# Variables (emploi du temps + salles)
emploi_du_temps = {}
emploi_du_temps_salles = {}

for classe in CLASSES:
    for j, jour in enumerate(JOURS):
        for h, heure in enumerate(HEURES):
            emploi_du_temps[(classe, j, h)] = model.NewIntVar(
                0, len(MATIERES), f"{classe}_{jour}_{heure}")
            emploi_du_temps_salles[(classe, j, h)] = model.NewIntVar(
                0, NOMBRE_DE_SALLES, f"salle_{classe}_{jour}_{heure}"
            )

# CONTRAINTES
for classe in CLASSES:
    niveau_classe = classe[:2]  # ex. "6e"

    # Liste des matières (selon ce qui existe dans volume_horaire[niveau])
    matieres_disponibles = list(volume_horaire[niveau_classe].keys())

    for j, jour in enumerate(JOURS):
        for h in range(len(HEURES)):
            # Pause déjeuner 12h-13h
            if h == 4:
                model.Add(emploi_du_temps[(classe, j, h)] == 0)
            # Pas de cours le mercredi après-midi
            if j == 2 and h > 4:
                model.Add(emploi_du_temps[(classe, j, h)] == 0)

        # Pas plus de 2 fois la même matière par jour
        for matiere in matieres_disponibles:
            occurrences = []
            for h in range(len(HEURES)):
                if h != 4 and not (j == 2 and h > 4):
                    is_matiere = model.NewBoolVar(f"{classe}_{jour}_{h}_{matiere}")
                    model.Add(emploi_du_temps[(classe, j, h)] == MATIERES.index(matiere) + 1).OnlyEnforceIf(is_matiere)
                    model.Add(emploi_du_temps[(classe, j, h)] != MATIERES.index(matiere) + 1).OnlyEnforceIf(is_matiere.Not())
                    occurrences.append(is_matiere)
            model.Add(sum(occurrences) <= 2)

    # Respect du volume horaire global
    for matiere in matieres_disponibles:
        heures_total = volume_horaire[niveau_classe][matiere]
        occurrences = []
        for j, jour in enumerate(JOURS):
            for h in range(len(HEURES)):
                if h != 4 and not (j == 2 and h > 4):
                    is_matiere = model.NewBoolVar(f"{classe}_{jour}_{h}_{matiere}_count")
                    model.Add(emploi_du_temps[(classe, j, h)] == MATIERES.index(matiere) + 1).OnlyEnforceIf(is_matiere)
                    model.Add(emploi_du_temps[(classe, j, h)] != MATIERES.index(matiere) + 1).OnlyEnforceIf(is_matiere.Not())
                    occurrences.append(is_matiere)

        model.Add(sum(occurrences) == heures_total)

# Bloquer M. Martin le mercredi matin (s’il est le prof d’Histoire)
for classe in CLASSES:
    niveau_classe = classe[:2]

    # Vérif si "Histoire" fait partie du volume horaire
    if "Histoire" in volume_horaire[niveau_classe]:
        # Récupérer le prof d'Histoire
        prof_h = profs["Histoire"]
        # Si c'est un dict, on prend soit le niveau, soit "defaut"
        if isinstance(prof_h, dict):
            prof_histoire = prof_h.get(niveau_classe, prof_h.get("defaut", "Prof inconnu"))
        else:
            prof_histoire = prof_h

        if prof_histoire == "M. Martin":
            # Interdire l'affectation de la matière Histoire (index) le mercredi matin (0..3)
            idx_histoire = MATIERES.index("Histoire") + 1
            for heure in range(4):
                model.Add(emploi_du_temps[(classe, 2, heure)] != idx_histoire)

# Minimiser les heures de permanence
total_permanence = model.NewIntVar(0, len(CLASSES)*len(JOURS)*len(HEURES), "total_permanence")
permanence_vars = []

for classe in CLASSES:
    for j, jour in enumerate(JOURS):
        for h in range(1, len(HEURES)-1):
            permanence = model.NewBoolVar(f"permanence_{classe}_{jour}_{h}")
            model.Add(emploi_du_temps[(classe, j, h)] == 0).OnlyEnforceIf(permanence)
            model.Add(emploi_du_temps[(classe, j, h)] != 0).OnlyEnforceIf(permanence.Not())
            permanence_vars.append(permanence)

model.Add(total_permanence == sum(permanence_vars))

# Ajouter une contrainte optionnelle pour éviter que Mme Petit enseigne le jeudi après-midi
conflit_M_Petit = model.NewIntVar(0, 10, "conflit_M_Petit")
conflits = []

for classe in CLASSES:
    niveau_classe = classe[:2]
    if "Physique" in volume_horaire[niveau_classe]:
        # Récupérer le prof de Physique
        prof_p = profs["Physique"]
        if isinstance(prof_p, dict):
            prof_phys = prof_p.get(niveau_classe, prof_p.get("defaut", "Prof inconnu"))
        else:
            prof_phys = prof_p

        if prof_phys == "Mme Petit":
            # Jeudi = j=3, l'après-midi = heures 5..8
            for heure in range(5, 9):
                c = model.NewBoolVar(f"conflit_Petit_{classe}_Jeudi_{heure}")
                idx_physique = MATIERES.index("Physique") + 1

                model.Add(emploi_du_temps[(classe, 3, heure)] == idx_physique).OnlyEnforceIf(c)
                model.Add(emploi_du_temps[(classe, 3, heure)] != idx_physique).OnlyEnforceIf(c.Not())
                conflits.append(c)

model.Add(conflit_M_Petit == sum(conflits))

# On minimise (trous + conflits)
model.Minimize(total_permanence + conflit_M_Petit)

# PETIT DEBUG
for niveau in NIVEAUX:
    if "Maths" in volume_horaire[niveau]:
        prof_m = profs["Maths"]
        if isinstance(prof_m, dict):
            p = prof_m.get(niveau, prof_m.get("defaut", "Inconnu"))
        else:
            p = prof_m
        print(f"Vérification: Maths en {niveau} = {p}")

# 4) LANCEMENT DU SOLVEUR
# =======================
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 5) AFFICHAGE DU RÉSULTAT
# ========================
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for classe in CLASSES:
        print(f"\nEmploi du temps de la classe {classe}:\n")
        headers = ["Jour/Heure"] + HEURES
        table = []

        for j, jour in enumerate(JOURS):
            row = [jour]
            for h, heure in enumerate(HEURES):
                matiere_index = solver.Value(emploi_du_temps[(classe, j, h)])
                salle_index = solver.Value(emploi_du_temps_salles[(classe, j, h)])

                if matiere_index > 0:
                    matiere = MATIERES[matiere_index - 1]
                    # Récupération du prof
                    p = profs[matiere]
                    if isinstance(p, dict):
                        prof_nom = p.get(classe[:2], p.get("defaut", "Prof inconnu"))
                    else:
                        prof_nom = p

                    # Choix de salle
                    # (Ici, tu n'as pas de vraie contrainte multi-classe,
                    #  donc on se contente d'un index ou d'AFFECTATION_PROF_SALLE)
                    # On a pas défini 'SALLES' => on simplifie
                    if salle_index > 0:
                        # On n'a pas de dictionnaire SALLES, on utilise l'affectation manuelle
                        salle = AFFECTATION_PROF_SALLE.get(prof_nom, "Salle inconnue")
                    else:
                        salle = AFFECTATION_PROF_SALLE.get(prof_nom, "Salle inconnue")

                    row.append(f"{matiere}\n{prof_nom}\n[{salle}]")
                else:
                    row.append("---")

            table.append(row)

        print(tabulate(table, headers, tablefmt="grid"))
else:
    print("❌ Aucune solution trouvée.")
