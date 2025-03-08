from ortools.sat.python import cp_model
import random
from tabulate import tabulate

# Définition des constantes
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
HEURES = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h"]
MATIERES = ["Maths", "Français", "Histoire", "SVT", "Anglais", "Physique", "Techno", "EPS", "Arts Plastiques", "Musique"]

# Déclaration des professeurs avec leur matière attribuée
PROFESSEURS = {
    "Maths": {"6e": "M. Dupont", "5e": "M. Lemoine", "4e": "M. Didier", "3e": "M. Didier"},
    "Français": "Mme Bernard",
    "Histoire": "M. Martin",
    "SVT": "Mme Durand",
    "Anglais": "M. Thomas",
    "Physique": "Mme Petit",
    "Techno": "M. Robert",
    "EPS": "Mme Richard",
    "Arts Plastiques": "M. Morel",
    "Musique": "Mme Lefebvre"
}


# Volume horaire par niveau
VOLUME_HORAIRE = {
    "6e": {"Maths": 5, "Français": 4, "Histoire": 3, "SVT": 2, "Anglais": 2, "Physique": 3, "Techno": 2, "EPS": 2, "Arts Plastiques": 2, "Musique": 2},
    "5e": {"Maths": 5, "Français": 4, "Histoire": 3, "SVT": 2, "Anglais": 2, "Physique": 3, "Techno": 2, "EPS": 2, "Arts Plastiques": 2, "Musique": 2},
    "4e": {"Maths": 5, "Français": 4, "Histoire": 3, "SVT": 2, "Anglais": 2, "Physique": 3, "Techno": 2, "EPS": 2, "Arts Plastiques": 2, "Musique": 2},
    "3e": {"Maths": 5, "Français": 4, "Histoire": 3, "SVT": 2, "Anglais": 2, "Physique": 3, "Techno": 2, "EPS": 2, "Arts Plastiques": 2, "Musique": 2}
}

NIVEAUX = ["6e", "5e", "4e", "3e"]
CLASSES = [f"{niveau}{i+1}" for niveau in NIVEAUX for i in range(2)]

# 🔵 Affectation manuelle des salles pour les matières spécialisées
AFFECTATION_PROF_SALLE = {
    "Mme Lefebvre": "Salle_Musique",
    "Mme Richard": "Gymnase",
    "M. Morel": "Salle_Arts",
    "Mme Petit": "Laboratoire",
}

# 🔵 Définition des salles générales
SALLES_GENERALES = ["Salle_1", "Salle_2", "Salle_3", "Salle_4"]

# 🔵 Liste des professeurs qui n'ont pas de salle attitrée (évite les doublons avec les matières spécialisées)
professeurs_sans_salle = set()

for matiere, prof in PROFESSEURS.items():
    if isinstance(prof, dict):  # Gestion spéciale pour les profs de Maths avec plusieurs niveaux
        for niveau, prof_nom in prof.items():  # Parcourir chaque niveau (6e, 5e, 4e, 3e)
            if prof_nom not in AFFECTATION_PROF_SALLE:
                professeurs_sans_salle.add(prof_nom)
    elif prof not in AFFECTATION_PROF_SALLE:
        professeurs_sans_salle.add(prof)

professeurs_sans_salle = list(professeurs_sans_salle)  # Convertir en liste après suppression des doublons

# 🔵 Répartir les professeurs restants dans les salles générales (rotation si manque de salles)
for i, prof in enumerate(professeurs_sans_salle):
    AFFECTATION_PROF_SALLE[prof] = SALLES_GENERALES[i % len(SALLES_GENERALES)]

# 🔵 Affichage de la répartition des profs et salles
print("Répartition des professeurs sur les salles :")
for prof, salle in AFFECTATION_PROF_SALLE.items():
    print(f"{prof} → {salle}")


# Initialisation du modèle
model = cp_model.CpModel()

# Définition d'un nombre fixe de salles (ex: 10 salles disponibles)
NOMBRE_DE_SALLES = 10  

