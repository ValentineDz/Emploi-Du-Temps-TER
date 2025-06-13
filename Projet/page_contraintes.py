import json
import os
import pandas as pd
from dash import html, dcc, Input, Output, State, callback_context, dash_table, ALL, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from main_dash import app
from fonctions import *
from math import ceil
from textes import page_contraintes
from constantes import *

from styles import *


def layout_contraintes():
    """
    Construit le layout principal de la page "Contraintes" de l'application Dash.

    Cette page permet à l'utilisateur de renseigner les différentes contraintes
    horaires pour les professeurs, groupes/classes et salles, à travers :
    - des tableaux emploi du temps interactifs ;
    - des boutons pour définir des indisponibilités (partielles ou totales) ou disponibilités ;
    - des panneaux latéraux pour ajouter des contraintes par sélection de jours et d'heures.

    Elle inclut également une section "3.4 Contraintes planning" contenant :
    - le nombre d'heures maximal à la suite pour une matière ;
    - les contraintes de cours obligatoires/interdits à des moments précis ;
    - les enchaînements autorisés/interdits entre cours avec un nombre minimal d'occurrences.

    Les données sont lues depuis le fichier data/data_interface.json et utilisées
    pour générer dynamiquement :
    - les jours et heures affichés ;
    - les listes de professeurs, groupes/classes et salles ;
    - les contraintes déjà enregistrées (via store-*) pour chaque entité.

    Returns:
        html.Div: Composant Dash contenant la structure complète de la page
        avec en-tête, explication, accordéons de contraintes et boutons de navigation.
    """
    generer_professeurs_affichage()
    generer_volume_horaire()
    generer_salles_affichage()
    config = charger_config()

    # 1. Jours
    jours = (
        config["1_horaires"]["jours_classiques"]
    )

    # 2. Créneaux horaires affichés
    heures = config["affichage"]["horaires_affichage"]

    # 3. Professeurs
    profs = config["affichage"]["professeurs_affichage"]

    # 4. Groupes / classes : on prend les clés de 4_programme_national
    groupes = list(config["affichage"]["volume_horaire_affichage"].keys())

    # 5. Salles : on récupère le champ "Nom" dans 3_ressources → salles
    salles = config["affichage"]["salles_affichage"]
    # 6. Volume horaire (pour planning, enchaînements…)
    volume_horaire = config["affichage"]["volume_horaire_affichage"]


    # Chargement des données
    store_profs_data    = charger_contraintes_interface("profs")
    store_groupes_data  = charger_contraintes_interface("groupes")
    store_salles_data   = charger_contraintes_interface("salles")

    # Construction des AccordionItem pour chaque section
    items = [
        # Sections profs, groupes, salles
        make_section_contraintes(
            "profs",
            "Contraintes des professeurs",
            profs,
            store_profs_data,
            construire_recapitulatif(store_profs_data, heures),
            jours,
            heures
        ),
        make_section_contraintes(
            "groupes",
            "Contraintes des groupes/classes",
            groupes,
            store_groupes_data,
            construire_recapitulatif(store_groupes_data, heures),
            jours,
            heures
        ),
        make_section_contraintes(
            "salles",
            "Contraintes des salles",
            salles,
            store_salles_data,
            construire_recapitulatif(store_salles_data, heures),
            jours,
            heures
        ),
        # Section 3.4 Contrainte planning
        dbc.AccordionItem(
            html.Div([
                # 1) Nombre d'heures maximal à la suite
                html.H5("Nombre d'heures maximal à la suite"),
                html.Div(
                    style=style_flex_space_between,
                    children=[
                        html.Div([
                            html.Label("Qui :"),
                            dcc.Dropdown(
                                id="dropdown-qui-planning",
                                options=[],
                                multi=True,
                                placeholder="Sélectionner les classes "
                            )
                        ], style=style_dropdown_qui),
                        html.Div([
                            html.Label("Matière :"),
                            dcc.Dropdown(
                                id="dropdown-matiere-planning",
                                options=[],
                                multi=True,
                                placeholder="Sélectionner les matières"
                            )
                        ], style=style_dropdown_cours),
                        html.Div([
                            html.Label("Nombre d'heures :"),
                            dcc.Dropdown(
                                id="dropdown-nb-heures-planning",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner le nombre d'heures"
                            )
                        ], style=style_col_23),
                        html.Div([
                            html.Label("Étendue :"),
                            dcc.Dropdown(
                                id="dropdown-etendue-planning",
                                options=[
                                    {"label": "1/2 jours", "value": "1/2 jour"},
                                    {"label": "jours",     "value": "jour"}
                                ],
                                multi=False,
                                placeholder="Sélectionner l'étendue"
                            )
                        ], style=style_col_23),
                    ]
                ),
                html.Br(),
                html.Div([
                    dbc.Button("Appliquer", id="btn-appliquer-planning", color="primary", className="me-2"),
                    dbc.Button("Reset",      id="btn-reset-planning",      color="secondary"),
                ], className="text-center mb-4"),
                html.H5("Récapitulatif des contraintes planning", style=style_recap_title),
                dash_table.DataTable(
                    id="table-recap-planning",
                    columns=[
                        {"name":"Qui",         "id":"Qui"},
                        {"name":"Matière",     "id":"Matiere"},
                        {"name":"Nb d'heures", "id":"Nb_heures"},
                        {"name":"Étendue",     "id":"Etendue"},
                    ],
                    page_size=6,
                    page_action='native',
                    data=[],
                    row_deletable=True,
                    style_table=style_table_container,
                    style_cell=style_cell,
                    style_header=style_header,
                ),
                html.Hr(),
                # 2) Contrainte cours-planning
                html.H5("Contrainte cours-planning", className="mt-4"),
                html.Div(
                    style=style_flex_space_between,
                    children=[
                         html.Div([
                            html.Label("Qui :"),
                            dcc.Dropdown(
                                id="dropdown-qui-cours-planning",
                                options=[],
                                multi=True,
                                placeholder="Sélectionner les classes"
                            )
                        ], style=style_dropdown_qui),
                        html.Div([
                            html.Label("Matière :"),
                            dcc.Dropdown(
                                id="dropdown-matiere-cours-planning",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner les matières"
                            )
                        ], style=style_dropdown_cours),
                        html.Div([
                            html.Label("Jours :"),
                            dcc.Dropdown(
                                id="dropdown-jours-cours-planning",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner les jours"
                            )
                        ], style=style_col_19),
                        html.Div([
                            html.Label("Heures :"),
                            dcc.Dropdown(
                                id="dropdown-heures-cours-planning",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner les plages horaires"
                            )
                        ], style=style_col_19),
                    ]
                ),
                html.Br(),
                html.Div([
                    dbc.Button("Appliquer", id="btn-appliquer-cours-planning", color="primary", className="me-2"),
                    dbc.Button("Reset",      id="btn-reset-cours-planning",      color="secondary"),
                ], className="text-center mb-4"),
                html.H5("Récapitulatif Contrainte cours-planning", style=style_recap_title),
                dash_table.DataTable(
                    id="table-recap-cours-planning",
                    columns=[
                        {"name":"Qui","id":"Qui"},
                        {"name":"Type","id":"Type"},
                        {"name":"Matière","id":"Matiere"},
                        {"name":"Jour","id":"Jour"},
                        {"name":"Heure","id":"Heure"},
                    ],
                    page_size=6,
                    page_action='native',
                    data=[],
                    row_deletable=True,
                    style_table=style_table_container,
                    style_cell=style_cell,
                    style_header=style_header,
                ),
                html.Hr(),
                # 3) Enchaînement de cours
                html.H5("Enchaînement de cours", className="mt-4"),

                # Ligne des dropdowns
                html.Div(
                    style=style_flex_space_between,
                    children=[
                        html.Div([
                            html.Label("Qui :"),
                            dcc.Dropdown(
                                id="dropdown-qui-enchainement",
                                options=[],
                                multi=True,
                                placeholder="Sélectionner classes"
                            )
                        ], style=style_dropdown_qui),

                        html.Div([
                            html.Label("Type :"),
                            dcc.Dropdown(
                                id="dropdown-type-enchainement",
                                options=[
                                    {"label":"Obligation","value":"Obligation"},
                                    {"label":"Interdiction","value":"Interdiction"},
                                ],
                                clearable=True,
                                placeholder="Choisir un type"
                            )
                        ], style=style_dropdown_type),

                        html.Div([
                            html.Label("Cours A :"),
                            dcc.Dropdown(
                                id="dropdown-coursA-enchainement",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner Cours A"
                            )
                        ], style=style_dropdown_cours),

                        html.Div([
                            html.Label("Cours B :"),
                            dcc.Dropdown(
                                id="dropdown-coursB-enchainement",
                                options=[],
                                multi=False,
                                placeholder="Sélectionner Cours B"
                            )
                        ], style=style_dropdown_cours),

                        html.Div([
                            html.Label("Minimum :"),
                            dcc.Dropdown(
                                id="input-min-enchainement",
                                options=[],
                                placeholder="Minimal d'occurrences"
                            )
                        ], style=style_dropdown_minimum),
                    ]
                ),
                html.Br(),

                # Ligne des boutons Appliquer / Reset
                html.Div(
                    [
                        dbc.Button("Appliquer", id="btn-appliquer-enchainement", color="primary", className="me-2"),
                        dbc.Button("Reset",      id="btn-reset-enchainement",      color="secondary"),
                    ],
                    className="text-center mb-4"
                ),
                # Titre récapitulatif
                html.H5("Récapitulatif Contrainte enchaînement de cours", style=style_recap_title),
                dash_table.DataTable(
                    id="table-recap-enchainement",
                    columns=[
                        {"name": "Qui",      "id": "Qui"},
                        {"name": "Type",     "id": "Type"},
                        {"name": "Cours A",  "id": "CoursA"},
                        {"name": "Cours B",  "id": "CoursB"},
                        {"name": "Minimum",  "id": "Minimum"},
                    ],
                    page_size=6,
                    page_action='native',
                    data=[],
                    row_deletable=True,
                    style_table=style_table_container,
                    style_cell=style_cell_small,
                    style_header=style_header,
                ),
                # Stores
                dcc.Store(id="store-planning-data", data=charger_contraintes_3_4("planning")),
                dcc.Store(id="store-cours-planning-data", data=charger_contraintes_3_4("cours_planning")),
                dcc.Store(id="store-enchainement-data", data=charger_contraintes_3_4("enchainement")),
                dcc.Store(id="store-volume-horaire", data = volume_horaire),
            ], style={"padding": "1rem"}
            ),
            title=html.P("3.4 Contraintes planning", style = titre_accordion_h4),
            item_id="contraintes-planning"
        )
    ]
    # Retourne le layout global avec Accordion
    return html.Div([
        html.H1("Renseignement des contraintes de l'établissement",className="titre-section"),
        html.Hr(style=style_hr),
        html.P(page_contraintes,style=explication_style),
        dbc.Accordion(
            items,
            id="accordion-contraintes",
            start_collapsed=True,
            flush=True,
            always_open=False,
            style=style_accordeons
        ),

        html.Div([
            html.Div(id="redirect-page-contrainte-add"), 
            html.Br(),
            html.Div([
                html.Button([html.I(className="bi bi-arrow-left me-2"), "Page précédente"],
                            id="btn-previous-contrainte", n_clicks=0, className="btn btn-secondary", style=style_btn_suivant),
                html.Button(["Page suivante", html.I(className="bi bi-arrow-right ms-2")],
                            id="btn-next-contrainte", n_clicks=0, className="btn btn-primary", style=style_btn_suivant),
            ], style={"display": "flex", "justifyContent": "space-between", "marginTop": "30px"})
        ]), 
        dcc.Location(id="redirect-page-contrainte-add", refresh=True)
    ], style=global_page_style)
