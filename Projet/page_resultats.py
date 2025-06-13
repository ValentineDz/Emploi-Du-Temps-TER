"""
Page Dash dédiée à l'affichage et à la gestion des résultats de la génération d'emploi du temps.

Cette page présente deux sections principales organisées en accordéons :
- **Statistiques de complétion** : Affiche des cartes colorées indiquant le taux de respect des contraintes (volume horaire, contraintes obligatoires et optionnelles, taux global, nombre de violations) ainsi qu'un tableau détaillé listant chaque type de contrainte avec son statut, son taux de respect et le nombre de cas respectés. Une section repliable détaille les violations pour chaque contrainte non entièrement respectée. Les cartes changent de couleur dynamiquement : vert pour conforme, rouge sinon.
- **Gestion des emplois du temps** : Fournit une interface interactive pour visualiser et modifier les emplois du temps par classe, professeur ou salle, avec des modes d'affichage, d'édition, de déplacement et d'exportation en PDF. Inclut un panneau latéral pour les options d'édition ou d'exportation.

Les données statistiques sont extraites d'un fichier JSON via `charger_statistiques_contraintes()`. Les emplois du temps sont gérés via une structure de données globale (`edt_global`) avec des interactions dynamiques.
"""

import dash
import pandas as pd
from main_dash import app
from styles import *
import json
import copy
from dash import Dash, html, dcc, Input, Output, State, ctx, ALL, dash_table, no_update
import dash_bootstrap_components as dbc
import io
import zipfile
from fonctions import *
from textes import texte_page_resultats, texte_page_resultats_2, texte_page_resultats_3, texte_stats