# Initialisation des variables d'emploi du temps et d'affectation des salles
emploi_du_temps = {}
emploi_du_temps_salles = {}

for classe in CLASSES:
    for j, jour in enumerate(JOURS):
        for h, heure in enumerate(HEURES):
            emploi_du_temps[(classe, j, h)] = model.NewIntVar(0, len(MATIERES), f"{classe}_{jour}_{heure}")
            emploi_du_temps_salles[(classe, j, h)] = model.NewIntVar(0, NOMBRE_DE_SALLES, f"salle_{classe}_{jour}_{heure}")

# Contraintes :
for classe in CLASSES:
    niveau_classe = classe[:2]  # Extraire le niveau de la classe
    matieres_disponibles = list(VOLUME_HORAIRE[niveau_classe].keys())
    for j, jour in enumerate(JOURS):
        for h in range(len(HEURES)):
            # Pause déjeuner de 12h à 13h
            if h == 4:
                model.Add(emploi_du_temps[(classe, j, h)] == 0)
            # Pas de cours le mercredi après-midi
            if j == 2 and h > 4:
                model.Add(emploi_du_temps[(classe, j, h)] == 0)
        
        # Assurer une répartition équilibrée des matières en respectant le volume horaire
        for matiere in matieres_disponibles:
            occurrences = []
            for h in range(len(HEURES)):
                if h != 4 and not (j == 2 and h > 4):
                    var = model.NewBoolVar(f"{classe}_{jour}_{h}_{matiere}")
                    model.Add(emploi_du_temps[(classe, j, h)] == MATIERES.index(matiere) + 1).OnlyEnforceIf(var)
                    model.Add(emploi_du_temps[(classe, j, h)] != MATIERES.index(matiere) + 1).OnlyEnforceIf(var.Not())
                    occurrences.append(var)
            model.Add(sum(occurrences) <= 2)  # Pas plus de 2 fois par jour

    # Assurer le respect du volume horaire
    for matiere in matieres_disponibles:
        occurrences = []
        for j, jour in enumerate(JOURS):
            for h in range(len(HEURES)):
                if h != 4 and not (j == 2 and h > 4):
                    var = model.NewBoolVar(f"{classe}_{jour}_{h}_{matiere}_count")
                    model.Add(emploi_du_temps[(classe, j, h)] == MATIERES.index(matiere) + 1).OnlyEnforceIf(var)
                    model.Add(emploi_du_temps[(classe, j, h)] != MATIERES.index(matiere) + 1).OnlyEnforceIf(var.Not())
                    occurrences.append(var)
        model.Add(sum(occurrences) == VOLUME_HORAIRE[niveau_classe][matiere])
        
        
#  Bloquer uniquement M. Martin le mercredi matin
for classe in CLASSES:
    niveau_classe = classe[:2]  # Extraire le niveau de la classe (6e, 5e, etc.)

    # Vérifier si cette classe a M. Martin comme prof d'Histoire
    if "Histoire" in VOLUME_HORAIRE[niveau_classe]:
        prof_histoire = PROFESSEURS["Histoire"]
        
        # Si la classe est bien enseignée par M. Martin, on applique la contrainte
        if prof_histoire == "M. Martin":
            for heure in range(4):  # Matin = de 8h à 12h (heures 0 à 3)
                model.Add(emploi_du_temps[(classe, 2, heure)] != MATIERES.index("Histoire") + 1)  # 2 = Mercredi
                
          


# Minimiser les heures de permanence
total_permanence = model.NewIntVar(0, len(CLASSES) * len(JOURS) * len(HEURES), "total_permanence")
permanence_vars = []
for classe in CLASSES:
    for j, jour in enumerate(JOURS):
        for h in range(1, len(HEURES) - 1):  # On évite les premières et dernières heures de la journée
            permanence = model.NewBoolVar(f"permanence_{classe}_{jour}_{h}")
            model.Add(emploi_du_temps[(classe, j, h)] == 0).OnlyEnforceIf(permanence)
            model.Add(emploi_du_temps[(classe, j, h)] != 0).OnlyEnforceIf(permanence.Not())
            permanence_vars.append(permanence)