# Callbacks
from dash.exceptions import PreventUpdate
def make_callback_contraintes(entite: str, jours: list, heures: list):
    @app.callback(
        [
            Output(f"store-couleur-active-{entite}", "data", allow_duplicate=True),
            Output(f"store-cell-colors-{entite}",    "data", allow_duplicate=True),
            Output(f"store-recap-{entite}",          "data"),
            Output(f"table-edt-{entite}",            "style_data_conditional"),
            Output(f"table-recap-{entite}",          "data"),
            Output(f"store-{entite}-data",           "data", allow_duplicate=True),
            Output(f"select-{entite}", "value", allow_duplicate=True),

        ],
        [
            Input(f"btn-vert-{entite}",      "n_clicks"),
            Input(f"btn-orange-{entite}",    "n_clicks"),
            Input(f"btn-rouge-{entite}",     "n_clicks"),
            Input(f"btn-reset-{entite}",     "n_clicks"),
            Input(f"btn-appliquer-{entite}", "n_clicks"),
            Input(f"table-edt-{entite}",     "active_cell"),
            Input(f"table-recap-{entite}",   "data"),
        ],
        [
            State(f"dropdown-jours-{entite}",       "value"),
            State(f"dropdown-plages-{entite}",      "value"),
            State(f"dropdown-contraintes-{entite}", "value"),
            State(f"select-{entite}",               "value"),
            State(f"store-couleur-active-{entite}", "data"),
            State(f"store-cell-colors-{entite}",    "data"),
            State(f"store-recap-{entite}",          "data"),
            State(f"table-edt-{entite}",            "data"),
            State(f"store-{entite}-data",           "data"),
        ],
        prevent_initial_call=True
    )
    def update_contraintes(
        btn_vert, btn_orange, btn_rouge, btn_reset, btn_appliquer, active_cell, recap_data_input,
        selected_jours, selected_plages, contra_type, selectionnes,
        couleur_active, cell_colors, recap_data, table_data, store_data):

        from dash import callback_context

        ctx = callback_context.triggered_id
        couleur_active = couleur_active or "Disponible"
        cell_colors    = cell_colors or {}
        recap_data     = recap_data or []
        store_data     = store_data or {}

        if ctx == f"btn-vert-{entite}":
            nouvelle_couleur = "Disponible"
        elif ctx == f"btn-orange-{entite}":
            nouvelle_couleur = "Indisponibilité partielle"
        elif ctx == f"btn-rouge-{entite}":
            nouvelle_couleur = "Indisponibilité totale"
        else:
            nouvelle_couleur = couleur_active

        # Application via panneau
        if ctx == f"btn-appliquer-{entite}":
            if not selectionnes or not contra_type:
                raise PreventUpdate
            jours_cibles  = selected_jours or jours
            plages_cibles = selected_plages or [r["Heure"] for r in table_data]
            for jour in jours_cibles:
                for heure in plages_cibles:
                    idx = next((i for i, r in enumerate(table_data) if r["Heure"] == heure), None)
                    if idx is None:
                        continue
                    key = f"{idx}|{jour}"
                    for cible in selectionnes:
                        cell_colors[key] = contra_type
                        data = store_data.get(cible, {}).copy()
                        data[key] = contra_type
                        store_data[cible] = data
                        recap_data = [
                            e for e in recap_data
                            if not (e["Concerne"] == cible and e["Jour"] == jour and e["Heure"] == heure)
                        ]
                        if contra_type != "Disponible":
                            recap_data.append({
                                "Concerne":   cible,
                                "Jour":       jour,
                                "Heure":      heure,
                                "Contrainte": contra_type
                            })

        # Réinitialisation
        elif ctx == f"btn-reset-{entite}":
            default_cells = {
                f"{i}|{j}": "Disponible"
                for i in range(len(table_data))
                for j in jours
            }
            if selectionnes:
                for cible in selectionnes:
                    store_data[cible] = default_cells.copy()
                recap_data = [e for e in recap_data if e["Concerne"] not in selectionnes]
                cell_colors = store_data.get(selectionnes[0], default_cells)
            else:
                store_data = {}
                recap_data = []
                cell_colors = default_cells

        # Clic sur une cellule
        elif ctx == f"table-edt-{entite}" and active_cell and nouvelle_couleur:
            row = active_cell.get("row")
            col = active_cell.get("column_id")
            if row is not None and col in jours:
                heure = table_data[row]["Heure"]
                key = f"{row}|{col}"
                for cible in selectionnes or []:
                    cell_colors[key] = nouvelle_couleur
                    data = store_data.get(cible, {}).copy()
                    data[key] = nouvelle_couleur
                    store_data[cible] = data
                    recap_data = [
                        e for e in recap_data
                        if not (e["Concerne"] == cible and e["Jour"] == col and e["Heure"] == heure)
                    ]
                    if nouvelle_couleur != "Disponible":
                        recap_data.append({
                            "Concerne":   cible,
                            "Jour":       col,
                            "Heure":      heure,
                            "Contrainte": nouvelle_couleur
                        })

        # Suppression dans le récapitulatif
        elif ctx == f"table-recap-{entite}":
            new_store_data = {}
            for entry in recap_data_input:
                nom = entry["Concerne"]
                jour = entry["Jour"]
                heure = entry["Heure"]
                contrainte = entry["Contrainte"]
                try:
                    idx = heures.index(heure)
                except ValueError:
                    continue
                key = f"{idx}|{jour}"
                new_store_data.setdefault(nom, {})[key] = contrainte

            store_data = new_store_data
            recap_data = recap_data_input

            if selectionnes:
                ref = store_data.get(selectionnes[0], {})
                same = all(store_data.get(sel, {}) == ref for sel in selectionnes)
                if not same:
                    selectionnes = [selectionnes[0]]

                cible = selectionnes[0]
                default_cells = {
                    f"{i}|{j}": "Disponible"
                    for i in range(len(table_data))
                    for j in jours
                }
                cell_colors = store_data.get(cible, default_cells)
            else:
                cell_colors = {}

            styles = build_styles(cell_colors)
            save_constraints_interface(entite, store_data)

            return (
                couleur_active,
                cell_colors,
                recap_data,
                styles,
                recap_data,
                store_data,
                selectionnes
            )

        # Sélection d'une entité
        else:
            if selectionnes:
                premier = selectionnes[0]
                default_cells = {
                    f"{i}|{j}": "Disponible"
                    for i in range(len(table_data))
                    for j in jours
                }
                cell_colors = store_data.get(premier, default_cells)

        styles = build_styles(cell_colors)
        save_constraints_interface(entite, store_data)

        return (
            nouvelle_couleur,
            cell_colors,
            recap_data,
            styles,
            recap_data,
            store_data,
            selectionnes
        )