def layout_resultats():
    """
    Génère le layout principal de la page de résultats et de gestion d'emploi du temps.

    Cette fonction crée une interface Dash avec deux sections principales organisées en accordéons :
    - Statistiques de complétion: Affiche des cartes colorées indiquant le respect des contraintes
      (volume horaire, contraintes obligatoires/optionnelles, taux global, violations) et un tableau
      détaillé des contraintes avec une section repliable pour les violations.
    - Gestion des emplois du temps: Fournit une interface interactive pour visualiser et modifier
      les emplois du temps par classe, professeur ou salle, avec des modes d'affichage, d'édition,
      de déplacement et d'exportation PDF. Inclut un panneau latéral pour les options et un tableau
      split par semaine (A et B).

    Les données sont extraites via `charger_statistiques_contraintes()` pour les statistiques et
    `charger_donnees_edt()` pour les emplois du temps. Les cartes changent de couleur dynamiquement
    (vert pour conforme, rouge sinon).

    Returns:
        html.Div: Composant principal contenant les deux accordéons, stylisé selon le thème de l'application.
    """
    pourcentage_global, table_data, violations, details_violations_grouped, stats_globales = charger_statistiques_contraintes()
    edt_global, _ = charger_donnees_edt()

    # Volume horaire : vert si 100%, sinon rouge
    vh = stats_globales["volume_horaire"]
    vh_fond = "#D5F5E3" if vh == "100.0%" else "#FADBD8"
    vh_texte = "#1E8449" if vh == "100.0%" else "#922B21"

    # Contraintes obligatoires : vert si 100%, sinon rouge
    obl = stats_globales["contraintes_obligatoires"]
    obl_fond = "#D5F5E3" if obl == "100.0%" else "#FADBD8"
    obl_texte = "#1E8449" if obl == "100.0%" else "#922B21"

    # Contraintes optionnelles : vert si ≥ 80%, rouge sinon
    opt = float(stats_globales["contraintes_optionnelles"].replace("%", "")) if stats_globales["contraintes_optionnelles"] != "-" else 100
    opt_fond = "#D5F5E3" if opt >= 80 else "#FADBD8"
    opt_texte = "#1E8449" if opt >= 80 else "#922B21"

    # Contraintes respectées globales : vert ≥ 80%, rouge sinon
    glob_fond = "#D5F5E3" if pourcentage_global >= 80 else "#FADBD8"
    glob_texte = "#1E8449" if pourcentage_global >= 80 else "#922B21"

    # Contraintes non respectées : rouge si > 0
    nb_viol = len(violations)
    viol_fond = "#FADBD8" if nb_viol > 0 else "#D5F5E3"
    viol_texte = "#922B21" if nb_viol > 0 else "#1E8449"

    # Layout de la gestion des emplois du temps 
    timetable_layout = html.Div([
        html.H2("Emploi du temps", style=h2_style),

        # Sélecteurs principaux
        html.Div([
            dcc.Dropdown(
                id="vue-dropdown",
                options=[
                    {"label": "Par classe", "value": "edt_classe"},
                    {"label": "Par professeur", "value": "edt_prof"},
                    {"label": "Par salle", "value": "edt_salle"},
                ],
                value="edt_classe",
                style=vue_dropdown_style
            ),
            dcc.Dropdown(id="entite-dropdown", style=entite_dropdown_style),
            html.Div([
                dbc.RadioItems(
                    options=[
                        {"label": "Affichage", "value": "view"},
                        {"label": "Édition", "value": "edit"},
                        {"label": "Déplacement", "value": "move"},
                        {"label": "Export", "value": "export"},
                    ],
                    value="view",
                    id="mode-radio",
                    inline=True,
                    style=radio_container_style
                ),
            ], style=radio_items_style)
        ], style=selectors_container_style),

        # Bouton de téléchargement PDF
        html.Div([dcc.Download(id="download-pdf")], style=download_button_container_style),

        html.Div(id="alert-area", style=alert_area_style),

        # Zone principale : sidepanel + tableau
        html.Div([
            html.Div(id="sidepanel-wrapper", children=html.Div(id="sidepanel", style=sidepanel_style)),
            html.Div([
                html.Div(id="table-title", style=table_title_style),
                html.Div(id="table-split")
            ], style={"flex": "1"})
        ], style=main_container_style),

        # Option export
        dcc.Checklist(
            id="export-options-panel",
            options=[
                {"label": "Emploi du temps affiché", "value": "current"},
                {"label": "Toutes les classes", "value": "all_classes"},
                {"label": "Tous les enseignants", "value": "all_profs"},
                {"label": "Toutes les salles", "value": "all_salles"},
            ],
            value=[],
            style={"display": "none"}
        ),
        
        # Bouton cachés pour le layout
        dcc.Input(id="input-matiere-A", type="text", style={"display": "none"}),
        dcc.Input(id="input-prof-A", type="text", style={"display": "none"}),
        dcc.Input(id="input-salle-A", type="text", style={"display": "none"}),
        dcc.Input(id="input-classe-A", type="text", style={"display": "none"}),
        dcc.Input(id="input-matiere-B", type="text", style={"display": "none"}),
        dcc.Input(id="input-prof-B", type="text", style={"display": "none"}),
        dcc.Input(id="input-salle-B", type="text", style={"display": "none"}),
        dcc.Input(id="input-classe-B", type="text", style={"display": "none"}),
        html.Button("Enregistrer", id="btn-save-edit", style={"display": "none"}),
        html.Button("Supprimer", id="btn-delete", style={"display": "none"}),
        html.Button("Annuler", id="btn-cancel-edit", style={"display": "none"}),
        html.Button("Télécharger", id="btn-export-panel", style={"display": "none"}),
        html.Button("Supprimer Semaine A", id="btn-delete-a", style={"display": "none"}),
        html.Button("Supprimer Semaine B", id="btn-delete-b", style={"display": "none"}),

        # Stores Dash
        dcc.Store(id="edt-memory", data=edt_global),
        dcc.Store(id="move-source", data=None),
        dcc.Store(id="edit-source", data=None),
        dcc.Store(id="pending-action", data=None),
        dcc.Store(id="configuration-options", data=[]),
        dcc.Store(id="store-save-edit-clicks", data=0),
        dcc.Store(id="store-delete-clicks", data=0),
        dcc.Store(id="store-cancel-edit-clicks", data=0),
        dcc.Store(id="store-delete-a-clicks", data=0),
        dcc.Store(id="store-delete-b-clicks", data=0),
        dcc.Store(id="store-export-panel-clicks", data=0),
        
    ])

    # Contenu de la page
    return html.Div([
        html.H1("Résultat et gestion de l'emploi du temps"),
        html.Hr(style=style_hr),
        html.P(texte_page_resultats, style=explication_style),
        html.Ul([
            html.Li(texte_page_resultats_2),
            html.Li(texte_page_resultats_3),
        ], style=explication_style),
        html.Br(),

        dbc.Accordion([
            # Premier accordéon : Statistiques de complétion
            dbc.AccordionItem([
                html.P(texte_stats, style=explication_style),
                html.H4("Chiffres clés :"),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Volume horaire respecté", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(stats_globales["volume_horaire"], className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": vh_fond, "color": vh_texte, "height": "100px"}), width=4),

                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Contraintes obligatoires", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(stats_globales["contraintes_obligatoires"], className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": obl_fond, "color": obl_texte, "height": "100px"}), width=4),

                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Contraintes optionnelles", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(stats_globales["contraintes_optionnelles"], className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": opt_fond, "color": opt_texte, "height": "100px"}), width=4),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Contraintes totales", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(f"{len(table_data)} types analysés", className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": "#D6EAF8", "color": "#154360", "height": "100px"}), width=4),

                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Contraintes respectées à", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(f"{pourcentage_global:.2f} %", className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": glob_fond, "color": glob_texte, "height": "100px"}), width=4),

                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Contraintes non respectées", className="text-center"),
                        dbc.CardBody(html.Div(html.H4(f"{nb_viol} type(s)", className="card-title"),
                                            className="d-flex justify-content-center align-items-center", style=style_cartes))
                    ], style={"backgroundColor": viol_fond, "color": viol_texte, "height": "100px"}), width=4),
            ]),

                html.Br(),
                html.H4("Détail par type de contraintes :"),
                html.Div(
                    dash_table.DataTable(
                        columns=[
                            {"name": "Contrainte", "id": "contrainte"},
                            {"name": "Statut", "id": "statut"},
                            {"name": "Respectées", "id": "respectees"},
                            {"name": "Total", "id": "total"},
                            {"name": "Taux (%)", "id": "taux"}
                        ],
                        data=table_data,
                        style_cell=style_cell,
                        style_header=style_header_table,
                        style_data_conditional=style_conditionnel_stats
                    ),
                    style=style_table
                ),

                html.Br(),
                html.H5("Voici le détail des violations de contraintes :"),
                html.Div([
                    html.Details([
                        html.Summary(nom, style=style_summary_violations),
                        html.Ul([html.Li(detail) for detail in sorted(details)])
                    ]) for nom, details in sorted(details_violations_grouped.items())
                ], style=style_marge_gauche)
            ], title=html.H4("1. Statistiques de complétion de l'emploi du temps")),

            # Deuxième accordéon : Gestion des emplois du temps
            dbc.AccordionItem([
                timetable_layout
            ], title=html.H4("2. Gestion des emplois du temps"))
        ], style=style_accordeons, active_item=None)
    ], style=global_page_style)



