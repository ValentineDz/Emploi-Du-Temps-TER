"""
Page Dash dédiée à la configuration des contraintes optionnelles de l'emploi du temps.

Elle permet à l'utilisateur de :
1. Définir des contraintes sur le poids du matériel scolaire par niveau et matière ;
2. Paramétrer les capacités du réfectoire et des permanences, ainsi que des règles associées (ex. fin de journée anticipée pour les plus jeunes) ;
3. Hiérarchiser les contraintes optionnelles par ordre d'importance (via un tableau réordonnable).

La page inclut :
- Des accordéons rétractables avec saisie conditionnelle ;
- Des callbacks pour pré-remplir et sauvegarder dynamiquement les données ;
- Une navigation vers les autres pages de configuration (contraintes / calculs).
"""

from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc

from styles import *
from fonctions import *
from textes import *
from constantes import *

# ----- LAYOUT PRINCIPAL DE LA PAGE -----
def layout_contraintes_optionnelles():
    """
    Construit et retourne le layout complet de la page "Contraintes optionnelles".

    Composants principaux :
    - Section 1 : Contrainte sur le poids du matériel scolaire :
        * Activation de la contrainte ;
        * Sélection d'un niveau ;
        * Tableau des poids par matière ;
        * Saisie du poids maximal journalier ;
        * Informations explicatives avec exemples.

    - Section 2 : Paramètres du réfectoire et de la permanence :
        * Capacité maximale du réfectoire ;
        * Pourcentage d'élèves demi-pensionnaires ;
        * Capacité maximale de la permanence ;
        * Option "fin plus tôt pour les jeunes".

    - Section 3 : Classement des contraintes optionnelles :
        * Tableau réordonnable avec boutons Monter / Descendre ;
        * Stockage de l'ordre dans un `dcc.Store`.

    - Navigation bas de page : boutons "Page précédente" et "Page suivante".

    Returns:
        html.Div: Le layout Dash prêt à être affiché dans l'application.
    """
   
    return html.Div([
        # Stores : 
        dcc.Store(id="store-refresh-ordre", data=0),
        dcc.Store(id="store-horaires-sauvegarde", data=None),
        dcc.Store(id="freeze-callbacks", data=False),

        # Titre 
        html.H1("Contraintes optionnelles (non obligatoires)", className="my-4"),
        html.Hr(style=style_hr),
        html.P(texte_explications_page_contrainte_optionnelles, style=explication_style),
        html.Br(),

        # Section sur le poids du matériel
        html.H2("1. Poids du matériel scolaire par niveau"),
        html.P(texte_explications_poids_materiel, style=explication_style),

        # Accordéon contenant la table des poids par matière
        dbc.Accordion([
            dbc.AccordionItem([
                html.Label("Souhaitez-vous appliquer une contrainte sur le poids du matériel scolaire ?"),
                dcc.RadioItems(
                    id="activer-poids-materiel",
                    options=OUI_NON,
                    value="non",
                    inline=True,
                    style=style_liste_choix
                ),
                html.Br(),

                html.Div(id="bloc-poids-materiel-conditionnel"),
            ], title=html.H4("1.1 Poids du matériel scolaire par matière et par niveau"))
        ], style=style_accordeons, start_collapsed=True, flush=True, active_item=None),

        html.Br(),
        # Section sur les contraintes optionnelles
        html.H2("2. Réfectoire et permanences", className="my-3"),
        html.P(texte_explications_page_refectoire_permanences, style=explication_style),

        dbc.Accordion([
            dbc.AccordionItem([
                html.P(texte_explications_cantine, style=explication_style),
                html.H5("2.2.1 Réfectoire", className="my-3"),

                html.Div([
                    html.Label("Quelle est la capacité maximale du réfectoire en simultané ?", style=style_marge_droite),
                    dcc.Input(
                        id="capacite-cantine",
                        type="number",
                        min=0,
                        max=3000,
                        placeholder="Ex : 200",
                        style=style_input_refectoire_langues
                    ),
                    html.Span("Élèves")
                ]),
                html.Br(),

                html.Div([
                    html.Label("Quel pourcentage d'élèves mangent au réfectoire ?", style=style_marge_droite),
                    dcc.Input(
                        id="taux-cantine",
                        type="number",
                        min=0,
                        max=100,
                        step=1,
                        placeholder="Ex : 70",
                        style=style_input_refectoire_langues
                    ),
                    html.Span("%")
                ]),
                html.Br(),

                html.Div([
                    html.Label("Souhaitez-vous que les élèves les plus jeunes terminent plus tôt le midi ?"),
                    dcc.RadioItems(
                        id="fin-plus-tot-jeunes",
                        options=OUI_NON,
                        value="non",
                        inline=True,
                        style=style_liste_choix
                    )
                ]),
                html.Br(),

            ], title=html.H4("2.1 Informations sur le réfectoire")),
            
            dbc.AccordionItem([
                html.P(texte_explications_permanences, style=explication_style),
                html.H5("2.2.2 Permanences", className="my-3"),
                
                html.Div([
                    html.Label("Quelle est la capacité maximale en permanence ?", style=style_marge_droite),
                    dcc.Input(
                        id="capacite-permanence",
                        type="number",
                        min=0,
                        max=3000,
                        placeholder="Ex : 80",
                        style=style_input_refectoire_langues
                    ),
                    html.Span("Élèves")
                ]),
                    
                html.Br()
            ], title=html.H4("2.2 Capacité totale des salles de permanences")),
            dcc.Store(id="store-prefill-refectoire", data=True)
        ], style=style_accordeons, start_collapsed=True, flush=True, active_item=None),

        html.Br(),
        html.H2("3. Ordre d'importance des contraintes optionnelles", className="my-4"),
        html.P(texte_explications_ordre, style=explication_style),

        html.Div([
            
            html.P([html.I(className="bi bi-info-circle me-2"),"Le rang 1 est le plus important."], style={**explication_style, **style_marge_gauche}),
            dash_table.DataTable(
                id="table-ordre-contraintes",
                columns=[
                    {"name": "Rang", "id": "Rang"},
                    {"name": "Contrainte", "id": "Contrainte"}
                ],
                data=[
                    {"Rang": i + 1, "Contrainte": c}
                    for i, c in enumerate([
                        "Poids du matériel",
                        "Réfectoire et permanence",
                        "Salles",
                        "Profs",
                        "Classes",
                        "Enchaînement de cours"
                    ])
                ],
                row_selectable="single",
                style_as_list_view=True,
                style_header=style_header,
                style_table=style_table_ordo,
                style_data_conditional=style_cell_ordo,
            ),

            html.Div([
                html.Button([
                    html.I(className="bi bi-arrow-up me-1"), "Monter"
                ], id="btn-monter-contrainte", className="btn btn-outline-primary me-2", style=style_marge_droite),

                html.Button([
                    html.I(className="bi bi-arrow-down me-1"), "Descendre"
                ], id="btn-descendre-contrainte", className="btn btn-outline-primary", style=style_marge_gauche)
            ], style=style_centrer)
        ], style=style_ordo),

        dcc.Store(id="ordre-contraintes-store"),

        # Boutons de navigation (précédent / suivant)
        html.Div([
            html.Button([html.I(className="bi bi-arrow-left me-2"), "Page précédente"],
                        id="btn-previous-contrainte", n_clicks=0, className="btn btn-secondary", style=style_btn_suivant),
            html.Button(["Page suivante", html.I(className="bi bi-arrow-right ms-2")],
                        id="btn-next-contrainte", n_clicks=0, className="btn btn-primary", style=style_btn_suivant)
        ], style=style_boutons_bas),

        # Composant invisible de redirection
        dcc.Location(id="redirect-page-contrainte-opt-add", refresh=True)
    ], style=global_page_style)