def make_callback_update_table_styles_on_selection(entite: str, jours: list, heures: list):
    """
    Crée dynamiquement un callback Dash qui met à jour les styles d'affichage
    d'un tableau emploi du temps (DataTable) en fonction des contraintes enregistrées
    pour une entité sélectionnée (professeur, groupe ou salle).

    Ce callback est associé à une sélection d'entité (dropdown) et recharge les styles
    de la table correspondante (table-edt-{entite}), en colorant les cellules selon 
    leur statut de contrainte : "Disponible", "Partielle", "Indisponible".

    Args:
        entite (str): Nom de l'entité ciblée (ex. "prof", "groupe", "salle").
        jours (list): Liste des jours affichés dans la table (ex. ["Lundi", "Mardi", ...]).
        heures (list): Liste des heures ou plages horaires (ex. ["8h", "9h", ...]).

    Returns:
        function: Un callback Dash interne lié à l'entité, qui retourne une liste de 
        styles conditionnels à appliquer à la DataTable.
    """
    @app.callback(
        Output(f"table-edt-{entite}", "style_data_conditional", allow_duplicate=True),
        Input(f"select-{entite}", "value"),
        State(f"store-{entite}-data", "data"),
        prevent_initial_call=True
    )
    def update_table_style_on_selection(selectionnes, store_data):
        store_data = store_data or {}
        if not selectionnes:
            return []

        contraintes_partielles = store_data.get(selectionnes[0], {})
        contraintes_completes = {
            f"{i}|{j}": contraintes_partielles.get(f"{i}|{j}", "Disponible")
            for i in range(len(heures))
            for j in jours
        }

        return build_styles(contraintes_completes)


config = charger_config()
jours = config["1_horaires"]["jours_classiques"]
heures = config["affichage"]["horaires_affichage"]

make_callback_update_table_styles_on_selection("profs", jours, heures)
make_callback_update_table_styles_on_selection("groupes", jours, heures)
make_callback_update_table_styles_on_selection("salles", jours, heures)


def contraintes_identiques(ref_cfg, other_cfg, default_color="Disponible"):
    """
    Vérifie si deux configurations de contraintes sont identiques.

    Compare deux dictionnaires représentant des contraintes (par cellule horaire),
    en considérant que les cases absentes sont égales à une couleur par défaut
    (généralement "Disponible").

    Args:
        ref_cfg (dict): Dictionnaire de contraintes de référence.
        other_cfg (dict): Dictionnaire de contraintes à comparer.
        default_color (str, optional): Couleur utilisée par défaut pour les cases absentes.
            Par défaut "Disponible".

    Returns:
        bool: True si les deux configurations sont identiques pour toutes les cases
        (mêmes valeurs ou valeurs par défaut), False sinon.
    """
    ref_cfg = ref_cfg or {}
    other_cfg = other_cfg or {}

    # Set de toutes les clés utilisées
    all_keys = set(ref_cfg.keys()) | set(other_cfg.keys())
    for key in all_keys:
        if ref_cfg.get(key, default_color) != other_cfg.get(key, default_color):
            return False
    return True

def make_disable_options_callback(entite: str):
    """
    Crée un callback Dash qui désactive dynamiquement les options incompatibles
    dans le menu déroulant d'une entité (professeur, groupe ou salle).

    Le callback se base sur la configuration des contraintes stockées pour comparer
    chaque entité à l'entité actuellement sélectionnée. Celles ayant une configuration
    différente sont désactivées dans le dropdown.

    Args:
        entite (str): Type d'entité ciblée, doit être l'une des chaînes suivantes :
            "profs", "groupes", ou "salles".

    Returns:
        function: Callback Dash qui met à jour dynamiquement les options du composant
        select-{entite} en les désactivant si leurs contraintes ne correspondent
        pas à celles de l'entité sélectionnée.
    """
    @app.callback(
        Output(f"select-{entite}", "options"),
        Input(f"store-{entite}-data", "data"),
        Input(f"select-{entite}", "value")
    )
    def update_options(store_data, selected):
        from page_contraintes import charger_config  
        config = charger_config()

        if entite == "profs":
            liste_complete = config["affichage"]["professeurs_affichage"]
        elif entite == "groupes":
            liste_complete = list(config["affichage"]["volume_horaire_affichage"].keys())
        elif entite == "salles":
            liste_complete = config["affichage"]["salles_affichage"]
        else:
            liste_complete = []

        store_data = store_data or {}
        selected = selected or []
        if not selected:
            return [{"label": nom, "value": nom, "disabled": False} for nom in liste_complete]

        ref = selected[0]
        ref_cfg = store_data.get(ref, {})

        opts = []
        for nom in liste_complete:
            cfg = store_data.get(nom, {})
            disabled = not contraintes_identiques(ref_cfg, cfg)
            opts.append({"label": nom, "value": nom, "disabled": disabled})
        return opts



