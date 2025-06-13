"""
Page d'accueil du générateur d'emploi du temps.

Cette page présente :
- Le projet TER 2024-2025 réalisé dans le cadre du Master 1 MIASHS (Informatique et Cognition) ;
- Un bouton d'entrée vers l'application ("/informations") ;
- Une illustration visuelle du projet ;
- Un guide d'utilisation organisé en plusieurs étapes, regroupées dans un accordéon :
    - Introduction et navigation générale ;
    - Saisie des données de l'établissement (horaires, langues, options, ressources) ;
    - Définition des contraintes obligatoires et optionnelles ;
    - Phase de calcul (génération automatique) ;
    - Visualisation et analyse des résultats ;
    - Un lien de téléchargement du guide utilisateur en PDF.

Cette page constitue le point de départ de l'application et offre un aperçu pédagogique de l'outil.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from styles import *
from fonctions import copier_document_utilisateur

def layout_accueil():
    """
    Construit et retourne le layout complet de la page d'accueil de l'application.

    Composants affichés :
    - Un titre principal et une description du projet TER (objectif, contexte) ;
    - Un bouton "Commencer" menant à la page de saisie des informations de l'établissement ;
    - Une illustration du projet positionnée à droite du texte ;
    - Un guide d'utilisation sous forme d'accordéon, expliquant pas à pas le fonctionnement de l'outil :
        * Présentation des étapes ;
        * Paramétrage des données et contraintes ;
        * Lancement du solveur ;
        * Analyse des résultats.

    Returns:
        html.Div: Le layout Dash contenant la structure complète de la page d'accueil.
    """
    nom_fichier = copier_document_utilisateur()

    return html.Div([
        html.Div([
            html.Br(),
            # Partie gauche : Titre et contenu
            html.Div([
                html.H1("Générateur d'emploi du temps", style={
                    "fontSize": "3rem",
                    **style_marge_bas
                }),
                html.Hr(style={
                    "width": "200px",
                    **style_hr
                }),
                html.Br(),
                html.P([
                    "Dans le cadre de notre Master 1 MIASHS, parcours Informatique et Cognition, nous avons mené un projet TER visant à concevoir un générateur d'emplois du temps. ",
                    html.Br(),
                    "Cet outil permet de créer automatiquement des emplois du temps optimisés, en tenant compte des contraintes de l'établissement, des disponibilités des enseignants et de l'organisation des ressources."],
                    style=explication_style
                ),
                html.Br(),
                html.A([
                    html.I(className="bi bi-arrow-right-circle me-2"),
                    "Commencer"
                ], href="/informations", style=style_btn_commencer)
            ], style={"flex": "1", "minWidth": "0"}),

            # Partie droite : Illustration
            html.Div([
                html.Img(
                    src="/assets/Illustration_accueil.png",
                    style=style_illustration
                )
            ], style={"flex": "0 0 auto"})
        ], style=style_bloc_page_accueil),
        html.Br(),
        html.Hr(style=style_hr),

        #  ──────────────────────────────── GUIDE ────────────────────────────────
        html.H2("Guide d'utilisation", className="my-4"),

        dbc.Accordion([
            dbc.AccordionItem([
                html.P("Ce guide d'utilisation vous accompagne pas à pas dans la prise en main de l'outil, n'hésitez pas à télécharger le guide complet au bas de la page pour avoir la version PDF avec les illustrations."),
                html.P("Il est organisé selon les grandes étapes de la conception d'un emploi du temps : "
                    "la saisie des données de l'établissement, la définition des contraintes, le lancement du calcul, "
                    "et enfin l'analyse des résultats."),

                html.P("Voici les différentes parties du guide :"),
                html.Ul([
                    html.Li([
                        "La section ", html.Span("Saisie des données de votre établissement", style={'fontStyle': 'italic'}),
                        " vous permet de renseigner les horaires, les classes, les professeurs, les matières et les ressources disponibles."
                    ]),
                    html.Li([
                        "La section ", html.Span("Saisie des contraintes de votre établissement", style={'fontStyle': 'italic'}),
                        " vous permet de définir les indisponibilités, les contraintes pédagogiques, ainsi que les règles spécifiques."
                    ]),
                    html.Li([
                        "La section ", html.Span("Calculs", style={'fontStyle': 'italic'}),
                        " explique comment lancer la génération automatique d'un emploi du temps en fonction des données et contraintes saisies."
                    ]),
                    html.Li([
                        "La section ", html.Span("Résultats", style={'fontStyle': 'italic'}),
                        " présente l'emploi du temps généré, le respect des contraintes et les indicateurs de qualité."
                    ]),
                ])
            ], title="Introduction"),

            dbc.AccordionItem([
                html.Div([
                    html.H2("Réinitialisation et import", className="mt-4"),
                    html.P("Deux boutons sont disponibles en haut de la page : le bouton « Importer » permet de recharger un fichier JSON contenant des données précédemment sauvegardées. "
                            "Le bouton « Réinitialiser » permet d'effacer toutes les données après confirmation. Ces fonctionnalités permettent de gérer plusieurs établissements ou configurations.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Cliquer sur « Importer » pour charger un fichier JSON existant."),
                        html.Li("Cliquer sur « Réinitialiser » pour effacer toutes les données et repartir de zéro."),
                    ]),
                    html.Br(),

                    html.H2("1. Programme national", className="mt-3"),
                    html.P("Le programme national est pré-rempli pour les niveaux 6e, 5e, 4e et 3e. "
                            "Vous pouvez modifier les volumes horaires des disciplines selon les besoins de votre établissement. "
                            "L'EMC (Enseignement Moral et Civique) peut être inclus ou non dans le programme d'Histoire-Géographie.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 1 : Sélectionner un niveau pour afficher le programme."),
                        html.Li("Étape 2 : Modifier les volumes horaires des disciplines si besoin."),
                        html.Li("Étape 3 : Préciser si l'EMC est inclus ou non dans le cours d'Histoire-Géographie. Renseigner le volume associé, si ce n'est pas le cas."),
                    ]),
                    html.Br(),

                    html.H2("2. Informations globales", className="mt-4"),

                    html.H3("2.1 Horaires"),
                    html.P("Cette section permet de configurer les horaires types d'une journée. "
                            "Vous pouvez aussi définir des jours où il n'y a pas cours l'après-midi.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 4 : Choisir les journées de cours (ex : Lundi, Mardi, Mercredi, Jeudi et Vendredi) ainsi que les journées qui n'ont pas de cours l'après-midi (généralement le Mercredi)."),
                        html.Li("Étape 5 : Renseigner les horaires pour chaque période (le début minimum des cours du matin, etc.)."),
                        html.Li("Étape 6 : Définir la durée des créneaux, pauses et récréations."),
                    ]),
                    html.Br(),

                    html.H3("2.2 Langues"),
                    html.P("Vous pouvez indiquer les langues vivantes proposées par votre établissement. "
                            "Les LV1 et LV2 sont toujours présentes, tandis que les LV3 et LV4 peuvent être activées si besoin. "
                            "Pour chaque langue, vous pouvez ajouter des langues personnalisées, indiquer les niveaux concernés, et définir un volume horaire.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 7 : Sélectionner les LV1 et LV2 souhaitées et en ajouter au besoin."),
                        html.Li("Étape 8 : Activer et paramétrer les LV3 et LV4 si l'établissement en propose."),
                    ]),
                    html.Br(),

                    html.H3("2.3 Options"),
                    html.P("Certaines classes peuvent proposer des options spécifiques (ex : Latin, Théâtre, etc.). "
                            "Vous pouvez ici cocher les options proposées ou en ajouter manuellement, puis indiquer les niveaux concernés et le volume horaire associé.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 9 : Cocher les options proposées ou ajouter des options spécifiques à l'établissement en les saisissant si elles ne sont pas dans la liste des propositions."),
                        html.Li("Étape 10 : Définir les niveaux concernés pour chaque option disponible, à sélectionner via les slides (sélecteur de niveaux)."),
                        html.Li("Étape 11 : Renseigner les volumes horaires par niveau pour chaque option dans le tableau associé."),
                    ]),
                    html.Br(),

                    html.H2("3. Ressources de l'établissement", className="mt-4"),

                    html.H3("3.1 Classes et groupes"),
                    html.P("Vous pouvez importer un tableau de classes ou les saisir manuellement. "
                            "Chaque classe possède un niveau, un effectif et éventuellement des dépendances avec d'autres groupes (ex : groupes de langue). "
                            "Un générateur vous permet de créer rapidement plusieurs classes identiques.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 12 : Importer ou saisir manuellement les classes."),
                        html.Li("Étape 13 : Utiliser le générateur pour créer plusieurs classes identiques."),
                    ]),
                    html.Br(),

                    html.H3("3.2 Salles"),
                    html.P("Les salles peuvent être saisies ou importées avec leur nom, leur capacité et les matières qu'elles peuvent accueillir. "
                            "Si aucune matière n'est précisée, un ensemble par défaut est utilisé. "
                            "Un générateur est également disponible pour créer des salles en série.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 14 : Importer ou saisir les salles de l’établissement."),
                        html.Li("Étape 15 : Utiliser le générateur pour créer plusieurs salles similaires."),
                    ]),
                    html.Br(),

                    html.H3("3.3 Professeurs"),
                    html.P("Saisissez ou importez les professeurs de votre établissement avec leurs caractéristiques : civilité, nom, niveaux enseignés, matières, "
                            "volume horaire hebdomadaire, durée de préférence des cours et salle préférée éventuelle. "
                            "Un générateur permet également d'en créer plusieurs en une fois.",
                            style=explication_style),
                    html.Ul([
                        html.Li("Étape 16 : Importer ou saisir les  professeurs avec leurs informations."),
                        html.Li("Étape 17 : Utiliser le générateur pour ajouter plusieurs enseignants automatiquement."),
                    ])
                    
                ])
            ], title="Saisie des informations de l'établissement"),

            dbc.AccordionItem([

                html.H3("1. Contraintes des professeurs", className="mt-3"),
                html.P(
                    "Permet de définir les indisponibilités (partielles ou totales) de chaque enseignant à des créneaux spécifiques.",
                    style=explication_style
                ),
                html.Ul([
                    html.Li("Étape 1 : Sélectionner les professeurs auxquels il faut ajouter des contraintes."),
                    html.Li("Étape 2 : Entrer les nouvelles contraintes à l’aide des boutons ou grâce aux listes déroulantes à droite."),
                    html.Li("Étape 3 : Vérifier sur le tableau récapitulatif les contraintes entrées."),
                    html.Li("Étape 4 : Sélectionner les classes et groupes auxquels il faut ajouter des contraintes."),
                    html.Li("Étape 5 : Entrer les nouvelles contraintes à l’aide des boutons ou grâce aux listes déroulantes à droite."),
                    html.Li("Étape 6 : Vérifier sur le tableau récapitulatif les contraintes entrées."),
                ]),
                html.Br(),

                html.H3("2. Contraintes des groupes / classes", className="mt-4"),
                html.P(
                    "Même fonctionnement que pour les professeurs, mais appliqué aux classes ou groupes d'élèves.",
                    style=explication_style
                ),
                html.Ul([
                    html.Li("Étape 7 : Sélectionner les salles auxquelles il faut ajouter des contraintes."),
                    html.Li("Étape 8 : Entrer les nouvelles contraintes à l’aide des boutons ou grâce aux listes déroulantes à droite."),
                ]),
                html.Br(),

                html.H3("3. Contraintes des salles", className="mt-4"),
                html.P(
                    "Permet de marquer certains créneaux comme indisponibles pour certaines salles. C'est utile pour bloquer les créneaux d'entretien, de maintenance ou d'indisponibilité matérielle.",
                    style=explication_style
                ),
                html.Ul([
                    html.Li("Étape 9 : Vérifier sur le tableau récapitulatif les contraintes entrées."),
                    html.Li("Étape 10 : Sélectionnez dans les listes déroulantes les modalités souhaitées pour la contrainte et appliquer la contrainte."),
                ]),
                html.Br(),

                html.H3("4. Contraintes avancées du planning", className="mt-4"),

                html.H4("4.1 Nombre d'heures maximal à la suite"),
                html.P("Permet de limiter le nombre d'heures consécutives d'un même élève sur une demi-journée ou une journée entière.",
                    style=explication_style
            ),
                html.Ul([
                    html.Li("Étape 11 : Sélectionnez les classes, matières, nombre d'heures maximal, et l'étendue (1/2 journée ou journée)."),
                    html.Li("Étape 12 : Cliquez sur Appliquer pour enregistrer la contrainte."),
                ]),
                html.Br(),

                html.H4("4.2 Contrainte cours-planning"),
                html.P("Permet d'imposer ou d'interdire la tenue d'un cours pour une classe à un jour et une heure donnés.",
                    style=explication_style
                ),
                html.Ul([
                    html.Li("Étape 13 : Complétez les champs : classe(s), matière, jour, heure, et type (obligation ou interdiction), puis cliquez sur Appliquer."),
                ]),
                html.Br(),

                html.H4("4.3 Enchaînement de cours"),
                html.P("Permet de forcer ou d'interdire qu'un cours A soit suivi d'un cours B, avec un nombre minimal d'occurrences.",
                    style=explication_style
                ),
                html.Ul([
                    html.Li("Étape 14 : Choisissez les classes concernées, les deux cours (A puis B), le type d'enchaînement et le minimum d'occurrences."),
                    html.Li("Étape 15 : Vérifiez que les volumes horaires permettent cette contrainte, puis cliquez sur Appliquer."),
                ]),

            ], title="Saisie des contraintes de votre établissement"),

            dbc.AccordionItem([
                html.Div([
                    html.H3("1. Poids du matériel scolaire", className="mt-3"),
                    html.P(
                        "Cette contrainte optionnelle permet de limiter le poids du cartable par niveau. "
                        "Tu peux définir un poids maximal autorisé pour la journée, et attribuer un poids estimé pour chaque matière. "
                        "Une tolérance de 5% est appliquée automatiquement.",
                        style=explication_style
                    ),
                    html.Ul([
                        html.Li("Étape 1 : Sélectionnez un niveau (ex : 6e, 5e...)."),
                        html.Li("Étape 2 : Attribuez un poids estimé (en kg) à une ou plusieurs matières."),
                        html.Li("Étape 3 : Indiquez le poids maximal autorisé pour la journée."),
                    ]),
                    html.Br(),

                    html.H3("2. Réfectoire et permanences", className="mt-4"),
                    html.P(
                        "Cette section permet de spécifier les capacités des infrastructures liées à la pause méridienne. "
                        "Tu peux indiquer la capacité du réfectoire et des permanences, ainsi que le pourcentage d'élèves qui mangent à la cantine.",
                        style=explication_style
                    ),
                    html.Ul([
                        html.Li("Étape 4 : Saisissez la capacité maximale du réfectoire."),
                        html.Li("Étape 5 : Indiquez le pourcentage d'élèves mangeant au réfectoire."),
                        html.Li("Étape 6 : Activez ou non la priorité aux plus jeunes pour finir plus tôt."),
                        html.Li("Étape 7 : Renseignez la capacité maximale d'accueil en permanence."),
                    ]),
                    html.Br(),

                    html.H3("3. Ordre d'importance des contraintes", className="mt-4"),
                    html.P(
                        "Tu peux ici classer les contraintes optionnelles par ordre d'importance. "
                        "Cela permet à l'algorithme de génération de prioriser les contraintes à respecter lorsque toutes ne peuvent l'être en même temps.",
                        style=explication_style
                    ),
                    html.Ul([
                        html.Li("Étape 8 : Consulte l'ordre par défaut des contraintes."),
                        html.Li("Étape 9 : Utilise les flèches pour réorganiser les contraintes selon tes priorités."),
                        html.Li("Étape 10 : Le rang 1 correspond à la contrainte la plus importante."),
                    ])
                ]),
            ], title="Saisie des contraintes optionnelles de votre établissement"),

            dbc.AccordionItem([
                  html.Div([
                    html.H3("1.Lancer le calcul de l'emploi du temps", className="mt-3"),
                    html.P(
                        "Tout est configuré pour générer l'emploi du temps de létablissement."
                        "Le logiciel peut générer plusieurs emplois du temps pour ensuite les comparer et ressortir celui le plus adapté aux contraintes entrées précédemment."
                        ,style=explication_style
                    ),
                    html.Ul([
                        html.Li("Étape 1 : Entrer le nombre d’emplois du temps à générer"),
                        html.Li("Étape 2 : Lancer le calcul."),
                    ])
                ]),
                ],title="Lancer le calcul de l'emploi du temps"),

           dbc.AccordionItem(
            [
                # ---- PARTIE 1 : STATISTIQUES ----
                html.Div([
                    html.H3("1. Statistiques sur le respect des contraintes", className="mt-3"),
                    html.P(
                        "Consultez ici les statistiques de complétion de l’emploi du temps généré : respect du volume horaire, contraintes obligatoires et optionnelles. "
                        "Un code couleur indique rapidement si les objectifs sont atteints.",
                        style=explication_style
                    ),
                    html.Ul([
                        html.Li("Volume horaire : en vert si 100 % du volume a été placé, sinon en rouge."),
                        html.Li("Contraintes obligatoires : en vert si toutes respectées, sinon en rouge."),
                        html.Li("Contraintes optionnelles : en vert si ≥ 80 % respectées, sinon en rouge."),
                        html.Li("Tableau détaillé : liste chaque contrainte, son type, le nombre et le taux de respect."),
                        html.Li("Menu déroulant pour consulter le détail des violations de contraintes."),
                    ]),
                ]),

                html.Br(),

                # ---- PARTIE 2 : GESTION DES EMPLOIS DU TEMPS ----
                html.Div([
                    html.H3("2.1 Gestion des emplois du temps", className="mt-3"),
                    html.P(
                        "Affichez et gérez les emplois du temps. Sélectionnez une ressource à l’aide d’une liste déroulante : salle, professeur ou classe."
                        " Quatre modes de gestion sont disponibles :",
                        style=explication_style
                    ),
                    html.Ul([
                        html.Li("**Affichage** : Affiche en grand le tableau de l'emploi du temps sélectionné."),
                        html.Li("**Édition** : Permet de modifier le contenu d’un créneau."),
                        html.Li("**Déplacement** : Permet d’échanger ou déplacer des créneaux entre eux."),
                        html.Li("**Export** : Permet d’exporter l’emploi du temps sélectionné."),
                    ]),

                    html.Br(),

                    # -- Sous-partie : Edition --
                    html.H4("2.2 Mode édition"),
                    html.P("En mode édition, après avoir sélectionné un créneau vous pouvez"),
                    html.Ul([
                        html.Li("Sélectionner un créneau à modifier."),
                        html.Li("Éditer le contenu du créneau pour la semaine A ou la semaine B."),
                        html.Li("Supprimer le contenu de la semaine A ou de la semaine B."),
                    ]),

                    html.Br(),

                    # -- Sous-partie : Déplacement --
                    html.H4("2.3 Mode déplacement"),
                    html.P("En mode déplacement, après avoir sélectionné deux créneaux vous pouvez :"),
                    html.Ul([
                        html.Li("Échanger les deux créneaux."),
                        html.Li("Écraser le deuxième créneau avec le premier."),
                        html.Li("Déplacer uniquement le cours de la semaine A."),
                        html.Li("Déplacer uniquement le cours de la semaine B."),
                    ]),

                    html.Br(),

                    # -- Sous-partie : Export --
                    html.H4("2.4 Mode export"),
                    html.P("Permet d’exporter les emplois du temps au format PDF (dans une archive ZIP). Vous pouvez choisir d’exporter indivuduellement ou de façon groupé :"),
                    html.Ul([
                        html.Li("L’emploi du temps actuellement affiché."),
                        html.Li("Tous les emplois du temps des classes."),
                        html.Li("Tous les emplois du temps des professeurs."),
                        html.Li("Tous les emplois du temps des salles."),
                    ]),
                ]),
            ],
            title="Résultats et gestion de l'emploi du temps"),

            html.Br(),


            html.Div([
                html.A("Télécharger le Manuel d'utilisation complet (version PDF)", href=f"/assets/{nom_fichier}", target="_blank")
            ], style=style_telecharger_accueil)

        ],
        start_collapsed=True)
    ], style=global_page_style)


            
