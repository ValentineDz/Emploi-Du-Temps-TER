"""
Page Dash dédiée au lancement du solver

Cette page présente une sections principale organisée :
- Explication
- Saisie et bouton pour lancer le solver avec un nombre de runs définis
- Barre de chargements avec du textes pour donner des informations complémentaires.

"""

# Imports Dash : composants de base + interactivité
from dash import html, dcc, Input, Output, State, callback, dash
import dash_bootstrap_components as dbc


# Styles et textes personnalisés
from styles import *
from textes import texte_explications_page_calculs_1,texte_explications_page_calculs_2,texte_explications_page_calculs_3,texte_explications_page_calculs_4,texte_explications_page_calculs_5
import math
import threading

import time

# ---------- LAYOUT PRINCIPAL DE LA PAGE ----------
def layout_calculs():
    return html.Div([
        # Stockage interne pour gérer le déclenchement du calcul
        dcc.Store(id="store-demarrage", data=False, storage_type="memory"),
        dcc.Store(id="store-resultats-solver", storage_type="session"),
        dcc.Store(id="store-progress", data=0),  # Pour suivre l'avancement
        dcc.Interval(id="interval-chargement", interval=1000, n_intervals=0, disabled=True),  # Boucle de progression
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
            # Message principal de statut
            html.Div(id="message-calcul", style={"fontSize": "18px", "fontWeight": "bold", "marginBottom": "10px"}),
            
            # Étape détaillée
            html.Div(id="etape-calcul", style={"fontSize": "14px", "color": "#666", "marginBottom": "15px"}),
            
            dbc.Spinner(html.Div(id="spinner-container"), spinner_style=style_spinner),

            html.Br(),

            # Barre de progression du calcul
            html.Div(id="progress-bar-container", children=[
                dbc.Progress(id="barre-calcul", value=0, striped=True, animated=True, style={"height": "30px"})
            ], style={"marginTop": "20px"}),

            # Informations détaillées sur la progression
            html.Div([
               html.Div(id="temps-estime", style={**style_temps_estime, "marginTop": "5px"}),
               html.Div(id="taux-regroupes", style={"fontSize": "14px", "marginTop": "8px", "display": "flex", "gap": "20px","textAlign":"center","width": "100%"}),
            ]),

            # NOUVEAU : Bouton pour aller aux résultats (affiché seulement quand terminé)
            html.Div(id="bouton-resultats-container", children=[
                html.Br(),
                dbc.Button([
                    html.I(className="bi bi-graph-up me-2"),
                    "Voir les résultats"
                ], id="btn-voir-resultats", color="success", size="lg")
            ], style={"display": "none", "textAlign": "center", "marginTop": "20px"}),

        ], style={"display": "none"}),  # Caché par défaut

        html.Br(), html.Br(),

        # Bouton pour revenir à la page précédente (contraintes optionnelles)
        html.Div([
            dbc.Button([
                html.I(className="bi bi-arrow-left me-2"),
                "Page précédente"
            ], id="btn-retour-contraintes", color="secondary")
        ], style={"textAlign": "left", "marginTop": "200px", "marginLeft": "20px"}),

    ], style=global_page_style)


# ---------- CALLBACKS ----------

# Callback déclenché au clic sur "Lancer le calcul"
@callback(
    Output("bloc-chargement", "style"),           # Affiche le bloc
    Output("interval-chargement", "disabled"),    # Active le tick
    Output("store-progress", "data"),             # Réinitialise la progression
    Output("store-demarrage", "data"),            # Indique que le calcul démarre
    Input("btn-lancer-calcul", "n_clicks"),
    prevent_initial_call=True
)
def demarrer_calcul(n):
    """
    Démarre le processus de calcul d'emploi du temps.
    
    Callback Dash déclenché lors du clic sur le bouton "Lancer le calcul".
    Initialise l'interface de suivi en affichant le bloc de chargement,
    activant l'intervalle de mise à jour, et préparant les variables de suivi.
    
    Args:
        n (int): Nombre de clics sur le bouton (fourni automatiquement par Dash)
    
    Returns:
        tuple: Un tuple contenant :
            - dict: Style CSS pour afficher le bloc de chargement {"display": "block"}
            - bool: False pour activer l'intervalle de mise à jour
            - int: 0 pour réinitialiser la progression
            - bool: True pour indiquer que le calcul démarre
    
    Note:
        Ce callback utilise prevent_initial_call=True pour éviter l'exécution
        au chargement initial de la page.
    """
    return {"display": "block"}, False, 0, True