@app.callback(
    [
        Output("store-cours-planning-data",  "data",allow_duplicate=True),
        Output("table-recap-cours-planning", "data"),
    ],
    Input("btn-appliquer-cours-planning", "n_clicks"),
    [
        State("dropdown-matiere-cours-planning",  "value"),
        State("dropdown-qui-cours-planning",      "value"),
        State("dropdown-jours-cours-planning",    "value"),
        State("dropdown-heures-cours-planning",   "value"),
        State("store-cours-planning-data",        "data"),
    ],
    prevent_initial_call=True
)
def maj_cours_planning(n_clicks, matieres, quis, jours_sel, heures_sel, store_data): 
    """
    Supprime certaines contraintes de type 'nombre d'heures à la suite' selon les filtres appliqués.

    Si aucun filtre n'est spécifié (ni Qui, ni Matière, ni Nb_heures, ni Étendue),
    toutes les contraintes sont supprimées (reset complet).
    Sinon, seules les contraintes correspondant exactement à la sélection sont retirées.

    Args:
        n_clicks (int): Nombre de clics sur le bouton "Réinitialiser".
        qui (str | list): Classe(s) ou groupe(s) ciblé(s) par les contraintes.
        matiere (str | list): Matière(s) concernée(s).
        nb_heures (int | list | None): Nombre d'heures maximum à la suite à supprimer.
        etendue (str): Étendue temporelle de la contrainte (ex. : "matin", "après-midi").
        store (list[dict]): Liste actuelle des contraintes enregistrées.

    Returns:
        Tuple[list, list]: Nouvelle version du store (filtrée) en double pour mise à jour.
    """
    if not n_clicks:
        raise PreventUpdate
    base = store_data or []
    mat_list = matieres if isinstance(matieres, list) else [matieres] if matieres else []
    qui_list = quis if isinstance(quis, list) else [quis] if quis else []
    jours_list = jours_sel if isinstance(jours_sel, list) else [jours_sel] if jours_sel else []
    heures_list= heures_sel if isinstance(heures_sel, list) else [heures_sel] if heures_sel else []

    for m in mat_list:
        for q in qui_list:  
            for j in jours_list:
                for h in heures_list:
                    base.append({
                        "Type":    "Obligation",
                        "Matiere": m,
                        "Qui":     q,
                        "Jour":    j,
                        "Heure":   h,
                    })
    return base, base

# Reset pour "Nombre d'heures maximal"
def reset_planning(n_clicks, qui, matiere, nb_heures, etendue, store):
    if not n_clicks:
        raise PreventUpdate

    data = store or []
    # normaliser en listes
    qui_list   = qui      or []
    mat_list   = matiere  or []
    if isinstance(nb_heures, list):
        nb_list = nb_heures
    elif nb_heures is not None:
        nb_list = [nb_heures]
    else:
        nb_list = []
    etendue_str = (etendue or "").replace("_", " ")

    # si aucun filtre → tout reset
    if not (qui_list or mat_list or nb_list or etendue_str):
        return [], []

    # sinon, ne garder que les lignes qui NE MATCHENT PAS tous les filtres
    def matches(e):
        if qui_list   and e["Qui"]       not in qui_list:   return False
        if mat_list   and e["Matiere"]   not in mat_list:   return False
        if nb_list    and e["Nb_heures"] not in nb_list:    return False
        if etendue_str and e["Etendue"]   != etendue_str:    return False
        return True

    new_data = [e for e in data if not matches(e)]
    return new_data, new_data

# Callbacks Contrainte cours-planning

def maj_contraintes_cours_planning(n_appliquer, n_reset,
                                   type_contraint, matiere, classes, jour, heure, store_data, volume):
    """
    Supprime certaines contraintes de type 'nombre d'heures à la suite' selon les filtres appliqués.

    Si aucun filtre n'est spécifié (ni Qui, ni Matière, ni Nb_heures, ni Étendue),
    toutes les contraintes sont supprimées (reset complet).
    Sinon, seules les contraintes correspondant exactement à la sélection sont retirées.

    Args:
        n_clicks (int): Nombre de clics sur le bouton "Réinitialiser".
        qui (str | list): Classe(s) ou groupe(s) ciblé(s) par les contraintes.
        matiere (str | list): Matière(s) concernée(s).
        nb_heures (int | list | None): Nombre d'heures maximum à la suite à supprimer.
        etendue (str): Étendue temporelle de la contrainte (ex. : "matin", "après-midi").
        store (list[dict]): Liste actuelle des contraintes enregistrées.

    Returns:
        Tuple[list, list]: Nouvelle version du store (filtrée) en double pour mise à jour.
    """
    ctx = callback_context.triggered_id
    store = store_data or []
    new_store = []

    classes = classes if isinstance(classes, list) else [classes] if classes else []

    if ctx == "btn-appliquer-cours-planning":
        if not all([type_contraint, matiere, classes, jour, heure]):
            raise PreventUpdate

        for cls in classes:
            if type_contraint == "Obligation":
                vol = volume.get(cls, {}).get(matiere)
                if not vol:
                    continue  # matière inexistante pour cette classe

                # Nombre d'obligations déjà imposées pour cette matière et cette classe
                count = sum(
                    1 for e in store
                    if e["Type"] == "Obligation" and e["Matiere"] == matiere and e["Qui"] == cls
                )
                if count >= vol:
                    continue  # on dépasse le quota, on ignore

            # Supprimer doublon exact
            store = [e for e in store if not (
                e["Type"] == type_contraint and
                e["Matiere"] == matiere and
                e["Qui"] == cls and
                e["Jour"] == jour and
                e["Heure"] == heure
            )]

            new_store.append({
                "Type": type_contraint,
                "Matiere": matiere,
                "Qui": cls,
                "Jour": jour,
                "Heure": heure
            })

        store.extend(new_store)

    elif ctx == "btn-reset-cours-planning":
        def matches(e):
            if matiere and e["Matiere"] != matiere: return False
            if type_contraint and e["Type"] != type_contraint: return False
            if classes and e["Qui"] not in classes: return False
            if jour and e["Jour"] != jour: return False
            if heure and e["Heure"] != heure: return False
            return True
        store = [e for e in store if not matches(e)]

    enregistrer_contraintes_3_4("cours_planning", store)
    return store, store