@app.callback(
    Output("entite-dropdown", "options"),
    Output("entite-dropdown", "value"),
    Output("table-title", "children"),
    Input("vue-dropdown", "value"),
    Input("entite-dropdown", "value"),
    Input("edt-memory", "data")
)
def maj_liste_entites(vue, current_entite,edt):
    """
    Met à jour les options et la valeur du sélecteur d'entité en fonction de la vue sélectionnée.

    Cette fonction récupère la liste des entités (classes, professeurs, salles) disponibles pour la vue donnée,
    met à jour les options du menu déroulant, sélectionne une valeur par défaut ou conserve la valeur actuelle si valide,
    et définit le titre du tableau.

    Args:
        vue (str): Type de vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').
        current_entite (str): Valeur actuellement sélectionnée dans le menu déroulant.
        edt (dict): Données globales de l'emploi du temps.

    Returns:
        tuple: Contient trois éléments :
            - list: Liste des options pour le menu déroulant (format [{"label": str, "value": str}, ...]).
            - str or None: Valeur sélectionnée pour le menu déroulant.
            - str or None: Titre du tableau (actuellement None dans l'implémentation).
    """
    if not edt or vue not in edt:
        return [], None, None
    
    entites = get_entites(edt, vue)
    options = [{"label": e, "value": e} for e in entites]
    value = current_entite if current_entite in entites else (entites[0] if entites else None)
    label = {"edt_classe": "Classe", "edt_prof": "Professeur", "edt_salle": "Salle"}[vue]
    title = None
    return options, value, title

@app.callback(
    Output("table-split", "children"),
    Input("edt-memory", "data"),
    Input("vue-dropdown", "value"),
    Input("entite-dropdown", "value"),
    Input("move-source", "data"),
    Input("mode-radio", "value"),
    Input("edit-source", "data"),
    prevent_initial_call=False
)
def update_table_split(edt, vue, entite, move_source, mode, edit_source):
    """
    Met à jour le tableau d'emploi du temps affiché séparé entre Semaine A et Semaine B.

    Cette fonction génère un tableau en fonction des données de l'emploi du temps, de la vue sélectionnée
    (classe, professeur, salle), de l'entité choisie, du mode actif (affichage, édition, déplacement),
    et des informations sur la source de déplacement ou d'édition.

    Args:
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Type de vue sélectionnée ("edt_classe", "edt_prof", "edt_salle").
        entite (str): Entité sélectionnée (ex. nom de la classe, du professeur, ou de la salle).
        move_source (dict or None): Données de la source pour un déplacement de créneau.
        mode (str): Mode actif ("view", "edit", "move", "export").
        edit_source (dict or None): Données du créneau en cours d'édition.

    Returns:
        str or html.Div: Contenu du tableau d'emploi du temps ou chaîne vide si aucune entité n'est sélectionnée.
    """
    if not entite:
        return ""
    return build_split_table(edt, vue, entite, mode, move_source, edit_source)

