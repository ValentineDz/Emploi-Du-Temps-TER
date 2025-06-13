"""
Fichier centralisant tous les styles CSS utilisés dans l'application Dash.

Contient des dictionnaires Python définissant les propriétés CSS pour :
- Les composants visuels (boutons, cartes, tableaux, dropdowns, etc.) ;
- Les textes explicatifs, titres et mises en page ;
- La structuration globale des pages (marges, alignements, flex, containers) ;
- Les composants spécifiques comme :
    * les messages de validation / erreur,
    * les sections repliables,
    * les boutons de disponibilité ou d'importation,
    * les tableaux d'ordonnancement ou de contraintes.
"""

# Styles pour les liens de la navbar
nav_link_style = {
    'color': 'rgba(0, 0, 0, 0.6)', 
    'padding': '10px',
    'textDecoration': 'none'
}

active_nav_link_style = {
    'color': 'white',
    'fontWeight': 'bold',
    'padding': '10px',
    'textDecoration': 'none'
}

# Styles généraux
texte_style = {
    'textAlign': 'justify',
    'margin': '20px'
}

title_style = {
    'textAlign': 'center',
    'marginTop': '5px',
    'fontSize': '16px',
    'fontWeight': 'bold'
}

value_style = {
    'textAlign': 'center',
    'fontSize': '20px',
    'fontWeight': 'bold'
}

# Styles des composants Dash
graph_style = {
    'border': '1px solid #DDD',
    'borderRadius': '5px',
    'padding': '2px',
    'margin': '5px'
}

dropdown_style = {
    'width': '95%',
    'max-width': '500px',  
    'margin': '10px auto',
    'white-space': 'normal',
    'line-height': '0.7',  
    'font-size': '12px'
}

sidebar_style = {
    'backgroundColor': "#f8f9fa",
    'padding': '20px',
    'border': '2px solid #dee2e6',
    'margin': '20px'
}

selector_title_style = {
    'marginTop': '10px',
    'marginBottom': '5px'
}

card_style = {
    'border': '1px solid #DDD',
    'borderRadius': '8px',
    'margin': '2px',
    'marginBottom': '12px',
    'boxShadow': '2px 2px 10px #ccc'
}

# Styles des tableaux
style_data = {
    'whiteSpace': 'normal',
    'textAlign': 'center',
    'height': '12px'
}

style_header = {
    'backgroundColor': 'rgb(230, 230, 230)',
    'fontWeight': 'bold',
    'textAlign': 'center'
}


# Style pour les textes explicatifs
explication_style = {
    'fontStyle': 'italic',
    'color': '#444',
    "textAlign": "justify"
}

style_liste_choix = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'gap': '50px',
    'marginLeft': '20px'
}

# Style global de mise en page
global_page_style = {
    "marginLeft": "80px",
    "marginRight": "80px",
    "marginTop": "20px",
    "marginBottom": "40px"
}

style_format_donnes_info = {
    "backgroundColor": "#f8f9fa",
    "border": "1px solid #ccc",
    "borderRadius": "6px",
    "padding": "15px",
    "marginBottom": "15px"
}

style_zone_import = { 
    "height": "60px",
    "lineHeight": "60px",
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "borderRadius": "5px",
    "textAlign": "center",
    "marginBottom": "15px"

}

style_table_import = {
    "marginBottom": "15px",
    "borderRadius": "6px",
}

