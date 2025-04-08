import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# 1. Initialisation de l'application avec thème professionnel et mode sombre
app = Dash(__name__, 
           external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
           meta_tags=[{'name': 'viewport', 
                      'content': 'width=device-width, initial-scale=1.0'}])
app.title = "Analytics Dashboard - Business Intelligence"

# Variable pour le mode sombre
dark_mode = False

# 2. Connexion à la base de données et fonctions CRUD
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ventes_magasin.db')
    return sqlite3.connect(db_path)

def get_data():
    conn = get_db_connection()
    
    query = """
    SELECT v.id, v.date, v.montant, v.quantite,
           p.nom as produit, p.categorie, p.prix_unitaire,
           c.nom as client, c.ville, c.email
    FROM ventes v
    JOIN produits p ON v.produit_id = p.id
    JOIN clients c ON v.client_id = c.id
    """
    
    df = pd.read_sql(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    df['mois'] = df['date'].dt.to_period('M').astype(str)
    df['trimestre'] = df['date'].dt.to_period('Q').astype(str)
    df['jour_semaine'] = df['date'].dt.day_name()
    
    conn.close()
    return df

def get_clients():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM clients", conn)
    conn.close()
    return df

def get_produits():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM produits", conn)
    conn.close()
    return df

def add_client(nom, ville, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (nom, ville, email) VALUES (?, ?, ?)", 
                   (nom, ville, email))
    conn.commit()
    conn.close()

def update_client(client_id, nom, ville, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET nom=?, ville=?, email=? WHERE id=?", 
                   (nom, ville, email, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()

def add_produit(nom, categorie, prix_unitaire):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produits (nom, categorie, prix_unitaire) VALUES (?, ?, ?)", 
                   (nom, categorie, prix_unitaire))
    conn.commit()
    conn.close()

def update_produit(produit_id, nom, categorie, prix_unitaire):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produits SET nom=?, categorie=?, prix_unitaire=? WHERE id=?", 
                   (nom, categorie, prix_unitaire, produit_id))
    conn.commit()
    conn.close()

def delete_produit(produit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produits WHERE id=?", (produit_id,))
    conn.commit()
    conn.close()

# Chargement initial des données
df = get_data()
clients_df = get_clients()
produits_df = get_produits()

# 3. Calcul des KPI
ca_total = df['montant'].sum()
ventes_total = df['quantite'].sum()
clients_uniques = df['client'].nunique()
panier_moyen = ca_total / len(df)

# 4. Layout professionnel avec mode sombre et gestion CRUD
app.layout = dbc.Container(fluid=True, id='main-container', children=[
    # Store pour le mode sombre
    dcc.Store(id='dark-mode-store', data={'dark_mode': False}),
    
    # En-tête avec logo, titre et bouton mode sombre
    dbc.Row([
        dbc.Col(html.Div([
            html.Img(src="assets/logo.png", height=40, className="me-2"),
            html.H1("Tableau de Bord Commercial", className="display-6", id='title'),
            dbc.Button(
                html.I(className="fas fa-moon"),
                id="dark-mode-toggle",
                color="link",
                className="ms-auto"
            )
        ], className="d-flex align-items-center"), width=12)
    ], className="mb-4 py-3 border-bottom", id='header'),
    
    # Cartes KPI
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.Span("CA Total", className="h6")),
            dbc.CardBody([
                html.H4(f"{ca_total:,.2f}€", className="card-title"),
                html.Small("+12% vs période précédente", className="text-success")
            ])
        ], className="shadow-sm kpi-card"), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.Span("Ventes", className="h6")),
            dbc.CardBody([
                html.H4(f"{ventes_total:,}", className="card-title"),
                html.Small("+8% vs période précédente", className="text-success")
            ])
        ], className="shadow-sm kpi-card"), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.Span("Clients", className="h6")),
            dbc.CardBody([
                html.H4(f"{clients_uniques}", className="card-title"),
                html.Small("+5 nouveaux clients", className="text-info")
            ])
        ], className="shadow-sm kpi-card"), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.Span("Panier Moyen", className="h6")),
            dbc.CardBody([
                html.H4(f"{panier_moyen:,.2f}€", className="card-title"),
                html.Small("Stable vs période précédente", className="text-muted")
            ])
        ], className="shadow-sm kpi-card"), md=3)
    ], className="mb-4"),
    
    # Onglets principaux
    dbc.Tabs([
        # Onglet 1: Vue d'ensemble
        dbc.Tab(label="Vue d'Ensemble", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='evolution-ca'), md=8),
                dbc.Col(dcc.Graph(id='repartition-ca'), md=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id='top-produits'), md=6),
                dbc.Col(dcc.Graph(id='top-clients'), md=6)
            ])
        ]),
        
        # Onglet 2: Analyse détaillée
        dbc.Tab(label="Analyse Avancée", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Filtres"),
                        dbc.CardBody([
                            html.Label("Période:"),
                            dcc.DatePickerRange(
                                id='date-range',
                                min_date_allowed=df['date'].min(),
                                max_date_allowed=df['date'].max(),
                                start_date=df['date'].min(),
                                end_date=df['date'].max(),
                                className="mb-3"
                            ),
                            
                            html.Label("Catégories:"),
                            dcc.Dropdown(
                                id='categorie-filter',
                                options=[{'label': cat, 'value': cat} for cat in df['categorie'].unique()],
                                multi=True,
                                placeholder="Toutes catégories"
                            ),
                            
                            html.Label("Villes:", className="mt-3"),
                            dcc.Dropdown(
                                id='ville-filter',
                                options=[{'label': ville, 'value': ville} for ville in df['ville'].unique()],
                                multi=True,
                                placeholder="Toutes villes"
                            )
                        ])
                    ], className="shadow-sm")
                ], md=3),
                
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(dcc.Graph(id='sunburst-chart'), label="Hiérarchie"),
                        dbc.Tab(dcc.Graph(id='heatmap-chart'), label="Heatmap")
                    ])
                ], md=9)
            ])
        ]),
        
        # Onglet 3: Données brutes
        dbc.Tab(label="Données", children=[
            html.Div([
                html.Div([
                    dbc.Button("Exporter CSV", id="btn-export", color="primary", className="me-2"),
                    dcc.Download(id="download-data")
                ], className="mb-3"),
                
                dash_table.DataTable(
                    id='datatable',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    page_size=15,
                    filter_action="native",
                    sort_action="native",
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'whiteSpace': 'normal',
                        'height': 'auto'
                    }
                )
            ], className="p-3")
        ]),
        
        # Nouvel onglet: Gestion des clients
        dbc.Tab(label="Gestion Clients", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Ajouter/Modifier Client"),
                        dbc.CardBody([
                            dbc.Input(id='client-id', type='hidden'),
                            dbc.Input(id='client-nom', placeholder="Nom", className="mb-2"),
                            dbc.Input(id='client-ville', placeholder="Ville", className="mb-2"),
                            dbc.Input(id='client-email', placeholder="Email", type='email', className="mb-3"),
                            dbc.Button("Ajouter", id="btn-add-client", color="primary", className="me-2"),
                            dbc.Button("Modifier", id="btn-update-client", color="warning", className="me-2"),
                            dbc.Button("Annuler", id="btn-cancel-client", color="secondary")
                        ])
                    ], className="shadow-sm mb-4")
                ], md=4),
                
                dbc.Col([
                    dash_table.DataTable(
                        id='clients-table',
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Nom", "id": "nom"},
                            {"name": "Ville", "id": "ville"},
                            {"name": "Email", "id": "email"},
                            {
                                "name": "Actions",
                                "id": "actions",
                                "type": "text",
                                "presentation": "markdown"
                            }
                        ],
                        data=clients_df.to_dict('records'),
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px'
                        },
                        editable=False
                    )
                ], md=8)
            ])
        ]),
        
        # Nouvel onglet: Gestion des produits
        dbc.Tab(label="Gestion Produits", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Ajouter/Modifier Produit"),
                        dbc.CardBody([
                            dbc.Input(id='produit-id', type='hidden'),
                            dbc.Input(id='produit-nom', placeholder="Nom", className="mb-2"),
                            dbc.Input(id='produit-categorie', placeholder="Catégorie", className="mb-2"),
                            dbc.Input(id='produit-prix', placeholder="Prix unitaire", type='number', className="mb-3"),
                            dbc.Button("Ajouter", id="btn-add-produit", color="primary", className="me-2"),
                            dbc.Button("Modifier", id="btn-update-produit", color="warning", className="me-2"),
                            dbc.Button("Annuler", id="btn-cancel-produit", color="secondary")
                        ])
                    ], className="shadow-sm mb-4")
                ], md=4),
                
                dbc.Col([
                    dash_table.DataTable(
                        id='produits-table',
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Nom", "id": "nom"},
                            {"name": "Catégorie", "id": "categorie"},
                            {"name": "Prix unitaire", "id": "prix_unitaire"},
                            {
                                "name": "Actions",
                                "id": "actions",
                                "type": "text",
                                "presentation": "markdown"
                            }
                        ],
                        data=produits_df.to_dict('records'),
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px'
                        },
                        editable=False
                    )
                ], md=8)
            ])
        ])
    ]),
    
    # Pied de page
    dbc.Row([
        dbc.Col(html.Div([
            html.Hr(),
            html.P("Dernière mise à jour: " + datetime.now().strftime("%d/%m/%Y %H:%M"), 
                  className="text-muted small")
        ]), width=12)
    ], className="mt-4")
])