@app.callback(
    Output("dropdown-qui-cours-planning", "options"),
    Output("dropdown-matiere-cours-planning", "options"),
    Output("dropdown-jours-cours-planning", "options"),
    Output("dropdown-heures-cours-planning", "options"),
    Input("dropdown-matiere-cours-planning", "value"),
    Input("dropdown-qui-cours-planning", "value"),
    Input("dropdown-jours-cours-planning", "value"),
    Input("dropdown-heures-cours-planning", "value"),
    State("store-cours-planning-data", "data"),
    State("store-volume-horaire", "data"),
)
def disable_incompatibles( matiere, qui_sel, jour, heure, store, volume): #type_,
    """
    Met à jour dynamiquement les listes déroulantes de la contrainte 'cours-planning' 
    en désactivant les options incompatibles.

    - Désactive une classe si elle a déjà une obligation à ce créneau.
    - Désactive une matière si toutes les classes sélectionnées ont atteint leur quota.
    - Désactive un jour ou une heure si le créneau est déjà occupé par une obligation.

    Args:
        type_ (str): Type de contrainte ("Obligation" ou "Interdiction").
        matiere (str): Matière actuellement sélectionnée.
        qui_sel (str | list): Classe(s) ou groupe(s) sélectionné(s).
        jour (str): Jour sélectionné.
        heure (str): Heure sélectionnée.
        store (list[dict]): Liste actuelle des contraintes enregistrées.
        volume (dict): Volume horaire défini pour chaque matière et chaque classe.

    Returns:
        Tuple[list, list, list, list]: 
            - Options pour la dropdown "Qui" (classes), 
            - Options pour "Matière",
            - Options pour "Jour",
            - Options pour "Heure",
        avec les éléments désactivés si nécessaire.
    """
    config = charger_config()
    jours = config["1_horaires"]["jours_classiques"]
    heures = config["affichage"]["horaires_affichage"]
    niveaux = sorted(volume.keys())
    toutes_matieres = sorted(set(m for v in volume.values() for m in v))
    jours_opts = jours
    heures_opts = heures
    store = store or []
    qui_sel = qui_sel if isinstance(qui_sel, list) else [qui_sel] if qui_sel else []

    def is_conflit(q, j, h):
        return any(
            e["Type"] == "Obligation" and e["Qui"] == q and e["Jour"] == j and e["Heure"] == h
            for e in store
        )

    # Désactiver classes si créneau déjà occupé
    qui_opts = []
    for q in niveaux:
        disabled =  jour and heure and is_conflit(q, jour, heure) 
        qui_opts.append({"label": q, "value": q, "disabled": disabled})

    # Désactiver matières si quota dépassé dans TOUTES les classes sélectionnées
    mat_opts = []
    for m in toutes_matieres:
        disable_matiere = False
        if qui_sel:
            disable_matiere = True
            for cls in qui_sel:
                vol = volume.get(cls, {}).get(m)
                if not vol:
                    continue
                used = sum(
                    1 for e in store
                    if e["Type"] == "Obligation" and e["Matiere"] == m and e["Qui"] == cls
                )
                if used < vol:
                    disable_matiere = False
                    break
        mat_opts.append({"label": m, "value": m, "disabled": disable_matiere})

    # Désactiver jours si conflits
    jour_opts = []
    for j in jours_opts:
        disabled = False
        if qui_sel and heure:
            disabled = any(is_conflit(q, j, heure) for q in qui_sel)
        jour_opts.append({"label": j, "value": j, "disabled": disabled})

    # Désactiver heures si conflits
    heure_opts = []
    for h in heures_opts:
        disabled = False
        if  qui_sel and jour: 
            disabled = any(is_conflit(q, jour, h) for q in qui_sel)
        heure_opts.append({"label": h, "value": h, "disabled": disabled})

    return qui_opts, mat_opts, jour_opts, heure_opts


from typing import Callable

# Fonction générique pour gérer les contraintes de la section 3.4
def make_callback_contrainte_3_4(
    cle_json: str,
    ids: dict,
    apply_logic: Callable,
    reset_logic: Callable
):
    """
    Crée dynamiquement un callback Dash générique pour gérer une contrainte de la section 3.4.

    Ce callback peut :
    - appliquer une contrainte en appelant apply_logic (lors du clic sur un bouton "Appliquer") ;
    - réinitialiser certaines contraintes via reset_logic (bouton "Réinitialiser") ;
    - synchroniser le store et le tableau si une ligne du tableau est modifiée manuellement (ex : suppression).

    Si une clé JSON est fournie, la nouvelle valeur est automatiquement enregistrée via
    enregistrer_contraintes_3_4.

    Args:
        cle_json (str): Nom de la clé JSON sous laquelle enregistrer les contraintes (ou "" si pas d'enregistrement).
        ids (dict): Dictionnaire contenant les IDs des composants Dash utilisés.
            Doit inclure les clés suivantes :
                - "store": ID du dcc.Store contenant les données.
                - "table": ID du DataTable.
                - "apply": ID du bouton "Appliquer".
                - "reset": ID du bouton "Réinitialiser".
                - "states": Liste des IDs des éléments d'état à passer aux fonctions logiques.
        apply_logic (Callable): Fonction prenant les states en argument et retournant (store, table) après application.
        reset_logic (Callable): Fonction prenant les states en argument et retournant (store, table) après réinitialisation.

    Returns:
        function: Callback Dash qui met à jour le contenu du tableau et du store associé.
    """
    @app.callback(
        [
            Output(ids["store"], "data", allow_duplicate=True),
            Output(ids["table"], "data", allow_duplicate=True),
        ],
        [
            Input(ids["apply"], "n_clicks"),
            Input(ids["reset"], "n_clicks"),
            Input(ids["table"], "data"),  
        ],
        [  State(i, "data" if i.startswith("store-") else "value")
           for i in ids["states"]
        ],
        prevent_initial_call=True
    )
    def _callback(n_apply, n_reset, data_table, *states):
        """
        Callback exécuté lors des interactions avec les boutons ou le tableau
        pour gérer dynamiquement une contrainte de la section 3.4.

        - Si le bouton "Appliquer" est cliqué, applique la logique métier via apply_logic
        et met à jour le store et le tableau.
        - Si le bouton "Réinitialiser" est cliqué, applique reset_logic pour filtrer ou nettoyer les données.
        - Si une ligne est supprimée manuellement du tableau, synchronise les données avec le store.
        - Enregistre les résultats dans le JSON via enregistrer_contraintes_3_4 si cle_json est fourni.

        Args:
            n_apply (int): Nombre de clics sur le bouton "Appliquer".
            n_reset (int): Nombre de clics sur le bouton "Réinitialiser".
            data_table (list): Données actuelles du tableau.
            *states: Valeurs des états définis dans ids["states"], passées à apply_logic ou reset_logic.

        Returns:
            tuple: Un tuple (store_data, table_data) à injecter dans les composants Dash correspondants.
        """
        ctx = callback_context.triggered_id

        if ctx == ids["apply"]:
            result = apply_logic(*states)
        elif ctx == ids["reset"]:
            result = reset_logic(*states)
        elif ctx == ids["table"]:
            # Suppression d'une ligne : on synchronise store et json
            result = (data_table, data_table)
        else:
            raise PreventUpdate

        if cle_json:
            enregistrer_contraintes_3_4(cle_json, result[0])

        return result
    
# ----------------------- CALLBACK PLANNING -----------------------
ids_planning = {
    "apply": "btn-appliquer-planning",
    "reset": "btn-reset-planning",
    "store": "store-planning-data",
    "table": "table-recap-planning",
    "states": [
        "dropdown-qui-planning",
        "dropdown-matiere-planning",
        "dropdown-nb-heures-planning",
        "dropdown-etendue-planning",
        "store-planning-data",
        "store-volume-horaire"
    ],
    "store_state": "store-planning-data"
}

def apply_logic_planning(qui, matiere, nb_heures, etendue, store_data, volume_horaire):
    """
    Applique une contrainte de type "nombre d'heures maximal à la suite" pour une combinaison
    de classe (ou prof/salle), matière, étendue et nombre d'heures.

    Cette fonction utilise maj_contrainte_nb_heures pour ajouter ou mettre à jour
    les contraintes en fonction des paramètres fournis.

    Args:
        qui (str or list): Élément concerné (ex. : nom de classe).
        matiere (str or list): Nom(s) de matière concernée(s).
        nb_heures (int or list): Nombre d'heures maximal autorisé à la suite.
        etendue (str): Étendue de la contrainte (Jour, Semaine, etc.).
        store_data (list): Liste actuelle des contraintes enregistrées.
        volume_horaire (dict): Volume horaire disponible pour chaque entité.

    Returns:
        tuple: Données mises à jour sous forme (store_data, table_data) prêtes à être enregistrées.
    """
    store_data = store_data or []
    return maj_contrainte_nb_heures(1, qui, matiere, nb_heures, etendue, store_data, volume_horaire)

