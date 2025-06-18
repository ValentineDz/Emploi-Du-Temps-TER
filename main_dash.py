# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
]



app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets)
