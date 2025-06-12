"""
Page principale de saisie des informations d'établissement dans l'application Dash
pour la génération automatique d'emploi du temps.

Cette page permet à l'utilisateur de configurer toutes les données de base avant le calcul :

1. Programme national par niveau :
   - Permet de modifier les volumes horaires des disciplines du tronc commun.
   - Prend en compte des options personnalisées (avec niveaux et horaires associés).

2. Horaires de l'établissement :
   - Définition des créneaux horaires jour par jour (heure début/fin, pause déjeuner, etc.).
   - Utilisation de composants horloge personnalisés.

3. Langues de l'établissement :
   - Sélection dynamique des LV1, LV2, LV3, LV4 selon les niveaux ;
   - Gestion des langues personnalisées (ajout/suppression dynamique via champ "Autre").

4. Options disponibles :
   - Sélection des options proposées (arts, latin, sport, etc.) ;
   - Gestion dynamique des options "Autre", associées à des niveaux et volumes horaires.

5. Ressources de l'établissement :
   - Importation ou saisie manuelle des classes, professeurs, salles ;
   - Initialisation automatique de volumes horaires selon le programme national.

Cette page inclut :
- De nombreux callbacks pour gérer l'affichage conditionnel, la validation, l'enregistrement JSON automatique.
- Des composants dynamiques liés à la structure du fichier data_interface.json.
- Des volets de type dbc.AccordionItem pour organiser la saisie étape par étape.

Returns:
    html.Div: Le layout complet de la page d'informations de l'établissement.
"""

import os
import json
import pandas as pd
import dash
from dash import ctx, Input, Output, State, callback, dash_table, html, dcc, no_update, ALL, MATCH
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from main_dash import app
from styles import *
from fonctions import *
from textes import *
from constantes import *

import base64
import io

#################################################################################################################################################################
# Page de renseignement des informations de l'établissement

