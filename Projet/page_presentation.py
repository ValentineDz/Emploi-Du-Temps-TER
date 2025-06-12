"""
Page Dash de présentation du projet TER.

Cette page statique introduit :
- Le contexte académique du projet (Master 1 MIASHS - Informatique et Cognition, UGA) ;
- Les objectifs généraux du générateur d'emploi du temps ;
- La composition de l'équipe projet (étudiants répartis en deux groupes) ;
- Le nom de l'encadrante ;
- Une section de remerciements.

Elle fournit également deux tableaux formatés avec Dash DataTable pour afficher les membres du projet et les encadrants.
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc
from styles import explication_style, style_cell, style_header_table, style_table, style_marge_bas, global_page_style, style_hr

def layout_presentation():
    """
    Génère le layout de la page de présentation du projet TER 2024-2025.

    Cette page statique présente :
    - Le contexte du projet, développé dans le cadre du Master 1 MIASHS, parcours Informatique et Cognition à l'UGA.
    - L'objectif général : proposer un outil de génération automatique d'emploi du temps scolaire adapté aux contraintes spécifiques d'un collège.
    - L'équipe projet, répartie en deux sous-groupes, avec tableau listant nom, prénom, numéro étudiant et adresse email.
    - L'encadrante du projet avec ses coordonnées.
    - Une section de remerciements (contenu libre à ajouter ultérieurement).

    Returns:
        html.Div: Composant Dash contenant l'ensemble de la structure HTML de la page.
    """
    return html.Div(
        children=[
            dbc.Container(
                children=[
                    html.H1("Présentation du projet"),
                    html.Hr(style=style_hr),
                    html.P("Ce projet TER 2024-2025 a été développé dans le cadre du Master 1 MIASHS, "
                        "parcours Informatique et Cognition de l'Université Grenoble Alpes. "
                        "L'objectif est de proposer un outil permettant de générer un emplois du temps "
                        "pour un collège en tenant compte des contraintes spécifiques de l'établissement.", style=explication_style),
                    html.Br(),
                
                    html.H2("Présentation des parties prenantes du projet", style=style_marge_bas),
                    html.H3("Équipe du projet", style=style_marge_bas),
                    html.P("L'équipe d'étudiants du projet se décompose en deux sous groupes. Voici les informations correspondants à chaque personne du groupe : ", 
                        style={'textAlign': 'justify'}),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Groupe", "id": "groupe"},
                            {"name": "Nom", "id": "nom"},
                            {"name": "Prénom", "id": "prenom"},
                            {"name": "Numéro étudiant", "id": "numero"},
                            {"name": "Adresse Email", "id": "email"}
                        ],
                        data=[
                            {"groupe":"1", "nom": "Deschamps", "prenom": "Kylian", "numero":"12020735", "email": "kylian.deschamps@etu.univ-grenoble-alpes.fr"},
                            {"groupe":"1", "nom": "Duez-Faurie", "prenom": "Valentine", "numero":"12107343", "email": "valentine.duez-faurie@etu.univ-grenoble-alpes.fr"},
                            {"groupe":"1", "nom": "Eramil", "prenom": "Kadir", "numero":"12007778", "email": "kadir.eramil@etu.univ-grenoble-alpes.fr "},
                            {"groupe":"2", "nom": "Arbaut", "prenom": "Jean-Baptiste", "numero":"12107693", "email": "jean-baptiste.arbaut@etu.univ-grenoble-alpes.fr"},
                            {"groupe":"2", "nom": "Pilloud", "prenom": "Aubry", "numero":"12415527", "email": "aubry.pilloud@etu.univ-grenoble-alpes.fr"},
                            {"groupe":"2", "nom": "Tropel", "prenom": "Célia", "numero":"12102558", "email": "celia.tropel@etu.univ-grenoble-alpes.fr"}
                        ],
                        style_table=style_table,
                        style_header=style_header_table,
                        style_cell=style_cell
                    ),
                    
                    html.Br(),
                    html.H3("Encadrants", style=style_marge_bas),
                    dash_table.DataTable(
                        columns=[
                            {"name": "Nom", "id": "nom"},
                            {"name": "Prénom", "id": "prenom"},
                            {"name": "Adresse Email", "id": "email"}
                        ],
                        data=[
                            {"nom": "Landry", "prenom": "Aurélie", "email": "aurelie.landry@univ-grenoble-alpes.fr"},
                        ],
                        style_table=style_table,
                        style_header=style_header_table,
                        style_cell=style_cell
                        ),
                
                html.Br(),
                html.Hr(style=style_hr),
                html.H2("Remerciements", style=style_marge_bas),
                html.P("Nous tenons à remercier Mme Landry, maître d'ouvrage du projet, qui a également assuré un rôle de référente tout au long de l'année. Son accompagnement, ses retours réguliers et sa disponibilité ont été essentiels à l'orientation et à l'avancement de notre travail."),
                html.P("Nos remerciements vont également à M. Pellier, pour ses conseils techniques tout au long du premier semestre et au début du second. Il nous a apporté un cadre méthodologique rigoureux et des recommandations précieuses. Plus largement, nous remercions l'ensemble du jury de la soutenance du premier semestre pour leurs retours sur le projet et la présentation." ),
                html.P("Enfin, nous souhaitons remercier M. Laffond, principal d'un collège, pour le temps qu'il nous a consacré afin de nous expliquer en détail les pratiques actuelles de création d'emplois du temps dans son établissement. Il nous a également transmis des jeux de données réels (anonymisés), qui ont été utiles pour évaluer la volumétrie d'informations ainsi que pour nos tests.")
                    
                ],
                style=style_marge_bas
            )
        ], style=global_page_style
    )