@app.callback(
    [
        Output("edt-memory", "data", allow_duplicate=True),
        Output("move-source", "data", allow_duplicate=True),
        Output("pending-action", "data", allow_duplicate=True),
        Output("alert-area", "children", allow_duplicate=True),
        Output("edit-source", "data", allow_duplicate=True),
        Output("download-pdf", "data", allow_duplicate=True)
    ],
    [
        Input({"type": "cellule", "vue": ALL, "entite": ALL, "jour": ALL, "heure": ALL, "semaine": ALL}, "n_clicks"),
        Input("btn-save-edit", "n_clicks"),
        Input("btn-delete", "n_clicks"),
        Input("btn-cancel-edit", "n_clicks"),
        Input("btn-export-panel", "n_clicks"),
        Input("btn-delete-a", "n_clicks"),
        Input("btn-delete-b", "n_clicks"),
    ],
    [
        State("mode-radio", "value"),
        State("move-source", "data"),
        State("edit-source", "data"),
        State("pending-action", "data"),
        State("vue-dropdown", "value"),
        State("entite-dropdown", "value"),
        State("edt-memory", "data"),
        State("input-matiere-A", "value"),
        State("input-prof-A", "value"),
        State("input-salle-A", "value"),
        State("input-classe-A", "value"),
        State("input-matiere-B", "value"),
        State("input-prof-B", "value"),
        State("input-salle-B", "value"),
        State("input-classe-B", "value"),
        State("export-options-panel", "value"),
    ],
    prevent_initial_call=True
)
def global_callback(
    cell_clicks, n_save, n_delete, n_cancel_edit, n_export,
    n_delete_a, n_delete_b,
    mode, move_source, edit_source, pending, vue, entite, edt,
    mat_a, prof_a, salle_a, classe_a, mat_b, prof_b, salle_b, classe_b, export_options
):
    """
    Gère les interactions globales de la page de gestion des emplois du temps.

    Cette fonction traite les actions suivantes :
    - Sélection d'une cellule pour édition ou déplacement.
    - Enregistrement des modifications d'un créneau horaire.
    - Suppression d'un créneau horaire.
    - Annulation de l'édition ou du déplacement.
    - Exportation des emplois du temps en PDF (actuel, toutes classes, tous profs, toutes salles).

    Elle met à jour les données de l'emploi du temps, les états de sélection, les actions en attente,
    les messages d'alerte, et génère un fichier ZIP pour l'exportation PDF.

    Args:
        cell_clicks (list): Liste des clics sur les cellules du tableau.
        n_save (int): Nombre de clics sur le bouton 'Enregistrer'.
        n_delete (int): Nombre de clics sur le bouton 'Supprimer'.
        n_cancel_edit (int): Nombre de clics sur le bouton 'Annuler'.
        n_export (int): Nombre de clics sur le bouton 'Télécharger' pour l'export PDF.
        n_delete_a (int): Nombre de clics sur le bouton 'Supprimer Semaine A'.
        n_delete_b (int): Nombre de clics sur le bouton 'Supprimer Semaine B'.
        mode (str): Mode actif ('view', 'edit', 'move', 'export').
        move_source (dict or None): Données de la source pour un déplacement de créneau.
        edit_source (dict or None): Données du créneau en cours d'édition.
        pending (dict or None): Action en attente (ex. déplacement à confirmer).
        vue (str): Type de vue sélectionnée ('edt_classe', 'edt_prof', 'edt_salle').
        entite (str): Entité sélectionnée (ex. nom de la classe, du professeur, ou de la salle).
        edt (dict): Données globales de l'emploi du temps.
        mat_a, prof_a, salle_a, classe_a (str): Valeurs des champs d'entrée pour la semaine A.
        mat_b, prof_b, salle_b, classe_b (str): Valeurs des champs d'entrée pour la semaine B.
        export_options (list): Options sélectionnées pour l'export PDF.

    Returns:
        tuple: Contient six éléments :
            - dict: Données mises à jour de l'emploi du temps.
            - dict or None: Données de la source de déplacement.
            - dict or None: Données de l'action en attente.
            - str or dash.dbc.Alert: Message d'alerte à afficher.
            - dict or None: Données du créneau en cours d'édition.
            - dash.dcc.send_bytes or dash.no_update: Données du fichier ZIP pour l'export PDF ou no_update.
    """

    edt_new = copy.deepcopy(edt)
    trig = ctx.triggered_id

    # Sélection d'une cellule pour édition ou déplacement
    if isinstance(trig, dict) and trig.get("type") == "cellule":
        jour = trig["jour"]
        heure = trig["heure"]
        semaine = trig.get("semaine", "A")
        entite_ = trig.get("entite")
        vue_ = trig.get("vue", vue)
        cell_a = edt[vue_]["Semaine A"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
        cell_b = edt[vue_]["Semaine B"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
        if mode == "edit":
            edit = {"vue": vue, "semaine": semaine, "entite": entite, "jour": jour, "heure": heure}
            return (
                edt, move_source, pending, "",
                edit, no_update
            )
        elif mode == "move":
            if not move_source:
                if has_content(edt, vue, entite, jour, heure):
                    return (
                        edt, {"vue": vue, "entite": entite, "jour": jour, "heure": heure, "semaine": semaine},
                        None, dbc.Alert("Cours sélectionné ! Cliquez sur un autre cours.", color="info", dismissable=True),
                        None, no_update
                    )
                return (
                    edt, move_source, pending, dbc.Alert("Cellule vide !", color="warning", dismissable=True),
                    None, no_update
                )
            else:
                source = move_source
                dest = {"jour": jour, "heure": heure, "semaine": semaine}
                if source["jour"] == dest["jour"] and source["heure"] == dest["heure"]:
                    return (
                        edt, None, None, dbc.Alert("Sélection annulée.", color="secondary", dismissable=True),
                        None, no_update
                    )
                if not has_content(edt, vue, entite, source["jour"], source["heure"]):
                    return (
                        edt, None, None, dbc.Alert("Source vide !", color="warning", dismissable=True),
                        None, no_update
                    )
                if not has_content(edt, vue, entite, dest["jour"], dest["heure"]):
                    return (
                        edt, move_source, {"source": source, "dest": dest}, "",
                        None, no_update
                    )
                else:
                    return (
                        edt, move_source, {"source": source, "dest": dest}, "",
                        None, no_update
                    )
        return (edt, move_source, pending, "", None, no_update)

    # Enregistrement d'une édition
    if trig == "btn-save-edit" and edit_source:
        vue = edit_source["vue"]
        entite_ = edit_source["entite"]
        jour = edit_source["jour"]
        heure = edit_source["heure"]

        # --- Semaine A ---
        old_cell_a = edt[vue]["Semaine A"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
        new_cell_a = {
            "matiere": [x.strip() for x in (mat_a if mat_a is not None else safe_join(old_cell_a.get("matiere", []))).split(",") if x.strip()],
            "professeurs": [x.strip() for x in (prof_a if prof_a is not None else safe_join(old_cell_a.get("professeurs", []) or old_cell_a.get("prof", []))).split(",") if x.strip()],
            "salle": [x.strip() for x in (salle_a if salle_a is not None else safe_join(old_cell_a.get("salle", []))).split(",") if x.strip()],
            "classe": [x.strip() for x in (classe_a if classe_a is not None else safe_join(old_cell_a.get("classe", []))).split(",") if x.strip()]
        }
        if any([mat_a, prof_a, salle_a, classe_a]):
            if not edt_new[vue]["Semaine A"].get(entite_, {}).get(jour, {}):
                edt_new[vue]["Semaine A"][entite_][jour] = {}
            edt_new[vue]["Semaine A"][entite_][jour][heure] = new_cell_a

        # --- Semaine B ---
        old_cell_b = edt[vue]["Semaine B"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
        new_cell_b = {
            "matiere": [x.strip() for x in (mat_b if mat_b is not None else safe_join(old_cell_b.get("matiere", []))).split(",") if x.strip()],
            "professeurs": [x.strip() for x in (prof_b if prof_b is not None else safe_join(old_cell_b.get("professeurs", []) or old_cell_b.get("prof", []))).split(",") if x.strip()],
            "salle": [x.strip() for x in (salle_b if salle_b is not None else safe_join(old_cell_b.get("salle", []))).split(",") if x.strip()],
            "classe": [x.strip() for x in (classe_b if classe_b is not None else safe_join(old_cell_b.get("classe", []))).split(",") if x.strip()]
        }
        if any([mat_b, prof_b, salle_b, classe_b]):
            if not edt_new[vue]["Semaine B"].get(entite_, {}).get(jour, {}):
                edt_new[vue]["Semaine B"][entite_][jour] = {}
            edt_new[vue]["Semaine B"][entite_][jour][heure] = new_cell_b

        sauvegarder_edt_global(edt_new)
        return (
            edt_new, None, None, dbc.Alert("Cours modifié !", color="success", dismissable=True),
            None, no_update
        )

    # Suppression d'un cours
    if trig == "btn-delete" and edit_source:
        vue = edit_source["vue"]
        semaine = edit_source["semaine"]
        entite_ = edit_source["entite"]
        jour = edit_source["jour"]
        heure = edit_source["heure"]
        if is_cours_plein(edt, vue, entite_, jour, heure):
            for sem in ["A", "B"]:
                try:
                    if heure in edt_new[vue][f"Semaine {sem}"][entite_][jour]:
                        del edt_new[vue][f"Semaine {sem}"][entite_][jour][heure]
                except Exception:
                    pass
        else:
            try:
                if heure in edt_new[vue][f"Semaine {semaine}"][entite_][jour]:
                    del edt_new[vue][f"Semaine {semaine}"][entite_][jour][heure]
            except Exception:
                pass
        sauvegarder_edt_global(edt_new)
        return (
            edt_new, None, None, dbc.Alert("Cours supprimé !", color="danger", dismissable=True),
            None, no_update
        )

    # Suppression Semaine A
    if trig == "btn-delete-a" and edit_source:
        vue = edit_source["vue"]
        entite_ = edit_source["entite"]
        jour = edit_source["jour"]
        heure = edit_source["heure"]
        try:
            if heure in edt_new[vue]["Semaine A"][entite_][jour]:
                del edt_new[vue]["Semaine A"][entite_][jour][heure]
        except Exception:
            pass
        sauvegarder_edt_global(edt_new)
        return (
            edt_new, None, None, dbc.Alert("Cours supprimé (Semaine A) !", color="danger", dismissable=True),
            None, no_update
        )

    # Suppression Semaine B
    if trig == "btn-delete-b" and edit_source:
        vue = edit_source["vue"]
        entite_ = edit_source["entite"]
        jour = edit_source["jour"]
        heure = edit_source["heure"]
        try:
            if heure in edt_new[vue]["Semaine B"][entite_][jour]:
                del edt_new[vue]["Semaine B"][entite_][jour][heure]
        except Exception:
            pass
        sauvegarder_edt_global(edt_new)
        return (
            edt_new, None, None, dbc.Alert("Cours supprimé (Semaine B) !", color="danger", dismissable=True),
            None, no_update
        )

    # Annulation de l'édition
    if trig == "btn-cancel-edit":
        return (edt, None, None, "", None, no_update)

    # Export PDF depuis le panneau latéral
    if trig == "btn-export-panel" and export_options:
        pdf_buffers = []
        filenames = []
        if "current" in export_options and entite:
            mat = get_table_matrix_pdf(edt, vue, entite)
            label = {"edt_classe": "Classe", "edt_prof": "Prof", "edt_salle": "Salle"}[vue]
            title = f"Emploi du temps {label} {entite}"
            pdf_buffers.append(make_pdf(title, mat))
            filenames.append(f"{label}_{entite}.pdf")
        if "all_classes" in export_options:
            for cl in get_entites(edt, "edt_classe"):
                mat = get_table_matrix_pdf(edt, "edt_classe", cl)
                title = f"Emploi du temps Classe {cl}"
                pdf_buffers.append(make_pdf(title, mat))
                filenames.append(f"Classe_{cl}.pdf")
        if "all_profs" in export_options:
            for prof in get_entites(edt, "edt_prof"):
                mat = get_table_matrix_pdf(edt, "edt_prof", prof)
                title = f"Emploi du temps Enseignants {prof}"
                pdf_buffers.append(make_pdf(title, mat))
                filenames.append(f"Professeurs_{prof}.pdf")
        if "all_salles" in export_options:
            for salle in get_entites(edt, "edt_salle"):
                mat = get_table_matrix_pdf(edt, "edt_salle", salle)
                title = f"Emploi du temps Salle {salle}"
                pdf_buffers.append(make_pdf(title, mat))
                filenames.append(f"Salle_{salle}.pdf")
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, mode="w") as z:
            for fn, pdf in zip(filenames, pdf_buffers):
                z.writestr(fn, pdf)
        zip_buf.seek(0)
        return (
            edt, None, None, dbc.Alert("Export PDF prêt !", color="success", dismissable=True),
            None, dcc.send_bytes(zip_buf.read(), "emplois_du_temps.zip")
        )

    # Cas par défaut
    return (edt, move_source, pending, "", None, no_update)

@app.callback(
    Output("sidepanel", "children"),
    [
        Input("mode-radio", "value"),
        Input("move-source", "data"),
        Input("pending-action", "data"),
        Input("edit-source", "data"),
        Input("edt-memory", "data"),
        Input("vue-dropdown", "value"),
        Input("entite-dropdown", "value"),
    ],
    prevent_initial_call=False
)
def update_sidepanel(mode, move_source, pending_action, edit_source, edt, vue, entite):
    """
    Met à jour le contenu du panneau latéral (sidepanel) en fonction du mode actif.

    Cette fonction génère le contenu du panneau latéral pour les modes suivants :
    - Mode "edit" : Affiche un formulaire pour modifier un créneau horaire.
    - Mode "export" : Affiche un panneau pour sélectionner les options d'export PDF.
    - Mode "move" : Affiche les options de déplacement pour deux créneaux sélectionnés.
    - Mode "view" (par défaut) : Affiche un message indiquant qu'aucune sélection n'est active.

    Args:
        mode (str): Mode actif ("view", "edit", "move", "export").
        move_source (dict or None): Données de la source pour un déplacement de créneau.
        pending_action (dict or None): Action en attente (ex. déplacement à confirmer).
        edit_source (dict or None): Données du créneau en cours d'édition.
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Type de vue sélectionnée ("edt_classe", "edt_prof", "edt_salle").
        entite (str): Entité sélectionnée (ex. nom de la classe, du professeur, ou de la salle).

    Returns:
        html.Div: Contenu du panneau latéral adapté au mode actif.
    """
    # --- Mode édition ---
    if mode == "edit":
        if edit_source:
            semaine = edit_source.get("semaine", "A")
            jour = edit_source.get("jour")
            heure = edit_source.get("heure")
            entite_ = edit_source.get("entite")
            vue_ = edit_source.get("vue", vue)
            cell_a = edt[vue_]["Semaine A"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
            cell_b = edt[vue_]["Semaine B"].get(entite_, {}).get(jour, {}).get(heure, {}) or {}
            return html.Div([
                html.H4("Édition du créneau", style=edit_h4_style),
                html.P(f"{jour} {heure} - Semaine A", style=edit_p_style),
                build_edit_panel(cell_a, vue_, "A"),
                dbc.Button("Supprimer Semaine A", id="btn-delete-a-visible", color="danger", style={"marginBottom": "10px"}),
                html.Hr(),
                html.P(f"{jour} {heure} - Semaine B", style=edit_p_style),
                build_edit_panel(cell_b, vue_, "B"),
                dbc.Button("Supprimer Semaine B", id="btn-delete-b-visible", color="danger", style={"marginBottom": "10px"}),
                html.Div([
                    dbc.Button("Enregistrer", id="btn-save-edit-visible", color="primary", style={"marginRight": "10px"}),
                    dbc.Button("Annuler", id="btn-cancel-edit-visible", color="secondary"),
                ], style=edit_buttons_container_style),
            ])
        else:
            return html.Div([
                html.H4("Options d'édition", style=edit_h4_style),
                html.P("Sélectionnez un créneau pour voir les options disponibles.", style=edit_message_style),
                html.Div("Cliquez sur un créneau pour l'éditer ou ajouter un cours.", style=edit_no_selection_style)
            ])

    # --- Mode export ---
    if mode == "export":
        return html.Div([
            html.H5("Exporter en PDF", style=export_h5_style),
            dbc.Checklist(
                options=[
                    {"label": "Emploi du temps affiché", "value": "current"},
                    {"label": "Toutes les classes", "value": "all_classes"},
                    {"label": "Tous les enseigants", "value": "all_profs"},
                    {"label": "Toutes les salles", "value": "all_salles"},
                ],
                value=[],
                id="export-options-panel-visible",
                style=export_checklist_style,
                key=f"export-{vue}-{entite}"
            ),
            dbc.Button("Télécharger", id="btn-export-panel-visible", color="primary"),
        ])
    # --- Mode déplacement ---
    if mode == "move":
        if not move_source:
            return html.Div([
                html.H4("Options de transformation", style=view_h4_style),
                html.P("Sélectionnez deux créneaux dans le tableau pour voir les options disponibles.", style=view_message_style),
                html.Div("Aucune sélection", style=view_no_selection_style)
            ])
        if not pending_action:
            return html.Div([
                html.H6("Créneau source sélectionné :", style=move_h6_style),
                html.P(f"{move_source['jour']} - {move_source['heure']}", style=move_p_style),
                html.P("Cliquez sur un autre créneau pour voir les options de transformation.", style=move_message_style)
            ], style=move_selection_style)
        source = pending_action["source"]
        dest = pending_action["dest"]
        options = get_configuration_options(edt, vue, entite, source, dest)
        if not options:
            return html.Div("Aucune option disponible pour cette combinaison", style=move_no_options_style)
        checklist_options = [
            {
                "label": html.Span([
                    html.Strong(option["label"]),
                    html.Br(),
                    build_option_preview_dash(edt, vue, entite, source, dest, option["action"])
                ], style={"display": "block"}),
                "value": option["id"]
            }
            for option in options
        ]
        return html.Div([
            html.H5("Choisissez une option :", style=move_h5_style),
            dcc.Checklist(
                id="move-checkbox-choice",
                options=checklist_options,
                value=[],
                inputStyle=move_checklist_input_style,
                labelStyle=move_checklist_style
            ),
            html.Div([
                dbc.Button("Appliquer", id="btn-apply", color="primary", style={"marginRight": "10px"}),
                dbc.Button("Annuler", id="btn-cancel", color="secondary")
            ], style=move_buttons_container_style)
        ])

    # --- Mode affichage (par défaut) ---
    return html.Div([
        html.H4("Options de transformation", style=view_h4_style),
        html.P("Sélectionnez deux créneaux dans le tableau pour voir les options disponibles.", style=view_message_style),
        html.Div("Aucune sélection", style=view_no_selection_style)
    ])

@app.callback(
    Output("sidepanel-wrapper", "style"),
    Input("mode-radio", "value"),
)
def hide_sidepanel(mode):
    """
    Contrôle la visibilité du panneau latéral en fonction du mode sélectionné.

    Le panneau latéral est masqué en mode "view" et visible dans les autres modes
    (édition, déplacement, export).

    Args:
        mode (str): Mode actif ("view", "edit", "move", "export").

    Returns:
        dict: Style CSS pour le conteneur du panneau latéral (visible ou masqué).
    """
    if mode == "view":
        return sidepanel_hidden_style
    return sidepanel_visible_style

@app.callback(
    Output("edit-source", "data", allow_duplicate=True),
    Output("move-source", "data", allow_duplicate=True),
    Output("pending-action", "data", allow_duplicate=True),
    Input("mode-radio", "value"),
    prevent_initial_call=True
)
def reset_selection_on_mode_change(mode):
    """
    Réinitialise les sélections actives lors d'un changement de mode.

    Cette fonction réinitialise les données de sélection pour l'édition, le déplacement,
    et les actions en attente lorsque l'utilisateur change de mode (affichage, édition, déplacement, export).

    Args:
        mode (str): Mode actif ("view", "edit", "move", "export").

    Returns:
        tuple: Contient trois éléments, tous None pour réinitialiser :
            - None: Données du créneau en cours d'édition.
            - None: Données de la source de déplacement.
            - None: Données de l'action en attente.
    """
    return None, None, None

@app.callback(
    [
        Output("edt-memory", "data", allow_duplicate=True),
        Output("move-source", "data", allow_duplicate=True),
        Output("pending-action", "data", allow_duplicate=True),
        Output("alert-area", "children", allow_duplicate=True),
    ],
    [
        Input("btn-apply", "n_clicks"),
        Input("btn-cancel", "n_clicks"),
    ],
    [
        State("pending-action", "data"),
        State("edt-memory", "data"),
        State("vue-dropdown", "value"),
        State("entite-dropdown", "value"),
        State("move-checkbox-choice", "value"),
    ],
    prevent_initial_call=True
)
def apply_move(n_apply, n_cancel, pending_action, edt, vue, entite, selected_option_ids):
    """
    Applique ou annule une transformation de déplacement de créneau.

    Cette fonction traite les actions suivantes :
    - Applique une transformation (ex. déplacement ou échange de créneaux) en fonction de l'option sélectionnée.
    - Annule la sélection de déplacement et réinitialise les états.

    Args:
        n_apply (int): Nombre de clics sur le bouton "Appliquer".
        n_cancel (int): Nombre de clics sur le bouton "Annuler".
        pending_action (dict or None): Action en attente (ex. déplacement à confirmer).
        edt (dict): Données globales de l'emploi du temps.
        vue (str): Type de vue sélectionnée ("edt_classe", "edt_prof", "edt_salle").
        entite (str): Entité sélectionnée (ex. nom de la classe, du professeur, ou de la salle).
        selected_option_ids (list): Liste des identifiants des options de transformation sélectionnées.

    Returns:
        tuple: Contient quatre éléments :
            - dict or no_update: Données mises à jour de l'emploi du temps ou no_update si non modifié.
            - dict or no_update: Données de la source de déplacement (None si réinitialisé).
            - dict or no_update: Données de l'action en attente (None si réinitialisé).
            - str or dbc.Alert: Message d'alerte à afficher ou no_update si non applicable.
    """
    trig = ctx.triggered_id
    if trig == "btn-cancel":
        return edt, None, None, ""
    if trig == "btn-apply" and pending_action and selected_option_ids:
        selected_option_id = selected_option_ids[0]
        options = get_configuration_options(edt, vue, entite, pending_action["source"], pending_action["dest"])
        action = next((opt["action"] for opt in options if opt["id"] == selected_option_id), "overwrite_any")
        edt_new = apply_transformation(edt, vue, entite, pending_action["source"], pending_action["dest"], action)
        sauvegarder_edt_global(edt_new)
        return edt_new, None, None, dbc.Alert("Transformation appliquée !", color="success", dismissable=True)
    return no_update, no_update, no_update, no_update

@app.callback(
    Output("move-checkbox-choice", "value"),
    Input("move-checkbox-choice", "value"),
    prevent_initial_call=True
)
def single_checkbox(selected):
    """
    Limite la sélection à une seule option dans la liste de choix pour les transformations.

    Cette fonction garantit que seule la dernière option sélectionnée dans la checklist
    des transformations (déplacement) est conservée.

    Args:
        selected (list): Liste des options actuellement sélectionnées.

    Returns:
        list: Liste contenant uniquement la dernière option sélectionnée ou une liste vide si aucune sélection.
    """
    if selected:
        return [selected[-1]]
    return []


@app.callback(
    Output("store-save-edit-clicks", "data"),
    Input("btn-save-edit-visible", "n_clicks"),
    State("store-save-edit-clicks", "data"),
    prevent_initial_call=True
)
def sync_save_edit_visible(n, current):
    
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("store-delete-clicks", "data"),
    Input("btn-delete-visible", "n_clicks"),
    State("store-delete-clicks", "data"),
    prevent_initial_call=True
)
def sync_delete_visible(n, current):
    """
    Synchronise les clics du bouton de suppression visible avec le store.

    Incrémente le compteur de clics dans le store associé pour refléter les interactions avec le bouton visible  Supprimer .

    Args:
        n (int or None): Nombre de clics sur le bouton visible  Supprimer .
        current (int): Valeur actuelle du compteur de clics dans le store.

    Returns:
        int: Nouvelle valeur du compteur de clics.
    """
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("store-cancel-edit-clicks", "data"),
    Input("btn-cancel-edit-visible", "n_clicks"),
    State("store-cancel-edit-clicks", "data"),
    prevent_initial_call=True
)
def sync_cancel_edit_visible(n, current):
    """
    Synchronise les clics du bouton d’annulation d’édition visible avec le store.

    Incrémente le compteur de clics dans le store associé pour refléter les interactions avec le bouton visible  Annuler .

    Args:
        n (int or None): Nombre de clics sur le bouton visible  Annuler .
        current (int): Valeur actuelle du compteur de clics dans le store.

    Returns:
        int: Nouvelle valeur du compteur de clics.
    """
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("btn-save-edit", "n_clicks"),
    Input("store-save-edit-clicks", "data"),
    prevent_initial_call=True
)
def trigger_save_edit(n):
    """
    Synchronise la valeur du bouton  Enregistrer  avec la valeur du store.

    Cette fonction met à jour le nombre de clics du bouton  Enregistrer  en fonction de la valeur enregistrée dans le store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton  Enregistrer .
    """
    return n

@app.callback(
    Output("btn-delete", "n_clicks"),
    Input("store-delete-clicks", "data"),
    prevent_initial_call=True
)
def trigger_delete(n):
    """
    Synchronise la valeur du bouton  Supprimer  avec la valeur du store.

    Cette fonction met à jour le nombre de clics du bouton  Supprimer  en fonction de la valeur enregistrée dans le store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton  Supprimer .
    """
    return n

@app.callback(
    Output("btn-cancel-edit", "n_clicks"),
    Input("store-cancel-edit-clicks", "data"),
    prevent_initial_call=True
)
def trigger_cancel_edit(n):
    """
    Synchronise la valeur du bouton  Annuler  avec la valeur du store.

    Cette fonction met à jour le nombre de clics du bouton  Annuler  en fonction de la valeur enregistrée dans le store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton  Annuler .
    """
    return n

@app.callback(
    Output("input-matiere-A", "value"),
    Input("input-matiere-A-visible", "value"),
    prevent_initial_call=True
)
def sync_matiere_a(val):
    """
    Synchronise la valeur du champ matière A entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  matière A  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val


@app.callback(
    Output("export-options-panel", "value"),
    Input("export-options-panel-visible", "value"),
    prevent_initial_call=True
)
def sync_export_options(val):
    """Synchronise les options d'exportation entre le panneau visible et caché.

    Met à jour les options d'exportation sélectionnées dans le panneau caché avec celles du panneau visible.

    Args:
        val (list): Options d'exportation sélectionnées dans le panneau visible.

    Returns:
        list: Options d'exportation synchronisées pour le panneau caché.
    """
    return val

@app.callback(
    Output("store-delete-a-clicks", "data"),
    Input("btn-delete-a-visible", "n_clicks"),
    State("store-delete-a-clicks", "data"),
    prevent_initial_call=True
)
def sync_delete_a_visible(n, current):
    """Synchronise les clics du bouton visible delete_a avec le store correspondant.

    Incrémente le compteur de clics dans le store associé pour refléter les interactions avec le bouton visible.

    Args:
        n (int or None): Nombre de clics sur le bouton visible.
        current (int): Valeur actuelle du compteur dans le store.

    Returns:
        int: Nouvelle valeur du compteur de clics.
    """
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("store-delete-b-clicks", "data"),
    Input("btn-delete-b-visible", "n_clicks"),
    State("store-delete-b-clicks", "data"),
    prevent_initial_call=True
)
def sync_delete_b_visible(n, current):
    """Synchronise les clics du bouton visible delete_b avec le store correspondant.

    Incrémente le compteur de clics dans le store associé pour refléter les interactions avec le bouton visible.

    Args:
        n (int or None): Nombre de clics sur le bouton visible.
        current (int): Valeur actuelle du compteur dans le store.

    Returns:
        int: Nouvelle valeur du compteur de clics.
    """
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("btn-delete-a", "n_clicks"),
    Input("store-delete-a-clicks", "data"),
    prevent_initial_call=True
)
def trigger_delete_a(n):
    """
    Synchronise la valeur du bouton delete_a avec la valeur du store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton delete_a.
    """
    return n

@app.callback(
    Output("btn-delete-b", "n_clicks"),
    Input("store-delete-b-clicks", "data"),
    prevent_initial_call=True
)
def trigger_delete_b(n):
    """
    Synchronise la valeur du bouton delete_b avec la valeur du store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton delete_b.
    """
    return n

@app.callback(
    Output("input-prof-A", "value"),
    Input("input-prof-A-visible", "value"),
    prevent_initial_call=True
)
def sync_prof_a(val):
    """
    Synchronise la valeur du champ professeur A entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  professeur A  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-salle-A", "value"),
    Input("input-salle-A-visible", "value"),
    prevent_initial_call=True
)
def sync_salle_a(val):
    """
    Synchronise la valeur du champ salle A entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  salle A  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-classe-A", "value"),
    Input("input-classe-A-visible", "value"),
    prevent_initial_call=True
)
def sync_classe_a(val):
    """
    Synchronise la valeur du champ classe A entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  classe A  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-matiere-B", "value"),
    Input("input-matiere-B-visible", "value"),
    prevent_initial_call=True
)
def sync_matiere_b(val):
    """
    Synchronise la valeur du champ matière B entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  matière B  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-prof-B", "value"),
    Input("input-prof-B-visible", "value"),
    prevent_initial_call=True
)
def sync_prof_b(val):
    """
    Synchronise la valeur du champ professeur B entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  professeur B  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-salle-B", "value"),
    Input("input-salle-B-visible", "value"),
    prevent_initial_call=True
)
def sync_salle_b(val):
    """
    Synchronise la valeur du champ salle B entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  salle B  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("input-classe-B", "value"),
    Input("input-classe-B-visible", "value"),
    prevent_initial_call=True
)
def sync_classe_b(val):
    """
    Synchronise la valeur du champ classe B entre la version visible et le store caché.

    Met à jour la valeur stockée pour le champ  classe B  en fonction de la saisie visible.

    Args:
        val (str): Valeur saisie dans le champ visible.

    Returns:
        str: Valeur synchronisée à stocker.
    """
    return val

@app.callback(
    Output("store-export-panel-clicks", "data"),
    Input("btn-export-panel-visible", "n_clicks"),
    State("store-export-panel-clicks", "data"),
    prevent_initial_call=True
)
def sync_export_panel_visible(n, current):
    """
    Synchronise les clics du bouton visible d'exportation de panel avec le store correspondant.

    Incrémente le compteur de clics dans le store associé pour refléter les interactions avec le bouton visible d’exportation de panel.

    Args:
        n (int or None): Nombre de clics sur le bouton visible.
        current (int): Valeur actuelle du compteur dans le store.

    Returns:
        int: Nouvelle valeur du compteur de clics.
    """
    if n is None:
        return current
    return (current or 0) + 1

@app.callback(
    Output("btn-export-panel", "n_clicks"),
    Input("store-export-panel-clicks", "data"),
    prevent_initial_call=True
)
def trigger_export_panel(n):
    """
    Synchronise la valeur du bouton d'exportation de panel avec la valeur du store.

    Args:
        n (int): Nombre de clics enregistrés dans le store.

    Returns:
        int: Nouvelle valeur à attribuer au bouton d'exportation de panel.
    """
    return n