def reset_logic_planning(qui, matiere, nb_heures, etendue, store_data, volume_horaire):
    """
    Supprime une ou plusieurs contraintes "nombre d'heures à la suite" selon les filtres fournis.

    Args:
        qui (str or list): Élément concerné (classe, prof, salle).
        matiere (str or list): Matières à filtrer.
        nb_heures (int or list): Nombre d'heures associé à la contrainte.
        etendue (str): Étendue de la contrainte (Jour, Semaine, etc.).
        store_data (list): Données de contraintes enregistrées.

    Returns:
        tuple: Liste mise à jour des contraintes sous forme (store_data, table_data).
    """
    return reset_planning(1, qui, matiere, nb_heures, etendue, store_data)

make_callback_contrainte_3_4(
    cle_json="planning",
    apply_logic=apply_logic_planning,
    reset_logic=reset_logic_planning,
    ids=ids_planning
)

# ------------------- CALLBACK COURS PLANNING ---------------------
ids_cours_planning = {
    "apply": "btn-appliquer-cours-planning",
    "reset": "btn-reset-cours-planning",
    "store": "store-cours-planning-data",
    "table": "table-recap-cours-planning",
    "states": [
        "dropdown-matiere-cours-planning",
        "dropdown-qui-cours-planning",
        "dropdown-jours-cours-planning",
        "dropdown-heures-cours-planning",
        "store-cours-planning-data",
        "store-volume-horaire" 
    ],
    "store_state": "store-cours-planning-data"
}

def apply_logic_cours( matiere, classes, jour, heure, store_data, volume_horaire): 
    """
    Applique une contrainte de type "cours-planning" pour une ou plusieurs classes, une matière,
    et un créneau horaire spécifique.

    Cette fonction est utilisée pour ajouter une contrainte d'obligation ou d'interdiction
    d'avoir cours à un moment précis, en respectant les volumes horaires définis.

    Args:
        type_contraint (str): Type de contrainte ("Obligation" ou "Interdiction").
        matiere (str): Nom de la matière concernée.
        classes (list): Liste des classes concernées.
        jour (str): Jour concerné.
        heure (str): Heure concernée.
        store_data (list): Contraintes actuellement enregistrées.
        volume_horaire (dict): Volume horaire disponible par matière et classe.

    Returns:
        tuple: Nouvelles données (store, table) à enregistrer dans le Store et le tableau.
    """
    return maj_contraintes_cours_planning(
        1, 0, "Obligation", matiere, classes, jour, heure,
        store_data, volume_horaire
    )

def reset_logic_cours( matiere, classes, jour, heure, store_data, volume_horaire):
    """
    Supprime des contraintes "cours-planning" existantes selon les filtres donnés.

    Cette fonction enlève les contraintes qui correspondent exactement aux paramètres fournis
    (type, matière, classe, jour, heure).

    Args:
        type_contraint (str): Type de contrainte ("Obligation" ou "Interdiction").
        matiere (str): Nom de la matière à filtrer.
        classes (list): Classes à considérer pour la suppression.
        jour (str): Jour concerné par la contrainte.
        heure (str): Heure concernée.
        store_data (list): Contraintes actuellement enregistrées.
        volume_horaire (dict): Volume horaire par matière et classe (non utilisé ici mais requis par l'API).

    Returns:
        tuple: Contraintes mises à jour après suppression, sous forme (store, table).
    """
    return maj_contraintes_cours_planning(
        0, 1, "Obligation", matiere, classes, jour, heure,
        store_data, volume_horaire
    )

make_callback_contrainte_3_4(
    cle_json="cours_planning",
    apply_logic=apply_logic_cours,
    reset_logic=reset_logic_cours,
    ids=ids_cours_planning
)

# ---------------------- CALLBACK ENCHAINEMENT --------------------
ids_enchainement = {
    "apply": "btn-appliquer-enchainement",
    "reset": "btn-reset-enchainement",
    "store": "store-enchainement-data",
    "table": "table-recap-enchainement",
    "states": [
        "dropdown-type-enchainement",
        "dropdown-coursA-enchainement",
        "dropdown-coursB-enchainement",
        "dropdown-qui-enchainement",
        "input-min-enchainement",
        "store-enchainement-data",
        "store-volume-horaire",
    ],
    "store_state": "store-enchainement-data"
}
def apply_logic_enchainement(
    type_, coursA, coursB, classes, minimum, store_data, volume_horaire
):
    """
    Applique une contrainte d'enchaînement de cours (autorisé ou interdit) entre deux matières pour une ou plusieurs classes.

    Cette contrainte permet de définir qu'un cours A doit (ou ne doit pas) être suivi d'un cours B,
    avec un nombre minimal d'occurrences, en respectant les volumes horaires disponibles pour chaque classe.

    Args:
        type_ (str): Type d'enchaînement ("Autorisé" ou "Interdit").
        coursA (str): Nom du cours initial (cours A).
        coursB (str): Nom du cours suivant (cours B).
        classes (list or str): Liste des classes concernées (ou une seule classe).
        minimum (int or str): Nombre minimal d'occurrences souhaitées pour l'enchaînement.
        store_data (list): Liste actuelle des contraintes d'enchaînement enregistrées.
        volume_horaire (dict): Dictionnaire des volumes horaires par classe et matière.

    Returns:
        tuple: Nouvelles contraintes d'enchaînement (store, table) mises à jour,
               prêtes à être stockées et affichées dans le tableau.
    """
    if not type_:
        raise PreventUpdate

    # Initialisation
    store = store_data or []
    classes = classes if isinstance(classes, list) else [classes] if classes else []
    minimum = int(minimum) if minimum else 1

    new_entries = []
    # Logique d'ajout d'enchaînements 
    for cls in classes:
        volA = volume_horaire.get(cls, {}).get(coursA, 0)
        volB = volume_horaire.get(cls, {}).get(coursB, 0)
        # on ignore si aucune capacité ou même cours
        if not volA or not volB or coursA == coursB:
            continue

        # Total déjà utilisé pour A→X et B→Y
        used_A = sum(
            int(e.get("Minimum", 1))
            for e in store
            if e["Qui"] == cls and e["CoursA"] == coursA
        )
        used_B = sum(
            int(e.get("Minimum", 1))
            for e in store
            if e["Qui"] == cls and e["CoursB"] == coursB
        )
        # on respecte les quotas
        if used_A + minimum > volA or used_B + minimum > volB:
            continue

        # on retire l'ancienne contrainte pour ce couple
        store = [
            e for e in store
            if not (e["Qui"] == cls and e["CoursA"] == coursA and e["CoursB"] == coursB)
        ]

        new_entries.append({
            "Type":    type_,
            "CoursA":  coursA,
            "CoursB":  coursB,
            "Qui":     cls,
            "Minimum": minimum
        })

    store.extend(new_entries)
    # Sauvegarde définitive
    enregistrer_contraintes_3_4("enchainement", store)
    return store, store