@callback(
    Output("redirect-calculs", "pathname", allow_duplicate=True),
    Input("btn-voir-resultats", "n_clicks"),
    prevent_initial_call=True
)
def aller_aux_resultats(n):
    """
    Redirige vers la page des résultats.
    
    Callback Dash déclenché lors du clic sur le bouton "Voir les résultats".
    Effectue une redirection vers la page "/resultats" de l'application.
    
    Args:
        n (int): Nombre de clics sur le bouton (fourni automatiquement par Dash)
    
    Returns:
        str or dash.no_update: Le chemin "/resultats" si le bouton a été cliqué,
                               sinon dash.no_update pour ne pas modifier la route
    """
    if n:
        return "/resultats"
    return dash.no_update


etat_solver = {"en_cours": False, "thread_demarre": False}


def lancer_solver_thread(nombre_runs):
    """
    Lance le solveur d'emploi du temps dans un thread séparé.
    
    Démarre l'exécution du solveur dans un thread indépendant pour éviter
    de bloquer l'interface utilisateur Dash. Gère l'état global du solver
    et assure la réinitialisation des variables de suivi.
    
    Args:
        nombre_runs (int): Nombre de runs d'optimisation à effectuer
    
    Side Effects:
        - Modifie l'état global `etat_solver` pour marquer le début d'exécution
        - Lance un thread daemon pour l'exécution du solver
        - Appelle reset_avancement() pour réinitialiser les variables de suivi
        - Appelle lancer_depuis_interface() pour démarrer l'optimisation
    
    Note:
        La fonction vérifie que le thread n'est pas déjà démarré avant de
        lancer une nouvelle instance. Le thread est marqué comme daemon
        pour être automatiquement terminé à la fermeture de l'application.
        
    Raises:
        Exception: Les erreurs du solver sont capturées et affichées dans
                  la console, mais ne remontent pas à l'appelant.
    """

    def tache():
        try:
            from solver import lancer_depuis_interface, reset_avancement
            # Réinitialise l'avancement avant de commencer
            reset_avancement()
            # Lance le calcul
            lancer_depuis_interface(nombre_runs)
        except Exception as e:
            print(f"Erreur dans le thread solver: {e}")
        finally:
            etat_solver["en_cours"] = False
            etat_solver["thread_demarre"] = False

    if not etat_solver["thread_demarre"]:
        etat_solver["en_cours"] = True
        etat_solver["thread_demarre"] = True
        threading.Thread(target=tache, daemon=True).start()


