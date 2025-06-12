# http://127.0.0.1:8050/

from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from styles import *
from main_dash import app
app.config.suppress_callback_exceptions = True

from page_accueil import layout_accueil
from page_presentation import layout_presentation
from page_informations import layout_informations 
from page_resultats import layout_resultats
from page_contraintes_optionnelles import layout_contraintes_optionnelles
from page_calculs import layout_calculs
from page_contraintes import layout_contraintes
from styles import style_footer, nav_link_style

from constantes import INITIALISATION_FICHIER
INITIALISATION_FICHIER


# Barre de navigation
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("1. Accueil", href="/accueil", id="nav-accueil", style=nav_link_style)),
        dbc.NavItem(dbc.NavLink("2. Informations", href="/informations", id="nav-informations", style=nav_link_style)),  
        dbc.NavItem(dbc.NavLink("3. Contraintes", href="/contraintes", id="nav-contraintes", style=nav_link_style)), 
        dbc.NavItem(dbc.NavLink("4. Contraintes Optionnelles", href="/contraintes-optionnelles", id="nav-contraintes-optionnelles", style=nav_link_style)), 
        dbc.NavItem(dbc.NavLink("5. Calculs", href="/calculs", id="nav-calculs", style=nav_link_style)),
        dbc.NavItem(dbc.NavLink("6. Résultats", href="/resultats", id="nav-resultats", style=nav_link_style))
    ],
    brand=html.Div([
        html.Img(src="/assets/logo.png", height="40px", style={"marginRight": "10px"}),
        html.Span("TER - EDT", style={"fontWeight": "bold", "fontSize": "1.2rem"})
    ], style={"display": "flex", "alignItems": "center"}),
    brand_href="/accueil",
    color="#A3B18A", 
    dark=False,
    fluid=True
)

# Bas de page (footer)
footer = html.Footer(
    children=[
        html.Hr(),
        html.P("Projet TER 2024-2025 - Université Grenoble Alpes"),
        html.A("Présentation", href="/presentation", style={'textDecoration': 'none', 'color': 'grey', 'flex': '1', 'textAlign': 'left'}),
    ],
    style=style_footer
)

# Layout principal avec flexbox
app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div(id='page-content', style={'flex': '1', 'padding': '20px'}),
        footer
    ],
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '100vh'
    }
)

# Callback pour le routage
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/informations':
        return layout_informations()
    elif pathname == '/contraintes':
        return layout_contraintes()
    elif pathname == '/contraintes-optionnelles':
        return layout_contraintes_optionnelles()
    elif pathname == '/calculs':
        return layout_calculs()
    elif pathname == '/resultats':
        return layout_resultats()
    elif pathname == '/presentation':
        return layout_presentation()
    else:
        return layout_accueil()  # Par défaut, affiche la page d'accueil

# Utilisation en production
server = app.server

if __name__ == '__main__':
    app.run(debug=True)