@app.callback(
    [
        Output("store-enchainement-data", "data"),
        Output("table-recap-enchainement", "data"),
    ],
    Input("btn-reset-enchainement", "n_clicks"),
    [
        State("dropdown-type-enchainement",   "value"),
        State("dropdown-coursA-enchainement", "value"),
        State("dropdown-coursB-enchainement", "value"),
        State("dropdown-qui-enchainement",    "value"),
        State("input-min-enchainement",       "value"),
        State("store-enchainement-data",      "data"),
    ],
    prevent_initial_call=True
)
def reset_enchainement(n_clicks, type_, coursA, coursB, classes, minimum, store_data):
    """
    Supprime les contraintes d'enchaînement correspondant aux filtres renseignés 
    (type, cours A, cours B, classes, minimum), ou toutes si aucun filtre n'est fourni.

    Cette fonction est utilisée lorsqu'un utilisateur clique sur le bouton "Réinitialiser"
    de la section Enchaînement. Elle purge uniquement les contraintes qui correspondent
    strictement aux filtres, ou bien tout le store s'il n'y a aucun filtre.

    Args:
        n_clicks (int): Nombre de clics sur le bouton de réinitialisation (déclencheur).
        type_ (str): Type de contrainte ("Autorisé" ou "Interdit").
        coursA (str): Cours précédent dans l'enchaînement.
        coursB (str): Cours suivant dans l'enchaînement.
        classes (str or list): Classe(s) concernée(s) par la contrainte.
        minimum (int or str): Nombre minimal d'occurrences de la contrainte.
        store_data (str or list): Store actuel des contraintes d'enchaînement (JSON ou liste d'objets).

    Returns:
        tuple: Deux listes identiques contenant les contraintes restantes après suppression,
               à stocker et afficher dans le tableau récapitulatif.
    """
    if not n_clicks:
        raise PreventUpdate

    # --- 1) Chargement/normalisation du store_data ---
    if isinstance(store_data, str):
        try:
            raw = json.loads(store_data)
        except json.JSONDecodeError:
            raw = []
    else:
        raw = store_data or []

    store = []
    for e in raw:
        if isinstance(e, str):
            try:
                obj = json.loads(e)
            except json.JSONDecodeError:
                continue
            store.append(obj)
        elif isinstance(e, dict):
            store.append(e)

    # --- 2) Préparation des filtres ---
    # classes peut être une string ou une liste
    classes = classes if isinstance(classes, list) else [classes] if classes else []
    minimum = str(minimum) if minimum else ""

    # si aucun filtre renseigné → purge totale
    if not any([type_, coursA, coursB, classes, minimum]):
        return [], []

    # --- 3) Fonction de détection d'une ligne à supprimer ---
    def matches(entry):
        # 3.1 Type
        if type_   and entry.get("Type")    != type_:
            return False
        # 3.2 Cours A
        if coursA and entry.get("CoursA")  != coursA:
            return False
        # 3.3 Cours B
        if coursB and entry.get("CoursB")  != coursB:
            return False
        # 3.4 Classe(s)
        if classes and entry.get("Qui")    not in classes:
            return False
        # 3.5 Minimum
        if minimum and str(entry.get("Minimum", "")) != minimum:
            return False
        return True

    # --- 4) On enlève seulement les entrées qui satisfont tous les filtres ---
    new_store = [e for e in store if not matches(e)]
    return new_store, new_store 

make_callback_contrainte_3_4("enchainement", ids_enchainement, apply_logic_enchainement, reset_enchainement)

config = charger_config()
jours = config["1_horaires"]["jours_classiques"]
heures = config["affichage"]["horaires_affichage"]

make_callback_contraintes("profs", jours, heures)
make_callback_contraintes("groupes", jours, heures)
make_callback_contraintes("salles", jours, heures)

make_disable_options_callback("profs")
make_disable_options_callback("groupes")
make_disable_options_callback("salles")

@app.callback(
    Output("dropdown-qui-planning", "options"),
    Output("dropdown-matiere-planning", "options"),
    Output("dropdown-nb-heures-planning", "options"),
    Input("dropdown-qui-planning", "value"),
    Input("dropdown-matiere-planning", "value"),
    State("store-volume-horaire", "data"),
)
def maj_options_doubles(classes_sel, matieres_sel, volume_horaire):
    """
    Met à jour dynamiquement les options disponibles dans les menus déroulants de la section
    "Nombre d'heures maximal à la suite", en fonction des sélections actuelles de classes
    et de matières.

    - Désactive les classes qui ne possèdent pas toutes les matières sélectionnées.
    - Désactive les matières qui ne sont pas disponibles dans toutes les classes sélectionnées.
    - Calcule la valeur maximale possible pour le nombre d'heures consécutives à autoriser.

    Args:
        classes_sel (list or str): Liste ou valeur unique de classes sélectionnées.
        matieres_sel (list or str): Liste ou valeur unique de matières sélectionnées.
        volume_horaire (dict): Dictionnaire du volume horaire par classe et par matière,
            tel que chargé depuis le store "store-volume-horaire".

    Returns:
        tuple:
            - list[dict]: Options des classes avec champs label, value, disabled.
            - list[dict]: Options des matières avec champs label, value, disabled.
            - list[dict]: Options numériques pour le nombre d'heures, en fonction du maximum détecté.
    """
    niveaux_disponibles = sorted(volume_horaire.keys())
    toutes_matieres = sorted(set(m for v in volume_horaire.values() for m in v))

    classes_sel = classes_sel or []
    matieres_sel = matieres_sel or []

    # --- MATIERES ---
    matieres_options = []
    for mat in toutes_matieres:
        if not classes_sel:
            disabled = False
        else:
            disabled = any(mat not in volume_horaire.get(c, {}) for c in classes_sel)
        matieres_options.append({"label": mat, "value": mat, "disabled": disabled})

    # --- CLASSES ---
    qui_options = []
    for cls in niveaux_disponibles:
        if not matieres_sel:
            disabled = False
        else:
            disabled = any(mat not in volume_horaire.get(cls, {}) for mat in matieres_sel)
        qui_options.append({"label": cls, "value": cls, "disabled": disabled})

    # --- HEURES ---
    max_val = 1
    for cls in classes_sel or niveaux_disponibles:
        for mat in matieres_sel or toutes_matieres:
            val = volume_horaire.get(cls, {}).get(mat)
            if isinstance(val, list):
                val = max(val)
            if isinstance(val, (int, float)):
                max_val = max(max_val, ceil(val))

    heures_options = [{"label": str(i), "value": i} for i in range(1, max_val + 1)]

    return qui_options, matieres_options, heures_options