#### ----------- CALLBACKS ----------- ####

@callback(
    Output("activer-poids-materiel", "value"),
    Input("store-prefill-refectoire", "data"), 
    prevent_initial_call=False
)
def prefill_activer_poids(_):
    """
    Pré-remplit le sélecteur 'activer-poids-materiel' selon les données enregistrées.

    Si au moins un niveau possède une configuration de poids, la valeur par défaut est "oui".
    Sinon, on sélectionne "non".

    Returns:
        str: "oui" ou "non"
    """
    data = charger_donnees_interface()
    poids = data.get("contraintes_additionnelles", {}).get("poids_par_niveau", {})
    # Si au moins un niveau a des données => on coche oui
    if any(poids.get(niv) for niv in poids):
        return "oui"
    return "non"

# Callback pour afficher les matières du niveau sélectionné + les poids existants
@callback(
    Output("table-poids-par-matiere", "data"),
    Output("poids-max-journalier", "value"),
    Input("niveau-poids", "value")
)
def charger_matieres_et_poids(niveau):
    """
    Charge dynamiquement les matières et les poids estimés enregistrés pour un niveau donné.

    Utilisé pour remplir le tableau éditable des poids par matière.

    Args:
        niveau (str): Le niveau sélectionné (ex. "6e").

    Returns:
        list[dict]: Données du tableau à afficher.
        float|None: Poids maximal journalier enregistré (si disponible).
    """
    if not niveau:
        raise PreventUpdate

    data = charger_donnees_interface()
    matieres = data.get("affichage", {}).get("volume_horaire_affichage", {}).get(niveau, {})
    poids_enregistres = data.get("contraintes_additionnelles", {}).get("poids_par_niveau", {}).get(niveau, {})
    poids_max = poids_enregistres.get("poids_max")

    tableau = []
    for mat in sorted(set(matieres.keys()) | set(poids_enregistres.keys()) - {"poids_max"}):
        poids = poids_enregistres.get(mat, "")
        tableau.append({"Matiere": mat, "Poids": poids})

    return tableau, poids_max