# 5. Callbacks pour l'interactivité
# Callback pour les graphiques principaux (inchangé)
@callback(
    [Output('evolution-ca', 'figure'),
     Output('repartition-ca', 'figure'),
     Output('top-produits', 'figure'),
     Output('top-clients', 'figure'),
     Output('sunburst-chart', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('datatable', 'data')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('categorie-filter', 'value'),
     Input('ville-filter', 'value')]
)
def update_all(start_date, end_date, categories, villes):
    filtered_df = df.copy()
    
    # Filtrage par date
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['date'] >= start_date) & 
            (filtered_df['date'] <= end_date)
        ]
    
    # Filtrage par catégorie
    if categories:
        filtered_df = filtered_df[filtered_df['categorie'].isin(categories)]
    
    # Filtrage par ville
    if villes:
        filtered_df = filtered_df[filtered_df['ville'].isin(villes)]
    
    # Graphique 1: Évolution du CA
    fig1 = px.line(
        filtered_df.groupby('mois')['montant'].sum().reset_index(),
        x='mois',
        y='montant',
        title="Évolution du Chiffre d'Affaires",
        labels={'mois': 'Mois', 'montant': 'CA (€)'}
    )
    fig1.update_layout(hovermode="x unified")
    
    # Graphique 2: Répartition du CA
    fig2 = px.pie(
        filtered_df.groupby('categorie')['montant'].sum().reset_index(),
        names='categorie',
        values='montant',
        title="Répartition par Catégorie",
        hole=0.4
    )
    
    # Graphique 3: Top produits
    fig3 = px.bar(
        filtered_df.groupby('produit')['montant'].sum().nlargest(10).reset_index(),
        x='produit',
        y='montant',
        title="Top 10 Produits",
        color='produit'
    )
    
    # Graphique 4: Top clients
    fig4 = px.bar(
        filtered_df.groupby('client')['montant'].sum().nlargest(10).reset_index(),
        x='client',
        y='montant',
        title="Top 10 Clients",
        color='client'
    )
    
    # Graphique 5: Sunburst
    fig5 = px.sunburst(
        filtered_df,
        path=['categorie', 'produit'],
        values='montant',
        title="Analyse Hiérarchique"
    )
    
    # Graphique 6: Heatmap
    heatmap_data = filtered_df.pivot_table(
        index='jour_semaine',
        columns=filtered_df['date'].dt.hour,
        values='montant',
        aggfunc='sum'
    )
    fig6 = go.Figure(go.Heatmap(
        x=heatmap_data.columns,
        y=heatmap_data.index,
        z=heatmap_data.values,
        colorscale='Viridis'
    ))
    fig6.update_layout(title="Heatmap des Ventes par Jour/Heure")
    
    return fig1, fig2, fig3, fig4, fig5, fig6, filtered_df.to_dict('records')