@callback(
    Output("barre-calcul", "value"),
    Output("temps-estime", "children"),
    Output("message-calcul", "children"),
    Output("etape-calcul", "children"),
    Output("taux-regroupes", "children"),   
    Output("interval-chargement", "disabled", allow_duplicate=True),
    Output("bouton-resultats-container", "style"),
    Output("store-progress", "data", allow_duplicate=True),
    Output("store-resultats-solver", "data"),
    Input("interval-chargement", "n_intervals"),
    State("store-progress", "data"),
    State("store-demarrage", "data"),
    State("input-nombre-runs", "value"),
    prevent_initial_call=True
)
def progression(n, progress_store, actif, nombre_runs):
    """
    Met à jour l'interface de progression du calcul en temps réel.
    
    Callback Dash principal pour le suivi de l'avancement du calcul d'emploi
    du temps. Gère le démarrage du solver, la mise à jour de tous les éléments
    d'interface (barre de progression, temps, messages, taux) et la finalisation
    avec récupération des résultats.
    
    Args:
        n (int): Nombre d'intervalles écoulés (tick de l'interval component)
        progress_store (int): Valeur de progression stockée (0-100)
        actif (bool): Indique si le calcul a été démarré
        nombre_runs (int): Nombre de runs d'optimisation configuré
    
    Returns:
        tuple: Un tuple de 9 éléments pour mettre à jour l'interface :
            - int: Valeur de la barre de progression (0-100)
            - str: Texte d'estimation de temps
            - str: Message principal de statut
            - str: Message détaillé de l'étape courante
            - str: Informations sur les taux de réussite
            - bool: État de l'intervalle (activé/désactivé)
            - dict: Style CSS du container des boutons résultats
            - int: Nouvelle valeur de progression à stocker
            - dict or dash.no_update: Données des résultats finaux
    
    Information:
        - Au premier tick (progress_store == 0) : lance le solver dans un thread
        - Pendant l'exécution : met à jour la progression via get_avancement_info()
        - À la fin : récupère et stocke les résultats finaux, affiche le bouton résultats
        - En cas d'erreur : affiche un message d'erreur et désactive l'intervalle
    
    Raises:
        dash.exceptions.PreventUpdate: Si le calcul n'est pas actif ou n == 0
        
    Note:
        Ce callback utilise des imports dynamiques pour éviter les dépendances
        circulaires avec le module solver.
    """
    if not actif or n == 0:
        raise dash.exceptions.PreventUpdate

    # Au premier tick, lance le solver
    if progress_store == 0 and not etat_solver["thread_demarre"]:
        lancer_solver_thread(nombre_runs)
        etat_solver["temps_debut"] = time.time()
        if nombre_runs == 1:
            message_initial = "Démarrage du calcul 1 essai "
            temps_initial = ""
        else:
            message_initial = f"Démarrage du calcul ({nombre_runs} essais)"
            temps_initial = "⏳ Préparation du calcul..."
        return (
            5, temps_initial, message_initial, 
            "Initialisation du solveur...", 
            "",   # taux_regroupes vide
            False, {"display": "none"}, 1, dash.no_update
        )

    # Récupère les informations d'avancement depuis le solver
    try:
        from solver import get_avancement_info
        info = get_avancement_info()

        # 1. Message principal selon la phase
        messages_phases = {
            "attente": "Prêt à démarrer",
            "preparation": "Préparation du calcul",
            "calcul": "Calcul des emplois du temps",
            "finalisation": "Finalisation",
            "termine": "✅ Calcul terminé avec succès !"
        }
        message_principal = messages_phases.get(info["phase"], "Calcul en cours...")
        if info["phase"] == "calcul" and info["run_actuel"] > 0:
            message_principal += f" ({info['run_actuel']}/{info['total_runs']})"

        # 2. Étape détaillée
        etapes_detaillees = {
            "pret": "Cliquez sur 'Lancer le calcul'",
            "preparation": "Initialisation du solveur...",
            "en_cours":"",
            "termine": "" 
        }
        etape_detaillee = etapes_detaillees.get(info["etape"], "")


        # 3. Formatage du temps
        temps_str = ""
        if info["total_runs"] == 1:
            if info["temps_debut"] > 0:
                elapsed = time.time() - info["temps_debut"]
                mins, secs = divmod(elapsed, 60)
                temps_str = f"⏱️ Temps écoulé : {int(mins)}m{int(secs):02d}s"
            else:
                temps_str = ""
        else:
            temps_ecoule_str = ""
            if info["temps_debut"] > 0:
                elapsed = time.time() - info["temps_debut"]
                mins, secs = divmod(elapsed, 60)
                temps_ecoule_str = f"⏱️ Temps écoulé : {int(mins)}m{int(secs):02d}s"

            if info["run_actuel"] == 1 and info["temps_moyen_par_run"] == 0:
                temps_str = f"{temps_ecoule_str} | ⏳ Calcul de l'estimation..."
            elif info["temps_estime_restant"] > 0 and info["temps_moyen_par_run"] > 0:
                mins, secs = divmod(info["temps_estime_restant"], 60)
                if mins >= 60:
                    heures = int(mins // 60)
                    mins_restantes = int(mins % 60)
                    temps_restant_str = f" Reste environ {heures}h{mins_restantes:02d}m"
                else:
                    temps_restant_str = f" Reste environ {int(mins)}m{int(secs):02d}s"
                heure_fin_str = ""
                if info.get("heure_fin_estimee"):
                    heure_fin_str = f" (fin estimé {info['heure_fin_estimee'].strftime('%H:%M')})"
                temps_str = f"{temps_ecoule_str} | {temps_restant_str}{heure_fin_str}"
            else:
                temps_str = f"{temps_ecoule_str} | ⏳ Calcul en cours..."

        # 4. Regroupement des taux
        dernier_taux = ""
        meilleur_taux = ""
        if info["taux_actuel"] > 0:
            dernier_taux = f"Dernier taux calculé : {info['taux_actuel']*100:.1f}%"
        if info["meilleur_taux"] > 0:
            meilleur_taux = f"Meilleur taux calculé pour le moment : {info['meilleur_taux']*100:.1f}%"
        taux_regroupes_text = ""
        if dernier_taux or meilleur_taux:
            if dernier_taux and meilleur_taux:
                taux_regroupes_text = f"{dernier_taux} | {meilleur_taux}"
            else:
                taux_regroupes_text = dernier_taux or meilleur_taux

        # 5. Fin du calcul : affichage spécial
        if info["termine"]:
            if info["temps_debut"] > 0:
                elapsed_total = time.time() - info["temps_debut"]
                mins, secs = divmod(elapsed_total, 60)
                if mins >= 60:
                    heures = int(mins // 60)
                    mins_restantes = int(mins % 60)
                    temps_final = f"✅ Terminé en {heures}h{mins_restantes:02d}m{int(secs):02d}s"
                else:
                    temps_final = f"✅ Terminé en {int(mins)}m{int(secs):02d}s"
            else:
                temps_final = "✅ Calcul terminé"

            # Récupération des résultats
            resultats = {}
            try:
                from solver import fusions_par_run, taux_par_run, meilleur_seed, meilleure_fusion, meilleur_resultats
                resultats = {
                    "fusions_par_run": fusions_par_run,
                    "taux_par_run": taux_par_run,
                    "meilleur_seed": meilleur_seed,
                    "meilleure_fusion": meilleure_fusion,
                    "meilleur_resultats": meilleur_resultats,
                }
                try:
                    from solver import fusion_choisie
                    resultats["fusion_choisie"] = fusion_choisie
                except:
                    pass
            except Exception as e:
                print(f"Impossible de récupérer tous les résultats: {e}")

            # Message principal bien terminé
            return (
                100, temps_final, 
                messages_phases["termine"],    # Affiche "✅ Calcul terminé avec succès !"
                etape_detaillee,
                taux_regroupes_text,
                True, {"display": "block", "textAlign": "center", "marginTop": "20px"},
                100, {"success": True}
            )

        # Retour normal pendant le calcul
        return (
            info["pourcentage"], temps_str, message_principal, etape_detaillee,
            taux_regroupes_text,
            False, {"display": "none"}, info["pourcentage"], dash.no_update
        )

    except ImportError as e:
        print(f"Module solver pas disponible: {e}")
        return (
            10, "Chargement...", "Chargement du solveur", 
            "Importation des modules...", "",
            False, {"display": "none"}, progress_store + 1, dash.no_update
        )

    except Exception as e:
        print(f"Erreur dans progression: {e}")
        import traceback
        traceback.print_exc()
        return (
            progress_store, f"Erreur: {str(e)}", "❌ Erreur durant le calcul", 
            "Voir console pour détails", "",
            True, {"display": "none"}, progress_store, dash.no_update
        )