@app.callback(
    Output("dropdown-qui-enchainement", "options"),
    Output("dropdown-coursA-enchainement", "options"),
    Output("dropdown-coursB-enchainement", "options"),
    Input("dropdown-qui-enchainement",    "value"),
    Input("dropdown-coursA-enchainement", "value"),
    Input("dropdown-coursB-enchainement", "value"),
    State("store-volume-horaire",         "data")
)
def update_enchainement_options(qui_sel, matA_sel, matB_sel, volume):
    """
    Met à jour dynamiquement les options des menus déroulants pour la contrainte
    d'enchaînement de cours (section 3.4).

    En fonction des classes sélectionnées et des cours A/B choisis :
    - désactive les classes qui ne proposent pas les deux cours ;
    - ajuste les listes de cours A et B aux matières effectivement disponibles ;
    - garantit la cohérence des choix (ex : intersection des matières si plusieurs classes sélectionnées).

    Args:
        qui_sel (str or list): Classe(s) actuellement sélectionnée(s).
        matA_sel (str): Cours A actuellement sélectionné.
        matB_sel (str): Cours B actuellement sélectionné.
        volume (dict): Dictionnaire du volume horaire {classe: {matière: volume}}.

    Returns:
        tuple:
            - list[dict]: Options pour le dropdown "Qui" (classes) avec attributs désactivés si incompatibles.
            - list[dict]: Options pour le dropdown "Cours A".
            - list[dict]: Options pour le dropdown "Cours B".
    """
    # 1) Préparation
    niveaux = sorted(volume.keys())
    toutes_matieres = sorted({m for mats in volume.values() for m in mats})

    # normalisation de qui_sel
    if isinstance(qui_sel, list):
        classes_sel = qui_sel
    elif qui_sel:
        classes_sel = [qui_sel]
    else:
        classes_sel = []

    # 2) Options pour "Qui" : désactiver si la classe n'a pas A ou B
    qui_opts = []
    for cls in niveaux:
        okA = (not matA_sel) or (matA_sel in volume.get(cls, {}))
        okB = (not matB_sel) or (matB_sel in volume.get(cls, {}))
        qui_opts.append({
            "label":    cls,
            "value":    cls,
            "disabled": not (okA and okB)
        })

    # 3) Options pour Cours A
    if classes_sel:
        # intersection des matières dans les classes sélectionnées
        matsA = set(volume[classes_sel[0]].keys())
        for cls in classes_sel[1:]:
            matsA &= set(volume[cls].keys())
    elif matB_sel:
        # union des matières dans toutes les classes qui ont B
        matsA = set()
        for cls, mats in volume.items():
            if matB_sel in mats:
                matsA |= set(mats.keys())
    else:
        matsA = set(toutes_matieres)

    coursA_opts = [
        {"label": m, "value": m, "disabled": m not in matsA}
        for m in toutes_matieres
    ]

    # 4) Options pour Cours B (symétrique)
    if classes_sel:
        matsB = set(volume[classes_sel[0]].keys())
        for cls in classes_sel[1:]:
            matsB &= set(volume[cls].keys())
    elif matA_sel:
        matsB = set()
        for cls, mats in volume.items():
            if matA_sel in mats:
                matsB |= set(mats.keys())
    else:
        matsB = set(toutes_matieres)

    coursB_opts = [
        {"label": m, "value": m, "disabled": m not in matsB}
        for m in toutes_matieres
    ]

    return qui_opts, coursA_opts, coursB_opts


def reset_enchainement(type_, coursA, coursB, classes, minimum, store_data):
    """
    Recharge entièrement les données d'enchaînement de cours depuis le JSON d'origine.

    Cette fonction est utilisée pour restaurer les données de la contrainte
    "enchaînement de cours" à leur état précédent ou pour annuler des modifications locales.

    Args:
        type_ (str): Type d'enchaînement (ex. : "Autorisé", "Interdit").
        coursA (str): Cours A sélectionné.
        coursB (str): Cours B sélectionné.
        classes (str or list): Classe(s) concernée(s).
        minimum (int): Nombre minimal d'occurrences.
        store_data (list): Données en cache (non utilisées ici).

    Returns:
        tuple:
            - list: Données d'enchaînement rechargées depuis le fichier JSON.
            - list: Idem (pour synchroniser le tableau d'affichage).
    """
    new_store = charger_contraintes_3_4("enchainement")
    return new_store, new_store

@app.callback(
    Output("input-min-enchainement", "options"),
    Input("dropdown-coursA-enchainement", "value"),
    Input("dropdown-coursB-enchainement", "value"),
    Input("dropdown-qui-enchainement", "value"),
    State("store-volume-horaire", "data"),
    State("store-enchainement-data", "data")
)
def update_minimum_dropdown(coursA, coursB, classes, volume, store):
    """
    Met à jour les options du dropdown "Minimum" pour l'enchaînement de cours,
    en fonction des volumes horaires restants pour chaque classe.

    La valeur maximale autorisée dépend :
    - du volume horaire disponible pour coursA et coursB dans chaque classe ;
    - des contraintes d'enchaînement déjà existantes dans le store.

    Args:
        coursA (str): Nom du cours précédent.
        coursB (str): Nom du cours suivant.
        classes (str or list): Classe(s) sélectionnée(s).
        volume (dict): Dictionnaire {classe: {matière: volume horaire}}.
        store (list): Contraintes d'enchaînement déjà enregistrées.

    Returns:
        list[dict]: Liste d'options pour le dropdown "Minimum", désactivées si supérieures au volume restant.
    """
    if not coursA or not coursB or not classes:
        return [{"label": str(i), "value": i, "disabled": True} for i in range(1, 6)]

    store = store or []
    classes = classes if isinstance(classes, list) else [classes]

    min_autorise = float("inf")

    for cls in classes:
        horaire = volume.get(cls, {})
        volA = horaire.get(coursA, 0)
        volB = horaire.get(coursB, 0)

        if not volA or not volB:
            continue

        # Total actuel sur A (A n'importe quoi)
        used_A = sum(
            int(e.get("Minimum", 1))
            for e in store
            if e["Qui"] == cls and e["CoursA"] == coursA
        )

        # Total actuel sur B (n'importe quoi B)
        used_B = sum(
            int(e.get("Minimum", 1))
            for e in store
            if e["Qui"] == cls and e["CoursB"] == coursB
        )

        reste_A = volA - used_A
        reste_B = volB - used_B

        min_autorise = min(min_autorise, reste_A, reste_B)

    if min_autorise <= 0:
        return [{"label": str(i), "value": i, "disabled": True} for i in range(1, 6)]

    return [
        {"label": str(i), "value": i, "disabled": i > min_autorise}
        for i in range(1, 6)
    ]

# --------- Initialisation des tableaux au lancement ---------
@app.callback(
    Output("table-recap-enchainement", "data", allow_duplicate=True),
    Input("store-enchainement-data", "data"),
    prevent_initial_call="initial_duplicate"
)
def init_table_recap_enchainement(data):
    """
    Initialise le tableau de récapitulatif des enchaînements à partir des données du store.

    Args:
        data (list): Données stockées pour les enchaînements (store-enchainement-data).

    Returns:
        list: Liste des contraintes à afficher dans le tableau.
    """
    return data or []

@app.callback(
    Output("table-recap-planning", "data", allow_duplicate=True),
    Input("store-planning-data", "data"),
    prevent_initial_call="initial_duplicate"
)
def init_table_recap_planning(data):
    """
    Initialise le tableau de récapitulatif du planning (nombre d'heures à la suite),
    à partir du store associé.

    Args:
        data (list): Données stockées pour la contrainte de planning.

    Returns:
        list: Données à afficher dans le tableau récapitulatif.
    """
    return data or []

@app.callback(
    Output("table-recap-cours-planning", "data", allow_duplicate=True),
    Input("store-cours-planning-data", "data"),
    prevent_initial_call="initial_duplicate"
)
def init_table_recap_cours(data):
    """
    Initialise le tableau de récapitulatif des contraintes cours-planning
    à partir du store correspondant.

    Args:
        data (list): Données enregistrées pour la contrainte cours-planning.

    Returns:
        list: Données du tableau de récapitulatif à afficher.
    """
    return data or []

#########################################################################################################
# Callback pour gérer la navigation entre les pages
@app.callback(
    Output("redirect-page-contrainte-add", "pathname"),
    Input("btn-previous-contrainte", "n_clicks"),
    Input("btn-next-contrainte", "n_clicks"),
    prevent_initial_call=True
)
def naviguer_page_contraintes(n_prec, n_suiv):
    """
    Gère la navigation entre les pages de l'application depuis la page "Contraintes".

    Cette fonction redirige l'utilisateur :
    - vers la page suivante ("/contraintes-optionnelles") s'il clique sur "Suivant" ;
    - vers la page précédente ("/informations") s'il clique sur "Précédent".

    Args:
        n_prec (int): Nombre de clics sur le bouton "Précédent".
        n_suiv (int): Nombre de clics sur le bouton "Suivant".

    Returns:
        str: L'URL de la page vers laquelle rediriger l'utilisateur.
    """
    triggered = ctx.triggered_id

    if triggered == "btn-next-contrainte":
        return "/contraintes-optionnelles"
    elif triggered == "btn-previous-contrainte":
        return "/informations"

    raise PreventUpdate