# Callback pour l'export CSV
@callback(
    Output("download-data", "data"),
    Input("btn-export", "n_clicks"),
    prevent_initial_call=True
)
def export_data(n_clicks):
    return dcc.send_data_frame(df.to_csv, "export_ventes.csv")

# Callbacks pour la gestion des clients
@callback(
    [Output('clients-table', 'data'),
     Output('client-id', 'value'),
     Output('client-nom', 'value'),
     Output('client-ville', 'value'),
     Output('client-email', 'value')],
    [Input('btn-add-client', 'n_clicks'),
     Input('btn-update-client', 'n_clicks'),
     Input('btn-cancel-client', 'n_clicks'),
     Input('clients-table', 'active_cell')],
    [State('client-id', 'value'),
     State('client-nom', 'value'),
     State('client-ville', 'value'),
     State('client-email', 'value')]
)
def manage_clients(add_click, update_click, cancel_click, active_cell, 
                  client_id, nom, ville, email):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'btn-add-client' and add_click:
        if nom and ville and email:
            add_client(nom, ville, email)
            return get_clients().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'btn-update-client' and update_click:
        if client_id and nom and ville and email:
            update_client(client_id, nom, ville, email)
            return get_clients().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'btn-cancel-client' and cancel_click:
        return get_clients().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'clients-table' and active_cell:
        row = active_cell['row']
        clients_data = get_clients().to_dict('records')
        client = clients_data[row]
        return dash.no_update, client['id'], client['nom'], client['ville'], client['email']
    
    return get_clients().to_dict('records'), dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callbacks pour la gestion des produits
