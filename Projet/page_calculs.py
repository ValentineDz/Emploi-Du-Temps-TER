# Imports Dash : composants de base + interactivité
from dash import html, dcc, Input, Output, State, callback, dash
import dash_bootstrap_components as dbc

# Application principale
from main_dash import app

# Styles et textes personnalisés
from styles import *
from textes import texte_explications_page_calculs_1,texte_explications_page_calculs_2,texte_explications_page_calculs_3,texte_explications_page_calculs_4,texte_explications_page_calculs_5
# from solver import avancement, avancement_max, temps_estime
import math
import threading




# ---------- LAYOUT PRINCIPAL DE LA PAGE ----------
def layout_calculs ():
    return html.Div([
        # Stockage interne pour gérer le déclenchement du calcul
        dcc.Store(id="store-demarrage", data=False, storage_type="memory"),
        dcc.Store(id="store-resultats-solver", storage_type="session"),
        dcc.Store(id="store-progress", data=0),  # Pour suivre l'avancement
        dcc.Interval(id="interval-chargement", interval=500, n_intervals=0, disabled=True),  # Boucle de progression
        dcc.Location(id="redirect-calculs", refresh=True),  # Redirection après calcul terminé

        # Titre et description de la page
        html.H2("Lancer le calcul de l'emploi du temps", className="my-4"),
        html.P([texte_explications_page_calculs_1,
                html.Br(),
                html.Br(),
                texte_explications_page_calculs_2,
                html.Br(),
                texte_explications_page_calculs_3,
                html.Br(),
                html.Br(),
                texte_explications_page_calculs_4,
                ], style={**explication_style, "marginBottom": "30px"}),
        html.Div([
            html.Label("Combien d'emplois du temps souhaitez-vous comparer ?", style={"fontWeight": "bold", "marginBottom": "10px"}),

            html.P(texte_explications_page_calculs_5, style=explication_style),

            dcc.Input(
                id="input-nombre-runs",
                type="number",
                value=10,
                min=1,
                step=1,
                style={"width": "100px", "marginRight": "40px"}
            ),
            # Bouton pour lancer le calcul
            dbc.Button([
                html.I(className="bi bi-play-fill me-2"),
                "Lancer le calcul"
            ], id="btn-lancer-calcul", color="primary", className="mb-3", style=style_marge_haut),
        ], style=style_générateurs),
        

        html.Br(), html.Br(),

        # Bloc affiché pendant le calcul (chargement)
        html.Div(id="bloc-chargement", children=[
            dbc.Spinner(html.Div(id="message-calcul"), spinner_style=style_spinner),

            html.Br(), html.Br(),

            # Barre de progression du calcul
            html.Div(id="progress-bar-container", children=[
                dbc.Progress(id="barre-calcul", value=0, striped=True, animated=True, style={"height": "30px"})
            ], style={"marginTop": "20px"}),

            # Affichage du temps estimé restant
            html.Div(id="temps-estime", style=style_temps_estime),

        ], style={"display": "none"}),  # Caché par défaut

        html.Br(), html.Br(),

        # Bouton pour revenir à la page précédente (contraintes optionnelles)
        html.Div([
            dbc.Button([
                html.I(className="bi bi-arrow-left me-2"),
                "Page précédente"
            ], id="btn-retour-contraintes", color="secondary")
        ], style={"textAlign": "left", "marginTop": "200px", "marginLeft": "20px"}), # A modifer 

    ], style=global_page_style)


# ---------- CALLBACKS ----------

# # Callback déclenché au clic sur "Lancer le calcul"
# @callback(
#     Output("bloc-chargement", "style"),           # Affiche le bloc
#     Output("interval-chargement", "disabled"),    # Active le tick
#     Output("store-progress", "data"),             # Réinitialise la progression
#     Output("store-demarrage", "data"),            # Indique que le calcul démarre
#     Input("btn-lancer-calcul", "n_clicks"),
#     prevent_initial_call=True
# )
# def demarrer_calcul(n):
#     return {"display": "block"}, False, 0, True

# etat_solver = {"en_cours": False}

# def lancer_solver_thread(nombre_runs):
#     def tache():
#         from solver import lancer_depuis_interface
#         lancer_depuis_interface(nombre_runs)
#         etat_solver["en_cours"] = False

#     etat_solver["en_cours"] = True
    
#     threading.Thread(target=tache, daemon=True).start()



# @callback(
#     Output("barre-calcul", "value"),
#     Output("temps-estime", "children"),
#     Output("message-calcul", "children"),
#     Output("interval-chargement", "disabled", allow_duplicate=True),
#     Output("redirect-calculs", "pathname"),
#     Output("store-progress", "data", allow_duplicate=True),
#     Output("store-resultats-solver", "data"),
#     Input("interval-chargement", "n_intervals"),
#     State("store-progress", "data"),
#     State("store-demarrage", "data"),
#     State("input-nombre-runs", "value"),
#     prevent_initial_call=True
# )
# def progression(n, progress, actif, nombre_runs):
#     if not actif or n == 0:
#         raise dash.exceptions.PreventUpdate

#     if progress == 0:
#         if not etat_solver["en_cours"]:
#             lancer_solver_thread(nombre_runs)
#         return 0, "Initialisation…", "Démarrage du solveur…", False, None, 0, dash.no_update

#     from solver import avancement, avancement_max, temps_estime  # au cas où valeurs changent dynamiquement
#     if avancement_max > 0:
#         progress = int((avancement / avancement_max) * 100)
#     else:
#         progress = 0

#     texte = f"{avancement} contraintes traitées"
#     temps = temps_estime or "Calcul en cours..."

#     if progress >= 100 or not etat_solver["en_cours"]:
#         from solver import fusions_par_run, taux_par_run, meilleur_seed, meilleure_fusion, meilleur_resultats
#         resultats = {
#             "fusions_par_run": fusions_par_run,
#             "taux_par_run": taux_par_run,
#             "meilleur_seed": meilleur_seed,
#             "meilleure_fusion": meilleure_fusion,
#             "meilleur_resultats": meilleur_resultats,
#         }
#         return 100, "", "Calcul terminé ✅", True, "/resultats", 100, resultats

#     return progress, temps, texte, False, None, progress, dash.no_update