style_btn_ajouter = {
    "padding": "4px 10px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}

style_btn_supprimer = {
    "backgroundColor": "#dc3545",
    "border": "none",
    "color": "white",
    "padding": "6px 12px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}

style_btn_suivant = {
    "color": "white",
    "padding": "8px 18px",
    "borderRadius": "6px",
    "fontSize": "16px",
    "cursor": "pointer",
    "marginTop": "30px",
    "marginBottom": "20px",
    "float": "right",
    "marginRight": "60px",
    "marginLeft": "60px"
}

style_btn_telecharger = {
    "color": "white",
    "padding": "6px 14px",
    "borderRadius": "6px",
    "cursor": "pointer"
}

style_message_import_supression = {
    "marginbottom": "30px",
    "marginTop": "20px",
    "marginLeft": "20px", 
    "color": "green", 
    "fontWeight": "bold"
    }

style_sections={
    "border": "1px solid #ddd", 
    "borderRadius": "6px", 
    "marginBottom": "8px"
    }

style_générateurs={
    "border": "1px solid #ccc",
    "borderRadius": "6px",
    "padding": "15px",
    "marginBottom": "25px",
    "backgroundColor": "#f9f9f9"
}

style_saisie_ressources = {
    "width": "90%",
    "marginLeft": "auto",
    "marginRight": "auto"
}

style_btn_import = {
    "padding": "6px 12px", 
    "border": "none",
    "textAlign": "center",
    "borderRadius": "6px",
    "backgroundColor": "#007bff",
    "cursor": "pointer",
    "display": "inline-block",
    "verticalAlign": "middle"
}

style_accordeons={
    "border": "1px solid #ddd", 
    "borderRadius": "6px", 
    "marginBottom": "8px"
 }

style_accordeons_contenus = {
    "width": "90%",
    "marginLeft": "auto",
    "marginRight": "auto"
}


style_dropdown_niveau={
    "width": "300px", 
    "marginBottom": "20px"
}

style_table={
    "width": "80%", 
    "marginLeft": "40px", 
    "overflowX": "auto"
}

style_header_table={
    'backgroundColor': '#f4f4f4', 
    'fontWeight': 'bold', 
    'textAlign': 'center', 
    "whiteSpace": "normal", 
    "height": "auto"
}

style_tooltip={
    "marginTop": "10px", 
    "display": "flex", 
    "alignItems": "center"
}

style_tooltip_info={
    "cursor": "pointer",
    "color": "#555",
    "fontSize": "1.2rem",
    "marginLeft": "8px"
}

style_input_hh_min = {
    "width": "80px", 
    "marginLeft": "20px", 
    "marginRight": "10px"
}

style_bouton_gauche = {
    "textAlign": "left",
    "marginTop": "30px",
    "marginLeft": "20px"
}

style_bouton_droite = {
    "textAlign": "right",
    "marginTop": "30px",
    "marginRight": "20px"
}

style_bloc_chargement = {
    "display": "none"
}

style_progress_bar = {
    "height": "30px",
    "marginTop": "20px"
}

style_tooltip_general = {
    "fontSize": "0.9rem"
}

style_spinner = {
    "width": "4rem", 
    "height": "4rem"
}
style_temps_estime = {
    "textAlign": "center", 
    "fontWeight": "bold", 
    "fontSize": "18px", 
    "marginTop": "10px"
}

style_poids_max = {
    "display": "flex",
    "alignItems": "center",
    "gap": "10px",
    "marginTop": "25px"
}

style_boutons_bas = {
    "display": "flex", 
    "justifyContent": "space-between"
}

style_footer = {
    'position': 'relative',
    'width': '100%',
    'padding': '10px',
    'textAlign': 'center'
}

style_tbl_horaires = {
    "display": "flex", 
    "alignItems": "center", 
    "marginBottom": "10px", 
    "gap": "20px"
}

style_input= {
    "display": "flex", 
    "alignItems": "center", 
    "gap": "5px",
    "marginBottom": "15px"
}

style_alinea = {
    "marginLeft": "40px", 
    "marginTop": "10px"
}

style_marge_droite = {
    "marginRight": "15px"
}

style_marge_gauche = {
    "marginLeft": "15px"
}

style_marge_haut = {
    "marginTop": "15px"
}

style_marge_bas = {
    "marginBottom": "20px"
}

style_labels_horaires = {
    "width": "50%", 
    "fontWeight": "bold"
}

style_date = {
    "width": "160px", 
    "marginTop": "8px", 
    "margin-left": "10px"
}

style_div_dates = {
    "display": "flex", 
    "alignItems": "center", 
    "marginTop": "5px"
}

style_input_refectoire_langues = {
    "width": "80px", 
    "marginRight": "6px", 
    "marginLeft": "6px"
}

style_non_visible = {
    "display": "none"
}

style_visible = {
    "display": "block"
}

style_cell = {
    "textAlign": "center",
    "padding": "10px"
}

style_gras = {
    "fontWeight": "bold"
}

style_message_import = {
    "margin": "10px auto", 
    "width": "90%", 
    "textAlign": "left"
}

style_btn_générer = {
    "padding": "4px 10px",
    "borderRadius": "6px",
    "marginLeft": "40px",
    "marginBottom": "15px",
    "cursor": "pointer"
}

style_générateurs_items = {
    "display": "flex", 
    "flexWrap": "wrap", 
    "gap": "5px"
}

style_erreur={
    "color": "red", 
    "marginTop": "8px"
}

style_boutons_bas_page = {
    "display": "flex", 
    "justifyContent": "space-between", 
    "marginTop": "30px"
}

style_input_autre = {
    "width": "300px"
}

style_autre_div = {
    "display": "flex", 
    "alignItems": "center", 
    "gap": "8px", 
    "marginBottom": "8px"
}

style_erreur_import = {
    "color": "red", 
    "margin": "10px auto", 
    "width": "90%", 
    "textAlign": "left"
}

style_import_correct = {
    "color": "green", 
    "margin": "10px auto", 
    "width": "90%", 
    "textAlign": "left"
}

style_bouton_import_reinit = {
    "display": "flex",
    "alignItems": "center",
    "gap": "12px"
}

style_cell_ordo = [
                {'if': {'column_id': 'Rang'}, 'textAlign': 'center'},
                {'if': {'column_id': 'Contrainte'}, 'textAlign': 'left'}
            ]

style_table_ordo = {
    "marginBottom": "15px",
    "border": "1px solid #dee2e6",
    "borderRadius": "0.5rem",
    "overflow": "hidden"
}

style_ordo = {
    "width": "50%",
    "margin": "auto",
    "padding": "20px",
    "border": "1px solid #dee2e6",
    "borderRadius": "0.75rem",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.05)"
}

style_centrer = {
    "textAlign": "center",
    "marginBottom": "30px",
    "marginTop": "10px"
}


style_btn_apply = {
    'marginTop': '15px',
    'width': '100%'
}
style_btn_dispnobible = {
    "backgroundColor": "#008000",
    "border": "none",
    "color": "white",
    "padding": "6px 12px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}
style_btn_indisponible = {
    "backgroundColor": "#ff7f00",
    "border": "none",
    "color": "white",
    "padding": "6px 12px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}
style_btn_totale = {
    "backgroundColor": "#dc3545",
    "border": "none",
    "color": "white",
    "padding": "6px 12px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}
style_btn_reset = {
    "backgroundColor": "#dc3545",
    "border": "none",
    "color": "white",
    "padding": "6px 12px",
    "borderRadius": "6px",
    "cursor": "pointer",
    "marginBottom": "10px",
    "marginTop": "10px"
}
style_collapse_button = {
    'marginBottom': '0.5rem',
    'width': '100%',
    'fontSize': '1.2rem',
    'fontWeight': 'bold'
}

style_flex_space_between = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'width': '100%'
}
style_content_left = {
    'width': '70%'
}
style_apply_panel = {
    'width': '28%',
    'padding': '15px',
    'border': '1px solid #ddd',
    'borderRadius': '4px',
    'backgroundColor': '#fafafa'
}

style_table_container = {
    'overflowX': 'auto',
    'width': '100%',
    'border': '1px solid #ddd'
}
style_cell_small = {
    'textAlign': 'center',
    'padding': '8px'
}

style_main_title = {
    'margin': '2rem 0',
    'textAlign': 'center',
    'fontSize': '2.5rem'
}
style_recap_title = {
    'textAlign': 'center',
    'marginBottom': '30px'
}
style_message = {
    'margin': '10px 0',
    'fontWeight': 'bold',
    'textAlign': 'center'
}

style_dropdown_center = {
    'width': '80%',
    'margin': 'auto'
}
style_label_margin_top = {
    'marginTop': '10px'
}

style_col_23 = {'width': '23%'}
style_col_19 = {'width': '19%'}
style_col_24 = {'width': '24%'}

style_dropdown_cours = {'width': '25%'}
style_dropdown_qui = {'width': '17%'}
style_dropdown_type = {'width': '17%'}
style_dropdown_minimum = {'width': '13%'}

style_hr = {
        "height": "4px",
        "backgroundColor": "#A3B18A", 
}

style_btn_commencer = {
    "fontSize": "1.2rem",
    "color": "#000000", 
    "border": "1px solid #ccc",
    "padding": "0.4rem 1rem",
    "borderRadius": "6px",
    "textDecoration": "none",
    "fontWeight": "500",
    "display": "inline-flex",
    "alignItems": "center",
    "transition": "all 0.2s ease"
}


style_illustration ={
    "height": "450px",
    "marginLeft": "40px",
    "borderRadius": "10px"
}

style_bloc_page_accueil= {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "flexWrap": "wrap",
    "marginBottom": "40px"
}

titre_accordion_h4 = {
    "fontSize": "1.5rem",

    "margin": "8px 0"
}

style_conditionnel_stats = [
    {
        'if': {'filter_query': '{taux} != "100.0%" && {taux} != "-"', 'column_id': 'taux'},
        'backgroundColor': '#f8d7da',
        'color': 'black'
    },
    {
        'if': {'filter_query': '{taux} = "100.0%"', 'column_id': 'taux'},
        'backgroundColor': '#d4edda',
        'color': 'black'
    }, 
    {
        'if': {
            'filter_query': '{statut} = "Obligatoire"',
            'column_id': 'statut'
        },
        'fontWeight': 'bold'
    }
]

style_summary_violations = {
    "fontWeight": "bold", 
    "cursor": "pointer"
}

style_cartes = {
    "height": "100%"
}


cours_style = {
    "fontSize": "10px",
    "lineHeight": "1.2",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    "whiteSpace": "normal",
    "wordBreak": "break-word",
    "textAlign": "center",
    "padding": "4px"
}

sous_style = "font-size:7.5px;color:#666;"
HEURE_HEIGHT = "70px"
SPLIT_BORDER = "1px dashed #999"
HORAIRE_BORDER = "1px solid #dee2e6"
MIDI_BG = "#f7f7f7"

# Styles pour generate_cell_content
cell_plein_style = {
    **cours_style,
    "height": HEURE_HEIGHT,
    "backgroundColor": "#d4edda",
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center"
}

cell_plein_source_style = {
    **cours_style,
    "height": HEURE_HEIGHT,
    "backgroundColor": "#ffcccc",
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center"
}

cell_demi_container_style = {
    "display": "flex",
    "height": HEURE_HEIGHT,
    "backgroundColor": "#ffffff"
}

cell_demi_container_selected_style = {
    "display": "flex",
    "height": HEURE_HEIGHT,
    "backgroundColor": "#ffcccc"
}

cell_demi_a_style = {
    "flex": 1,
    "paddingRight": "2px",
    "borderRight": SPLIT_BORDER,
    "height": HEURE_HEIGHT
}

cell_demi_b_style = {
    "flex": 1,
    "paddingLeft": "2px",
    "height": HEURE_HEIGHT
}

label_a_style = {
    "fontWeight": "bold",
    "color": "#0066cc",
    "fontSize": "8px",
    "marginBottom": "2px"
}

label_b_style = {
    "fontWeight": "bold",
    "color": "#cc6600",
    "fontSize": "8px",
    "marginBottom": "2px"
}

markdown_demi_style = {
    **cours_style,
    "fontSize": "9px"
}

# Styles pour build_split_table
header_style = {
    "backgroundColor": "#343a40",
    "color": "white",
    "padding": "10px",
    "fontWeight": "bold"
}

heure_cell_style = {
    "fontWeight": "bold",
    "backgroundColor": "#f8f9fa",
    "textAlign": "center",
    "padding": "10px",
    "border": HORAIRE_BORDER
}

cours_cell_style = {
    "border": "1px solid #dee2e6",
    "padding": "0",
    "verticalAlign": "top",
    "height": HEURE_HEIGHT,
    "background": "#fff",
    "cursor": "default"
}

cours_cell_plein_style = {
    "border": "2px solid #28a745",
    "padding": "0",
    "verticalAlign": "top",
    "height": HEURE_HEIGHT,
    "background": "#fff",
    "cursor": "pointer"
}

cours_cell_source_style = {
    "border": "3px solid #dc3545",
    "padding": "0",
    "verticalAlign": "top",
    "height": HEURE_HEIGHT,
    "background": "#fff",
    "cursor": "pointer"
}

cours_cell_midi_style = {
    "border": "1px solid #dee2e6",
    "padding": "0",
    "verticalAlign": "top",
    "height": HEURE_HEIGHT,
    "background": MIDI_BG,
    "cursor": "default"
}

table_style = {
    "tableLayout": "fixed",
    "width": "100%",
    "borderCollapse": "collapse",
    "margin": "20px auto",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "fontFamily": "sans-serif"
}

# Styles pour layout_resultats
h2_style = {
    "marginTop": "20px",
    "marginBottom": "20px",
    "textAlign": "center"
}

selectors_container_style = {
    "textAlign": "center",
    "marginBottom": "20px"
}

vue_dropdown_style = {
    "width": "220px",
    "display": "inline-block",
    "marginRight": "18px"
}

entite_dropdown_style = {
    "width": "320px",
    "display": "inline-block"
}

radio_items_style = {
    "display": "inline-block",
    "verticalAlign": "middle",
    "marginLeft": "40px"
}

radio_container_style = {
    "marginLeft": "25px"
}

download_button_container_style = {
    "textAlign": "right"
}

main_container_style = {
    "display": "flex",
    "maxWidth": "1400px",
    "margin": "0 auto",
    "padding": "20px"
}

sidepanel_style = {
    "flex": "0 0 400px",
    "marginRight": "20px",
    "backgroundColor": "#f8f9fa",
    "border": "1px solid #dee2e6",
    "borderRadius": "8px",
    "padding": "20px"
}

table_title_style = {
    "textAlign": "center",
    "marginBottom": "20px",
    "padding": "15px",
    "backgroundColor": "#e9ecef",
    "borderRadius": "8px"
}

alert_area_style = {
    "margin": "20px"
}

# Styles pour build_preview_table
preview_header_style = {
    "backgroundColor": "#343a40",
    "color": "white",
    "fontSize": "10px",
    "padding": "2px"
}

preview_heure_cell_style = {
    "fontSize": "9px",
    "backgroundColor": "#f8f9fa",
    "padding": "2px"
}

preview_cours_cell_style = {
    "fontSize": "8px",
    "padding": "1px",
    "border": "1px solid #eee",
    "backgroundColor": "#fff",
    "minWidth": "40px"
}

preview_cours_cell_plein_style = {
    "fontSize": "8px",
    "padding": "1px",
    "border": "1px solid #eee",
    "backgroundColor": "#d4edda",
    "minWidth": "40px"
}

preview_table_style = {
    "width": "100%",
    "fontSize": "8px",
    "borderCollapse": "collapse",
    "margin": "0"
}

preview_markdown_plein_style = {
    "fontSize": "8px"
}

preview_markdown_demi_style = {
    "fontSize": "7px"
}

preview_demi_container_style = {
    "display": "flex"
}

preview_demi_a_style = {
    "borderRight": "1px dashed #999",
    "flex": 1
}

preview_demi_b_style = {
    "flex": 1
}

# Styles pour build_export_panel
export_h5_style = {
    "marginBottom": "15px",
    "color": "#495057"
}


# Styles pour update_sidepanel
edit_h4_style = {
    "color": "#495057",
    "marginBottom": "15px"
}

edit_p_style = {
    "fontWeight": "bold",
    "marginBottom": "5px"
}

edit_no_selection_style = {
    "padding": "20px",
    "textAlign": "center",
    "color": "#999",
    "border": "2px dashed #ddd",
    "borderRadius": "8px"
}

edit_message_style = {
    "fontStyle": "italic",
    "color": "#6c757d",
    "marginBottom": "20px"
}

edit_buttons_container_style = {
    "marginTop": "20px",
    "textAlign": "center"
}

move_h6_style = {
    "color": "#28a745",
    "marginBottom": "10px"
}

move_p_style = {
    "fontWeight": "bold"
}

move_message_style = {
    "fontStyle": "italic",
    "color": "#666",
    "marginTop": "10px"
}

move_selection_style = {
    "padding": "15px",
    "border": "2px solid #28a745",
    "borderRadius": "8px",
    "backgroundColor": "#d4edda"
}

move_no_options_style = {
    "padding": "20px",
    "textAlign": "center",
    "color": "#999"
}

move_h5_style = {
    "marginBottom": "15px",
    "color": "#495057"
}

move_checklist_style = {
    "display": "block",
    "marginBottom": "12px"
}

move_checklist_input_style = {
    "marginRight": "8px"
}

move_buttons_container_style = {
    "marginTop": "20px",
    "textAlign": "center"
}

view_h4_style = {
    "color": "#495057",
    "marginBottom": "15px"
}

view_message_style = {
    "fontStyle": "italic",
    "color": "#6c757d",
    "marginBottom": "20px"
}

view_no_selection_style = {
    "padding": "20px",
    "textAlign": "center",
    "color": "#999",
    "border": "2px dashed #ddd",
    "borderRadius": "8px"
}

# Styles pour hide_sidepanel
sidepanel_hidden_style = {
    "width": "0",
    "minWidth": "0",
    "maxWidth": "0",
    "overflow": "hidden",
    "padding": "0",
    "marginRight": "0",
    "display": "none"
}

sidepanel_visible_style = {
    "width": "300px",
    "minWidth": "300px",
    "maxWidth": "300px",
    "marginRight": "10px"
}

# Style pour build_option_preview_dash
preview_container_style = {
    "border": "1px solid #bbb",
    "margin": "5px 0",
    "minWidth": "250px",
    "minHeight": "150px",
    "maxWidth": "250px",
    "maxHeight": "150px", 
    "overflow": "auto",
    "display": "block",
}


export_checklist_style = {
    "marginBottom": "15px"
}

style_telecharger_accueil = {
    "textAlign": "center", 
    "fontWeight": "bold"
}