# Callback de sauvegarde automatique dès qu'on modifie le tableau ou le poids max
@callback(
    Output("table-poids-par-matiere", "style_data_conditional", allow_duplicate=True),
    Output("store-refresh-ordre", "data", allow_duplicate=True),  # <-- AJOUTÉ
    Input("table-poids-par-matiere", "data"),
    Input("poids-max-journalier", "value"),
    State("niveau-poids", "value"),
    State("activer-poids-materiel", "value"),
    State("store-refresh-ordre", "data"),  # <-- AJOUTÉ
    prevent_initial_call=True
)
def sauvegarder_poids_par_niveau(table, poids_max, niveau, activation, refresh_val):
    """
    Sauvegarde les poids estimés par matière ainsi que le poids maximal journalier pour un niveau donné.

    Ne fait rien si la contrainte n'est pas activée.

    Args:
        table (list[dict]): Données du tableau (matières et poids).
        poids_max (float): Valeur maximale quotidienne saisie.
        niveau (str): Niveau concerné.
        activation (str): Valeur du bouton radio (oui / non).
        refresh_val (int): Compteur de rafraîchissement (incrémenté si sauvegarde).

    Returns:
        dash.no_update, int: Incrément de rafraîchissement.
    """
    if not niveau or not isinstance(table, list):
        raise PreventUpdate

    if activation != "oui":
        return no_update, dash.no_update

    sauvegarde = {}
    for ligne in table:
        mat = ligne.get("Matiere")
        try:
            poids = float(ligne.get("Poids"))
        except:
            poids = None
        if mat and poids is not None:
            sauvegarde[mat] = poids

    try:
        poids_max = float(poids_max)
        sauvegarde["poids_max"] = poids_max
    except:
        pass

    mettre_a_jour_section_interface(f"contraintes_additionnelles.poids_par_niveau.{niveau}", sauvegarde)
    return no_update, (refresh_val or 0) + 1