@callback(
    [Output('produits-table', 'data'),
     Output('produit-id', 'value'),
     Output('produit-nom', 'value'),
     Output('produit-categorie', 'value'),
     Output('produit-prix', 'value')],
    [Input('btn-add-produit', 'n_clicks'),
     Input('btn-update-produit', 'n_clicks'),
     Input('btn-cancel-produit', 'n_clicks'),
     Input('produits-table', 'active_cell')],
    [State('produit-id', 'value'),
     State('produit-nom', 'value'),
     State('produit-categorie', 'value'),
     State('produit-prix', 'value')]
)
def manage_produits(add_click, update_click, cancel_click, active_cell, 
                   produit_id, nom, categorie, prix):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'btn-add-produit' and add_click:
        if nom and categorie and prix:
            add_produit(nom, categorie, float(prix))
            return get_produits().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'btn-update-produit' and update_click:
        if produit_id and nom and categorie and prix:
            update_produit(produit_id, nom, categorie, float(prix))
            return get_produits().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'btn-cancel-produit' and cancel_click:
        return get_produits().to_dict('records'), '', '', '', ''
    
    elif triggered_id == 'produits-table' and active_cell:
        row = active_cell['row']
        produits_data = get_produits().to_dict('records')
        produit = produits_data[row]
        return dash.no_update, produit['id'], produit['nom'], produit['categorie'], produit['prix_unitaire']
    
    return get_produits().to_dict('records'), dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback pour le mode sombre
@app.callback(
    [Output('main-container', 'className'),
     Output('dark-mode-store', 'data'),
     Output('dark-mode-toggle', 'children'),
     Output('title', 'style')],
    [Input('dark-mode-toggle', 'n_clicks')],
    [State('dark-mode-store', 'data')]
)
def toggle_dark_mode(n_clicks, data):
    if n_clicks:
        dark_mode = not data['dark_mode']
        data['dark_mode'] = dark_mode
        
        if dark_mode:
            return (
                'bg-dark text-white', 
                data,
                html.I(className="fas fa-sun"),
                {'color': 'white'}
            )
        else:
            return (
                '', 
                data,
                html.I(className="fas fa-moon"),
                {'color': 'inherit'}
            )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# 6. Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True, port=8050)