model.Add(total_permanence == sum(permanence_vars))
model.Minimize(total_permanence)



# Ajouter une contrainte optionnelle pour éviter que M. Petit enseigne le jeudi après-midi
conflit_M_Petit = model.NewIntVar(0, 10, "conflit_M_Petit")  # Variable d'écart

conflits = []  # Liste des conflits à minimiser
for classe in CLASSES:
    niveau_classe = classe[:2]  # Récupérer le niveau de la classe

    # Vérifier si M. Petit est professeur de Physique dans cette classe
    if "Physique" in VOLUME_HORAIRE[niveau_classe]:
        prof_physique = PROFESSEURS["Physique"]
        
        if prof_physique == "Mme Petit":  # On vérifie bien que cette classe a Mme Petit
            for heure in range(5, 9):  # Après-midi = 13h-17h (indices 5 à 8)
                conflit = model.NewBoolVar(f"conflit_Petit_{classe}_Jeudi_{heure}")
                
                # Si Physique est attribué à ce créneau, on active la variable de conflit
                model.Add(emploi_du_temps[(classe, 3, heure)] == MATIERES.index("Physique") + 1).OnlyEnforceIf(conflit)
                model.Add(emploi_du_temps[(classe, 3, heure)] != MATIERES.index("Physique") + 1).OnlyEnforceIf(conflit.Not())
                
                conflits.append(conflit)  # On ajoute ce conflit à la liste

# Somme de tous les conflits pour Mme Petit
model.Add(conflit_M_Petit == sum(conflits))

# Ajout de la minimisation des conflits de Mme Petit dans la fonction objectif
model.Minimize(total_permanence + conflit_M_Petit)  # On minimise aussi ce conflit


for niveau in ["6e", "5e", "4e", "3e"]:
    print(f"Vérification pour le niveau {niveau}:")
    print(f"→ Maths en {niveau} : {PROFESSEURS['Maths'][niveau]}")

# Création du solveur et résolution du modèle
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Génère l'emploi du temps
for classe in CLASSES:
    print(f"\nEmploi du temps de la classe {classe}:\n")

    # En-tête des heures
    headers = ["Jour/Heure"] + HEURES
    table = []

    for j, jour in enumerate(JOURS):
        row = [jour]  # Première colonne = jour
        for h, heure in enumerate(HEURES):
            matiere_index = solver.Value(emploi_du_temps[(classe, j, h)])
            salle_index = solver.Value(emploi_du_temps_salles[(classe, j, h)])

            if matiere_index > 0:
                # Récupération de la matière et du professeur associé
                matiere = MATIERES[matiere_index - 1]

                if isinstance(PROFESSEURS[matiere], dict):  # Gestion spéciale pour Maths
                    niveau_classe = classe[:2]  # Extraire "6e", "5e", "4e" ou "3e"
                    prof = PROFESSEURS[matiere].get(niveau_classe, "Prof inconnu")  # Sélectionner le bon prof selon le niveau
                else:
                    prof = PROFESSEURS[matiere]  # Matières avec un seul professeur

                # Vérification de l'affectation des salles
                if salle_index > 0 and salle_index <= len(SALLES):
                    salle = list(SALLES.keys())[salle_index - 1]  # Salle affectée par OR-Tools
                else:
                    # Utiliser l'affectation manuelle des salles spécialisées ou générales
                    salle = AFFECTATION_PROF_SALLE.get(prof, "Salle inconnue")

                # Ajouter les données dans la ligne correspondante
                row.append(f"{matiere}\n{prof}\n[{salle}]")  # Affichage sur plusieurs lignes
            else:
                row.append("---")  # Case vide si aucun cours n'est affecté

        table.append(row)

    # Affichage du tableau sous forme de grille
    print(tabulate(table, headers, tablefmt="grid"))