def layout_informations():
    """
    Construit le layout principal de la page de configuration des informations d'établissement.

    Cette page regroupe tous les volets nécessaires à la configuration initiale avant la génération
    de l'emploi du temps. Elle est organisée en plusieurs sections repliables de type AccordionItem :

    1. Programme national :
        - Choix du niveau (6e à 3e) ;
        - Modification des volumes horaires par matière ;
        - Ajout d'options personnalisées avec niveaux associés.

    2. Horaires de l'établissement :
        - Définition des jours, des horaires de début, fin, pause déjeuner pour chaque jour ;

    3. Langues de l'établissement :
        - Sélection des langues vivantes (LV1 à LV4) ;
        - Possibilité d'activer ou désactiver LV3/LV4 ;
        - Ajout de langues personnalisées ;
        - Attribution des langues à des niveaux via sliders.

    4. Options disponibles :
        - Sélection des options proposées parmi plusieurs catégories ;
        - Ajout dynamique d'options personnalisées avec plage de niveaux et volume horaire.

    5. Ressources de l'établissement :
        - Saisie manuelle ou importation des classes, professeurs et salles ;
        - Visualisation dans des tableaux éditables.

    Returns:
        html.Div: Composant Dash contenant l'ensemble des éléments de saisie et d'explication.
    """
    return html.Div([
        dcc.Store(id="initialisation-donnees", data=True),
        dcc.Store(id="freeze-callbacks", data=False),
        html.H1("Renseignement des informations de l'établissement", className="my-4"),
        html.Hr(style=style_hr),
        html.P(texte_entete, style=explication_style),

        html.Div([
            # Ligne avec les deux actions côte à côte
            html.Div([
                dbc.Button([
                    html.I(className="bi bi-x-octagon me-2"),
                    "Réinitialiser toutes les données "
                ], id="btn-reset-data", style=style_btn_supprimer, className="me-3"),

                dcc.Upload(
                    id="import-json",
                    children=dbc.Button([
                        html.I(className="bi bi-upload me-2"),
                        "Importer des données depuis un fichier JSON"
                    ], style=style_btn_import),
                    accept=".json",
                    multiple=False
                )
            ], style=style_bouton_import_reinit),

            # Ligne avec le message d'état centré
            html.Div(
                html.Span(id="reset-message", style=style_message_import_supression),
            )
        ]),

        # Confirmation de réinitialisation des données
        dbc.Modal(
            [
                dbc.ModalHeader("Confirmation de réinitialisation"),
                dbc.ModalBody("Êtes-vous sûr de vouloir supprimer toutes les données enregistrées ?"),
                dbc.ModalFooter([
                    dbc.Button("Oui, réinitialiser", id="confirm-reset", color="danger"),
                    dbc.Button("Annuler", id="cancel-reset", className="ms-2")
                ])
            ],
            id="modal-reset-confirmation",
            is_open=False,
        ),

    #################################################################################################################################################################
        html.H2("1. Programme national", className="my-3"),
        html.P(texte_explications_programme, style=explication_style),

        dbc.Accordion([
        # Sous-section : programme national
            dbc.AccordionItem([
                html.Div([
                    # Section de validation du programme national
                    html.P("Sélectionnez un niveau pour consulter ou modifier son programme national :"),
                    dcc.Dropdown(
                        id="niveau-programme",
                        options=[{"label": niveau, "value": niveau} for niveau in ["6e", "5e", "4e", "3e"]],
                        placeholder="Choisir un niveau...",
                        style=style_dropdown_niveau
                    ),
                    # Tableau du programme national
                    dash_table.DataTable(
                        id="table-programme-par-niveau",
                        columns=[
                            {"name": "Discipline", "id": "Discipline", "editable": False},
                            {"name": "Volume horaire hebdomadaire (en H)", "id": "VolumeHoraire", "editable": True, "type": "numeric"},
                        ],
                        data=[],
                        editable=True,
                        style_table=style_table,
                        style_header=style_header_table,
                        style_cell=style_cell
                    ),

                    html.Br(),

                    # Comment est pris en compte l'EMC
                    dcc.Store(id="dummy-stockage-emc"),
                    html.Div([
                        html.H6("Enseignement moral et civique (EMC)"),
                        html.P("Est-il inclus avec l'Histoire-Géographie ?"),
                        dcc.RadioItems(
                            id="emc-inclus",
                            options=[
                                {"label": " Oui", "value": "oui"},
                                {"label": " Non", "value": "non"}
                            ],
                            inline=True,
                            labelStyle={"marginRight": "20px"}
                        ),
                        # Si EMC n'est pas inclus, on demande le volume horaire
                        html.Div([
                            html.Label("Si non, indiquez le volume horaire hebdomadaire :", style={"marginRight": "15px"}),

                            dcc.Input(
                                id="emc-volume",
                                type="number",
                                min=0,
                                step=0.5,
                                placeholder="ex : 0.5",
                                style=style_input_hh_min
                            ),
                            html.Span("H")
                        ], id="bloc-emc-volume", style={"display": "flex", "alignItems": "center", "gap": "5px", "marginBottom": "15px", "marginTop": "10px", "display": "none"})
                    ]),

                    dcc.Store(id="niveau-programme-precedent", data=None),
                    dcc.Store(id="stockage-emc-par-niveau", data={}),

                    html.Br(),
                ], style=style_accordeons_contenus)
            ], title=html.H4("1.1 Modification et validation du programme national")),
        ], style=style_accordeons,
        start_collapsed=True, flush=True, active_item=None),

        html.Br(),

    #################################################################################################################################################################
        html.H2("2. Informations globales de l'établissement", className="my-3"),

        dcc.Store(id="store-horaires-sauvegarde"),

        # Texte introductif expliquant l'objectif de la section
        html.P(texte_explications_informations, style=explication_style),
        
        # Accordéon contenant les sous-sections
        dbc.Accordion([
            # Sous-section : Horaires des journées classiques
            dbc.AccordionItem([
                html.Div([
                    # Explication du fonctionnement de la saisie des horaires
                    html.P(texte_explications_horaires, style=explication_style),
                    # Titre de la sous-section
                    html.H5("2.1.1 Les journées de cours", className="my-3"),

                    # Checklist pour sélectionner les jours   
                    html.P("Sélectionnez le(s) jour(s) de cours :"),
                    dcc.Checklist(
                        id="jours",
                        options=JOURS_SEMAINE,
                        value=[],
                        inline=True, 
                        style= style_liste_choix
                    ),
                    html.Br(),

                    html.P("Sélectionnez le(s) jour(s) n'ayant pas cours l'après-midi :"),
                    dcc.Checklist(
                        id="jours-particuliers",
                        options=JOURS_SEMAINE,
                        value=[],
                        inline=True, 
                        style=style_liste_choix
                    ),
                    html.Br(),

                    html.H5("2.1.2 Sélectionnez les horaires principaux", className="my-3"),
                    # Paragraphe avec info-bulle
                    html.Div([
                        html.P([
                            "Renseignez les horaires des journées classiques/ principales dans le tableau suivant : ",
                            html.I(className="bi bi-info-circle-fill", id="tooltip-horaires-info", style=style_tooltip_info)
                        ], style=style_tooltip),
                        
                        dbc.Tooltip(
                            "Les heures doivent être entre 0 et 23, les minutes entre 0 et 55 (par tranches de 5 min).",
                            target="tooltip-horaires-info",
                            placement="right"
                        )
                    ]),

                    # Tableau pour saisir les horaires
                    html.Div([
                        html.Div([
                            html.Label(description, style=style_labels_horaires),
                            html.Div([
                                dcc.Input(
                                    id={"type": "heure-input", "categorie": "classiques", "index": i},
                                    type="number",
                                    min=0,
                                    max=23,
                                    step=1,
                                    placeholder="HH",
                                    style=style_input_hh_min
                                ),
                                html.Span("H"),
                                dcc.Input(
                                    id={"type": "minute-input", "categorie": "classiques", "index": i},
                                    type="number",
                                    min=0,
                                    max=59,
                                    step=5,
                                    placeholder="MM",
                                    style=style_input_hh_min
                                ),
                                html.Span("MIN")
                            ])
                        ], style=style_tbl_horaires)
                        for i, description in enumerate(HORAIRES_LABELS)
                    ], id="bloc-horaires", style=style_alinea),

                    html.Br(),
                    
        #################################################################################################################################################################
                    html.H5("2.1.3 Les paramètres supplémentaires d'une journée", className="my-3"),
                    # Saisir la durée d'un créneau horaire classique
                    html.Div([
                        html.Label("Quelle est la durée d'un créneau horaire classique ?", style=style_marge_droite),
                        dcc.Input(
                            id="duree-creneau-classique",
                            type="number",
                            min=5,
                            max=180,
                            step=5,
                            placeholder="ex : 55",
                            style=style_input_hh_min
                        ),
                        html.Span("MIN")
                    ], style=style_input),

                    html.Br(),

                    # Saisir la durée des récréations
                    html.Div([
                        html.Label("Quelle est la durée des récréations (du matin et de l'après-midi) ?", style=style_marge_droite),
                        dcc.Input(
                            id="recre",
                            type="number",
                            min=0,
                            max=60,
                            step=5,
                            placeholder="ex : 15",
                            style=style_input_hh_min
                        ),
                        html.Span("MIN")
                    ], style=style_input),

                    html.Br(),
                    # Saisir la durée de la pause méridienne
                    html.Div([
                        html.Label("Quelle est la durée minimum de la pause méridienne ?", style=style_marge_droite),
                        dcc.Input(
                            id="pause-meridienne-heures",
                            type="number",
                            min=0,
                            max=5,
                            placeholder="0",
                            style=style_input_hh_min
                        ),
                        html.Span("H"),
                        dcc.Input(
                            id="pause-meridienne-minutes",
                            type="number",
                            min=0,
                            max=59,
                            step=5,
                            placeholder="30",
                            style=style_input_hh_min
                        ),
                        html.Span("MIN"),
                    ], style=style_input),

                    html.Br(),
                    html.Br(),

    #################################################################################################################################################################
                # # Cette section à été créée pour la réalisation complète d'un emploi du temps, sur une année scolaire. Ce n'est pas utilisé à ce jour par le solver.
                # # Nous laissons la possibilité à ceux qui le voudront de reprendre cette partie. Les callbacks associés sont aussi commentés. 

                    # Sous-section : Calendrier
                #     html.H5("2.1.4 Calendrier : Début des cours, fin des cours et vacances scolaires", className="my-3"),

                #     # Date de rentrée
                #     html.Div([
                #         html.Label("Date de début des cours (Rentrée) :"),
                #         dcc.DatePickerSingle(
                #             id="date-rentree",
                #             date=None,
                #             placeholder="JJ/MM/AAAA",
                #             display_format="DD/MM/YYYY",
                #             initial_visible_month=mois_de_x_n(9),
                #             style=style_date
                #         )
                #     ], style=style_marge_bas),

                #     # Fin d'année scolaire
                #     html.Div([
                #         html.Label("Date de fin des cours (Vacances d'été) :"),
                #         dcc.DatePickerSingle(
                #             id="date-vacances-ete",
                #             date=None,
                #             placeholder="JJ/MM/AAAA",
                #             display_format="DD/MM/YYYY",
                #             initial_visible_month=mois_de_x_n1(7),
                #             style=style_date
                #         )
                #     ], style=style_marge_bas),

                #     # Vacances scolaires
                #     html.Div([
                #         html.H6("Vacances scolaires :"),
                #         html.I(
                #             className="bi bi-info-circle-fill",
                #             id="tooltip-vacances-info",
                #             style=style_tooltip_info
                #         ),
                #         dbc.Tooltip(
                #             "Par défaut, les vacances sont calculées du vendredi soir au lundi de reprise.",
                #             target="tooltip-vacances-info",
                #             placement="right"
                #         )
                #     ], style=style_tooltip),

                #     # Liste des vacances scolaires
                #     html.Div([
                #         html.Div([
                #             html.Span("• Vacances de la Toussaint"),
                #             html.Div([
                #                 html.Span([html.I(className="bi bi-arrow-return-right"), " Du :"], style={"marginLeft": "40px"}),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "toussaint", "role": "debut"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n(10),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #                 html.Span("Au :"),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "toussaint", "role": "fin"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n(10),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #             ], style=style_div_dates)
                #         ], style=style_marge_bas),

                #         html.Div([
                #             html.Span("• Vacances de Noël"),
                #             html.Div([
                #                 html.Span([html.I(className="bi bi-arrow-return-right"), " Du :"], style={"marginLeft": "40px"}),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "noel", "role": "debut"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n(12),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #                 html.Span("Au :"),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "noel", "role": "fin"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n(12),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #             ], style=style_div_dates)
                #         ], style=style_marge_bas),

                #         html.Div([
                #             html.Span("• Vacances d'hiver"),
                #             html.Div([
                #                 html.Span([html.I(className="bi bi-arrow-return-right"), " Du :"], style={"marginLeft": "40px"}),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "hiver", "role": "debut"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n1(2),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #                 html.Span("Au :"),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "hiver", "role": "fin"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n1(2),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #             ], style=style_div_dates)
                #         ], style=style_marge_bas),

                #         html.Div([
                #             html.Span("• Vacances de # printemps"),
                #             html.Div([
                #                 html.Span([html.I(className="bi bi-arrow-return-right"), " Du :"], style={"marginLeft": "40px"}),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "# printemps", "role": "debut"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n1(4),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #                 html.Span("Au :"),
                #                 dcc.DatePickerSingle(
                #                     id={"type": "vacances", "periode": "# printemps", "role": "fin"},
                #                     display_format="DD/MM/YYYY",
                #                     date=None,
                #                     initial_visible_month=mois_de_x_n1(4),
                #                     placeholder="JJ/MM/AAAA",
                #                     style=style_date
                #                 ),
                #             ], style=style_div_dates)
                #         ], style=style_marge_bas),
                #     ], style=style_alinea),
                #     html.Br(),
                ], style=style_accordeons_contenus)
            ], title=html.H4("2.1 Horaires")),

    #################################################################################################################################################################
            # Sous-section : Langues de l'établissement
            dbc.AccordionItem([

                dcc.Store(id="store-langues-sauvegarde"),
                dcc.Store(id="dummy-reload-langues"),

                # Explication du fonctionnement de la saisie des langues
                html.P(texte_explications_langues , style=explication_style),
                
                # LV1
                html.H5("2.2.1 LV1 disponibles", className="my-3"),
                dcc.Store(id="autres-langues-lv1", data=[]),
                dcc.Store(id="nb-champs-lv1", data=0),
                generate_lang_selection("lv1"),
                html.Br(),

                # LV2
                html.H5("2.2.2 LV2 disponibles", className="my-3"),
                dcc.Store(id="autres-langues-lv2", data=[]),
                dcc.Store(id="nb-champs-lv2", data=0),
                generate_lang_selection("lv2"),
                html.Br(),

                # LV3
                html.H5("2.2.3 Avez-vous des LV3 ?", className="my-3"),
                dcc.Store(id="autres-langues-lv3", data=[]),
                dcc.Store(id="nb-champs-lv3", data=0),
                dcc.RadioItems(
                    id="lv3-exists",
                    options=OUI_NON,
                    value="non",
                    inline=True,
                    style=style_liste_choix
                ),
                html.Div(
                    id="lv3-container",
                    children=[
                        html.Br(),
                        html.H6("2.2.3 LV3 disponibles", className="my-3"),
                        generate_lang_selection("lv3"),
                        html.Div(id="autre-langue-container-lv3"),
                        dcc.Store(id=f"autres-langues-lv3", data=[]),
                        html.Br(),
                        html.Div([
                            html.Label("Niveaux concernés par les LV3 :", style=style_marge_bas),
                            dcc.RangeSlider(
                                id="slider-niveaux-lv3",
                                min=0, max=3, step=1, allowCross=False,
                                value=[2, 3],
                                marks={0: "6e", 1: "5e", 2: "4e", 3: "3e"}
                            )
                        ]),
                        html.Br(),
                        html.Div([
                            html.Label("Volume horaire hebdomadaire des LV3 (en heures) :"),
                            dcc.Input(id="volume-lv3", type="number", value=2, min=0, step=0.5, style=style_input_refectoire_langues),
                            html.Span("H")
                        ]),
                        html.Br()
                    ],
                    style=style_non_visible  # masqué si non
                ),

                # LV4
                html.Div(
                    id="lv4-question",
                    children=[
                        html.H5("2.2.4 Avez-vous des LV4 ?", className="my-3"),
                        dcc.RadioItems(
                            id="lv4-exists",
                            options=OUI_NON,
                            value="non",
                            inline=True,
                            style=style_liste_choix
                        )
                    ],
                    style=style_non_visible # masqué si LV3 = non
                ),

                dcc.Store(id="autres-langues-lv4", data=[]),
                dcc.Store(id="nb-champs-lv4", data=0),
                html.Div(
                    id="lv4-container",
                    children=[
                        html.Br(),
                        html.H6("2.2.4 LV4 disponibles", className="my-3"),
                        generate_lang_selection("lv4"),
                        html.Div(id="autre-langue-container-lv4"),
                        dcc.Store(id=f"autres-langues-lv4", data=[]),
                        html.Br(),
                        html.Div([
                            html.Label("Niveaux concernés par les LV4 :", style=style_marge_bas),
                            dcc.RangeSlider(
                                id="slider-niveaux-lv4",
                                min=0, max=3, step=1, allowCross=False,
                                value=[3, 3],
                                marks={0: "6e", 1: "5e", 2: "4e", 3: "3e"}
                            )
                        ]), 
                        html.Br(),   
                        html.Div([
                            html.Label("Volume horaire hebdomadaire des LV4 (en heures) :"),
                            dcc.Input(id="volume-lv4", type="number", value=2, min=0, step=0.5, style=style_input_refectoire_langues),
                            html.Span("H")
                        ]),
                        html.Br()
                    ],
                    style=style_non_visible  # masqué si non
                ),
                html.Br()

            ], title=html.H4("2.2 Langues de l'établissement")),

    #################################################################################################################################################################
            # Sous-section : Options de l'établissement
            dbc.AccordionItem([
                dcc.Store(id="store-options-sauvegarde"),
                html.H5("2.3.1 Options disponibles", className="my-3"),
                html.P(texte_explications_options, style=explication_style),
                # Options proposées
                html.Div([
                    html.Div([
                        html.H6(categorie),
                        dcc.Checklist(
                            id={'type': 'option-checklist', 'categorie': categorie},
                            options=formater_options(options),
                            value=[],
                            style=style_liste_choix,
                            inline=False
                        ),
                        html.Br()
                    ]) for categorie, options in CATEGORIES_OPTIONS.items()
                ]),

                # Autres options
                html.H6("Autres options"),
                # Store pour suivre les autres options saisies
                dcc.Store(id="autres-options-saisies", data=[""]), 
                # Bouton ajouter une autre option
                html.Button([
                    html.I(className="bi bi-plus-lg me-2"),
                    "Ajouter une autre option"
                ], id="add-autre-option", n_clicks=0, style=style_btn_ajouter),
                # Bloc dynamique pour les autres options
                html.Div(id="autres-options-container"),

                html.Div(id="bloc-volumes-par-option"),

                # Volume horaire des options
                html.H5("2.3.2 Volume horaire des options par niveau", className="mt-3"),
                html.P("Sélectionnez un niveau pour consulter ou modifier les volumes horaires des options :"),
                # Dropdown pour sélectionner le niveau
                dcc.Dropdown(
                    id="niveau-options",
                    options=[{"label": n, "value": n} for n in ["6e", "5e", "4e", "3e"]],
                    placeholder="Choisir un niveau...",
                    style=style_dropdown_niveau
                ),
                # Tableau pour saisir les volumes horaires des options
                dash_table.DataTable(
                    id="table-options-par-niveau",
                    columns=[
                        {"name": "Option", "id": "Option", "editable": False},
                        {"name": "Volume horaire hebdomadaire (en H)", "id": "Volume", "editable": True, "type": "numeric"},
                    ],
                    data=[],
                    editable=True,
                    style_table=style_table,
                    style_header=style_header_table,
                    style_cell=style_cell
                ),

                html.Br(),

                dcc.Store(id="niveau-options-precedent", data=None),
                dcc.Store(id="stockage-options-par-niveau", data={})

            ],title=html.H4("2.3 Options de l'établissement")),

        ], style=style_accordeons,
        start_collapsed=True, flush=True, active_item=None),

    #################################################################################################################################################################
        html.Br(),

        html.H2("3. Informations sur les ressources de l'établissement", className="my-4"),
        html.P(texte_explications_ressources, style=explication_style),
        
        dbc.Accordion([
            dbc.AccordionItem([
                html.P(texte_explications_classes, style=explication_style),

                html.Div([  
                    # Format attendu pour chaque colonne
                    html.Div([
                        html.P("Format attendu pour chaque colonne :", style=style_gras),
                        html.Ul([
                            html.Li([html.Span("Classe / Groupe", style=style_gras), " : Texte libre (ex : 6e1, 6ESP1, etc.)."]),
                            html.Li([html.Span("Niveau", style=style_gras), " : 6e, 5e, 4e ou 3e (le \"e\" est automatiquement ajouté si vous écrivez seulement le chiffre)."]),
                            html.Li([html.Span("Nombre d'élèves", style=style_gras), " : Nombre entier uniquement."]),
                            html.Li([html.Span("Classes / Groupes dépendants", style=style_gras), " : Noms des classes / groupes séparés par des virgules qui ont des élèves en commun avec le groupe / la classe de la ligne (ex : 6ESP1, 6ESP2, 6IT1, etc.)."]),
                            html.Li([html.Span("Matière du groupe", style=style_gras), " : Facultatif. À remplir uniquement si la ligne correspond à un groupe (ex : Espagnol, Latin, etc.)."])
                        ], style=style_marge_gauche)
                    ], style=style_format_donnes_info),

                    # Téléchargement d'un exemple de fichier
                    html.Div([
                        dbc.DropdownMenu(
                            label=html.Span([
                                html.I(className="bi bi-file-earmark-arrow-up"),
                                " Télécharger un exemple de fichier"
                            ]),
                            color="primary",
                            className="mb-2",
                            children=[
                                dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-csv me-2"), "Télécharger au format CSV"]), id="download-exemple-csv"),
                                dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-xlsx me-2"), "Télécharger au format XLSX"]), id="download-exemple-xlsx"),
                            ],
                            style=style_btn_telecharger
                        ),
                        dcc.Download(id="telechargement-exemple-classes")
                    ]),

                    # Zone d'importation de fichier 
                    html.Div([
                        dcc.Upload(
                            id="upload-classes",
                            children=html.Div([
                                html.I(className="bi bi-upload me-2"), 
                                "Glissez ou ", html.A("sélectionnez un fichier Excel ou CSV")
                            ]),
                            multiple=True, 
                            style=style_zone_import,
                            accept=".csv,.xls,.xlsx"
                        ),
                        dcc.Store(id="stockage-fichier-classes"),
                        dcc.Store(id="table-classes-vide", data=True),
                        dbc.Modal([
                            dbc.ModalHeader("Importer des classes"),
                            dbc.ModalBody("Le tableau contient déjà des données. Voulez-vous fusionner les nouvelles lignes ou remplacer complètement le tableau ?"),
                            dbc.ModalFooter([
                                dbc.Button("Fusionner", id="btn-fusionner-classes", color="primary", className="me-2"),
                                dbc.Button("Remplacer", id="btn-remplacer-classes", color="danger"),
                            ])
                        ], id="modal-choix-import", is_open=False),

                        html.Div(id="import-classes-message", style=style_message_import)
                    ]),

                    # Générateur de classes
                    html.Div([
                        html.H6("Ajouter plusieurs classes identiques : "),

                        html.Div([
                            html.Div([
                                html.Label("Nombre :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Input(id="nb-classes-generees", type="number", min=1, max=50, value=3, style=style_input_refectoire_langues)
                            ], style=style_input),

                            html.Div([
                                html.Label("Niveau :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Dropdown(
                                    id="niveau-classe-genere",
                                    options=[{"label": n, "value": n} for n in NIVEAUX],
                                    style={"width": "100px"}
                                )
                            ], style=style_input),

                            html.Div([
                                html.Label("Effectif :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Input(id="effectif-classe-genere", type="number", min=1, max=50, value=30, style=style_input_refectoire_langues)
                            ], style=style_input),

                            
                            html.Button([
                                html.I(className="bi bi-plus-lg me-2"),
                                "Générer les classes"
                            ], id="btn-generer-classes", n_clicks=0, style=style_btn_générer)
                        ], style=style_générateurs_items)
                    ], style=style_générateurs),

                    html.Div([
                        # Bouton pour supprimer les données du tableau
                        html.Div([
                            html.Button([
                                html.I(className="bi bi-x-lg me-2"),
                                "Effacer les données du tableau"
                            ], id="btn-effacer-classes", n_clicks=0, style=style_btn_supprimer)
                        ], style=style_bouton_droite),

                        # Tableau pour saisir les classes
                        dash_table.DataTable(
                            id="table-classes",
                            columns=[
                                {"name": "Nom de la classe", "id": "Classe", "type": "text", "editable": True},
                                {"name": "Niveau", "id": "Niveau", "type": "text", "editable": True},
                                {"name": "Nombre d'élèves", "id": "Effectif", "type": "numeric", "editable": True},
                                {"name": "Classes dépendantes", "id": "Dependances", "type": "text", "editable": True},
                                {"name": "Matière du groupe", "id": "MatiereGroupe", "type": "text", "editable": True} 
                            ],
                            data=[], 
                            editable=True,
                            row_deletable=True,
                            style_table=style_table_import,
                            style_header=style_header_table,
                            style_cell=style_cell
                        ),

                        html.Div(id="erreur-classes", style=style_erreur),

                        dcc.Store(id="dummy-stockage-classes"),

                        # Bouton pour ajouter une ligne
                        html.Div([
                            html.Button([
                                html.I(className="bi bi-plus-lg me-2"),
                                "Ajouter une ligne"
                            ], id="ajouter-ligne-classe", n_clicks=0, style=style_btn_ajouter)
                        ], style={**style_marge_bas,**style_marge_haut,**style_marge_gauche})

                    ])   
                ], style=style_saisie_ressources), 
            ], title=html.H4("3.1 Classes et groupes d'élèves")),

    #################################################################################################################################################################
            # 3.2 Salles
            dbc.AccordionItem([
                html.P(texte_explications_salles, style=explication_style),

                html.Div([  
                    # Format attendu pour chaque colonne
                    html.Div([
                            html.P("Format attendu pour chaque colonne :", style=style_gras),
                            html.Ul([
                                html.Li([html.Span("Nom", style=style_gras), " : nom de la salle."]),
                                html.Li([html.Span("Matières autorisées", style=style_gras), " : liste séparée par des virgules (ex : Mathématiques, Physique-Chimie). "
                                "Si vous ne renseignez rien, les matières autorisées seront : le français, les mathématiques, l'histoire-géographie, les langues et l'enseignement moral et civique."]),
                                html.Li([html.Span("Capacité", style=style_gras), " : nombre entier."])
                            ], style=style_marge_gauche)
                        ], style=style_format_donnes_info),

                    # Téléchargement d'un exemple de fichier
                    html.Div([
                        dbc.DropdownMenu(
                            label=html.Span([
                                html.I(className="bi bi-file-earmark-arrow-up"),
                                " Télécharger un exemple de fichier"
                            ]),
                            color="primary",
                            className="mb-2",
                            children=[
                                dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-csv me-2"), "Télécharger au format CSV"]), id="download-exemple-csv"),
                                dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-xlsx me-2"), "Télécharger au format XLSX"]), id="download-exemple-xlsx"),
                            ],
                            style=style_btn_telecharger
                        ),
                        dcc.Download(id="telechargement-exemple-salles")
                    ]),

                    # Zone d'importation de fichier
                    html.Div([
                        dcc.Upload(
                            id="upload-salles",
                            children=html.Div([
                                html.I(className="bi bi-upload me-2"),
                                "Glissez ou ", html.A("sélectionnez un fichier Excel ou CSV")
                            ]),
                            multiple=True,
                            style=style_zone_import,
                            accept=".csv,.xls,.xlsx"
                        ),
                        dcc.Store(id="stockage-fichier-salles"),
                        dcc.Store(id="table-salles-vide", data=True),
                        dbc.Modal([
                            dbc.ModalHeader("Importer des salles"),
                            dbc.ModalBody("Le tableau contient déjà des données. Voulez-vous fusionner les nouvelles lignes ou remplacer complètement le tableau ?"),
                            dbc.ModalFooter([
                                dbc.Button("Fusionner", id="btn-fusionner-salles", color="primary", className="me-2"),
                                dbc.Button("Remplacer", id="btn-remplacer-salles", color="danger"),
                            ])
                        ], id="modal-choix-import-salles", is_open=False),

                        html.Div(id="import-salles-message", style=style_message_import)
                    ]),

                    # Générateur de salles
                    html.Div([
                        html.H6("Ajouter plusieurs salles identiques", style=style_marge_bas),

                        html.Div([
                            html.Div([
                                html.Label("Nombre :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Input(id="nb-salles-generees", type="number", min=1, max=50, value=4, style=style_input_refectoire_langues)
                            ], style=style_input),

                            html.Div([
                                html.Label("Matières autorisées :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Input(id="matieres-salles-generees", type="text", style={**style_input_refectoire_langues, "width": "250px"})
                            ], style=style_input),

                            html.Div([
                                html.Label("Capacité :", style={**style_marge_droite,**style_marge_gauche}),
                                dcc.Input(id="capacite-salle-generee", type="number", min=5, max=100, value=30, style=style_input_refectoire_langues)
                            ], style=style_input),

                            html.Button([ html.I(className="bi bi-plus-lg me-2"), "Générer les salles"], id="btn-generer-salles", n_clicks=0, style=style_btn_générer)
                        ], style=style_générateurs_items)
                    ], style=style_générateurs),

                    html.Div([
                        # Bouton pour supprimer les données du tableau
                        html.Div([
                            html.Button([
                                html.I(className="bi bi-x-lg me-2"),
                                "Effacer les données du tableau"
                            ], id="btn-effacer-salles", n_clicks=0, style=style_btn_supprimer)
                        ], style=style_bouton_droite),

                        # Tableau pour saisir les salles
                        dash_table.DataTable(
                            id="table-salles",
                            columns=[
                                {"name": "Nom", "id": "Nom", "type": "text", "editable": True},
                                {"name": "Matières autorisées", "id": "Matieres", "type": "text", "editable": True},
                                {"name": "Capacité", "id": "Capacite", "type": "numeric", "editable": True},
                            ],
                            data=[],
                            editable=True,
                            row_deletable=True,
                            style_table=style_table_import,
                            style_cell=style_cell,
                            style_header=style_header_table
                        ),

                        html.Div(id="erreur-salles", style=style_erreur),

                        dcc.Store(id="dummy-stockage-salles"),

                        # Bouton pour ajouter une ligne
                        html.Div([
                            html.Button([
                                html.I(className="bi bi-plus-lg me-2"),
                                "Ajouter une ligne"
                                ], id="ajouter-ligne-salle", n_clicks=0, style=style_btn_ajouter)
                        ], style={**style_marge_bas,**style_marge_haut,**style_marge_gauche})
                    ])
                ], style=style_saisie_ressources)
            ], title=html.H4("3.2 Salles")),

    #################################################################################################################################################################
            # 3.3 Professeurs
            dbc.AccordionItem([
                html.P(texte_explications_professeurs, style=explication_style),

                html.Div([  
                    # Format attendu pour chaque colonne
                    html.Div([
                        html.P("Format attendu pour chaque colonne :", style=style_gras),
                        html.Ul([
                            html.Li([html.Span("Civilité", style=style_gras), " : M., Mme, etc."]),
                            html.Li([html.Span("Nom", style=style_gras), " : Nom du professeur."]),
                            html.Li([html.Span("Prénom", style=style_gras), " : Prénom du professeur."]),
                            html.Li([html.Span("Niveaux enseignés", style=style_gras), " : Liste séparée par des virgules (ex : 6e,5e)."]),
                            html.Li([html.Span("Matières", style=style_gras), " : Liste séparée par des virgules (ex : Mathématiques,Physique-chimie)."]),
                            html.Li([html.Span("Volume horaire par semaine", style=style_gras), " : Nombre (ex : 18)."]),
                            html.Li([html.Span("Durée préférée", style=style_gras), " : ex : 1, 1.5, 2..."]),
                            html.Li([html.Span("Salle de préférence", style=style_gras), " : Nom d'une salle (facultatif). Si vide, l'outil affectera une salle autorisée pour la matière."])
                        ], style=style_marge_gauche)
                    ], style=style_format_donnes_info),
                    
                    # Téléchargement d'un exemple de fichier
                html.Div([
                    dbc.DropdownMenu(
                        label=html.Span([
                            html.I(className="bi bi-file-earmark-arrow-up"),
                            " Télécharger un exemple de fichier"
                        ]),
                        color="primary",
                        className="mb-2",
                        children=[
                            dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-csv me-2"), "Télécharger au format CSV"]), id="download-exemple-csv"),
                            dbc.DropdownMenuItem(html.Span([html.I(className="bi bi-filetype-xlsx me-2"), "Télécharger au format XLSX"]), id="download-exemple-xlsx"),
                        ],
                        style=style_btn_telecharger
                    ),
                    dcc.Download(id="telechargement-exemple-professeurs")
                ]),

                # Zone d'importation de fichier
                html.Div([
                    dcc.Upload(
                        id="upload-professeurs",
                        children=html.Div([
                            html.I(className="bi bi-upload me-2"), 
                            "Glissez ou ", html.A("sélectionnez un fichier Excel ou CSV")
                        ]),
                        multiple=True, 
                        style=style_zone_import,
                        accept=".csv,.xls,.xlsx"
                    ),
                    dcc.Store(id="stockage-fichier-professeurs"),
                    dcc.Store(id="table-professeurs-vide", data=True),
                    dbc.Modal([
                        dbc.ModalHeader("Importer des professeurs"),
                        dbc.ModalBody("Le tableau contient déjà des données. Voulez-vous fusionner les nouvelles lignes ou remplacer complètement le tableau ?"),
                        dbc.ModalFooter([
                            dbc.Button("Fusionner", id="btn-fusionner-professeurs", color="primary", className="me-2"),
                            dbc.Button("Remplacer", id="btn-remplacer-professeurs", color="danger"),
                        ])
                    ], id="modal-choix-import-professeurs", is_open=False),

                    html.Div(id="import-professeurs-message", style=style_message_import)
                ]),

                # Générateur de professeurs
                html.Div([
                    html.H6("Ajouter plusieurs professeurs identiques", style=style_marge_bas),

                    html.Div([
                        html.Div([
                            html.Label("Nombre :", style={**style_marge_droite,**style_marge_gauche}),
                            dcc.Input(id="nb-profs-genere", type="number", min=1, max=50, placeholder="ex : 2", style=style_input_refectoire_langues)
                        ], style=style_input),

                        html.Div([
                            html.Label("Volume horaire :", style={**style_marge_droite,**style_marge_gauche}),
                            dcc.Input(id="volume-prof-genere", type="number", min=1, max=40, placeholder="ex : 20", style=style_input_refectoire_langues)
                        ], style=style_input),

                        html.Div([
                            html.Label("Durée préférée :", style={**style_marge_droite,**style_marge_gauche}),
                            dcc.Input(id="duree-prof-genere", type="text", placeholder="ex : 1.5", style=style_input_refectoire_langues)
                        ], style=style_input),

                        html.Div([
                            html.Label("Niveaux :", style={**style_marge_droite,**style_marge_gauche}),
                            dcc.Dropdown(
                                id="niveaux-prof-genere",
                                options=[{"label": n, "value": n} for n in NIVEAUX],
                                multi=True,
                                style={**style_input_refectoire_langues, "width": "180px"}
                            )
                        ], style={**style_input, "flexGrow": "1"}),

                        html.Button([
                            html.I(className="bi bi-plus-lg me-2"),
                            "Générer les professeurs"], id="btn-generer-profs", n_clicks=0, style=style_btn_générer)
                    ], style=style_générateurs_items)
                ], style=style_générateurs),

                html.Div([
                    # Bouton pour supprimer les données du tableau
                    html.Div([
                        html.Button([
                            html.I(className="bi bi-x-lg me-2"),
                            "Effacer les données du tableau"
                        ], id="btn-effacer-professeurs", n_clicks=0, style=style_btn_supprimer)
                    ], style=style_bouton_droite),

                    # Tableau pour saisir les professeurs
                    dash_table.DataTable(
                        id="table-professeurs",
                        columns=[
                            {"name": "Civilité", "id": "Civilite", "type": "text", "editable": True},
                            {"name": "Nom", "id": "Nom", "type": "text", "editable": True},
                            {"name": "Prénom", "id": "Prenom", "type": "text", "editable": True},
                            {"name": "Niveaux enseignés", "id": "Niveaux", "type": "text", "editable": True},
                            {"name": "Matières", "id": "Matieres", "type": "text", "editable": True},
                            {"name": "Volume horaire/semaine", "id": "Volume", "type": "numeric", "editable": True},
                            {"name": "Durée préférée", "id": "Duree", "type": "text", "editable": True},
                            {"name": "Salle de préférence", "id": "SallePref", "type": "text", "editable": True} 
                        ],  
                        data=[],
                        editable=True,
                        row_deletable=True,
                        style_table=style_table_import,
                        style_cell=style_cell,
                        style_header=style_header_table
                    ),
                    html.Div(id="erreur-professeurs", style=style_erreur),

                    dcc.Store(id="dummy-stockage-professeurs"),

                    # Bouton pour ajouter une ligne
                    html.Div([
                        html.Button([
                            html.I(className="bi bi-plus-lg me-2"),
                            "Ajouter une ligne"
                        ], id="ajouter-ligne-professeur", n_clicks=0, style=style_btn_ajouter)
                    ], style={**style_marge_bas,**style_marge_haut,**style_marge_gauche})
                ])
            ], style=style_saisie_ressources)
        ], title=html.H4("3.3 Professeurs")),

        ], style=style_accordeons, start_collapsed=True, flush=True, active_item=None),  

        # Boutons de navigation
        html.Div([
            html.Button([
                html.I(className="bi bi-arrow-left me-2"),
                "Page précédente"
            ], id="btn-precedent", n_clicks=0, className="btn btn-secondary", style=style_btn_suivant),

            html.Button([
                "Page suivante",
                html.I(className="bi bi-arrow-right ms-2")
            ], id="btn-suivant", n_clicks=0, className="btn btn-primary", style=style_btn_suivant)
        ], style=style_boutons_bas_page),

        dcc.Location(id="redirect-suivant", refresh=True)

    ], id="layout-informations", style=global_page_style)

################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################
@app.callback(
    Output("reset-message", "children"),
    Output("initialisation-donnees", "data"),
    Input("confirm-reset", "n_clicks"),
    Input("import-json", "contents"),
    State("import-json", "filename"),
    prevent_initial_call=False
)
def gerer_reset_ou_import(confirm_click, json_contents, json_filename):
    """
    Gère l'import d'un fichier JSON ou la réinitialisation des données de l'application.

    Deux comportements sont possibles selon l'élément déclencheur :
    - Si l'utilisateur clique sur le bouton "Réinitialiser", un squelette vierge est généré
      et sauvegardé dans data/data_interface.json, puis utilisé pour recharger l'interface.
    - Si un fichier JSON est importé, il est décodé et utilisé comme nouvelle base de données.
      Son contenu est sauvegardé puis transmis à l'interface.
    
    En cas d'erreur lors du décodage du fichier importé, un message d'erreur est affiché
    et les données précédentes sont conservées.

    Args:
        confirm_click (int): Nombre de clics sur le bouton "Réinitialiser".
        json_contents (str): Contenu encodé en base64 du fichier JSON importé.
        json_filename (str): Nom du fichier JSON importé.

    Returns:
        tuple:
            - str: Message à afficher à l'utilisateur (confirmation ou erreur).
            - dict | dash.no_update: Données JSON réinitialisées ou importées, ou dash.no_update en cas d'erreur.
    """
    triggered = ctx.triggered_id

    if triggered == "confirm-reset":
        donnees = generer_squelette_json_interface()
        os.makedirs("data", exist_ok=True)
        with open("data/data_interface.json", "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        return "Données réinitialisées avec succès.", donnees

    if triggered == "import-json" and json_contents and json_filename.endswith(".json"):
        try:
            content_type, content_string = json_contents.split(',')
            decoded = base64.b64decode(content_string)
            donnees = json.loads(decoded.decode('utf-8'))

            os.makedirs("data", exist_ok=True)
            with open("data/data_interface.json", "w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False, indent=2)

            return f"Données importées depuis « {json_filename} ». ", donnees
        except Exception as e:
            return f"Erreur lors de l'import : {e}", dash.no_update

    raise PreventUpdate

######################################################################
# SECTION 1.1 - Programme national
######################################################################
@callback(
    Output("emc-inclus", "value"),
    Output("emc-volume", "value"),
    Input("initialisation-donnees", "data"),
    State("niveau-programme", "value"),
    prevent_initial_call=True
)
def charger_emc_au_chargement(_, niveau):
    """
    Initialise les valeurs de la discipline EMC lors du premier chargement de la page.

    Si aucun niveau n'est encore sélectionné, on suppose par défaut le niveau "6e".

    Args:
        _ (dict): Données chargées dans le Store "initialisation-donnees".
        niveau (str): Niveau sélectionné (ex : "6e").

    Returns:
        tuple:
            - str: Valeur du champ "emc-inclus" ("oui" ou "non").
            - float|None: Volume horaire associé à l'EMC.
    """
    if not niveau:
        niveau = "6e"

    data = charger_donnees_interface()
    emc = data.get("4_programme_national", {}).get("emc", {}).get(niveau, {"inclus": "oui", "volume": None})
    return emc.get("inclus", "oui"), emc.get("volume", None)

@callback(
    Output("emc-inclus", "value", allow_duplicate=True),
    Output("emc-volume", "value", allow_duplicate=True),
    Input("niveau-programme", "value"),
    prevent_initial_call=True
)
def charger_emc(niveau):
    """
    Met à jour les champs relatifs à l'EMC lorsqu'un niveau est sélectionné.

    Args:
        niveau (str): Niveau scolaire sélectionné (ex : "5e").

    Returns:
        tuple:
            - str: Valeur du champ "emc-inclus".
            - float|None: Volume horaire associé à l'EMC pour ce niveau.
    """
    data = charger_donnees_interface()
    emc = data.get("4_programme_national", {}).get("emc", {}).get(niveau, {"inclus": "oui", "volume": None})
    return emc.get("inclus", "oui"), emc.get("volume", None)

@callback(
    Output("emc-inclus", "value", allow_duplicate=True),
    Output("emc-volume", "value", allow_duplicate=True),
    Input("initialisation-donnees", "data"),
    State("niveau-programme", "value"),
    prevent_initial_call=True
)

def initialiser_emc_au_chargement(_, niveau):
    """
    Réinitialise les champs relatifs à l'EMC lors d'un reset ou chargement de fichier JSON.

    Utilisé pour réinitialiser l'état du formulaire EMC au rechargement de données.

    Args:
        _ (dict): Données de "initialisation-donnees".
        niveau (str): Niveau sélectionné.

    Returns:
        tuple:
            - str: "oui" ou "non" selon que l'EMC est incluse.
            - float|None: Volume horaire d'EMC enregistré (si disponible).
    """
    data = charger_donnees_interface()
    emc = data.get("4_programme_national", {}).get("emc", {}).get(niveau or "6e", {})
    return emc.get("inclus", "oui"), emc.get("volume", None)

# Charge les données du programme national pour le niveau sélectionné
@callback(
    Output("table-programme-par-niveau", "data"),
    Input("niveau-programme", "value"),
    Input("emc-inclus", "value"),
)
def afficher_programme_et_corriger_emc(niveau, emc_inclus):
    """
    Met à jour le tableau du programme national pour un niveau donné,
    en ajustant le nom de la discipline "Histoire-Géographie" selon l'inclusion ou non de l'EMC.

    Args:
        niveau (str): Niveau sélectionné (ex : "4e").
        emc_inclus (str): "oui" ou "non", selon que l'EMC est incluse dans l'horaire.

    Returns:
        list[dict]: Liste de disciplines avec noms et volumes à afficher dans le tableau.
    """
    if not niveau:
        raise PreventUpdate

    data = charger_donnees_interface()
    prog = data.get("4_programme_national", {})
    lignes = prog.get(niveau, [])

    # Nom attendu selon emc_inclus
    nom_avec_emc = "Histoire-Géographie-EMC"
    nom_sans_emc = "Histoire-Géographie"

    nouvelles_lignes = []
    for ligne in lignes:
        nom = ligne.get("Discipline", "")
        vol = ligne.get("VolumeHoraire", None)

        if "histoire-géographie" in nom.lower():
            if emc_inclus == "oui":
                nouvelles_lignes.append({"Discipline": nom_avec_emc, "VolumeHoraire": vol})
            else:
                nouvelles_lignes.append({"Discipline": nom_sans_emc, "VolumeHoraire": vol})
        else:
            nouvelles_lignes.append(ligne)

    return nouvelles_lignes

@app.callback(
    Output("message-validation-programme", "children"),
    Input("table-programme-par-niveau", "data"),
    Input("emc-inclus", "value"),
    Input("emc-volume", "value"),
    State("niveau-programme", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_programme_niveau(table_data, emc_inclus, emc_volume, niveau, freeze):
    """
    Sauvegarde les volumes horaires saisis/modifiés pour un niveau donné
    dans la section "Programme national".

    La sauvegarde est déclenchée dès qu'un niveau est sélectionné ou modifié.

    Args:
        niveau (str): Niveau concerné.
        lignes_tableau (list[dict]): Contenu du tableau modifié.

    Returns:
        dash.no_update: Aucun retour visuel attendu.
    """
    if freeze:
        raise PreventUpdate
    if not niveau or not isinstance(table_data, list) or len(table_data) == 0:
        # On ne sauvegarde rien si le tableau est vide ou niveau invalide
        return dash.no_update

    data = charger_donnees_interface()

    # Nettoyer EMC du tableau
    table_data_sans_emc = [
        d for d in table_data if "enseignement moral et civique" not in d.get("Discipline", "").lower()
    ]

    ancien_prog = data.get("4_programme_national", {}).get(niveau, [])
    ancien_emc = data.get("4_programme_national", {}).get("emc", {}).get(niveau, {})

    # Vérifie si les données ont vraiment changé
    if (table_data_sans_emc == ancien_prog and
        ancien_emc.get("inclus") == emc_inclus and
        ancien_emc.get("volume") == (emc_volume if emc_inclus == "non" else None)):
        # Pas de changement, on ne sauvegarde pas
        return dash.no_update

    mettre_a_jour_section_interface(f"4_programme_national.{niveau}", table_data_sans_emc)
    mettre_a_jour_section_interface(f"4_programme_national.emc.{niveau}", {
        "inclus": emc_inclus,
        "volume": emc_volume if emc_inclus == "non" else None
    })
    return f"Programme de {niveau} enregistré."

@app.callback(
    Output("stockage-emc-par-niveau", "data"),
    Input("emc-inclus", "value"),
    Input("emc-volume", "value"),
    Input("niveau-programme", "value"),
    State("stockage-emc-par-niveau", "data"),
    prevent_initial_call=True
)
def maj_stockage_emc(emc_inclus, emc_volume, niveau, stockage):
    """
    Met à jour temporairement le stockage local des paramètres EMC par niveau.

    Cette fonction permet d'enregistrer dans le dcc.Store les valeurs
    sélectionnées pour l'inclusion de l'EMC et son volume horaire.

    - Lors d'un changement de champ EMC (inclus/volume), le stockage est mis à jour.
    - Lors d'un changement de niveau, le stockage est simplement renvoyé tel quel.

    Args:
        emc_inclus (str): "oui" ou "non", selon l'inclusion d'EMC.
        emc_volume (float|None): Volume horaire saisi (si non inclus).
        niveau (str): Niveau scolaire concerné.
        stockage (dict): Données en cours du dcc.Store "stockage-emc-par-niveau".

    Returns:
        dict: Nouveau contenu du stockage EMC par niveau.
    """
    triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    stockage = stockage or {}

    if triggered in ["emc-inclus", "emc-volume"]:
        if not niveau:
            raise PreventUpdate
        stockage[niveau] = {"inclus": emc_inclus, "volume": emc_volume}
        return stockage

    if triggered == "niveau-programme":
        # Lors du changement de niveau, on peut juste retourner le stockage actuel
        # ou initialiser si besoin (mais idéalement on lit dans le JSON pour l'affichage)
        return stockage

    raise PreventUpdate

@callback(
    Output("dummy-stockage-emc", "data"),
    Input("emc-inclus", "value"),
    Input("emc-volume", "value"),
    State("niveau-programme", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_emc_directement(inclus, volume, niveau, freeze):
    """
    Enregistre directement dans le JSON les valeurs de la discipline EMC pour un niveau donné.

    La sauvegarde est déclenchée à chaque modification, sauf si freeze est activé.

    Args:
        inclus (str): "oui" ou "non" pour inclusion d'EMC.
        volume (float|None): Volume horaire si EMC non incluse.
        niveau (str): Niveau scolaire sélectionné.
        freeze (bool): Si True, empêche toute sauvegarde.

    Returns:
        dash.no_update: Pas de sortie visible.
    """
    if freeze:
        raise PreventUpdate
    if not niveau:
        raise PreventUpdate

    volume_final = volume if inclus == "non" and volume not in [None, ""] else None
    mettre_a_jour_section_interface(f"4_programme_national.emc.{niveau}", {
        "inclus": inclus,
        "volume": volume_final
    })
    return dash.no_update

# Affiche le champ de volume horaire pour l'EMC uniquement si l'utilisateur indique qu'il n'est pas inclus
@app.callback(
    Output("bloc-emc-volume", "style"),
    Input("emc-inclus", "value")
)
def afficher_volume_emc(val):
    """
    Affiche ou masque le champ de saisie du volume horaire pour l'EMC,
    en fonction du choix "oui"/"non" pour son inclusion.

    Args:
        val (str): Valeur de "emc-inclus", soit "oui" soit "non".

    Returns:
        dict: Style CSS à appliquer (visible ou caché).
    """
    if val == "non":
        return style_marge_haut
    return style_non_visible

# Sauvegarde les données du programme pour le niveau précédent avant d'en changer
@callback(
    Output("niveau-programme-precedent", "data", allow_duplicate=True),
    Input("niveau-programme", "value"),
    State("niveau-programme-precedent", "data"),
    State("table-programme-par-niveau", "data"),
    State("emc-inclus", "value"),
    State("emc-volume", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_ancien_programme(niveau_actuel, niveau_precedent, table_data, emc_inclus, emc_volume, freeze):
    """
    Sauvegarde les données du programme national (général et EMC) pour le niveau précédemment sélectionné,
    juste avant un changement de niveau.

    Enregistre :
    - Le tableau principal de disciplines et volumes horaires ;
    - Le bloc EMC associé (inclusion et volume éventuel).

    Args:
        niveau_actuel (str): Niveau nouvellement sélectionné.
        niveau_precedent (str): Niveau actuellement visible à sauvegarder.
        table_data (list[dict]): Données du tableau table-programme-par-niveau.
        emc_inclus (str): "oui" ou "non" pour EMC.
        emc_volume (float|None): Volume horaire d'EMC (si non incluse).
        freeze (bool): Si True, empêche la sauvegarde.

    Returns:
        str: Niveau actuel (à stocker comme nouveau "niveau précédent").
    """
    if freeze:
        raise PreventUpdate

    # Si aucun niveau précédent n'était sélectionné, on ne sauvegarde rien
    if not niveau_precedent or not isinstance(table_data, list):
        return niveau_actuel

    # Mise à jour ciblée du programme général
    mettre_a_jour_section_interface(f"4_programme_national.{niveau_precedent}", table_data)

    # Mise à jour ciblée de la section EMC
    volume_final = emc_volume if emc_inclus == "non" and emc_volume not in [None, ""] else None
    mettre_a_jour_section_interface(f"4_programme_national.emc.{niveau_precedent}", {
        "inclus": emc_inclus,
        "volume": volume_final
    })

    return niveau_actuel

###############################################################################
# SECTION 1.2 - Horaires
###############################################################################
@callback(
    Output("jours", "value"),
    Output("jours-particuliers", "value"),
    Input("layout-informations", "id")
    )
def prefill_jours_horaires(_):
    """
    Préremplit les jours classiques et les jours particuliers affichés dans la configuration des horaires.

    Cette fonction est appelée au chargement de la page, à partir des données enregistrées
    dans le fichier JSON.

    Args:
        _ : Identifiant de la page (non utilisé, nécessaire pour déclencher le callback).

    Returns:
        tuple:
            - list[str]: Jours classiques sélectionnés.
            - list[str]: Jours particuliers sélectionnés.
    """
    data = charger_donnees_interface()
    jc = data.get("1_horaires", {}).get("jours_classiques", [])
    jp = data.get("1_horaires", {}).get("jours_particuliers", [])
    return jc, jp

@callback(
    Output({"type": "heure-input", "categorie": MATCH, "index": MATCH}, "value"),
    Output({"type": "minute-input", "categorie": MATCH, "index": MATCH}, "value"),
    Input("layout-informations", "id"),
    State({"type": "heure-input", "categorie": MATCH, "index": MATCH}, "id")
)
def prefill_horaires(_, ident):
    """
    Préremplit chaque champ horaire individuel (heure + minute) à partir des données JSON,
    pour un créneau donné (classique ou particulier), selon son index et sa catégorie.

    A ce jour, on ne gère pas les horaires particulier, la fonction est faite pour fonctionner 
    encore le jour où l'on ajoutera les horaires particuliers (si la structure reste la même que pour les jours classiques.)

    Cette fonction est utilisée pour restaurer les valeurs des sélecteurs d'heure après
    un rechargement ou une navigation.

    Args:
        _ : Identifiant de la page (nécessaire pour déclenchement).
        ident (dict): Dictionnaire contenant :
            - "categorie": "classique" ou "particulier"
            - "index": position du créneau dans la liste

    Returns:
        tuple:
            - int|None: Heure à préremplir (ou None si non disponible)
            - int|None: Minute à préremplir (ou None si non disponible)
    """
    data = charger_donnees_interface().get("1_horaires", {})
    categorie = ident["categorie"]  # "classique" ou "particulier"
    index = ident["index"]
    label = HORAIRES_LABELS[index]
    horaire_str = data.get(f"horaires_{categorie}", {}).get(label)

    if horaire_str and ":" in horaire_str:
        h, m = horaire_str.split(":")
        return int(h), int(m)
    return None, None


@callback(
    Output("duree-creneau-classique", "value"),
    Output("recre", "value"),
    Output("pause-meridienne-heures", "value"),
    Output("pause-meridienne-minutes", "value"),
    Input("layout-informations", "id")
)
def prefill_infos_journee(_):
    """
    Prérenseigne les informations globales de la journée scolaire :
    - Durée des créneaux ;
    - Récréations ;
    - Pause méridienne.

    Ces valeurs sont extraites du fichier JSON et utilisées pour remplir
    les champs correspondants dans l'interface.

    Args:
        _ : Identifiant de la page (utilisé uniquement pour déclenchement automatique).

    Returns:
        tuple:
            - int|None: Durée d'un créneau (en minutes).
            - int|None: Durée des récréations.
            - int: Heures de la pause méridienne.
            - int: Minutes de la pause méridienne.
    """
    data = charger_donnees_interface()
    horaires = data.get("1_horaires", {})
    pause = horaires.get("pause_meridienne", "00:00")
    h, m = pause.split(":") if ":" in pause else ("0", "0")
    return horaires.get("duree_creneau", None), horaires.get("recreations", None), int(h), int(m)

# @callback(
#     Output({"type": "vacances", "periode": ALL, "role": ALL}, "date"),
#     Input("layout-informations", "id")
# )
# def prefill_dates_calendrier(_):
    # """
    # Préremplit les champs de date des vacances scolaires pour chaque période (Toussaint, Noël, Hiver, Printemps).

    # Les dates sont extraites depuis la section "1_horaires" du fichier JSON, et restituées
    # sous forme de liste ordonnée correspondant à tous les composants DatePicker utilisés pour les vacances.

    # Args:
    #     _ : Identifiant de la page (non utilisé, sert uniquement de déclencheur).

    # Returns:
    #     list[str|None]: Liste des dates de début et de fin pour chaque période de vacances,
    #                     ou None si aucune valeur n'est enregistrée.
    # """
#     data = charger_donnees_interface()
#     vacances = data.get("1_horaires", {}).get("vacances", {})

#     ids = [
#         {"periode": "toussaint", "role": "debut"},
#         {"periode": "toussaint", "role": "fin"},
#         {"periode": "noel", "role": "debut"},
#         {"periode": "noel", "role": "fin"},
#         {"periode": "hiver", "role": "debut"},
#         {"periode": "hiver", "role": "fin"},
#         {"periode": "# printemps", "role": "debut"},
#         {"periode": "# printemps", "role": "fin"},
#     ]

#     sorties = [
#         vacances.get(item["periode"], {}).get(item["role"], None)
#         for item in ids
#     ]

#     return sorties

# @callback(
#     Output("date-rentree", "date"),
#     Output("date-vacances-ete", "date"),
#     Input("layout-informations", "id")
# )
# def afficher_dates_depuis_json(_):
    # """
    # Préremplit la date de rentrée scolaire et celle des vacances d'été à partir des données enregistrées.

    # Nettoie les champs vides ou mal formatés avant de les renvoyer à l'interface.

    # Args:
    #     _ : Identifiant de la page (non utilisé, déclencheur de chargement).

    # Returns:
    #     tuple:
    #         - str|None: Date de rentrée scolaire (format ISO ou None).
    #         - str|None: Date des vacances d'été (format ISO ou None).
    # """
#     data = charger_donnees_interface().get("1_horaires", {})
#     def corriger(val): return val if val and val.strip() else None
#     return corriger(data.get("date_rentree", "")), corriger(data.get("date_vacances_ete", ""))

#######################################
# Met à jour la liste des jours particuliers
@callback(
    Output("jours-particuliers", "options", allow_duplicate=True),
    Output("jours-particuliers", "value", allow_duplicate=True),
    Input("jours", "value"),
    prevent_initial_call=True
)
def maj_jours_sans_apresmidi(jours_selectionnes):
    """
    Met à jour dynamiquement les options du menu déroulant "Jours sans après-midi"
    en fonction des jours sélectionnés comme jours classiques.

    Le mercredi est pré-coché automatiquement s'il est présent.

    Args:
        jours_selectionnes (list[str]): Liste des jours cochés dans le menu principal des jours.

    Returns:
        tuple:
            - list[dict]: Liste des options à afficher dans le second menu déroulant.
            - list[str]: Valeurs sélectionnées par défaut (ex. ["Mercredi"]).
    """
    if not jours_selectionnes:
        return [], []

    # Tri dans l'ordre logique des jours
    jours_ordonnes = [j for j in ORDRE_JOURS if j in jours_selectionnes]

    options = [{"label": f" {j}", "value": j} for j in jours_ordonnes]
    value = ["Mercredi"] if "Mercredi" in jours_ordonnes else []

    return options, value
    return options, preselection

#######################################
# Corrige les horaires du tableau principal en les forçant au format HH:MM
@app.callback(
    Output('table-horaires', 'data'),
    Input('table-horaires', 'data'),
    prevent_initial_call=True
)
def valider_horaires(rows):
    """
    Corrige les horaires du tableau principal des créneaux en forçant le format "HH:MM".

    Chaque valeur est validée individuellement grâce à la fonction valider_format_horaire.

    Args:
        rows (list[dict]): Liste des lignes du tableau principal à valider.

    Returns:
        list[dict]: Lignes mises à jour avec les horaires corrigés.
    """
    for row in rows:
        row["Horaire"] = valider_format_horaire(row.get("Horaire", ""))
    return rows

# Corrige les horaires du tableau des jours particuliers
@app.callback(
    Output('table-horaires-particuliers', 'data'),
    Input('table-horaires-particuliers', 'data'),
    prevent_initial_call=True
)
def valider_horaires_part(rows):
    """
    Corrige les horaires du tableau des jours particuliers (ex. mercredi spécifique),
    en appliquant le format "HH:MM".

    Args:
        rows (list[dict]): Données du tableau des horaires particuliers.

    Returns:
        list[dict]: Données corrigées avec des horaires au bon format.
    """
    for row in rows:
        row["Horaire"] = valider_format_horaire(row.get("Horaire", ""))
    return rows

# @callback(
#     Output({"type": "vacances", "periode": MATCH, "role": "fin"}, "date", allow_duplicate=True),
#     Input({"type": "vacances", "periode": MATCH, "role": "debut"}, "date"),
#     prevent_initial_call=True
# )
# def completer_date_fin(date_debut):
    # """
    # Calcule automatiquement une date de fin de vacances à partir d'une date de début.

    # - Si la date de début est un vendredi, la date de fin est le dimanche du même week-end (+2 jours).
    # - Sinon, la date de fin est fixée à 9 jours après la date de début.

    # Args:
    #     date_debut (str): Date de début des vacances (format ISO "YYYY-MM-DD").

    # Returns:
    #     str: Date de fin estimée (format ISO "YYYY-MM-DD").
    # """
#     from datetime import datetime, timedelta
#     if not date_debut:
#         raise PreventUpdate

#     d = datetime.strptime(date_debut, "%Y-%m-%d")

#     # Si vendredi : fin = dimanche même week-end
#     if d.weekday() == 4:
#         date_fin = d + timedelta(days=2)
#     else:
#         date_fin = d + timedelta(days=9)

#    return date_fin.strftime("%Y-%m-%d")

# @callback(
#     Output({"type": "vacances", "periode": MATCH, "role": "debut"}, "date", allow_duplicate=True),
#     Input({"type": "vacances", "periode": MATCH, "role": "fin"}, "date"),
#     prevent_initial_call=True
# )
# def completer_date_debut(date_fin):
    # """
    # Calcule automatiquement une date de début de vacances à partir d'une date de fin.

    # La date de début correspond toujours au lundi de la semaine de la date de fin.

    # Args:
    #     date_fin (str): Date de fin des vacances (format ISO "YYYY-MM-DD").

    # Returns:
    #     str: Date de début estimée (format ISO "YYYY-MM-DD").
    # """
#     from datetime import datetime, timedelta
#     if not date_fin:
#         raise PreventUpdate

#     d = datetime.strptime(date_fin, "%Y-%m-%d")

#     # On revient au lundi de la même semaine
#     date_debut = d - timedelta(days=d.weekday())
#     return date_debut.strftime("%Y-%m-%d")

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True), 
    Input("jours", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_jours_classiques(data, freeze):
    """
    Sauvegarde la sélection des jours classiques (ex : lundi à vendredi) dans le fichier JSON.

    Args:
        data (list[str]): Liste des jours sélectionnés par l'utilisateur.
        freeze (bool): Si True, empêche toute modification.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("1_horaires.jours_classiques", data)
    return dash.no_update

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True), 
    Input("jours-particuliers", "value"),
    State("freeze-callbacks", "data"), 
    prevent_initial_call=True)
def save_jours_particuliers(data, freeze):
    """
    Sauvegarde la sélection des jours particuliers (ex : mercredi, vendredi...) dans le JSON.

    Args:
        data (list[str]): Jours particuliers sélectionnés.
        freeze (bool): Si True, empêche toute modification.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("1_horaires.jours_particuliers", data)
    return dash.no_update

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
    Input({"type": "heure-input", "categorie": ALL, "index": ALL}, "value"),
    Input({"type": "minute-input", "categorie": ALL, "index": ALL}, "value"),
    State({"type": "heure-input", "categorie": ALL, "index": ALL}, "id"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_horaires(heures, minutes, ids, freeze):
    """
    Enregistre dans le fichier JSON les horaires configurés manuellement pour chaque créneau.

    Les horaires sont construits à partir de l'heure et des minutes saisies,
    puis enregistrés dans les sections "horaires_classique" ou "horaires_particulier"
    selon la catégorie.

    Args:
        heures (list[int|None]): Heures sélectionnées pour chaque créneau.
        minutes (list[int|None]): Minutes sélectionnées pour chaque créneau.
        ids (list[dict]): Identifiants de chaque champ horaire (catégorie + index).
        freeze (bool): Si True, empêche toute sauvegarde.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    horaires = {}
    for h, m, ident in zip(heures, minutes, ids):
        index = ident["index"]
        categorie = ident["categorie"]
        label = HORAIRES_LABELS[index]
        h_val = int(h) if h is not None else None
        m_val = int(m) if m is not None else 0  # Si minutes absentes, considérer 00
        horaire = f"{h_val:02d}:{m_val:02d}" if h_val is not None else ""
        if categorie not in horaires:
            horaires[categorie] = {}
        horaires[categorie][label] = horaire
    for cat, valeurs in horaires.items():
        mettre_a_jour_section_interface(f"1_horaires.horaires_{cat}", valeurs)
    return dash.no_update

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True), 
    Input("duree-creneau-classique", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_duree_creneau(val, freeze):
    """
    Sauvegarde la durée d'un créneau (en minutes) dans la configuration des horaires.

    Args:
        val (int|None): Valeur saisie pour la durée des créneaux.
        freeze (bool): Si True, désactive la sauvegarde.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("1_horaires.duree_creneau", val)
    return dash.no_update

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True), 
    Input("recre", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_recreations(val, freeze):
    """
    Enregistre la durée des récréations dans la configuration horaire.

    Args:
        val (int|None): Valeur saisie pour la durée des récréations.
        freeze (bool): Si True, empêche la modification.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("1_horaires.recreations", val)
    return dash.no_update

# @callback(
#     Output("store-horaires-sauvegarde", "data", allow_duplicate=True), 
#     Input("date-rentree", "date"), 
#     State("freeze-callbacks", "data"),
#     prevent_initial_call=True)
# def save_date_rentree(date, freeze):
    # """
    # Sauvegarde la date de rentrée scolaire dans le fichier JSON.

    # Args:
    #     date (str): Date de rentrée au format ISO (YYYY-MM-DD).
    #     freeze (bool): Si True, empêche la sauvegarde.

    # Returns:
    #     dash.no_update
    # """
#     if freeze:  
#         raise PreventUpdate
#     mettre_a_jour_section_interface("1_horaires.date_rentree", date)
#     return dash.no_update

# @callback(
#     Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
#     Input("date-vacances-ete", "date"), 
#     State("freeze-callbacks", "data"),
#     prevent_initial_call=True)
# def save_date_vacances(date, freeze):
    # """
    # Sauvegarde la date des vacances d'été dans la configuration de l'établissement.

    # Args:
    #     date (str): Date de fin d'année (vacances d'été) au format ISO.
    #     freeze (bool): Si True, empêche la sauvegarde.

    # Returns:
    #     dash.no_update
    # """
#     if freeze:
#         raise PreventUpdate
#     mettre_a_jour_section_interface("1_horaires.date_vacances_ete", date)
#     return dash.no_update

# @callback(
#     Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
#     Input({"type": "vacances", "periode": ALL, "role": ALL}, "date"),
#     State({"type": "vacances", "periode": ALL, "role": ALL}, "id"),
#     State("freeze-callbacks", "data"),
#     prevent_initial_call=True
# )
# def sauvegarder_vacances(dates, ids, freeze):
    # """
    # Sauvegarde toutes les dates de vacances scolaires dans le JSON.

    # Cette fonction traite les 8 champs de date des vacances :
    # (début et fin pour Toussaint, Noël, Hiver, Printemps), identifiés dynamiquement.

    # Args:
    #     dates (list[str|None]): Liste des 8 dates saisies par l'utilisateur.
    #     ids (list[dict]): Identifiants des champs, contenant "periode" et "role" (début/fin).
    #     freeze (bool): Si True, empêche toute sauvegarde.

    # Returns:
    #     dash.no_update
    # """
#     if freeze or not dates or len(dates) != 8:
#         raise PreventUpdate
#     vacances = {}

#     for d, ident in zip(dates, ids):
#         if not d:
#             continue
#         periode = ident["periode"]
#         role = ident["role"]

#         if periode not in vacances:
#             vacances[periode] = {"debut": None, "fin": None}
#         vacances[periode][role] = d

#     mettre_a_jour_section_interface("1_horaires.vacances", vacances)
#     return dash.no_update

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
    Input("pause-meridienne-heures", "value"),
    Input("pause-meridienne-minutes", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def save_pause_meridienne(h, m, freeze):
    """
    Sauvegarde la durée de la pause méridienne dans le format HH:MM.

    Args:
        h (int|None): Heures saisies (ou None si champ vide).
        m (int|None): Minutes saisies (ou None si champ vide).
        freeze (bool): Si True, empêche toute modification.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    if h is None:
        h = 0
    if m is None:
        m = 0
    heure_str = f"{int(h):02d}:{int(m):02d}"
    mettre_a_jour_section_interface("1_horaires.pause_meridienne", heure_str)
    return dash.no_update

###############################################################################
# SECTION 2.1 - Langues
###############################################################################
@callback(
    Output("langues-lv1", "value"),
    Output("langues-lv2", "value"),
    Output("langues-lv3", "value"),
    Output("langues-lv4", "value"),
    Output("lv3-exists", "value"),
    Output("lv4-exists", "value"),
    Input("layout-informations", "id")
)
def prefill_langues(_):
    """
    Prérenseigne les sélections de langues (LV1 à LV4) depuis le JSON.

    Args:
        _ : Argument vide, valeur du layout.

    Returns:
        tuple: Valeurs pour LV1, LV2, LV3, LV4 et état d'activation LV3/LV4.
    """
    data = charger_donnees_interface().get("2_langues_et_options", {})
    return data.get("lv1", []), data.get("lv2", []), data.get("lv3", []), data.get("lv4", []), \
           ("oui" if data.get("lv3_active") else "non"), ("oui" if data.get("lv4_active") else "non")

@callback(
    Output("autres-langues-lv1", "data"),
    Output("autres-langues-lv2", "data"),
    Output("autres-langues-lv3", "data"),
    Output("autres-langues-lv4", "data"),
    Input("layout-informations", "id")
)
def prefill_autres_langues(_):
    """
    Prérenseigne les langues saisies manuellement pour LV1 à LV4 (à partir du JSON).

    Args:
        _ : Valeur de déclenchement.

    Returns:
        tuple: Listes de langues personnalisées LV1 à LV4.
    """
    autres = charger_donnees_interface().get("2_langues_et_options", {}).get("autres_langues", {})
    return (
        autres.get("lv1", []),
        autres.get("lv2", []),
        autres.get("lv3", []),
        autres.get("lv4", [])
    )

@callback(
    Output({"type": "option-checklist", "categorie": ALL}, "value"),
    Output("autres-options-saisies", "data"),
    Input("layout-informations", "id")
)
def prefill_options_depuis_json(_):
    """
    Prérenseigne les options d'établissement depuis le fichier JSON.

    Args:
        _ : Valeur de déclenchement.

    Returns:
        tuple: Valeurs par catégorie et liste des options personnalisées.
    """
    data = charger_donnees_interface().get("2_langues_et_options", {}).get("options", {})
    predef = data.get("predefinies", [])
    autres = data.get("autres", [])

    valeurs_par_cat = []
    for cat in CATEGORIES_OPTIONS:
        valeurs = [opt["value"] for opt in CATEGORIES_OPTIONS[cat] if opt["value"] in predef]
        valeurs_par_cat.append(valeurs)

    return valeurs_par_cat, autres

@callback(
    Output("autres-langues-lv1", "data", allow_duplicate=True),
    Output("autres-langues-lv2", "data", allow_duplicate=True),
    Output("autres-langues-lv3", "data", allow_duplicate=True),
    Output("autres-langues-lv4", "data", allow_duplicate=True),
    Input("dummy-reload-langues", "data"), 
    prevent_initial_call=True
)
def charger_autres_langues(_):
    """
    Recharge les langues personnalisées (non standards) saisies par l'utilisateur
    pour les LV1 à LV4, à partir du fichier JSON.

    Cette fonction est déclenchée par une mise à jour du dummy store,
    typiquement après un reset ou un import.

    Args:
        _ : Donnée d'entrée du déclencheur "dummy-reload-langues" (non utilisée).

    Returns:
        tuple:
            - list[str]: Langues personnalisées pour LV1.
            - list[str]: Langues personnalisées pour LV2.
            - list[str]: Langues personnalisées pour LV3.
            - list[str]: Langues personnalisées pour LV4.
    """
    data = charger_donnees_interface().get("2_langues_et_options", {}).get("autres_langues", {})
    return (
        list(data.get("lv1", [])),
        list(data.get("lv2", [])),
        list(data.get("lv3", [])),
        list(data.get("lv4", [])),
    )

# Affiche dynamiquement les champs de saisie si l'utilisateur coche "Autre" dans les langues LV1
@app.callback(
    Output("autre-langue-container-lv1", "children"),
    Input("langues-lv1", "value"),
    Input("autres-langues-lv1", "data")
)
def afficher_champs_dynamiques_lv1(selected_langs, valeurs):
    """
    Affiche dynamiquement les champs de saisie pour "Autre" si sélectionné dans LV1.

    Args:
        selected_langs (list): Langues sélectionnées par l'utilisateur.
        valeurs (list): Valeurs précédemment saisies.

    Returns:
        list: Composants HTML à afficher pour chaque langue personnalisée.
    """
    if not selected_langs or "Autre" not in selected_langs:
        return []

    valeurs = valeurs if valeurs else [""]
    if isinstance(valeurs, str):
        valeurs = [valeurs]

    champs = []
    for i, val in enumerate(valeurs):
        champs.append(
            html.Div([
                dcc.Input(
                    id={'type': 'input-autre-lv1', 'index': i},
                    type="text",
                    value=val or "",
                    placeholder="Saisissez une autre langue",
                    style={"width": "250px"}
                ),
                dbc.Button("✕", id={'type': 'supprimer-autre-lv1', 'index': i}, color="danger", size="sm", className="ms-2")
            ], style=style_autre_div)
        )

    return html.Div([
        html.Button([
            html.I(className="bi bi-plus-lg me-2"),
            "Ajouter une autre langue"
        ], id="add-langue-lv1", n_clicks=0, style=style_btn_ajouter),
        html.Div(champs, style={**style_input_autre, "flexDirection": "column"}),
        html.Br()
    ])

#######################################
# Gère la logique de création, suppression et mise à jour des langues saisies dans les champs dynamiques LV1
@callback(
    Output("autres-langues-lv1", "data", allow_duplicate=True),
    Input("add-langue-lv1", "n_clicks"),
    Input({'type': 'input-autre-lv1', 'index': ALL}, 'value'),
    Input({'type': 'supprimer-autre-lv1', 'index': ALL}, 'n_clicks'),
    State("autres-langues-lv1", "data"),
    prevent_initial_call=True
)
def gerer_langues_autres_lv1(n_clicks_add, valeurs_inputs, clicks_suppression, current_data):
    """
    Gère dynamiquement la liste des langues personnalisées saisies pour la LV1.

    Selon le composant déclencheur :
    - Si l'utilisateur clique sur "Ajouter", une entrée vide est ajoutée à la liste ;
    - Si un bouton de suppression est cliqué, la langue à l'index correspondant est retirée ;
    - Si un champ de saisie est modifié, la nouvelle liste est renvoyée telle quelle.

    Args:
        n_clicks_add (int): Nombre de clics sur le bouton "Ajouter une autre langue".
        valeurs_inputs (list[str]): Valeurs actuelles des champs de saisie de langues.
        clicks_suppression (list[int]): Nombre de clics sur chaque bouton de suppression.
        current_data (list[str]): Langues actuellement enregistrées dans le store.

    Returns:
        list[str]: Nouvelle liste des langues personnalisées pour LV1.

    Raises:
        dash.exceptions.PreventUpdate: Si aucun changement pertinent n'est détecté.
    """
    triggered = ctx.triggered_id
    langues = list(current_data) if current_data else []

    if triggered == "add-langue-lv1":
        if "" not in langues:
            langues.append("")
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "supprimer-autre-lv1":
        index = triggered.get("index")
        if index is not None and 0 <= index < len(langues):
            langues.pop(index)
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "input-autre-lv1":
        return valeurs_inputs

    raise PreventUpdate

#################################################################################################################################################################
# Affiche dynamiquement les champs de saisie si l'utilisateur coche "Autre" dans les langues LV2
@app.callback(
    Output("autre-langue-container-lv2", "children"),
    Input("langues-lv2", "value"),
    Input("autres-langues-lv2", "data")
)
def afficher_champs_dynamiques_lv2(selected_langs, valeurs):
    """
    Génère dynamiquement les champs de saisie pour les langues personnalisées (LV2)
    lorsque "Autre" est sélectionné dans la liste des langues.

    Args:
        selected_langs (list[str]): Langues sélectionnées dans le dropdown LV2.
        valeurs (list[str]): Langues personnalisées actuellement enregistrées.

    Returns:
        html.Div: Bloc HTML contenant les champs de saisie et les boutons de suppression.
    """
    if not selected_langs or "Autre" not in selected_langs:
        return []

    valeurs = valeurs or [""]
    if not valeurs:
        valeurs = [""]

    champs = []
    for i, val in enumerate(valeurs):
        champs.append(
            html.Div([
                dcc.Input(
                    id={'type': 'input-autre-lv2', 'index': i},
                    type="text",
                    value=val or "",
                    placeholder="Saisissez une autre langue",
                    style=style_input_autre
                ),
                dbc.Button("✕", id={'type': 'supprimer-autre-lv2', 'index': i}, color="danger", size="sm", className="ms-2")
            ], style=style_autre_div)
        )

    return html.Div([
        html.Button([
            html.I(className="bi bi-plus-lg me-2"),
            "Ajouter une autre langue"
        ], id="add-langue-lv2", n_clicks=0, style=style_btn_ajouter),
        html.Div(champs, style={**style_input_autre, "flexDirection": "column"}),
        html.Br()
    ])

#######################################
# Gère la logique de création, suppression et mise à jour des langues saisies dans les champs dynamiques LV2
@callback(
    Output("autres-langues-lv2", "data", allow_duplicate=True),
    Input("add-langue-lv2", "n_clicks"),
    Input({'type': 'input-autre-lv2', 'index': ALL}, 'value'),
    Input({'type': 'supprimer-autre-lv2', 'index': ALL}, 'n_clicks'),
    State("autres-langues-lv2", "data"),
    prevent_initial_call=True
)
def gerer_langues_autres_lv2(n_clicks_add, valeurs_inputs, clicks_suppression, current_data):
    """
    Gère l'ajout, la suppression et la mise à jour des langues personnalisées pour LV2.

    - Ajout d'une langue vide quand l'utilisateur clique sur "Ajouter" ;
    - Suppression ciblée via bouton ✕ ;
    - Mise à jour automatique via les champs de saisie.

    Args:
        n_clicks_add (int): Clics sur "Ajouter une autre langue".
        valeurs_inputs (list[str]): Valeurs actuelles des champs de saisie.
        clicks_suppression (list[int]): Clics sur les boutons de suppression.
        current_data (list[str]): Liste actuelle des langues personnalisées enregistrées.

    Returns:
        list[str]: Liste mise à jour des langues personnalisées.
    """
    triggered = ctx.triggered_id
    langues = list(current_data) if current_data else []

    if triggered == "add-langue-lv2":
        if "" not in langues:
            langues.append("")
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "supprimer-autre-lv2":
        index = triggered.get("index")
        if index is not None and 0 <= index < len(langues):
            langues.pop(index)
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "input-autre-lv2":
        return valeurs_inputs

    raise PreventUpdate

#################################################################################################################################################################
@callback(
    Output("niveaux-lv3", "value"),
    Input("layout-informations", "id")
)
def prefill_niveaux_lv3(_):
    """
    Prérenseigne les niveaux associés à LV3 au chargement de la page.

    Args:
        _ : Déclencheur automatique lors de l'ouverture de la page.

    Returns:
        list[int]: Plage de niveaux pour la LV3 (ex. [0, 3]).
    """
    data = charger_donnees_interface().get("2_langues_et_options", {}).get("langues", {})
    return data.get("lv3_niveaux", [0, 3])

# Affiche ou masque dynamiquement le bloc de saisie LV3 en fonction du choix "oui" ou "non"
@app.callback(
    Output("lv3-container", "style"),
    Input("lv3-exists", "value")
)
def afficher_lv3(value):
    """
    Affiche ou masque dynamiquement le conteneur de saisie de la LV3
    en fonction de la réponse de l'utilisateur ("oui"/"non").

    Args:
        value (str): Réponse de l'utilisateur sur l'activation de la LV3.

    Returns:
        dict: Style CSS à appliquer (visible ou non).
    """
    if value == "oui":
        return style_visible
    return style_non_visible

#######################################
# Gère la logique de création, suppression et mise à jour des langues saisies dans les champs dynamiques LV3
@callback(
    Output("autres-langues-lv3", "data", allow_duplicate=True),
    Input("add-langue-lv3", "n_clicks"),
    Input({'type': 'input-autre-lv3', 'index': ALL}, 'value'),
    Input({'type': 'supprimer-autre-lv3', 'index': ALL}, 'n_clicks'),
    State("autres-langues-lv3", "data"),
    prevent_initial_call=True
)
def gerer_langues_autres_lv3(n_clicks_add, valeurs_inputs, clicks_suppression, current_data):
    """
    Gère l'ajout, la suppression et la mise à jour des langues personnalisées pour LV3.

    - Ajout d'une ligne vide si l'utilisateur clique sur "Ajouter" ;
    - Suppression d'un élément via son index ;
    - Remplacement complet en cas de modification manuelle.

    Args:
        n_clicks_add (int): Nombre de clics sur "Ajouter".
        valeurs_inputs (list[str]): Valeurs saisies pour chaque langue personnalisée.
        clicks_suppression (list[int]): Clics sur chaque bouton de suppression.
        current_data (list[str]): Langues enregistrées actuellement.

    Returns:
        list[str]: Liste mise à jour des langues personnalisées pour LV3.
    """
    triggered = ctx.triggered_id
    langues = list(current_data) if current_data else []

    if triggered == "add-langue-lv3":
        if "" not in langues:
            langues.append("")
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "supprimer-autre-lv3":
        index = triggered.get("index")
        if index is not None and 0 <= index < len(langues):
            langues.pop(index)
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "input-autre-lv3":
        return valeurs_inputs

    raise PreventUpdate

#######################################
# Affiche dynamiquement les champs de saisie si l'utilisateur coche "Autre" dans les langues LV3
@app.callback(
    Output("autre-langue-container-lv3", "children"),
    Input("langues-lv3", "value"),
    Input("autres-langues-lv3", "data")
)
def afficher_champs_dynamiques_lv3(selected_langs, valeurs):
    """
    Génère dynamiquement les champs de saisie pour les langues personnalisées (LV3)
    lorsque "Autre" est sélectionné.

    Args:
        selected_langs (list[str]): Langues sélectionnées dans la liste LV3.
        valeurs (list[str]): Valeurs existantes à afficher dans les champs dynamiques.

    Returns:
        html.Div: Conteneur HTML contenant les champs de saisie et les boutons de suppression.
    """
    if not selected_langs or "Autre" not in selected_langs:
        return []

    champs = []
    valeurs = valeurs or [""]

    for i, val in enumerate(valeurs):
        champs.append(
            html.Div([
                dcc.Input(
                    id={'type': 'input-autre-lv3', 'index': i},
                    type="text",
                    value=val,
                    placeholder="Saisissez une autre langue",
                    style=style_input_autre
                ),
                dbc.Button("✕", id={'type': 'supprimer-autre-lv3', 'index': i}, color="danger", size="sm", className="ms-2")
            ], style=style_autre_div)
        )

    return html.Div([
        html.Button([
            html.I(className="bi bi-plus-lg me-2"),
            "Ajouter une autre langue"
        ], id="add-langue-lv3", n_clicks=0, style=style_btn_ajouter),
        html.Div(champs, style={**style_input_autre, "flexDirection": "column"}),
        html.Br()
    ])

@callback(
    Output("slider-niveaux-lv3", "value", allow_duplicate=True),
    Input("reset-message", "children"),
    prevent_initial_call=True
)
def reset_slider_lv3(_):
    """
    Réinitialise le slider de niveaux pour la LV3 (valeurs par défaut : [0, 3]).

    Args:
        _ : Déclencheur du reset (contenu du message de réinitialisation).

    Returns:
        list[int]: Plage de niveaux par défaut.
    """
    return [0, 3]

#################################################################################################################################################################
# Affiche la question "Souhaitez-vous proposer une LV4 ?" uniquement si une LV3 a été sélectionnée
@app.callback(
    Output("lv4-question", "style"),
    Input("lv3-exists", "value")
)
def afficher_question_lv4(value):
    """
    Affiche ou masque dynamiquement la question "Souhaitez-vous proposer une LV4 ?"
    uniquement si la LV3 a été activée.

    Args:
        value (str): Réponse à la question sur l'activation de la LV3 ("oui" ou "non").

    Returns:
        dict: Style CSS à appliquer (visible ou caché).
    """
    return style_visible if value == "oui" else style_non_visible

#######################################
# Affiche le bloc de saisie LV4 uniquement si LV3 est activée et que l'utilisateur a répondu "oui" pour la LV4
@callback(
    Output("lv4-container", "style"),
    Input("lv4-exists", "value")
)
def afficher_lv4(val):
    """
    Affiche le bloc de configuration pour la LV4 si l'utilisateur a répondu "oui"
    à la question correspondante.

    Args:
        val (str): Réponse de l'utilisateur à l'activation de la LV4.

    Returns:
        dict: Style CSS à appliquer pour le bloc LV4.
    """
    if val == "oui":
        return style_visible
    return style_non_visible

#######################################
# Affiche dynamiquement les champs de saisie si l'utilisateur coche "Autre" dans les langues LV4
@app.callback(
    Output("autre-langue-container-lv4", "children"),
    Input("langues-lv4", "value"),
    Input("autres-langues-lv4", "data")
)
def afficher_champs_dynamiques_lv4(selected_langs, valeurs):
    """
    Affiche dynamiquement les champs de saisie pour les langues personnalisées LV4
    lorsque "Autre" est sélectionné dans la liste.

    Args:
        selected_langs (list[str]): Langues cochées dans le dropdown LV4.
        valeurs (list[str]): Valeurs précédemment enregistrées (ou [""] par défaut).

    Returns:
        html.Div: Bloc HTML contenant les champs de saisie personnalisés LV4.
    """
    if not selected_langs or "Autre" not in selected_langs:
        return []

    champs = []
    valeurs = valeurs or [""]

    for i, val in enumerate(valeurs):
        champs.append(
            html.Div([
                dcc.Input(
                    id={'type': 'input-autre-lv4', 'index': i},
                    type="text",
                    value=val,
                    placeholder="Saisissez une autre langue",
                    style=style_input_autre
                ),
                dbc.Button("✕", id={'type': 'supprimer-autre-lv4', 'index': i}, color="danger", size="sm", className="ms-2")
            ], style=style_autre_div)
        )

    return html.Div([
        html.Button([
            html.I(className="bi bi-plus-lg me-2"),
            "Ajouter une autre langue"
        ], id="add-langue-lv4", n_clicks=0, style=style_btn_ajouter),
        html.Div(champs, style={**style_input_autre, "flexDirection": "column"}),
        html.Br()
    ])

#######################################
# Gère la logique de création, suppression et mise à jour des langues saisies dans les champs dynamiques LV4
@callback(
    Output("autres-langues-lv4", "data", allow_duplicate=True),
    Input("add-langue-lv4", "n_clicks"),
    Input({'type': 'input-autre-lv4', 'index': ALL}, 'value'),
    Input({'type': 'supprimer-autre-lv4', 'index': ALL}, 'n_clicks'),
    State("autres-langues-lv4", "data"),
    prevent_initial_call=True
)
def gerer_langues_autres_lv4(n_clicks_add, valeurs_inputs, clicks_suppression, current_data):
    """
    Gère dynamiquement les langues personnalisées saisies pour LV4 :
    ajout, suppression et mise à jour à la volée.

    Args:
        n_clicks_add (int): Nombre de clics sur "Ajouter une autre langue".
        valeurs_inputs (list[str]): Contenu des champs texte.
        clicks_suppression (list[int]): Liste des clics sur les boutons "✕".
        current_data (list[str]): Langues enregistrées dans le store actuel.

    Returns:
        list[str]: Liste mise à jour des langues personnalisées pour LV4.
    """
    triggered = ctx.triggered_id
    langues = list(current_data) if current_data else []

    if triggered == "add-langue-lv4":
        if "" not in langues:
            langues.append("")
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "supprimer-autre-lv4":
        index = triggered.get("index")
        if index is not None and 0 <= index < len(langues):
            langues.pop(index)
        return langues

    if isinstance(triggered, dict) and triggered.get("type") == "input-autre-lv4":
        return valeurs_inputs

    raise PreventUpdate

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True),
    Input("volume-lv3", "value"),
    Input("volume-lv4", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_volumes_lv3_lv4(vol_lv3, vol_lv4, freeze):
    """
    Sauvegarde dans le JSON les volumes horaires hebdomadaires associés aux LV3 et LV4.

    Args:
        vol_lv3 (int|None): Volume horaire défini pour la LV3.
        vol_lv4 (int|None): Volume horaire défini pour la LV4.
        freeze (bool): Si True, désactive la sauvegarde automatique.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.volume_lv3", vol_lv3)
    mettre_a_jour_section_interface("2_langues_et_options.volume_lv4", vol_lv4)
    return dash.no_update

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True), 
    Input("langues-lv1", "value"), 
    Input("langues-lv2", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_lv1_lv2(lv1, lv2, freeze):
    """
    Sauvegarde les langues sélectionnées pour LV1 et LV2 dans le fichier JSON grâce à mettre_a_jour_section_interface().

    Args:
        lv1 (list): Langues sélectionnées pour LV1.
        lv2 (list): Langues sélectionnées pour LV2.
        freeze (bool): Indique si l'écriture est temporairement désactivée.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.lv1", lv1)
    mettre_a_jour_section_interface("2_langues_et_options.lv2", lv2)
    return dash.no_update

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True), 
    Input("langues-lv3", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_lv3(val, freeze):
    """
    Sauvegarde la langue sélectionnée pour LV3 grâce à mettre_a_jour_section_interface().

    Args:
        val (list): Langues sélectionnées pour LV3.
        freeze (bool): État du verrouillage des callbacks.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.lv3", val)
    return dash.no_update

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True),
    Input("langues-lv4", "value"),
    State("freeze-callbacks", "data"),  
    prevent_initial_call=True)
def save_lv4(val, freeze):
    """
    Sauvegarde la langue sélectionnée pour LV4 grâce à mettre_a_jour_section_interface().

    Args:
        val (list): Langues sélectionnées pour LV4.
        freeze (bool): État du verrouillage des callbacks.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.lv4", val)
    return dash.no_update

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True), 
    Input("autres-langues-lv1", "data"), 
    Input("autres-langues-lv2", "data"), 
    Input("autres-langues-lv3", "data"), 
    Input("autres-langues-lv4", "data"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def save_autres_langues(data1, data2, data3, data4, freeze):
    """
    Sauvegarde les langues personnalisées (non pré-listées) pour LV1 à LV4.

    Args:
        data1, data2, data3, data4 (list): Langues personnalisées pour chaque LV.
        freeze (bool): Verrouillage des callbacks.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate

    nouvelles_donnees = {
        "lv1": [val.strip() for val in data1 if val.strip()],
        "lv2": [val.strip() for val in data2 if val.strip()],
        "lv3": [val.strip() for val in data3 if val.strip()],
        "lv4": [val.strip() for val in data4 if val.strip()]
    }

    mettre_a_jour_section_interface("2_langues_et_options.autres_langues", nouvelles_donnees)

    return dash.no_update

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True), 
    Input("lv3-exists", "value"), 
    Input("lv4-exists", "value"), 
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def save_lv3_lv4_active(lv3, lv4, freeze):
    """
    Sauvegarde l'activation ou non des niveaux LV3 et LV4.

    Args:
        lv3 (str): "oui" ou "non" pour activer LV3.
        lv4 (str): "oui" ou "non" pour activer LV4.
        freeze (bool): État du verrouillage.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.lv3_active", lv3 == "oui")
    mettre_a_jour_section_interface("2_langues_et_options.lv4_active", lv4 == "oui")
    return dash.no_update

@callback(
    Output("autres-langues-lv1", "data", allow_duplicate=True),
    Output("autres-langues-lv2", "data", allow_duplicate=True),
    Output("autres-langues-lv3", "data", allow_duplicate=True),
    Output("autres-langues-lv4", "data", allow_duplicate=True),
    Input("reset-message", "children"),
    prevent_initial_call=True
)
def init_autres_langues(_):
    """
    Recharge les langues personnalisées LV1 à LV4 depuis le JSON.

    Args:
        _ : valeur non utilisée (déclencheur du reset).

    Returns:
        tuple: Quatre listes de langues pour LV1, LV2, LV3, LV4.
    """
    autres = charger_donnees_interface().get("2_langues_et_options", {}).get("autres_langues", {})
    return (
        autres.get("lv1", []),
        autres.get("lv2", []),
        autres.get("lv3", []),
        autres.get("lv4", [])
    )

@callback(
    Output("store-langues-sauvegarde", "data", allow_duplicate=True),
    Input("slider-niveaux-lv3", "value"),
    Input("slider-niveaux-lv4", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_niveaux_lv3_lv4(niv_lv3, niv_lv4, freeze):
    """
    Sauvegarde les niveaux associés à LV3 et LV4 via sliders.

    Args:
        niv_lv3 (list): Plage de niveaux pour LV3.
        niv_lv4 (list): Plage de niveaux pour LV4.
        freeze (bool): État du verrouillage.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("2_langues_et_options.niveaux_lv3", niv_lv3)
    mettre_a_jour_section_interface("2_langues_et_options.niveaux_lv4", niv_lv4)
    return dash.no_update

@callback(
    Output("slider-niveaux-lv4", "value", allow_duplicate=True),
    Input("reset-message", "children"),
    prevent_initial_call=True
)
def reset_slider_lv4(_):
    """
    Réinitialise la plage de niveaux pour la LV4 à sa valeur par défaut.

    Cette fonction est appelée lors d'un reset ou d'un rechargement de données,
    afin de rétablir la sélection des niveaux de LV4 à [6e, 3e] codée ici comme [0, 3].

    Args:
        _ : Déclencheur (contenu de "reset-message"), utilisé uniquement pour activer le callback.

    Returns:
        list[int]: Plage de niveaux par défaut pour la LV4 ([0, 3]).
    """
    return [0, 3]

###############################################################################
# SECTION 2.2 - Options
###############################################################################
# Affiche les sliders de niveaux pour chaque option cochée ou saisie
@app.callback(
    Output("bloc-volumes-par-option", "children"),
    Input({'type': 'option-checklist', 'categorie': ALL}, 'value'),
    Input("autres-options-saisies", "data"),
)
def afficher_blocs_volumes_par_option(liste_checklist, autres_options):
    """
    Affiche un RangeSlider de niveaux pour chaque option sélectionnée ou saisie manuellement,
    en utilisant les données JSON pour préremplir les valeurs.

    Args:
        liste_checklist (list[list[str]]): Listes d'options cochées par catégorie.
        autres_options (list[str]): Liste des options saisies manuellement.

    Returns:
        list[html.Div]: Composants contenant un slider par option.
    """

    slider_marks = {i: NIVEAUX[i] for i in range(4)}
    data = charger_donnees_interface()
    valeurs_existees = data.get("2_langues_et_options", {}).get("options", {}).get("niveaux_par_option", {})

    options = set()
    for sous_liste in liste_checklist:
        options.update(sous_liste)
    options.update([opt.strip() for opt in autres_options if opt.strip()])

    composants = []
    for opt in sorted(options):
        composants.append(html.Div([
            html.H6(f"Option : {opt}", style=style_marge_haut),
            html.P(f"Quels sont les niveaux concernés par l'option « {opt} » ?", style=style_marge_bas),
            dcc.RangeSlider(
                id={'type': 'slider-niveaux-option', 'option': opt},
                min=0, max=3, step=1,
                marks=slider_marks,
                value=valeurs_existees.get(opt, [0, 3]),
                allowCross=False,
                included=True
            ),
            html.Br()
        ], style=style_marge_bas))

    return composants

#######################################
# Affiche les options concernées par le niveau sélectionné et leur volume horaire
@app.callback(
    Output("table-options-par-niveau", "data"),
    Input("niveau-options", "value"),
    State({'type': 'slider-niveaux-option', 'option': ALL}, 'value'),
    State({'type': 'slider-niveaux-option', 'option': ALL}, 'id'),
)
def afficher_options_par_niveau(niveau, sliders_values, sliders_ids):
    """
    Affiche les options disponibles pour un niveau donné, ainsi que leur volume horaire.

    Args:
        niveau (str): Niveau sélectionné (ex : "5e").
        sliders_values (list[list[int]]): Valeurs des sliders (plage de niveaux) pour chaque option.
        sliders_ids (list[dict]): Identifiants associés à chaque slider (contenant le nom de l'option).

    Returns:
        list[dict]: Données à afficher dans le tableau des options pour ce niveau.
    """
    if not niveau:
        raise PreventUpdate

    i_niveau = NIVEAUX.index(niveau)

    # 1. Options qui couvrent ce niveau (selon les sliders)
    options_visibles = []
    for val, ident in zip(sliders_values, sliders_ids):
        if not val or not isinstance(val, list) or len(val) != 2:
            continue
        debut, fin = sorted(val)
        if debut <= i_niveau <= fin:
            options_visibles.append(ident["option"])

    # 2. On récupère les données actuelles dans le JSON (toutes les options déjà enregistrées)
    data = charger_donnees_interface()
    options_data = data.get("options_par_niveau", {}).get(niveau, [])

    # 3. On fusionne intelligemment
    filtrees = []
    deja_vues = set()

    for opt in options_data:
        nom = opt.get("Option", "").strip()
        if nom in options_visibles:
            filtrees.append(opt)
            deja_vues.add(nom)

    for opt in options_visibles:
        if opt not in deja_vues:
            filtrees.append({"Option": opt, "Volume": 1})

    return filtrees

# Gère l'ajout, la suppression et la mise à jour des options saisies manuellement
@app.callback(
    Output("autres-options-saisies", "data", allow_duplicate=True),
    Input("add-autre-option", "n_clicks"),
    Input({'type': 'input-autre-option', 'index': ALL}, 'value'),
    Input({'type': 'supprimer-option', 'index': ALL}, 'n_clicks'),
    State("autres-options-saisies", "data"),
    prevent_initial_call=True
)
def gerer_autres_options(n_clicks_add, valeurs_inputs, clicks_suppression, current_data):
    """
    Gère dynamiquement l'ajout, la suppression et la modification d'options saisies manuellement.

    Args:
        n_clicks_add (int): Nombre de clics sur le bouton "Ajouter".
        valeurs_inputs (list[str]): Valeurs actuelles des champs de saisie.
        clicks_suppression (list[int]): Liste des clics sur les boutons ✕.
        current_data (list[str]): Liste actuelle d'options saisies.

    Returns:
        list[str]: Liste mise à jour des options personnalisées.
    """
    triggered = ctx.triggered_id
    options = current_data or []

    if not triggered and n_clicks_add:
        options.append("")
        return options

    if triggered == "add-autre-option":
        options.append("")
        return options

    if isinstance(triggered, dict) and triggered.get("type") == "supprimer-option":
        index = triggered.get("index")
        if index is not None and 0 <= index < len(options):
            options.pop(index)
        return options

    if isinstance(triggered, dict) and triggered.get("type") == "input-autre-option":
        return valeurs_inputs

    raise PreventUpdate

#######################################
# Affiche dynamiquement les champs de saisie pour les options personnalisées
@app.callback(
    Output("autres-options-container", "children"),
    Input("autres-options-saisies", "data")
)
def afficher_blocs_autres_options(valeurs):
    """
    Génère dynamiquement les champs de saisie pour les options personnalisées.

    Args:
        valeurs (list[str]): Options saisies actuellement.

    Returns:
        list[html.Div]: Composants de saisie correspondants aux options.
    """
    if not valeurs:
        return []

    composants = []
    for i, val in enumerate(valeurs):
        composants.append(html.Div([
            html.Div([
                dcc.Input(
                    id={'type': 'input-autre-option', 'index': i},
                    type="text",
                    value=val,
                    placeholder="Saisissez une autre option",
                    style=style_input_autre
                ),
                dbc.Button("✕", id={'type': 'supprimer-option', 'index': i}, color="danger", size="sm", className="ms-2")
            ], style=style_autre_div)
        ], style=style_marge_bas))

    return composants

#######################################
# Sauvegarde les données du tableau en quittant un niveau
@app.callback(
    Output("niveau-options-precedent", "data", allow_duplicate=True),
    Input("niveau-options", "value"),
    State("niveau-options-precedent", "data"),
    State("table-options-par-niveau", "data"),
    prevent_initial_call=True
)
def sauvegarder_ancien_tableau_options(niveau_actuel, niveau_precedent, tableau):
    """
    Sauvegarde le tableau des options d'un niveau lorsqu'on en sélectionne un autre.

    Args:
        niveau_actuel (str): Niveau sélectionné actuellement.
        niveau_precedent (str): Niveau précédent dont les données doivent être sauvegardées.
        tableau (list[dict]): Données du tableau (options + volumes).

    Returns:
        str: Le nouveau niveau sélectionné.
    """
    if niveau_precedent and isinstance(tableau, list):
        data = charger_donnees_interface()
        data.setdefault("options_par_niveau", {})[niveau_precedent] = tableau
        sauvegarder_donnees_interface(data)
    return niveau_actuel

#######################################
@app.callback(
    Output("message-validation-options", "children"),
    Input("btn-valider-options", "n_clicks"),
    State("niveau-options", "value"),
    State("table-options-par-niveau", "data"),
    prevent_initial_call=True
)
def valider_tableau_options(n_clicks, niveau, tableau):
    """
    Sauvegarde manuellement le tableau des options pour un niveau donné
    lorsque l'utilisateur clique sur le bouton "Valider les options".

    Args:
        n_clicks (int): Nombre de clics sur le bouton.
        niveau (str): Niveau actuellement sélectionné.
        tableau (list[dict]): Contenu du tableau des options.

    Returns:
        str: Message de confirmation ou d'erreur.
    """
    if not niveau or not tableau:
        return "Aucune donnée à enregistrer."
    data = charger_donnees_interface()
    data.setdefault("options_par_niveau", {})[niveau] = tableau
    sauvegarder_donnees_interface(data)
    return f"Options de {niveau} enregistrées avec succès."

#######################################
# Affiche les champs de volume horaire par niveau pour une option donnée
@callback(
    Output({'type': 'bloc-volumes-option', 'option': MATCH}, 'children'),
    Input({'type': 'slider-niveaux-option', 'option': MATCH}, 'value'),
    State({'type': 'slider-niveaux-option', 'option': MATCH}, 'id'),
)
def afficher_tableaux_volumes(slider_range, id_dict):
    """
    Affiche les champs de saisie de volume horaire pour chaque niveau couvert par une option.

    Args:
        slider_range (list[int]): Plage de niveaux sélectionnée via le RangeSlider.
        id_dict (dict): Identifiant de l'option concernée.

    Returns:
        list[html.Div]: Liste de composants pour la saisie des volumes.
    """
    option = id_dict["option"]

    if not slider_range or not isinstance(slider_range, list) or len(slider_range) != 2:
        raise PreventUpdate

    debut, fin = slider_range
    debut, fin = min(debut, 3), max(fin, 0)

    lignes = []
    for i in range(debut, fin + 1):
        niveau = NIVEAUX[i]
        lignes.append(html.Div([
            html.Label(niveau, style={"width": "80px"}),
            dcc.Input(
                id={'type': 'input-volume-option', 'option': option, 'niveau': niveau},
                type="number", min=0, step=0.5, value=1,
                style=style_input_refectoire_langues
            ),
            html.Span("h")
        ], style=style_autre_div))

    return lignes

@app.callback(
    Output("store-options-sauvegarde", "data", allow_duplicate=True),
    Input({'type': 'option-checklist', 'categorie': ALL}, 'value'),
    Input("autres-options-saisies", "data"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def save_options(checklists, autres, freeze):
    """
    Sauvegarde les options cochées et saisies dans la structure JSON.

    Args:
        checklists (list[list[str]]): Options sélectionnées par catégorie.
        autres (list[str]): Options saisies manuellement.
        freeze (bool): Si True, empêche la sauvegarde.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    toutes = [opt for sous_liste in checklists for opt in sous_liste]
    mettre_a_jour_section_interface("2_langues_et_options.options.predefinies", toutes)
    mettre_a_jour_section_interface("2_langues_et_options.options.autres", autres)
    return dash.no_update

@callback(Output("store-options-sauvegarde", "data", allow_duplicate=True),
    Input({"type": "slider-niveaux-option", "option": ALL}, "value"),
    State({"type": "slider-niveaux-option", "option": ALL}, "id"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True)
def save_niveaux_par_option(valeurs, ids, freeze):
    """
    Sauvegarde la plage de niveaux associée à chaque option via RangeSlider.

    Args:
        valeurs (list[list[int]]): Valeurs des sliders pour chaque option.
        ids (list[dict]): Identifiants contenant le nom des options.
        freeze (bool): Si True, empêche la sauvegarde.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    result = {}
    for val, ident in zip(valeurs, ids):
        result[ident["option"]] = val
    mettre_a_jour_section_interface("2_langues_et_options.options.niveaux_par_option", result)
    return dash.no_update

###############################################################################
# SECTION 3.1 - Classes
###############################################################################
@callback(
    Output("table-classes", "data"),
    Output("table-professeurs", "data"),
    Output("table-salles", "data"),
    Input("layout-informations", "id")
)
def prefill_ressources(_):
    """
    Préremplit les tableaux de classes, professeurs et salles à partir du fichier JSON.

    Args:
        _ : Déclencheur lié au chargement de la page.

    Returns:
        tuple:
            - list[dict]: Données des classes.
            - list[dict]: Données des professeurs.
            - list[dict]: Données des salles.
    """
    data = charger_donnees_interface().get("3_ressources", {})
    return data.get("classes", []), data.get("professeurs", []), data.get("salles", [])


@app.callback(
    Output("stockage-fichier-classes", "data", allow_duplicate=True),
    Output("modal-choix-import", "is_open", allow_duplicate=True),
    Output("table-classes", "data", allow_duplicate=True),
    Output("import-classes-message", "children", allow_duplicate=True),
    Output("import-classes-message", "style", allow_duplicate=True),
    Input("upload-classes", "contents"),
    State("upload-classes", "filename"),
    State("table-classes", "data"),
    prevent_initial_call=True
)
def traiter_import(contents, filenames, tableau_data):
    """
    Traite l'import de fichiers contenant des données de classes.
    Si le tableau est vide, les données sont insérées directement.
    Sinon, un modal s'ouvre pour choisir entre fusion ou remplacement.

    Args:
        contents (str|list): Contenu encodé du fichier importé.
        filenames (str|list): Noms de fichiers correspondants.
        tableau_data (list[dict]): Données actuelles du tableau des classes.

    Returns:
        tuple: Stockage temporaire, état du modal, nouvelle table, message, style du message.
    """
    if not contents:
        raise PreventUpdate

    if isinstance(contents, str):
        contents = [contents]
        filenames = [filenames]

    fichiers = [{"contents": c, "filename": f} for c, f in zip(contents, filenames)]
    colonnes_attendues = {"Classe", "Niveau", "Effectif", "Dependances", "MatiereGroupe"}
    donnees_importees = []

    for fichier in fichiers:
        try:
            content_type, content_string = fichier["contents"].split(",")
            decoded = base64.b64decode(content_string)
            extension = fichier["filename"].split(".")[-1]

            if extension in ["xls", "xlsx", "xlsm"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif extension == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return dash.no_update, False, dash.no_update, f"Format non pris en charge : {fichier['filename']}", style_erreur_import

            if not colonnes_attendues.issubset(df.columns):
                return dash.no_update, False, dash.no_update, f"Colonnes attendues manquantes dans : {fichier['filename']}", style_erreur_import

            donnees_importees.extend(df.to_dict("records"))

        except Exception as e:
            return dash.no_update, False, dash.no_update, f"Erreur dans {fichier['filename']} : {str(e)}", style_erreur_import

    if not tableau_data:
        return fichiers, False, donnees_importees, "Fichier(s) importé(s) avec succès !", style_import_correct

    return fichiers, True, dash.no_update, dash.no_update, dash.no_update

#######################################
# Applique le choix de fusion ou de remplacement du tableau après import
@app.callback(
    Output("table-classes", "data", allow_duplicate=True),
    Output("import-classes-message", "children", allow_duplicate=True),
    Output("modal-choix-import", "is_open", allow_duplicate=True),
    Output("import-classes-message", "style", allow_duplicate=True),
    Input("btn-fusionner-classes", "n_clicks"),
    Input("btn-remplacer-classes", "n_clicks"),
    State("stockage-fichier-classes", "data"),
    State("table-classes", "data"),
    prevent_initial_call=True
)
def appliquer_import_classes(n_fusion, n_remplacement, stockage, data_actuelle):
    """
    Fusionne ou remplace les données de classes avec celles issues du fichier importé.

    Args:
        n_fusion (int): Clics sur le bouton de fusion.
        n_remplacement (int): Clics sur le bouton de remplacement.
        stockage (list): Données importées stockées temporairement.
        data_actuelle (list[dict]): Données actuelles du tableau.

    Returns:
        tuple:
            - list[dict]: Nouvelles données du tableau.
            - str: Message de confirmation ou d'erreur.
            - bool: Fermeture du modal.
            - dict: Style du message.
    """
    if not stockage:
        raise PreventUpdate

    fichiers = stockage if isinstance(stockage, list) else [stockage]
    colonnes_attendues = {"Classe", "Niveau", "Effectif", "Dependances", "MatiereGroupe"}
    nouvelles_donnees = []

    for fichier in fichiers:
        try:
            content_type, content_string = fichier["contents"].split(",")
            decoded = base64.b64decode(content_string)
            extension = fichier["filename"].split(".")[-1]

            if extension in ["xls", "xlsx", "xlsm"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif extension == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return dash.no_update, f"Extension non prise en charge : {fichier['filename']}", False, style_erreur_import

            if not colonnes_attendues.issubset(df.columns):
                return dash.no_update, f"Colonnes manquantes dans : {fichier['filename']}", False, style_erreur_import

            nouvelles_donnees.extend(df.to_dict("records"))

        except Exception as e:
            return dash.no_update, f"Erreur lecture {fichier['filename']} : {str(e)}", False, style_erreur_import

    if ctx.triggered_id == "btn-fusionner-classes":
        donnees_finales = (data_actuelle or []) + nouvelles_donnees
    elif ctx.triggered_id == "btn-remplacer-classes":
        donnees_finales = nouvelles_donnees
    else:
        raise PreventUpdate

    return donnees_finales, "Fichier(s) importé(s) avec succès !", False, style_import_correct

#######################################
# Met à jour l'état booléen "tableau vide" en fonction du contenu actuel
@app.callback(
    Output("table-classes-vide", "data"),
    Input("table-classes", "data")
)
def maj_etat_vide(table_data):
    """
    Indique si le tableau des classes est vide ou non.

    Args:
        table_data (list[dict]): Données actuelles du tableau des classes.

    Returns:
        bool: True si le tableau est vide, False sinon.
    """
    return not bool(table_data)

#######################################
# Ajoute une ligne ou efface tout le tableau selon le bouton cliqué
@app.callback(
    Output("table-classes", "data", allow_duplicate=True),
    Output("import-classes-message", "children"),
    Output("import-classes-message", "style"),
    Input("ajouter-ligne-classe", "n_clicks"),
    Input("btn-effacer-classes", "n_clicks"),
    Input("table-classes", "data"),
    prevent_initial_call=True
)
def maj_table_classes(n_ajout, n_effacer, current_data):
    """
    Gère l'ajout, la réinitialisation ou l'auto-remplissage du tableau des classes.

    Args:
        n_ajout (int): Clics sur le bouton "Ajouter une ligne".
        n_effacer (int): Clics sur le bouton "Effacer tout".
        current_data (list[dict]): Données actuelles du tableau.

    Returns:
        tuple:
            - list[dict]: Données du tableau mises à jour.
            - str|dash.no_update: Message à afficher.
            - dict|dash.no_update: Style du message.
    """
    triggered = ctx.triggered_id

    if triggered == "ajouter-ligne-classe":
        current_data = current_data or []
        current_data.append({"Classe": "", "Niveau": "", "Effectif": "", "Dependances": "", "MatiereGroupe": ""})
        return current_data, no_update, no_update

    elif triggered == "btn-effacer-classes":
        return [], "", style_non_visible

    elif triggered == "table-classes":
        if not current_data:
            # Ajout automatique de deux lignes d'exemple si le tableau est vide
            return CLASSES_DEFAUT, no_update, no_update

        # Normalisation des niveaux (6 → 6e)
        niveaux_valides = {"6e", "5e", "4e", "3e"}
        for row in current_data:
            niveau = str(row.get("Niveau", "")).strip().lower()
            if niveau in {"6", "5", "4", "3"}:
                row["Niveau"] = f"{niveau}e"
            elif niveau in niveaux_valides:
                row["Niveau"] = niveau
            else:
                row["Niveau"] = ""

        return current_data, no_update, no_update

    raise PreventUpdate

#######################################
# Fournit un fichier d'exemple à télécharger au format CSV ou Excel
@app.callback(
    Output("telechargement-exemple-classes", "data"),
    Input("download-exemple-csv", "n_clicks"),
    Input("download-exemple-xlsx", "n_clicks"),
    prevent_initial_call=True
)
def telecharger_exemple(n_csv, n_xlsx):
    """
    Génère un fichier d'exemple pour les classes à télécharger au format CSV ou Excel.

    Args:
        n_csv (int): Clics sur le bouton "Télécharger CSV".
        n_xlsx (int): Clics sur le bouton "Télécharger Excel".

    Returns:
        dash.send_data_frame: Fichier à télécharger.
    """
    triggered = ctx.triggered_id

    if triggered == "download-exemple-csv":
        return dcc.send_data_frame(DF_CLASSES.to_csv, "exemple_classes.csv", index=False)
    elif triggered == "download-exemple-xlsx":
        return dcc.send_data_frame(DF_CLASSES.to_excel, "exemple_classes.xlsx", index=False)

    raise PreventUpdate

@callback(
    Output("table-classes", "data", allow_duplicate=True),
    Input("reset-message", "children"),
    Input("btn-generer-classes", "n_clicks"),
    State("table-classes", "data"),
    State("nb-classes-generees", "value"),
    State("niveau-classe-genere", "value"),
    State("effectif-classe-genere", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def generer_classes(_, n_clicks, data, nb_classes, niveau, effectif, freeze):
    """
    Génère un ensemble de classes à partir des paramètres fournis.

    Args:
        _ : Déclencheur (reset-message ou autre).
        n_clicks (int): Clics sur le bouton "Générer".
        data (list[dict]): Données actuelles des classes.
        nb_classes (int): Nombre de classes à générer.
        niveau (str): Niveau concerné (ex : "5e").
        effectif (int): Effectif fixe par classe.
        freeze (bool): Si True, désactive toute modification.

    Returns:
        list[dict]: Liste des classes générées.
    """
    if freeze:
        raise PreventUpdate
    if not nb_classes or not niveau or not effectif:
        raise PreventUpdate

    data = data or []
    prefix = niveau
    debut = len(data) + 1
    for i in range(nb_classes):
        data.append({
            "Classe": f"{prefix}{i + debut}",
            "Niveau": niveau,
            "Effectif": str(effectif),
            "Dependances": "",
            "MatiereGroupe": ""
        })
    mettre_a_jour_section_interface("3_ressources.classes", data)
    return data

@callback(
    Output("dummy-stockage-classes", "data", allow_duplicate=True),
    Output("erreur-classes", "children", allow_duplicate=True),
    Input("table-classes", "data"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_classes(data, freeze):
    """
    Sauvegarde les données des classes après validation, avec contrôle de cohérence :
    - Noms de classes uniques ;
    - Effectif valide (entre 1 et 50) ;
    - Dépendances existantes.

    Args:
        data (list[dict]): Données à sauvegarder.
        freeze (bool): Si True, empêche toute modification.

    Returns:
        tuple:
            - dash.no_update: Pas de mise à jour directe.
            - str|html.Span: Message d'erreur ou vide si tout est valide.
    """
    if freeze:
        raise PreventUpdate

    # Vérification des noms de classes uniques
    noms = [c.get("Classe", "").strip() for c in data if c.get("Classe")]
    if len(noms) != len(set(noms)):
        return dash.no_update, html.Span([
            html.I(className="bi bi-exclamation-octagon me-2"),
            "Les noms de classes doivent être uniques."
        ])

    for i, c in enumerate(data):
        nom_classe = c.get("Classe", f"Ligne {i+1}")

        # Vérification de l'effectif
        try:
            eff = int(c.get("Effectif", -1))
            if not (1 <= eff <= 50):
                return dash.no_update, html.Span([
                    html.I(className="bi bi-exclamation-octagon me-2"),
                    f"L'effectif de la classe « {nom_classe} » doit être entre 1 et 50."
                ])
        except ValueError:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"L'effectif de la classe « {nom_classe} » doit être un nombre entier."
            ])

        # Vérification des dépendances
        dependances = c.get("Dependances", "")
        if dependances:
            noms_dependances = [d.strip() for d in dependances.split(",") if d.strip()]
            noms_classes_existants = [cl.get("Classe", "").strip() for cl in data]
            for dep in noms_dependances:
                if dep not in noms_classes_existants:
                    return dash.no_update, html.Span([
                        html.I(className="bi bi-exclamation-octagon me-2"),
                        f"La dépendance « {dep} » dans la classe « {nom_classe} » n'existe pas parmi les classes déclarées."
                    ])

    mettre_a_jour_section_interface("3_ressources.classes", data)
    return dash.no_update, ""

###############################################################################
# SECTION 3.2 - Professeurs
###############################################################################
# Traite le fichier importé et affiche le modal si le tableau contient déjà des données
@app.callback(
    Output("stockage-fichier-professeurs", "data", allow_duplicate=True),
    Output("modal-choix-import-professeurs", "is_open", allow_duplicate=True),
    Output("table-professeurs", "data", allow_duplicate=True),
    Output("import-professeurs-message", "children", allow_duplicate=True),
    Output("import-professeurs-message", "style", allow_duplicate=True),
    Input("upload-professeurs", "contents"),
    State("upload-professeurs", "filename"),
    State("table-professeurs", "data"),
    prevent_initial_call=True
)
def traiter_import(contents, filenames, tableau_data):
    """
    Gère l'import de fichier pour les professeurs.
    Si le tableau est vide, les données sont intégrées directement.
    Sinon, un modal propose de fusionner ou de remplacer.
    
    Args:
        contents (str | list): Contenu encodé du ou des fichiers.
        filenames (str | list): Nom du ou des fichiers uploadés.
        tableau_data (list): Données actuelles du tableau.

    Returns:
        tuple: Plusieurs sorties Dash selon si un modal est nécessaire ou non.
    """
    if not contents:
        raise PreventUpdate

    if isinstance(contents, str):
        contents = [contents]
        filenames = [filenames]

    fichiers = [{"contents": c, "filename": f} for c, f in zip(contents, filenames)]
    colonnes_attendues = {"Civilite", "Nom", "Prenom", "Niveaux", "Matieres", "Volume", "Duree"}
    donnees_importees = []

    for fichier in fichiers:
        try:
            content_type, content_string = fichier["contents"].split(",")
            decoded = base64.b64decode(content_string)
            extension = fichier["filename"].split(".")[-1]

            if extension in ["xls", "xlsx", "xlsm"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif extension == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return dash.no_update, False, dash.no_update, f"Format non pris en charge : {fichier['filename']}", style_erreur_import

            if not colonnes_attendues.issubset(df.columns):
                return dash.no_update, False, dash.no_update, f"Colonnes attendues manquantes dans : {fichier['filename']}", style_erreur_import
            donnees_importees.extend(df.to_dict("records"))

        except Exception as e:
            return dash.no_update, False, dash.no_update, f"Erreur dans {fichier['filename']} : {str(e)}", style_erreur_import

    if not tableau_data:
        return fichiers, False, donnees_importees, "Fichier(s) importé(s) avec succès !", style_import_correct

    return fichiers, True, dash.no_update, dash.no_update, dash.no_update

#######################################
# Applique la fusion ou le remplacement des données après confirmation via le modal
@app.callback(
    Output("table-professeurs", "data", allow_duplicate=True),
    Output("import-professeurs-message", "children", allow_duplicate=True),
    Output("modal-choix-import-professeurs", "is_open", allow_duplicate=True),
    Output("import-professeurs-message", "style", allow_duplicate=True),
    Input("btn-fusionner-professeurs", "n_clicks"),
    Input("btn-remplacer-professeurs", "n_clicks"),
    State("stockage-fichier-professeurs", "data"),
    State("table-professeurs", "data"),
    prevent_initial_call=True
)
def appliquer_import(n_fusion, n_remplacement, stockage, data_actuelle):
    """
    Applique l'action choisie par l'utilisateur (fusion ou remplacement) pour importer des données de professeurs.

    Lorsqu'un fichier est chargé et que le tableau contient déjà des données, cette fonction permet soit :
    - de fusionner les nouvelles données avec l'existant,
    - soit de les remplacer totalement,
    selon le bouton cliqué.

    Les fichiers sont décodés, parsés (CSV ou Excel), et vérifiés pour contenir toutes les colonnes attendues.

    Args:
        n_fusion (int): Nombre de clics sur le bouton "Fusionner les professeurs".
        n_remplacement (int): Nombre de clics sur le bouton "Remplacer les professeurs".
        stockage (dict or list): Données encodées du fichier importé, récupérées depuis le Store.
        data_actuelle (list): Liste actuelle des professeurs dans le tableau avant import.

    Returns:
        tuple:
            - list: Nouvelles données du tableau des professeurs à afficher.
            - str: Message d'information à afficher sous le tableau.
            - bool: État du modal (False = fermé).
            - dict: Style du message (vert pour succès, rouge pour erreur).
    """
    if not stockage:
        raise PreventUpdate

    fichiers = stockage if isinstance(stockage, list) else [stockage]
    colonnes_attendues = {"Civilite", "Nom", "Prenom", "Niveaux", "Matieres", "Volume", "Duree", "SallePref"}
    nouvelles_donnees = []

    for fichier in fichiers:
        try:
            content_type, content_string = fichier["contents"].split(",")
            decoded = base64.b64decode(content_string)
            extension = fichier["filename"].split(".")[-1]

            if extension in ["xls", "xlsx", "xlsm"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif extension == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return dash.no_update, f"Extension non prise en charge : {fichier['filename']}", False, style_erreur_import

            if not colonnes_attendues.issubset(df.columns):
                return dash.no_update, f"Colonnes manquantes dans : {fichier['filename']}", False, style_erreur_import

            nouvelles_donnees.extend(df.to_dict("records"))

        except Exception as e:
            return dash.no_update, f"Erreur lecture {fichier['filename']} : {str(e)}", False, style_erreur_import

    if ctx.triggered_id == "btn-fusionner-professeurs":
        donnees_finales = (data_actuelle or []) + nouvelles_donnees
    elif ctx.triggered_id == "btn-remplacer-professeurs":
        donnees_finales = nouvelles_donnees
    else:
        raise PreventUpdate

    return donnees_finales, "Fichier(s) importé(s) avec succès !", False, style_import_correct

#######################################
# Indique si le tableau des professeurs est vide
@app.callback(
    Output("table-professeurs-vide", "data"),
    Input("table-professeurs", "data")
)
def maj_etat_vide(table_data):
    """
    Détermine si le tableau des professeurs est vide.

    Args:
        table_data (list[dict] or None): Données actuelles du tableau des professeurs.

    Returns:
        bool: True si le tableau est vide ou None, False sinon.
    """
    return not bool(table_data)

#######################################
@app.callback(
    Output("table-professeurs", "data", allow_duplicate=True),
    Output("import-professeurs-message", "children"),
    Output("import-professeurs-message", "style"),
    Input("ajouter-ligne-professeur", "n_clicks"),
    Input("btn-effacer-professeurs", "n_clicks"),
    Input("table-professeurs", "data"),
    prevent_initial_call=True
)
def maj_table_professeurs(n_ajout, n_effacer, current_data):
    """
    Gère l'ajout, l'effacement ou l'initialisation automatique du tableau des professeurs.

    Args:
        n_ajout (int): Nombre de clics sur le bouton d'ajout de ligne.
        n_effacer (int): Nombre de clics sur le bouton d'effacement du tableau.
        current_data (list[dict] or None): Données actuelles du tableau des professeurs.

    Returns:
        tuple:
            - list[dict]: Nouvelles données du tableau des professeurs.
            - str: Message d'information ou d'erreur à afficher.
            - dict: Style CSS à appliquer au message.
    """
    triggered = ctx.triggered_id

    if triggered == "ajouter-ligne-professeur":
        current_data = current_data or []
        current_data.append({
            "Civilite": "", "Nom": "", "Prenom": "", "Niveaux": "",
            "Matieres": "", "Volume": "", "Duree": "", "SallePref": ""
        })
        return current_data, no_update, no_update

    elif triggered == "btn-effacer-professeurs":
        return [], "", style_non_visible

    elif triggered == "table-professeurs":
        if not current_data:
            # Ajout automatique des deux lignes d'exemple
            return PROFS_DEFAUT, no_update, no_update

        return current_data, no_update, no_update

    raise PreventUpdate

#######################################
# Fournit un exemple de fichier à télécharger au format CSV ou Excel
@app.callback(
    Output("telechargement-exemple-professeurs", "data"),
    Input("download-prof-csv", "n_clicks"),
    Input("download-prof-xlsx", "n_clicks"),
    prevent_initial_call=True
)
def telecharger_exemple_prof(n_csv, n_xlsx):
    """
    Génère un fichier d'exemple contenant deux lignes de professeurs,
    au format CSV ou Excel selon le bouton cliqué.

    Args:
        n_csv (int): Nombre de clics sur le bouton de téléchargement CSV.
        n_xlsx (int): Nombre de clics sur le bouton de téléchargement Excel.

    Returns:
        flask.Response: Fichier à télécharger via Dash (dcc.send_data_frame).

    Raises:
        PreventUpdate: Si aucun des deux boutons n'a été cliqué.
    """
    if ctx.triggered_id == "download-prof-csv":
        return dcc.send_data_frame(DF_PROFS.to_csv, "exemple_professeurs.csv", index=False)
    elif ctx.triggered_id == "download-prof-xlsx":
        return dcc.send_data_frame(DF_PROFS.to_excel, "exemple_professeurs.xlsx", index=False)

    raise PreventUpdate

@callback(
    Output("table-professeurs", "data", allow_duplicate=True),
    Input("btn-generer-profs", "n_clicks"),
    State("table-professeurs", "data"),
    State("nb-profs-genere", "value"),
    State("volume-prof-genere", "value"),
    State("duree-prof-genere", "value"),
    State("niveaux-prof-genere", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def generer_profs(n_clicks, data, nb_profs, volume, duree, niveaux, freeze):
    """
    Génère un nombre spécifié de professeurs avec des paramètres par défaut, puis les ajoute
    à la table des professeurs actuelle. La génération est bloquée si le flag freeze est activé.

    Args:
        n_clicks (int): Nombre de clics sur le bouton "Générer".
        data (list[dict] or None): Données actuelles du tableau des professeurs.
        nb_profs (int): Nombre de professeurs à générer.
        volume (int): Volume horaire hebdomadaire par professeur.
        duree (float): Durée préférée d'un créneau de cours (en heures).
        niveaux (list[str]): Liste des niveaux pris en charge par chaque professeur (ex: ["6e", "5e"]).
        freeze (bool): Indicateur de blocage de mise à jour (empêche la génération si True).

    Returns:
        list[dict]: Nouvelles données du tableau des professeurs avec les lignes générées ajoutées.

    Raises:
        PreventUpdate: Si les conditions ne sont pas réunies (freeze actif ou champs manquants).
    """
    if freeze:
        raise PreventUpdate
    if not nb_profs or not volume or not duree or not niveaux:
        raise PreventUpdate

    data = data or []
    debut = len(data) + 1
    for i in range(nb_profs):
        data.append({
            "Civilite": "M.",
            "Nom": f"Professeur_{i + debut}",
            "Prenom": f"A ajouter",
            "Niveaux": ",".join(niveaux),
            "Matieres": "",
            "Volume": str(volume),
            "Duree": str(duree),
            "SallePref": ""
        })
    mettre_a_jour_section_interface("3_ressources.professeurs", data)
    return data

@callback(
    Output("table-professeurs", "data", allow_duplicate=True),
    Output("erreur-professeurs", "children", allow_duplicate=True),
    Input("table-professeurs", "data"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_professeurs(data, freeze):
    """
    Valide et sauvegarde les données du tableau des professeurs.

    Effectue les vérifications suivantes pour chaque ligne :
    - Unicité de la combinaison Civilité + Nom + Prénom.
    - Validité des niveaux (doivent appartenir à {"6e", "5e", "4e", "3e"}).
    - Durée préférée comprise entre 0.25 et 4 heures.
    - Volume horaire compris entre 1 et 40 heures.
    - Salle préférée (si renseignée) doit exister dans les salles définies.

    Si toutes les lignes sont valides, les données sont enregistrées dans le Store via mettre_a_jour_section_interface.

    Args:
        data (list[dict]): Données saisies dans le tableau des professeurs.
        freeze (bool): Indicateur pour empêcher toute mise à jour si True.

    Returns:
        Tuple[list[dict] or no_update, html.Span or str]:
            - Données mises à jour du tableau (ou dash.no_update en cas d'erreur).
            - Message d'erreur HTML détaillé en cas de validation échouée, sinon chaîne vide.

    Raises:
        PreventUpdate: Si freeze est activé.
    """
    if freeze:
        raise PreventUpdate
    niveaux_valides = {"6e", "5e", "4e", "3e"}
    salles_existantes = [
        s.get("Nom", "").strip()
        for s in charger_donnees_interface().get("3_ressources", {}).get("salles", [])
    ]

    identifiants = []
    for i, p in enumerate(data):
        civilite = p.get("Civilite", "").strip()
        nom = p.get("Nom", "").strip()
        prenom = p.get("Prenom", "").strip()
        identifiant = f"{civilite} {nom} {prenom}"

        # Vérif unicité
        if identifiant in identifiants:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"Le professeur « {identifiant} » est en double. Chaque combinaison Civilité + Nom + Prénom doit être unique."
            ])
        identifiants.append(identifiant)

        # Vérif niveaux
        niveaux = [n.strip() for n in p.get("Niveaux", "").split(",") if n.strip()]
        if not all(n in niveaux_valides for n in niveaux):
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"Les niveaux indiqués pour « {identifiant} » sont invalides. Utilisez uniquement 6e, 5e, 4e ou 3e séparés par des virgules."
            ])

        # Vérif durée
        try:
            duree = float(p.get("Duree", 0))
            if not (0.25 <= duree <= 4):
                return dash.no_update, html.Span([
                    html.I(className="bi bi-exclamation-octagon me-2"),
                    f"La durée préférée pour « {identifiant} » doit être comprise entre 0.25 et 4 heures."
                ])
        except ValueError:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"La durée préférée pour « {identifiant} » doit être un nombre (ex. : 1.5)."
            ])

        # Vérif volume
        try:
            volume = int(p.get("Volume", 0))
            if not (1 <= volume <= 40):
                return dash.no_update, html.Span([
                    html.I(className="bi bi-exclamation-octagon me-2"),
                    f"Le volume horaire pour « {identifiant} » doit être entre 1 et 40 heures."
                ])
        except ValueError:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"Le volume horaire pour « {identifiant} » doit être un nombre entier."
            ])

        # Vérif salle préférée
        salle = p.get("SallePref", "").strip()
        if salle and salle not in salles_existantes:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"La salle préférée « {salle} » pour « {identifiant} » n'existe pas dans la liste des salles."
            ])

    mettre_a_jour_section_interface("3_ressources.professeurs", data)
    return data, ""

###############################################################################
# SECTION 3.3 - Salles
###############################################################################
colonnes_salles = ["Nom", "Matieres", "Capacite"]
style_vert = {"margin": "10px auto", "width": "90%", "color": "green", "textAlign": "left"}
style_rouge = {"margin": "10px auto", "width": "90%", "color": "red", "textAlign": "left"}

# Indique si le tableau des salles est vide
@app.callback(
    Output("table-salles-vide", "data"),
    Input("table-salles", "data")
)
def maj_etat_salles_vide(data):
    """
    Vérifie si le tableau des salles est vide.

    Cette fonction renvoie un booléen indiquant si la liste des salles est vide,
    ce qui peut être utilisé pour conditionner l'affichage ou certaines actions dans l'interface.

    Args:
        data (list[dict] or None): Liste des salles actuellement présentes dans le tableau.

    Returns:
        bool: True si le tableau est vide ou None, False sinon.
    """
    return not bool(data)

#######################################
# Efface toutes les données du tableau des salles
@app.callback(
    Output("table-salles", "data", allow_duplicate=True),
    Output("import-salles-message", "children", allow_duplicate=True),
    Output("import-salles-message", "style", allow_duplicate=True),
    Output("stockage-fichier-salles", "data", allow_duplicate=True),
    Input("btn-effacer-salles", "n_clicks"),
    prevent_initial_call=True
)
def effacer_tableau_salles(n):
    """
    Réinitialise complètement le tableau des salles.

    Efface toutes les données du tableau des salles, supprime tout message d'importation 
    et réinitialise le stockage temporaire des fichiers importés.

    Args:
        n (int): Nombre de clics sur le bouton d'effacement des salles.

    Returns:
        tuple: Une quadruple sortie contenant :
            - list: Liste vide pour le tableau des salles.
            - str: Message vide.
            - dict: Style de message masqué.
            - None: Réinitialisation du stockage de fichiers.
    """
    return [], "", style_non_visible, None

#######################################
# Ajoute une ligne vide au tableau des salles
@app.callback(
    Output("table-salles", "data", allow_duplicate=True),
    Input("ajouter-ligne-salle", "n_clicks"),
    State("table-salles", "data"),
    prevent_initial_call=True
)
def ajouter_ligne_salle(n, data):
    """
    Ajoute une nouvelle ligne vide au tableau des salles.

    Cette fonction permet d'ajouter dynamiquement une ligne vide pour que l'utilisateur
    puisse saisir manuellement une salle.

    Args:
        n (int): Nombre de clics sur le bouton d'ajout de salle.
        data (list[dict] or None): Données existantes du tableau des salles.

    Returns:
        list[dict]: Liste mise à jour des données, avec une ligne vide ajoutée.
    """
    data = data or []
    data.append({col: "" for col in colonnes_salles})
    return data

#######################################
@app.callback(
    Output("table-salles", "data", allow_duplicate=True),
    Input("table-salles", "data"),
    prevent_initial_call=True
)
def initialiser_si_vide(data):
    """
    Initialise le tableau des salles avec une ligne d'exemple si celui-ci est vide.

    Cette fonction est appelée automatiquement si aucune donnée n'est présente
    dans le tableau. Elle injecte des exemples prédéfinis pour aider l'utilisateur
    à comprendre le format attendu.

    Args:
        data (list[dict] or None): Données actuellement présentes dans le tableau.

    Returns:
        list[dict]: Liste contenant des lignes d'exemple si le tableau est vide.

    Raises:
        PreventUpdate: Si le tableau contient déjà des données, aucun changement n'est effectué.
    """
    if not data:
        return SALLES_DEFAUT
    raise PreventUpdate

#######################################
# Fournit un exemple de fichier de salles (CSV ou Excel)
@app.callback(
    Output("telechargement-exemple-salles", "data"),
    Input("download-salle-csv", "n_clicks"),
    Input("download-salle-xlsx", "n_clicks"),
    prevent_initial_call=True
)
def telecharger_exemple_salle(n_csv, n_xlsx):
    """
    Génère un fichier d'exemple contenant deux lignes de salles au format CSV ou Excel.

    En fonction du bouton cliqué, un fichier exemple_salles.csv ou exemple_salles.xlsx
    est généré à partir du DataFrame DF_SALLES et proposé en téléchargement.

    Args:
        n_csv (int): Nombre de clics sur le bouton de téléchargement CSV.
        n_xlsx (int): Nombre de clics sur le bouton de téléchargement Excel.

    Returns:
        flask.Response: Objet Dash permettant le téléchargement du fichier.
    
    Raises:
        PreventUpdate: Si aucun des deux boutons n'est cliqué.
    """
    if ctx.triggered_id == "download-salle-csv":
        return dcc.send_data_frame(DF_SALLES.to_csv, "exemple_salles.csv", index=False)
    elif ctx.triggered_id == "download-salle-xlsx":
        return dcc.send_data_frame(DF_SALLES.to_excel, "exemple_salles.xlsx", index=False)

    raise PreventUpdate

#######################################
# Traite l'import d'un fichier pour les salles : insère ou propose modal si déjà des données
@app.callback(
    Output("stockage-fichier-salles", "data", allow_duplicate=True),
    Output("modal-choix-import-salles", "is_open", allow_duplicate=True),
    Output("table-salles", "data", allow_duplicate=True),
    Output("import-salles-message", "children", allow_duplicate=True),
    Output("import-salles-message", "style", allow_duplicate=True),
    Input("upload-salles", "contents"),
    State("upload-salles", "filename"),
    State("table-salles", "data"),
    prevent_initial_call=True
)
def importer_salles(contents, filenames, current_data):
    """
    Gère l'import de fichiers de salles au format CSV ou Excel.

    Si le tableau actuel est vide, les données importées sont insérées immédiatement.
    Sinon, une fenêtre modale est affichée pour laisser le choix entre fusionner ou remplacer.

    Args:
        contents (str or list): Contenu encodé du/des fichier(s) importé(s).
        filenames (str or list): Nom(s) de fichier(s) associé(s) à contents.
        current_data (list[dict]): Données déjà présentes dans le tableau des salles.

    Returns:
        tuple:
            - list[dict]: Fichiers stockés temporairement pour traitement.
            - bool: True si modal à afficher, sinon False.
            - list[dict] or dash.no_update: Nouvelles données à afficher dans le tableau.
            - str or dash.no_update: Message utilisateur sur l'import.
            - dict: Style CSS du message (succès ou erreur).
    """
    if not contents:
        raise PreventUpdate

    if isinstance(contents, str):
        contents = [contents]
        filenames = [filenames]

    fichiers = [{"contents": c, "filename": f} for c, f in zip(contents, filenames)]
    donnees = []

    for f in fichiers:
        try:
            content_type, content_string = f["contents"].split(",")
            decoded = base64.b64decode(content_string)
            ext = f["filename"].split(".")[-1]

            if ext in ["xls", "xlsx"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif ext == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return no_update, False, no_update, f"Extension non supportée : {f['filename']}", style_rouge

            if not set(colonnes_salles).issubset(df.columns):
                return no_update, False, no_update, f"Colonnes manquantes dans : {f['filename']}", style_rouge

            donnees.extend(df[colonnes_salles].to_dict("records"))

        except Exception as e:
            return no_update, False, no_update, f"Erreur lecture {f['filename']} : {str(e)}", style_rouge

    if not bool(current_data):
        return fichiers, False, donnees, "Fichier(s) importé(s) avec succès !", style_vert
    else:
        return fichiers, True, no_update, no_update, no_update

#######################################
# Applique la fusion ou le remplacement des données après import
@app.callback(
    Output("table-salles", "data", allow_duplicate=True),
    Output("import-salles-message", "children", allow_duplicate=True),
    Output("modal-choix-import-salles", "is_open", allow_duplicate=True),
    Output("import-salles-message", "style", allow_duplicate=True),
    Input("btn-fusionner-salles", "n_clicks"),
    Input("btn-remplacer-salles", "n_clicks"),
    State("stockage-fichier-salles", "data"),
    State("table-salles", "data"),
    prevent_initial_call=True
)
def appliquer_import_salles(fusion, remplacement, stockage, table_data):
    """
    Applique le choix de fusion ou de remplacement des données importées dans le tableau des salles.

    Les fichiers sont relus depuis le stockage temporaire, les données extraites sont ensuite
    fusionnées avec les données existantes ou les remplacent selon le bouton cliqué.

    Args:
        fusion (int): Nombre de clics sur le bouton "Fusionner".
        remplacement (int): Nombre de clics sur le bouton "Remplacer".
        stockage (list[dict]): Liste des fichiers encodés stockés précédemment.
        table_data (list[dict]): Données actuelles du tableau des salles.

    Returns:
        tuple:
            - list[dict]: Nouvelles données du tableau.
            - str: Message utilisateur.
            - bool: Indique si la modal doit rester ouverte (False).
            - dict: Style CSS du message de retour.
    """
    if not stockage:
        raise PreventUpdate

    fichiers = stockage if isinstance(stockage, list) else [stockage]
    nouvelles_donnees = []

    for f in fichiers:
        try:
            content_type, content_string = f["contents"].split(",")
            decoded = base64.b64decode(content_string)
            ext = f["filename"].split(".")[-1]

            if ext in ["xls", "xlsx"]:
                df = pd.read_excel(io.BytesIO(decoded), dtype=str)
            elif ext == "csv":
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), dtype=str)
            else:
                return no_update, f"Extension non supportée : {f['filename']}", False, style_rouge

            if not set(colonnes_salles).issubset(df.columns):
                return no_update, f"Colonnes manquantes : {f['filename']}", False, style_rouge

            nouvelles_donnees.extend(df[colonnes_salles].to_dict("records"))

        except Exception as e:
            return no_update, f"Erreur {f['filename']} : {str(e)}", False, style_rouge

    if ctx.triggered_id == "btn-fusionner-salles":
        donnees_finales = (table_data or []) + nouvelles_donnees
    elif ctx.triggered_id == "btn-remplacer-salles":
        donnees_finales = nouvelles_donnees
    else:
        raise PreventUpdate

    return donnees_finales, "Fichier(s) importé(s) avec succès !", False, style_vert

#################################################################################################################################################################
# Affiche ou masque la fenêtre modale de confirmation de réinitialisation
@app.callback(
    Output("modal-reset-confirmation", "is_open"),
    Input("btn-reset-data", "n_clicks"),
    Input("confirm-reset", "n_clicks"),
    Input("cancel-reset", "n_clicks"),
    State("modal-reset-confirmation", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open):
    """
    Ouvre ou ferme la fenêtre modale de confirmation de réinitialisation des données.

    La fenêtre s'ouvre lorsqu'on clique sur "Réinitialiser", et se ferme
    lorsqu'on clique sur "Confirmer" ou "Annuler".

    Args:
        n1 (int): Nombre de clics sur le bouton "Réinitialiser".
        n2 (int): Nombre de clics sur le bouton "Confirmer".
        n3 (int): Nombre de clics sur le bouton "Annuler".
        is_open (bool): État actuel de la fenêtre modale.

    Returns:
        bool: Nouvel état de la fenêtre (True si ouverte, False si fermée).
    """
    triggered = ctx.triggered_id
    if triggered == "btn-reset-data":
        return True
    if triggered in {"confirm-reset", "cancel-reset"}:
        return False
    return is_open

#######################################
@callback(
    Output("table-salles", "data", allow_duplicate=True),
    Input("btn-generer-salles", "n_clicks"),
    State("table-salles", "data"),
    State("nb-salles-generees", "value"),
    State("matieres-salles-generees", "value"),
    State("capacite-salle-generee", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def generer_salles(n_clicks, data, nb_salles, matiere, capacite, freeze):
    """
    Génère automatiquement un nombre donné de salles avec une matière associée et une capacité définie.

    Chaque salle reçoit un nom auto-incrémenté basé sur le nombre de salles déjà présentes.

    Args:
        n_clicks (int): Nombre de clics sur le bouton de génération.
        data (list[dict]): Données actuelles du tableau des salles.
        nb_salles (int): Nombre de salles à générer.
        matiere (str): Matière à affecter à chaque salle générée.
        capacite (int): Capacité à affecter à chaque salle.
        freeze (bool): Si True, la génération est bloquée.

    Returns:
        list[dict]: Données des salles mises à jour.
    
    Raises:
        PreventUpdate: Si le formulaire est incomplet ou figé.
    """
    if freeze:
        raise PreventUpdate
    if not nb_salles or not capacite:
        raise PreventUpdate

    data = data or []
    debut = len(data) + 1
    for i in range(nb_salles):
        data.append({
            "Nom": f"Salle_{i + debut}",
            "Matieres": matiere,
            "Capacite": str(capacite)
        })
    mettre_a_jour_section_interface("3_ressources.salles", data)
    return data

@callback(
    Output("dummy-stockage-salles", "data", allow_duplicate=True),
    Output("erreur-salles", "children", allow_duplicate=True),
    Input("table-salles", "data"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_salles(data, freeze):
    """
    Sauvegarde les données saisies pour les salles et effectue des vérifications de cohérence.

    Vérifie notamment :
    - L'unicité des noms de salles
    - Que les capacités sont bien des entiers entre 0 et 500

    Args:
        data (list[dict]): Données saisies dans le tableau des salles.
        freeze (bool): Si True, empêche la sauvegarde.

    Returns:
        tuple:
            - dash.no_update: Les données ne sont pas modifiées (écriture dans fichier JSON uniquement).
            - Union[str, html.Span]: Message d'erreur ou chaîne vide si tout est valide.
    
    Raises:
        PreventUpdate: Si le processus est figé par freeze.
    """
    if freeze:
        raise PreventUpdate
    noms = [s.get("Nom", "").strip() for s in data if s.get("Nom")]
    if len(noms) != len(set(noms)):
        return dash.no_update, html.Span([
            html.I(className="bi bi-exclamation-octagon me-2"),
            "Les noms de salles doivent être uniques."
        ])

    # Vérifie que les capacités sont dans [0, 100]
    for i, s in enumerate(data):
        try:
            cap = int(s.get("Capacite", -1))
            if not (0 <= cap <= 500):
                return dash.no_update, html.Span([
                    html.I(className="bi bi-exclamation-octagon me-2"),
                    f"La capacité de la salle « {s.get('Nom', f'Salle {i+1}')} » doit être entre 0 et 500."
                ])
        except ValueError:
            return dash.no_update, html.Span([
                html.I(className="bi bi-exclamation-octagon me-2"),
                f"La capacité de la salle « {s.get('Nom', f'Salle {i+1}')} »  doit être un nombre entier."
            ])

    mettre_a_jour_section_interface("3_ressources.salles", data)
    return dash.no_update, ""

###############################################################################
# SECTION 4 - Export / Calcul automatique (bouton suivant)
###############################################################################
@callback(
    Output("redirect-suivant", "pathname"),
    Input("btn-suivant", "n_clicks"),
    Input("btn-precedent", "n_clicks"),
    prevent_initial_call=True
)
def naviguer(n_suivant, n_precedent):
    """
    Gère la navigation entre les pages de l'application via les boutons "Suivant" et "Précédent".

    Lors du clic sur "Suivant", déclenche des fonctions de pré-calcul avant de rediriger.
    Lors du clic sur "Précédent", renvoie à la page d'accueil.

    Args:
        n_suivant (int): Nombre de clics sur le bouton "Suivant".
        n_precedent (int): Nombre de clics sur le bouton "Précédent".

    Returns:
        str: Nouvelle URL vers laquelle rediriger l'utilisateur ("/contraintes" ou "/accueil").

    Raises:
        PreventUpdate: Si aucun bouton valide n'a été cliqué.
    """
    triggered = ctx.triggered_id

    if triggered == "btn-suivant":
        calculer_horaires_affichage()
        generer_professeurs_affichage()
        generer_volume_horaire()
        generer_salles_affichage()
        return "/contraintes"

    elif triggered == "btn-precedent":
        return "/accueil"

    raise PreventUpdate

###############################################################################
@callback(
    Output("freeze-callbacks", "data", allow_duplicate=True),
    Input("reset-message", "children"),
    prevent_initial_call=True
)
def desactiver_freeze(_):
    """
    Réactive les callbacks après une réinitialisation (défreezing).

    Utilisé pour permettre à nouveau les interactions après un reset global.

    Args:
        _ (Any): Contenu du composant déclencheur (non utilisé).

    Returns:
        bool: False, pour indiquer que les callbacks ne sont plus figés.
    """
    return False