###########################################################################################################
@callback(
    Output("capacite-cantine", "value"),
    Output("taux-cantine", "value"),
    Output("capacite-permanence", "value"),
    Output("fin-plus-tot-jeunes", "value"),
    Input("store-prefill-refectoire", "data"),
    prevent_initial_call=False
)
def prefill_cantine_permanence(_):
    """
    Charge les valeurs préenregistrées pour le réfectoire et les permanences
    dans les champs correspondants.

    Returns:
        tuple: Capacité cantine, taux cantine, capacité permanence, fin_jeunes (oui/non)
    """
    data = charger_donnees_interface().get("contraintes_additionnelles", {})
    bloc = data.get("cantine_permanence", {})
    capacite = bloc.get("capacite_cantine", None)
    taux = bloc.get("taux_cantine", None)
    permanence = bloc.get("capacite_permanence", None)
    fin_jeunes = data.get("fin_jeunes_plus_tot", False)
    return capacite, taux, permanence, "oui" if fin_jeunes else "non"

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
    Output("store-refresh-ordre", "data", allow_duplicate=True),
    Input("capacite-cantine", "value"),
    Input("taux-cantine", "value"),
    Input("capacite-permanence", "value"),
    Input("fin-plus-tot-jeunes", "value"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_donnees_cantine(capacite, taux, permanence, fin, freeze):
    """
    Sauvegarde les valeurs saisies concernant le réfectoire et les permanences
    dans le fichier JSON de configuration.

    Ne fait rien si `freeze` est activé.

    Returns:
        dash.no_update, int: Incrément de rafraîchissement.
    """
    if freeze:
        raise PreventUpdate
    valeurs = {
        "capacite_cantine": capacite,
        "taux_cantine": taux,
        "capacite_permanence": permanence,
        "fin_jeunes_plus_tot": fin
    }
    mettre_a_jour_section_interface("contraintes_additionnelles.cantine_permanence", valeurs)
    return dash.no_update, 1

#########################################################################################################
@callback(
    Output("table-ordre-contraintes", "data"),
    Output("ordre-contraintes-store", "data"),
    Input("store-refresh-ordre", "data"),
    prevent_initial_call=False
)
def charger_ordre_contraintes(_):
    """
    Génère dynamiquement la liste ordonnée des contraintes optionnelles actives.

    L'ordre est basé sur les données existantes, filtré selon les contraintes encore pertinentes.

    Returns:
        tuple: (table_data à afficher, ordre effectif des contraintes)
    """
    data = charger_donnees_interface()

    # Liste dynamique des contraintes réellement actives
    contraintes_dynamiques = []

    poids_par_niveau = data.get("contraintes_additionnelles", {}).get("poids_par_niveau", {})
    if any(bool(poids_par_niveau.get(niv)) for niv in poids_par_niveau):
        contraintes_dynamiques.append("Poids du matériel")

    cantine = data.get("contraintes_additionnelles", {}).get("cantine_permanence", {})
    if cantine.get("capacite_cantine") or cantine.get("capacite_permanence"):
        contraintes_dynamiques.append("Réfectoire et permanence")

    contraintes_data = data.get("contraintes", {})
    if contraintes_data.get("profs", {}).get("indisponibilites_partielles"):
        contraintes_dynamiques.append("Professeurs")
    if contraintes_data.get("salles", {}).get("indisponibilites_partielles"):
        contraintes_dynamiques.append("Salles")
    if contraintes_data.get("groupes", {}).get("indisponibilites_partielles"):
        contraintes_dynamiques.append("Classes / groupes")

    # On part de l'ordre sauvegardé
    ordre_sauvegarde = data.get("contraintes_additionnelles", {}).get("ordre_contraintes", [])

    # Conserver uniquement les contraintes encore actives
    ordre_filtré = [c for c in ordre_sauvegarde if c in contraintes_dynamiques]

    # Ajouter à la fin les nouvelles contraintes absentes de l'ordre enregistré
    contraintes_finales = ordre_filtré + [c for c in contraintes_dynamiques if c not in ordre_filtré]

    table = [{"Rang": i + 1, "Contrainte": c} for i, c in enumerate(contraintes_finales)]
    return table, contraintes_finales



@callback(
    Output("table-ordre-contraintes", "data", allow_duplicate=True),
    Output("ordre-contraintes-store", "data", allow_duplicate=True),
    Output("table-ordre-contraintes", "selected_rows", allow_duplicate=True),
    Input("btn-monter-contrainte", "n_clicks"),
    Input("btn-descendre-contrainte", "n_clicks"),
    State("table-ordre-contraintes", "selected_rows"),
    State("ordre-contraintes-store", "data"),
    prevent_initial_call=True
)
def modifier_ordre(monter, descendre, selected, ordre_actuel):
    """
    Permet de déplacer une contrainte vers le haut ou le bas dans le tableau d'ordre.

    Args:
        monter, descendre (int): Nombre de clics sur les boutons.
        selected (list[int]): Ligne sélectionnée dans le tableau.
        ordre_actuel (list[str]): Ordre actuel des contraintes.

    Returns:
        tuple: (nouveau tableau, nouvel ordre, ligne sélectionnée mise à jour)
    """
    if not selected or not ordre_actuel:
        raise PreventUpdate

    index = selected[0]
    triggered = ctx.triggered_id
    new_order = ordre_actuel[:]

    if triggered == "btn-monter-contrainte" and index > 0:
        new_order[index - 1], new_order[index] = new_order[index], new_order[index - 1]
        new_index = index - 1
    elif triggered == "btn-descendre-contrainte" and index < len(new_order) - 1:
        new_order[index + 1], new_order[index] = new_order[index], new_order[index + 1]
        new_index = index + 1
    else:
        raise PreventUpdate

    # On reconstruit le tableau avec le rang mis à jour
    table_data = [{"Rang": i + 1, "Contrainte": c} for i, c in enumerate(new_order)]

    return table_data, new_order, [new_index]

@callback(
    Output("store-horaires-sauvegarde", "data", allow_duplicate=True),
    Input("ordre-contraintes-store", "data"),
    State("freeze-callbacks", "data"),
    prevent_initial_call=True
)
def sauvegarder_ordre_contraintes(ordre, freeze):
    """
    Enregistre l'ordre actuel des contraintes dans le fichier JSON.

    Ne fait rien si `freeze` est activé.

    Returns:
        dash.no_update
    """
    if freeze:
        raise PreventUpdate
    mettre_a_jour_section_interface("contraintes_additionnelles.ordre_contraintes", ordre)
    return dash.no_update

#########################################################################################################
@callback(
    Output("bloc-poids-materiel-conditionnel", "children"),
    Input("activer-poids-materiel", "value")
)
def afficher_bloc_si_oui(choix):
    """
    Affiche ou masque le bloc de configuration du poids du matériel scolaire.

    Args:
        choix (str): "oui" ou "non"

    Returns:
        html.Div | None: Bloc de contenu à afficher, ou rien.
    """
    if choix != "oui":
        return None

    return  html.Div([
                # Dropdown pour choisir un niveau (6e à 3e)
                html.Label("Sélectionnez un niveau afin de pouvoir saisir les poids du matériel associés :"),
                dcc.Dropdown(
                    id="niveau-poids",
                    options=[{"label": n, "value": n} for n in NIVEAUX],
                    placeholder="Choisir un niveau...",
                    style=style_dropdown_niveau
                ),

                # Titre du tableau + info-bulle
                html.Div([
                    html.P(["Tableau des poids des matières", 
                        html.I(className="bi bi-info-circle-fill", id="info-poids-optionnels",
                        style=style_tooltip_info)]
                    , style=style_tooltip),
                    dbc.Tooltip(
                        "Vous pouvez ne remplir que certaines matières. Les poids sont optionnels.",
                        target="info-poids-optionnels",
                        placement="right"
                    ),
                ]),
                
                # Tableau éditable avec les matières et les poids associés
                dash_table.DataTable(
                    id="table-poids-par-matiere",
                    columns=[
                        {"name": "Matière", "id": "Matiere", "editable": False},
                        {"name": "Poids estimé (kg)", "id": "Poids", "editable": True, "type": "numeric"}
                    ],
                    data=[],
                    editable=True,
                    style_table=style_table,
                    style_header=style_header_table,
                    style_cell=style_cell
                ),

                html.Br(),

                # Zone de saisie du poids maximal autorisé par jour
                html.Div([
                    html.Label("Poids maximal autorisé par jour :", style=style_marge_gauche),
                    dcc.Input(
                        id="poids-max-journalier",
                        type="number",
                        min=1,
                        step=0.1,
                        placeholder="ex : 7.5",
                        style={**style_input, **style_marge_haut}
                    ),
                    html.Span("KG"),
                    
                    html.I(
                        className="bi bi-info-circle-fill",
                        id="tooltip-poids-max-info",
                        style={**style_tooltip_info, **style_marge_gauche}
                    ),

                    dbc.Tooltip(
                        "Une tolérance de 5 % vis-à-vis de cette valeur maximale est ensuite appliquée.",
                        target="tooltip-poids-max-info",
                        placement="right"
                    ),
                ], style=style_poids_max),
                html.Br(),
                

                html.Div([
                    html.P("Le poids maximal recommandé est fixé à 10 % du poids moyen d'un élève. "
                        "Voici les poids moyens estimés :"),

                    html.Ul([
                        html.Li("6e : 35 kg"),
                        html.Li("5e : 38 kg"),
                        html.Li("4e : 43 kg"),
                        html.Li("3e : 48 kg")
                    ]),

                    html.P([
                        html.I("Source : "),
                        html.A("Étude ESTEBAN (2014–2016), Santé publique France",
                            href="https://www.apop-france.com/uploads/elfinder/doc-telecharger/ESTEBAN.pdf",
                            target="_blank")
                    ]),
                    html.Br(),

                    html.P("Exemple de poids estimés pour une classe de 4e :"),

                    dash_table.DataTable(
                        columns=[
                            {"name": "Matière", "id": "Matiere"},
                            {"name": "Poids estimé (kg)", "id": "Poids"}
                        ],
                        data=[
                            {"Matiere": "Français", "Poids": 2},
                            {"Matiere": "Mathématiques", "Poids": 0.8},
                            {"Matiere": "Histoire-Géographie et EMC", "Poids": 1.55},
                            {"Matiere": "Physique-Chimie", "Poids": 1},
                            {"Matiere": "SVT", "Poids": 1.2},
                            {"Matiere": "Technologie", "Poids": 0.33},
                            {"Matiere": "LV1_Anglais", "Poids": 0.65},
                            {"Matiere": "EPS", "Poids": 1},
                            {"Matiere": "Arts plastiques", "Poids": 0.4},
                            {"Matiere": "Musique", "Poids": 0.8}
                        ],
                        style_table=style_table,
                        style_header=style_header_table,
                        style_cell=style_cell
                    )

                ], style={**explication_style, **style_format_donnes_info}),

                html.Br(),
            ], style=style_accordeons_contenus)

@callback(
    Output("store-refresh-ordre", "data", allow_duplicate=True),
    Input("activer-poids-materiel", "value"),
    State("store-refresh-ordre", "data"),
    prevent_initial_call=True
)
def reset_si_desactivation_poids(choix, refresh_state):
    """
    Réinitialise les données liées au poids du matériel scolaire
    si l'utilisateur désactive cette contrainte.

    Returns:
        int: Compteur de rafraîchissement incrémenté.
    """
    if ctx.triggered_id != "activer-poids-materiel" or choix != "non":
        raise PreventUpdate

    data = charger_donnees_interface()
    if "poids_par_niveau" in data.get("contraintes_additionnelles", {}):
        data["contraintes_additionnelles"]["poids_par_niveau"] = {}
        sauvegarder_donnees_interface(data)
        return (refresh_state or 0) + 1

    raise PreventUpdate

#########################################################################################################
# Callback pour gérer la navigation entre les pages
@callback(
    Output("redirect-page-contrainte-opt-add", "pathname"),
    Input("btn-previous-contrainte", "n_clicks"),
    Input("btn-next-contrainte", "n_clicks"),
    prevent_initial_call=True
)
def naviguer_page_contraintes_optionnelles(n_prec, n_suiv):
    """
    Gère la navigation entre pages : redirige vers /contraintes ou /calculs selon le bouton cliqué.

    Returns:
        str: Chemin de la page cible.
    """
    triggered = ctx.triggered_id

    # Redirection vers la page suivante
    if triggered == "btn-next-contrainte":
        return "/calculs"

    # Redirection vers la page précédente
    elif triggered == "btn-previous-contrainte":
        return "/contraintes"

    raise PreventUpdate