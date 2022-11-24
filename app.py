# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math
import base64
import requests
import re
import pandas as pd
#import arrow
import io
#from flask import Flask
from flask import Flask, request, render_template,url_for,redirect
import dash
from dash.dependencies import Input, Output, State
#import dash_table as dt
from dash import dash_table as dt
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
import dash_bio as dashbio
#import dash_bootstrap_components as dbc
from dash import html,dcc
import plotly.express as px
# my imports
from pymongo import MongoClient
import dash_cytoscape as cyto
import networkx as nx
import json
import collections
import numpy as np
from functools import reduce
from dash.exceptions import PreventUpdate
from skimage.io import imread

# Multi-dropdown options
#from controls import CATEGORIES, REGIONS, METRICS


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.ppi

server = Flask(__name__)

@server.route('/')
def index():
    return render_template('index.html')

# route to get data from html form and insert data into database
@server.route('/feedback', methods=["GET", "POST"])
def form_entry():
    data = {}
    if request.method == "POST":
        data['Name'] = request.form['name']
        data['Surname'] = request.form['surname']
        data['Institute'] = request.form['insti']
        data['Country'] = request.form['country']
        data['Email'] = request.form['email']
        data['Role'] = request.form['role']
        data['Message'] = request.form['message']
        data['Msg_type'] = request.form['msgtype']
        #data['Date_Time'] = arrow.now("Asia/Calcutta").format()
       
        db.feedback.insert_one(data)

    return render_template("index.html")




@server.route('/blog.html')
def blog():
    return render_template('blog.html')



font_awesome = 'https://use.fontawesome.com/releases/v5.10.2/css/all.css'
code_pen = 'https://codepen.io/chriddyp/pen/bWLwgP.css'

external_stylesheets = [code_pen,font_awesome]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server,routes_pathname_prefix='/konnect2prot/')
app.title = "k2p"
app.config.suppress_callback_exceptions = True

colors = [['red','tee'], ['blue','triangle'], ['grey','none']]

#app = dash.Dash(__name__)
#app.config.suppress_callback_exceptions = True
#server = app.server

cyto.load_extra_layouts()

# Create controls
'''
category_options = [{'label': str(category),
                     'value': str(category)}
                    for category in CATEGORIES]

region_options = [{'label': str(region),
                   'value': str(region)}
                  for region in REGIONS]

country_options = [{'label': str(country),
                    'value': str(country)}
                   for country in REGIONS['All']]

metric_options = [{'label': str(metric),
                   'value': str(metric)}
                  for metric in METRICS]
'''

# Load data
#df = pd.read_csv('data/all_companies.csv')
#dataset = df.to_dict(orient='index')
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.ppi_test
colors = [['red','tee'], ['blue','triangle'], ['grey','none']]
#TABLE_COLUMNS=['Name','Degree','InDegree','OutDegree','Betweenness','Clustering','Closeness','Katz']
TABLE_COLUMNS=['Name','Degree','InDegree','OutDegree','Betweenness','Clustering','Closeness']
result_columns = ['Name', 'InDegree','OutDegree', 'Betweenness', 'Clustering', 'Closeness',
                  'Protein Class', 'Location', 'Activates', 'Deactivates', 'Activated',
                  'Deactivated']# not in use
result_columns=['Name', 'Degree', 'InDegree', 'OutDegree', 'Betweenness', 'Clustering',
       'Closeness','Katz' ,'Protein Class', 'Location', 'Inhibitors',
       'PDB complex(Count)']# Not in use
result_columns=['Name', 'Degree', 'InDegree', 'OutDegree', 'Betweenness', 'Clustering',
       'Closeness' ,'Protein Class', 'Location', 'Inhibitors',
       'PDB complex(Count)']

#################function starts#############################
def gen_hallmark():
    
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    nodes = [
        {
            'data': {'id': short, 'label': label},
            'position': {'x': 20*lat, 'y': -20*long}
        }
        for short, label, long, lat in (
            ('la', 'PPI', 34.03, -118.25),
            ('nyc', 'Pathways', 40.71, -74),
            ('to', 'Processes', 43.65, -79.38),
            ('mtl', 'Function', 45.50, -73.57),
            ('van', 'Disease', 49.28, -123.12),
            ('chi', 'Ligand', 41.88, -87.63),
            ('bos', 'Localization', 42.36, -71.06),
            ('hou', 'Mutation', 29.76, -95.37)
        )
    ]

    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in (
            ('van', 'la'),
            ('la', 'chi'),
            ('hou', 'chi'),
            ('to', 'mtl'),
            ('mtl', 'bos'),
            ('nyc', 'bos'),
            ('to', 'hou'),
            ('to', 'nyc'),
            ('la', 'nyc'),
            ('nyc', 'bos')
        )
    ]

    element = nodes + edges
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data end^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^styling start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    default_stylesheet = [
        {
            "selector": 'node',
            'style': {
                "opacity": 1,
                'height': 15,
                'width': 15,
                'background-color': '#222222',
                "label": "data(label)"
            }
        },
        {
        'selector': '.search',
        'style': {
            'background-color': 'red'
        }
    },
        {
            "selector": 'edge',
            'style': {
                'target-arrow-color': 'black',
                #"target-arrow-shape": "triangle-tee",
                "curve-style": "bezier",
                "opacity": 0.9,
                'width': 2
            }
        },

        *[{
            "selector": '.' + color,
            'style': {'line-color': color,"target-arrow-shape":arrow}
        } for color,arrow in colors]
    ]
    return    cyto.Cytoscape(
            id='hallmark_network',
            stylesheet=default_stylesheet,
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '500px'},
            elements=element
        )


################################################################
def gen_signa():
    
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    nodes = [
        {
            'data': {'id': short, 'label': label},
            'position': {'x': 20*lat, 'y': -20*long}
        }
        for short, label, long, lat in (
            ('la', 'PPI', 34.03, -118.25),
            ('nyc', 'Pathways', 40.71, -74),
            ('to', 'Processes', 43.65, -79.38),
            ('mtl', 'Function', 45.50, -73.57),
            ('van', 'Disease', 49.28, -123.12),
            ('chi', 'Ligand', 41.88, -87.63),
            ('bos', 'Localization', 42.36, -71.06),
            ('hou', 'Mutation', 29.76, -95.37)
        )
    ]

    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in (
            ('van', 'la'),
            ('la', 'chi'),
            ('hou', 'chi'),
            ('to', 'mtl'),
            ('mtl', 'bos'),
            ('nyc', 'bos'),
            ('to', 'hou'),
            ('to', 'nyc'),
            ('la', 'nyc'),
            ('nyc', 'bos')
        )
    ]

    element = nodes + edges
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data end^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^styling start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    default_stylesheet = [
        {
            "selector": 'node',
            'style': {
                "opacity": 1,
                'height': "data(size)",
                'width': "data(size)",
                'background-color': '#222222',
                "label": "data(label)"
            }
        },
        {
        'selector': '.search',
        'style': {
            'background-color': 'red'
        }
    },
        {
            "selector": 'edge',
            'style': {
                'target-arrow-color': 'black',
                #"target-arrow-shape": "triangle-tee",
                "curve-style": "bezier",
                "opacity": 0.9,
                'width': 2
            }
        },

        *[{
            "selector": '.' + color,
            'style': {'line-color': color,"target-arrow-shape":arrow}
        } for color,arrow in colors]
    ]
    return    cyto.Cytoscape(
            id='signa_network',
            stylesheet=default_stylesheet,
            layout={'name': 'concentric'},
            style={'width': '100%', 'height': '500px'},
            elements=element
        )

#################function starts#############################
def gen_net():
    
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    nodes = [
        {
            'data': {'id': short, 'label': label},
            'position': {'x': 20*lat, 'y': -20*long}
        }
        for short, label, long, lat in (
            ('la', 'PPI', 34.03, -118.25),
            ('nyc', 'Pathways', 40.71, -74),
            ('to', 'Processes', 43.65, -79.38),
            ('mtl', 'Function', 45.50, -73.57),
            ('van', 'Disease', 49.28, -123.12),
            ('chi', 'Ligand', 41.88, -87.63),
            ('bos', 'Localization', 42.36, -71.06),
            ('hou', 'Mutation', 29.76, -95.37)
        )
    ]

    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in (
            ('van', 'la'),
            ('la', 'chi'),
            ('hou', 'chi'),
            ('to', 'mtl'),
            ('mtl', 'bos'),
            ('nyc', 'bos'),
            ('to', 'hou'),
            ('to', 'nyc'),
            ('la', 'nyc'),
            ('nyc', 'bos')
        )
    ]

    element = nodes + edges
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^dummy data end^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^styling start^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    default_stylesheet = [
        {
            "selector": 'node',
            'style': {
                "opacity": 1,
                'height': 15,
                'width': 15,
                'background-color': '#222222',
                "label": "data(label)"
            }
        },
        {
        'selector': '.search',
        'style': {
            'background-color': 'red'
        }
    },
        {
            "selector": 'edge',
            'style': {
                'target-arrow-color': 'black',
                #"target-arrow-shape": "triangle-tee",
                "curve-style": "bezier",
                "opacity": 0.3,
                'width': 2
            }
        },

        *[{
            "selector": '.' + color,
            'style': {'line-color': color,"target-arrow-shape":arrow}
        } for color,arrow in colors]
    ]
    return    cyto.Cytoscape(
            id='cytoscape-update-layout',
            zoom=0.5,
            stylesheet=default_stylesheet,
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '700px'},
            elements=element
        )
#######################function 2##########################################
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),header=None)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded),header=None)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    prots=df[0].to_list()

    return  prots
#########################function 3########################
def cyto_2_graph(con_elements):
    g=nx.DiGraph()
    my_sub_node=get_nodes(con_elements)
    if len(con_elements)>18:
        cnt=0
        for el in con_elements:

            #print(el['data'])
            # if len(el['data'])>2:
            #     g.add_edge(el['data']['source'],el['data']['target'])
            # else:
            #     cnt+=1
            #     #print('node found',cnt)
            #     g.add_node(el['data']['id'])

            try:
                g.add_edge(el['data']['source'],el['data']['target'])
            except Exception as e:
                g.add_node(el['data']['id'])
                continue

    g_sub=g.subgraph(my_sub_node)
    return g_sub

#################function 4#################################
def update_nodes_tmp(el_tmp,ul):

    el_copy=el_tmp.copy()
    cnt=0
    for itm in el_tmp:
        try:
            tmp=itm['data']['label']
            #print('New length',len(el_copy))
            #print(itm)
            if  tmp not in ul:
                el_copy.remove(itm)
                #print(itm)
        except Exception as e:
            cnt+=1
            continue
   
    return el_copy

def get_current_valid_edges(current_nodes, all_edges):
    """Returns edges that are present in Cytoscape:
    its source and target nodes are still present in the graph.
    """
    valid_edges = []
    node_ids = {n['data']['id'] for n in current_nodes}

    for e in all_edges:
        if e['data']['source'] in node_ids and e['data']['target'] in node_ids:
            valid_edges.append(e)
    return valid_edges
def update_nodes(el_tmp,ul):

    el_copy=el_tmp.copy()
    #valid_edges = []
    current_nodes=[]
    all_edges=[]
    cnt=0
    for itm in el_copy:
        # if the element is a node
        if 'source' not in itm['data']:
            if itm['data']['label'] in ul:
                current_nodes.append(itm)
        else:
            all_edges.append(itm)
    val_edges = get_current_valid_edges(current_nodes, all_edges)
    return val_edges+current_nodes
####################function 5#############################
def get_nodes(el):
    nodes=[]
    for itm in el:
        try:
            nodes.append(itm['data']['label'])
        except Exception as e:
            continue
    return nodes

def get_edges(el):
    edges=[]
    for itm in el:
        try:
            tmp=itm['data']['source']
            edges.append(itm['data'])
        except Exception as e:
            continue
    return edges
#################functions ends#############################

def get_dummy_fig(t_msg="Enriched dummy item (Click analyse to get results)"):
    pval=[1,2,3,4]
    rank=[1,2,3,4]
    name=['dummy1','dummy2','dummy3','dummy4']
    fig = px.bar( x=pval, y=rank,title=t_msg, orientation='h' , text=name,labels=dict(x="P values of dummy", y="Rank dummy"))
    return fig

# mapbox access token.



example_prots='RB1\nPPP1CA\nTP53\nCSNK2A1\nCDK1\nCHEK1\nEEF2K\nEGFR\nERBB2\nCDC7\nAR\nBRCA1\nMAPK6\nSIRT1\nNME1\nEIF2AK2'

singal_tooltip='Black nodes are signaling pathways\nRed nodes are proteins\n\nBCR\t Signaling by B cell receptor\n HH\t Signaling by Hedgehog\n HIPPO\t Signaling by Hippo\n IIP\t Innate immune pathways\n JAK/STAT\t Janus Activating Kinase/ Signal Transducer and Activator of Transcription\n Notch\t Signaling by Notch\n TCR\t Signaling by T cell receptor\n TGF\t Signaling by Transforming Growth Factor beta\n TLR\t  Toll-Like receptor signaling\n TNF\t Signaling by Tumor necrosis factor\n NHR\t Signaling by Nuclear hormone receptor\n RTK\t Signaling by Receptor tyrosine kinase\n WNT/Wingless\t Signaling by WNT\n'

# mapbox_access_token = 'pk.eyJ1Ijoic25ha2VicnlhbiIsImEiOiJja2J0dzZnaWEwMWxuMnhsYnUxZTBobWNqIn0.B0E9GC_uNHbz8b9BYDn0Ng'
sub_head_css={
            'textAlign': 'center',
            'font':'Courier New',
            'font-weight':'900',
            'color':'white',
            'font-size':'x-large'
            }

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}



exp_legend=html.Div([
                        html.Div([
                            html.Ul([
                                html.Li([html.Span(['one'],style={'background':'#EF553B'})]),
                                html.Li([html.Span(['two'],style={'background':'#636EFA'})])

                                ],className='legend-labels')
                            ],className='legend-scale')
                        ],className='my-legend')
# Create app layout
print('current url',app.get_asset_url("k2p_logo_final.png"))
app.layout = html.Div(
    [
        # dcc.Store(id='aggregate_data'),
        html.Div(
            id="banner",
            className="banner",
            children=[html.A(href="/",children=[html.Img(src=app.get_asset_url("k2p_logo_final.png"))])],
        ),
        html.Div(
            [
                html.Div(
                    [   #html.Div(id='intermediate-value', children=["AKT1"],style={'display': 'none'})
                        
                        
                        html.P(
                            #'Enter Protein Name/s OR Upload a list',
                            ['Enter Protein Name(s)',dcc.RadioItems( id='query_type',options=[ {'label': 'Gene Symbol', 'value': 'gene_symbol'}, {'label': 'Uniprot ID', 'value': 'uniprot_id'}], value='gene_symbol',labelStyle={'display': 'inline-block'})],
                            className="row"
                        ),
                        dcc.Textarea(id = 'Textarea Input',placeholder = 'Enter protein name/names',value=example_prots,style={"height": "50px", "width": "100%"}),
                        #html.B("______________OR________________",style={'textAlign': 'right'}),
                        html.Div(['Use ',html.A(id='example_button',children='Example'),' OR'],style={'textAlign': 'center','fontWeight': 'bold'}),
                        dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        'Drag and Drop a list or ',
                                        html.A('Select File')
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin-top': '10px',
                                        'margin-bottom': '10px'
                                    }),
                        dcc.Dropdown(
                                id='dropdown-update-layout',
                                value='grid',
                                clearable=False,
                                className='dcc_control',
                                #style={'display': 'inline-block'},

                                options=[
                                    {'label': name.capitalize(), 'value': name}
                                    for name in ['klay','dagre','spread','cola','euler','breadthfirst','cose-bilkent','preset','grid', 'random', 'circle', 'cose', 'concentric']
                                ]
                            ),
                        html.Button(children = 'Search',id = 'save button',type = 'submit',n_clicks = 0,style={'margin': 'auto','display': 'flex'}),

                        #html.Button(children = 'Calculate',id = 'cp_calculate',type = 'submit',n_clicks = 0),
                        dcc.Download(id="unmatch_prot"),
                        html.Div(['Choose filter(s)'],className='control_label'),
                        html.Label(
                                    [
                                        "Location",
                                        dcc.Dropdown(id="location", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            html.Label(
                                    [
                                        "Molecular Function",
                                        dcc.Dropdown(id="function", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            html.Label(
                                    [
                                        "Biological Process",
                                        dcc.Dropdown(id="process", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            html.Label(
                                    [
                                        "Pathways",
                                        dcc.Dropdown(id="pathway", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            html.Label(
                                    [
                                        "Disease",
                                        dcc.Dropdown(id="disease", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            html.Label(
                                    [
                                        "Tissue expression",
                                        dcc.Dropdown(id="tissue", multi=False,style={"width": "100%"}),
                                    ]
                                ),
                            #html.Div(['Network Analysis'],style={'textAlign': 'center','fontWeight': 'bold'}),
                            
                            html.Div([
                              html.Button(children = 'Reset Filters',id = 'reset',type = 'submit',n_clicks = 0,style={'margin': 'auto','margin-top': '10px','display': 'flex'}),
                              html.Button(children = 'Apply Filters',id = 'apply_fil',type = 'submit',n_clicks = 0,style={'margin': 'auto','margin-top': '10px','display': 'flex'}),
                                ],className='row'),
                            html.Br(),
                            html.Button(children = 'Analyse',id = 'cp_calculate',type = 'submit',n_clicks = 0,style={'margin': 'auto','margin-top': '10px','display': 'flex'}),
                            dcc.Loading(html.Div(id='analyse_status'))
                            

                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        #dcc.Graph(id='founded_year_graph')
                        #html.Div(id="interaction_network", children=gen_net())
                       html.Div([
                         html.Img(id="btn-get-png",src=app.get_asset_url("download.png"), height=30,style={"margin-right": "15px"},title='Download Network Snapshot',className='click_icon'),
                         html.Img(id="rescale",src=app.get_asset_url("rescale.png"), height=30,style={"margin-right": "15px"},title='Rescale Network',className='click_icon'),
                         html.Img(id="zoom-in",src=app.get_asset_url("zoom-in.png"), height=30,style={"margin-right": "15px"},title='Zoom In',className='click_icon'),
                         html.Img(id="zoom-out",src=app.get_asset_url("zoom-out.png"), height=30)],style={'margin': 'auto','margin-top': '10px','display': 'inline-block','justify-content': 'space-between'},title='Zoom Out',className='click_icon'),
                         dcc.Loading(id='cyto_loading',children=html.Div(children=gen_net())),
                         html.Div(id='net_info',className='four columns')
                    ],
                    className='pretty_container eight columns'

                ),
            ],
            className='row'
        ),
        html.Div(
                            [
                               html.Div(
                                    [
                                        html.H5('Local properties'),'(Click Node/Edge to retrieve)'
                                        ],
                                        className='twelve columns',style={'text-align': 'center'}),
                               html.Div([
                                html.Div(id='func_info')
                                ],style={'display': 'none'}
                                #,className='four columns'

                                )

                            ],

                            className='pretty_container row',
                            
                        ),
        html.Div(
                            [
                                html.Div([dcc.Tabs(id="tabs-styled-with-inline", value='tab-0', children=[
                                                                dcc.Tab(label='Node info', value='tab-0', style=tab_style, selected_style=tab_selected_style),
                                                                dcc.Tab(label='PDB Complex', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                                                                dcc.Tab(label='Ligands', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                                                                dcc.Tab(label='Mutation (disease)', value='tab-3', style=tab_style, selected_style=tab_selected_style),
                                                                dcc.Tab(label='Interaction trivia', value='tab-4', style=tab_style, selected_style=tab_selected_style),
                                                            ], style=tabs_styles),dcc.Loading(html.Div(id='tabs-content-inline'))
                                ],
                                  className='pretty_container twelve columns',style={
                                                                                        'padding':'10px',
                                                                                        'margin':'10px',
                                                                                        'box-shadow': '0 3px 5px rgba(57, 63, 72, 0.3)'
                                                                                        })
                            ],

                            className='pretty_container row',
                            
                        ),


        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'PDB Complex',
                            className="control_label"
                        ),
                        html.Div(id='docking')
                    ],
                    className='pretty_container six columns'
                ),
                html.Div(
                    [
                        html.P(
                            'Ligands',
                            className="control_label"
                        ),
                        html.Div(id="ligand")
                    ],
                    className='pretty_container six columns'
                )
            ],
            className='row',style={'display': 'none'}
        ),
         html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Interaction Reference',
                            className="control_label"
                        ),
                        html.Div(id='click_info')
                    ],
                    className='pretty_container six columns'
                ),
                html.Div(

                    [
                        html.P(
                            'Mutation in disease',
                            className="control_label"
                        ),
                        html.Div(id="disease_mutation")
                    ],
                    className='pretty_container six columns'
                )
            ],
            className='row',style={'display': 'none'}
        ),


        html.Div(
                            [
                               html.Div(
                                    [
                                        html.H5('Global properties'),'(Click "Analyse" to retrieve)'
                                        ],
                                        className='twelve columns',style={'text-align': 'center'})
                                

                            ],

                            className='pretty_container row',
                            
                        ),
        html.Div(
                            [
                               
                                
                                    'Enrichment panel',
                            
                            ],

                            className='banner',
                            style=sub_head_css
                        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='pathway_graph')
                    ],
                    className='pretty_container six columns'
                ),
                html.Div(
                    [
                        dcc.Graph(id='process_graph')
                    ],
                    className='pretty_container six columns'
                )
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='pclass_graph')
                    ],
                    className='pretty_container six columns',
                    #id='map_graph-Container'
                ),
                html.Div(
                    [
                        dcc.Graph(id='disease_graph'),
                        #html.Button('Reset Category', id='reset_category'),
                    ],
                    #className='six columns',
                    className='pretty_container six columns',
                    #id='category_graph-Container'
                )
            ],
            className='row'
        ),
        html.Div(
                            [
                               
                                
                                    'Topological panel'
                            
                            ],

                            className='banner',
                            style=sub_head_css
                        ),
        html.Div(
            [
                html.Div(
                    [   
                        #html.Label("Topological properties", style={'textAlign': 'center'}),
                        dt.DataTable(
                            id='complex_para',
                            columns=[{"name":i, "id":i} for i in TABLE_COLUMNS],
                            #data='',
                            sort_action='native',
                            filter_action='native',
                            page_action='native',
                            page_current=0,
                            page_size=12,
                            style_cell={'fontSize':12, 'font-family':'arial'},
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                        ),
                    ],
                    className='pretty_container six columns'
                ),
                html.Div(
                    [
                        dcc.Graph(id='network_para_graph'),
                        
                      
                    ],
                    #className='four columns',
                    className='pretty_container six columns',
                    style={'textAlign': 'center'}
                ),
            ],
            #className='pretty_container row'
            className='row'
        ),
        html.Div(
                            [
                               
                                
                                    'Results for top spreaders',
                                
                            ],

                            className='banner',
                            style=sub_head_css
                        ),
        html.Div(
            [
                html.Div(
                    [   
                        #html.Label("Topological properties", style={'textAlign': 'center'}),
                        dt.DataTable(
                            id='top_stats',
                            columns=[{"name":i, "id":i} for i in result_columns],
                            #data='',
                            sort_action='native',
                            #filter_action='native',
                            page_action='native',
                            page_current=0,
                            page_size=12,
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'lineHeight': '15px'
                            },
                            style_cell={'fontSize':12, 'font-family':'arial'},
                            style_table={'overflowX': 'auto','table-layout': 'fixed'},
                            style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                            editable=True,
                            
                            export_format='xlsx',
                            

                        ),
                    ],
                    className='pretty_container twelve columns',style={
                    'padding':'10px',
                    'margin':'10px',
                    'box-shadow': '0 3px 5px rgba(57, 63, 72, 0.3)'
                    }
                ),
                
            ],
            #className='pretty_container row'
            className='row'
        ),
          html.Div(

              [     
                    #"Pathway clustergram of the triggers",
                    html.Div([
                    html.Div(className="banner",children=["Pathway clustergram of top spreaders"],style=sub_head_css),
                    #html.H4('Pathway clustergram of the triggers'),
                    html.Div([dcc.Graph(id='top_pathway',style={'height':'100%','width':'100%'})])
                    ],className='pretty_container twelve columns',style={
                    'padding':'10px',
                    'margin':'10px',
                    'box-shadow': '0 3px 5px rgba(57, 63, 72, 0.3)'
                    })
              ],
              className='row'
            ),
        # html.Div(
        #     [
        #         html.Div(
        #             [
        #                 #dcc.Graph(id='top_pathway')
        #                 #html.Div(id='top_pathway')
        #             ],
        #             className='pretty_container six columns',
        #             id='map_graph-Container'
        #         ),
        #         html.Div(
        #             [
        #                 dcc.Graph(id='top_expression'),
        #                 #html.Button('Reset Category', id='reset_category'),
        #             ],
        #             #className='six columns',
        #             className='pretty_container six columns',
        #             id='category_graph-Container'
        #         )
        #     ],
        #     className='row'
        # ),
        html.Div(
            [
                html.Div(
                    [   

                        dcc.Graph(id='location_graph'),
                        #html.Button('Reset Category', id='reset_category'),
                    ],
                    #className='six columns',
                    className='pretty_container six columns',
                    id='loc_graph-Container'
                ),
                html.Div(
                    [
                        dcc.Graph(id='sub_network_para_graph'),
                        
                      
                    ],
                    #className='four columns',
                    className='pretty_container six columns',
                    style={'textAlign': 'center'}
                ),
            ],
            #className='pretty_container row'
            className='row'
        ),
        html.Div(
            [
                html.Div(
                        [html.Div(className="banner",children=["Hallmarks of top spreaders"],style=sub_head_css),
                        #dcc.Graph(id='Does_effect_graph'),
                        html.Div(children=gen_hallmark()),
                        dcc.Download(id="hallmark_dwnload"),
                        html.Div([
                            html.Div([html.Img(id="hallmark_info",src=app.get_asset_url("information.png"), height=30,style={"margin-right": "15px"},title='Black nodes are disease hallmarks\nRed nodes are proteins',className='click_icon')],className='six columns'),
                        dcc.Dropdown(
                                id='hallmark-update-layout',
                                value='circle',
                                clearable=False,
                                className='dcc_control',
                                style={'width': '50%'},

                                options=[
                                    {'label': name.capitalize(), 'value': name}
                                    for name in ['klay','dagre','spread','cola','euler','breadthfirst','cose-bilkent','preset','grid', 'random', 'circle', 'cose', 'concentric']
                                ]
                            ),

                        html.Button('Download', id='hall_d_button')],className='row'),
                    ],
                    #className='six columns',
                    className='pretty_container six columns'
                ),

                html.Div(
                    [
                        #dcc.Graph(id='Gets_effect_graph'),
                        html.Div(className="banner",children=["Signaling of top spreaders"],style=sub_head_css),
                        html.Div(children=gen_signa()),
                        #dcc.Tooltip(id="graph-tooltip", direction='bottom'),
                        dcc.Download(id="signa_dwnload"),
                        html.Div([
                        html.Div([html.Img(id="signa_info",src=app.get_asset_url("information.png"), height=30,style={"margin-right": "15px"},title=singal_tooltip,className='click_icon')],className='six columns'),
                        dcc.Dropdown(
                                id='signa-update-layout',
                                value='circle',
                                clearable=False,
                                className='dcc_control',
                                style={'width': '50%'},

                                options=[
                                    {'label': name.capitalize(), 'value': name}
                                    for name in ['klay','dagre','spread','cola','euler','breadthfirst','cose-bilkent','preset','grid', 'random', 'circle', 'cose', 'concentric']
                                ]
                            ),
                        html.Button('Download', id='signa_d_button')
                        ],className='row'),
                        #children=gen_signa()
                      
                    ],
                    #className='four columns',
                    className='pretty_container six columns',
                    #style={'textAlign': 'center'}
                ),
            ],
            #className='pretty_container row'
            className='row'
        ),
        html.Div(
            [
                #dcc.Store(id='intermediate-value')
                html.Div(id='intermediate-value',style={'display': 'none'}),
                html.Div(id='unmatch-value',style={'display': 'none'}),
                dcc.Store(id='memory_net',storage_type='session'),
                
                html.Div(html.P(["Copyright ©2021 Dr. Samrat Chatterjee's LAB (THSTI)", html.Br(), 'Developed by Shivam']))
            ]
        )
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


# Helper functions

def get_func_info(gene,trim_str='Function [CC]\nFUNCTION: '):
    
    db=client.ppi_test
    my_db=db.database1
    res=my_db.find({'name':gene.upper()},{'id':1,'name':1,'_id':0})
    u_id=res[0]['id']
    g_id=res[0]['name']
    
    url=f'https://rest.uniprot.org/uniprotkb/{u_id}?format=json&fields=cc_function'
    my_hnd=requests.get(url)
    url_json=my_hnd.json()
    #return url_txt
    page_txt=url_json['comments'][0]['texts'][0]['value']
    if page_txt:
        func_info=my_hnd.text.split(' (')[0][len(trim_str):]+'.'
        flines=page_txt.split('.')
        func_info=flines[0]+'.'+flines[-1]+'.'
        #func_info=page_txt
    else:
        func_info='Not Found'
    return g_id,u_id,func_info


def query_db_net(prots):
    query=prots.copy()
    if prots:
    #print(prots)
    #my_res=data.find({'name':{'$in':prots}});
    #db = client.ppi
        my_data = db.edge_lists2
        my_res = my_data.find({'$or':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1})
        cnt=0
        prots=[]
        for res in my_res:
            cnt+=1
            prots.append(res['ENTITYA'])
            prots.append(res['ENTITYB'])
            #print(res)
    prots=list(set(prots))
    my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1,'EFFECT':1})
    
    g = nx.DiGraph()
    colors = ['red', 'blue', 'green', 'yellow', 'pink']
    cy_nodes=[]
    cy_edges=[]
    #disease=[]
    nodes=set()
    for res in my_res:

        #disease=disease+res['Disease']
        source = res['ENTITYA']
        target = res['ENTITYB']
        
        if 'up' in res['EFFECT']:
                color='blue'
        elif 'down' in res['EFFECT']:
            color ='red'
        else: 
            color ='grey'
        
        cy_edges.append({  # Add the Edge Node
                'data': {'source': source, 'target': target},
                'classes': color
            })
        if source in query:
            cat='search'
        else:
            cat='not_search'
        
        if source not in nodes:  # Add the source node
            nodes.add(source)
            cy_nodes.append({"data": {"id": source,'label':source}, "classes": cat})

        if target in query:
        #print(target)
            cat='search'
        else:
            cat='not_search'

        if target not in nodes:  # Add the target node
            nodes.add(target)
            cy_nodes.append({"data": {"id": target,'label':target }, "classes": cat})
    return cy_edges,cy_nodes,nodes


def query_signa_net(top_prots):
    #query=top_prots.copy()
    my_data = db.signaling
    my_res=my_data.find({ 'source_name':{'$in':top_prots} },{'source_name':1,'source_pathways':1,'_id':0})
    temp=list(my_res)
    network_df=pd.DataFrame(temp)
    sig_paths=list(network_df['source_pathways'].unique())
    my_sig_prot=network_df.groupby(['source_pathways']).size()
    my_res=my_data.find({ 'source_pathways':{'$in':sig_paths} },{'source_name':1,'source_pathways':1,'_id':0})
    temp=list(my_res)
    network_df=pd.DataFrame(temp)
    total_sig_prot=network_df.groupby(['source_pathways']).size()
    path_score=my_sig_prot.divide(total_sig_prot)
    #print("This is pathway score",path_score)
    #path_score
    #########score calculated above#########################
 
    my_data = db.signaling
    #my_res = my_data.find({'$or':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1})
    my_res=my_data.find({ 'source_name':{'$in':top_prots} },{'source_name':1,'source_pathways':1,'_id':0})
    cnt=0
    # prots=[]
    # for res in my_res:
    #     cnt+=1
    #     prots.append(res['source_name'])
    #     prots.append(res['source_pathways'])
        #print(res)
    #prots=list(set(prots))
    #my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1,'EFFECT':1})
    
    g = nx.Graph()
    colors = ['red', 'blue', 'green', 'yellow', 'pink']
    cy_nodes=[]
    cy_edges=[]
    #disease=[]
    nodes=set()
    for res in my_res:

        #disease=disease+res['Disease']
        source = res['source_name']
        target = res['source_pathways']
        
        
        cy_edges.append({  # Add the Edge Node
                'data': {'source': source, 'target': target}
                #,'classes': color
            })
        
        # if source in query:
        #     cat='search'
        # else:
        #     cat='not_search'

        if source not in nodes:  # Add the source node
            nodes.add(source)
            cy_nodes.append({'data': {'id': source,'label':source,'size':10}, 'classes': 'search'})

        # if target in query:
        # #print(target)
        #     cat='search'
        # else:
        #     cat='not_search'

        if target not in nodes:  # Add the target node
            nodes.add(target)
            #cy_nodes.append({'data': {'id': target,'label':target,'size':path_score[target]*1000 }, 'classes': 'not_search'})
            cy_nodes.append({'data': {'id': target,'label':target,'size':10 }, 'classes': 'not_search'})


    return cy_edges,cy_nodes,nodes

def query_hallmark_net(top_prots):
    #query=top_prots.copy()
    #my_data = db.signaling
    #my_res=my_data.find({ 'source_name':{'$in':top_prots} },{'source_name':1,'source_pathways':1,'_id':0})
    #temp=list(my_res)
    #network_df=pd.DataFrame(temp)
    #sig_paths=list(network_df['source_pathways'].unique())
    #my_sig_prot=network_df.groupby(['source_pathways']).size()
    #my_res=my_data.find({ 'source_pathways':{'$in':sig_paths} },{'source_name':1,'source_pathways':1,'_id':0})
    #temp=list(my_res)
    #network_df=pd.DataFrame(temp)
    #total_sig_prot=network_df.groupby(['source_pathways']).size()
    #path_score=my_sig_prot.divide(total_sig_prot)
    #path_score
    #########score calculated above#########################
 
    my_data = db.hallmarks
    #my_res = my_data.find({'$or':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1})
    my_res=my_data.find({ 'Gene Symbol':{'$in':top_prots} },{'Gene Symbol':1,'Hallmark':1,'References':1,'_id':0})
    cnt=0
    # prots=[]
    # for res in my_res:
    #     cnt+=1
    #     prots.append(res['source_name'])
    #     prots.append(res['source_pathways'])
        #print(res)
    #prots=list(set(prots))
    #my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':prots }},{ "ENTITYB": {'$in':prots }}]},{'ENTITYA':1,'ENTITYB':1,'EFFECT':1})
    
    g = nx.Graph()
    colors = ['red', 'blue', 'green', 'yellow', 'pink']
    cy_nodes=[]
    cy_edges=[]
    #disease=[]
    nodes=set()
    for res in my_res:

        #disease=disease+res['Disease']
        source = res['Gene Symbol']
        target = res['Hallmark']
        ref = res['References']
        
        cy_edges.append({  # Add the Edge Node
                'data': {'source': source, 'target': target,'Ref':ref}
                #,'classes': color
            })
        
        # if source in query:
        #     cat='search'
        # else:
        #     cat='not_search'

        if source not in nodes:  # Add the source node
            nodes.add(source)
            cy_nodes.append({'data': {'id': source,'label':source}, 'classes': 'search'})

        # if target in query:
        # #print(target)
        #     cat='search'
        # else:
        #     cat='not_search'

        if target not in nodes:  # Add the target node
            nodes.add(target)
            cy_nodes.append({'data': {'id': target,'label':target }, 'classes': 'not_search'})


    return cy_edges,cy_nodes,nodes

def fetch_dropdown(nodes):
    #my_data = db.database1
    #my_res = my_data.find({ "name": {'$in':list(nodes) }},{'name':1,'location':1,'biological_proc':1,'molecular_func':1,'pathway_class':1,'diseases':1,'tissue_exp':1})
   
    location=[]
    function=[]
    process=[]
    pathway=[]
    disease=[]
    tissue_exp=[]
    total_prot=[]

    db=client.ppi
    my_data = db.database1
    my_res = my_data.find({ "name": {'$in':list(nodes) }},{'location':1,'biological_proc':1,'molecular_func':1,'pathway_class':1,'diseases':1,'tissue_exp':1,'_id':0})


    #res_df=pd.DataFrame(my_res)
    for res in my_res:
        #print('this is res',res)
        #total_prot.append(res['name'])
        if res['location']:
            location.extend(res['location'])
        if res['molecular_func']:
            function.extend(res['molecular_func'])
        if res['biological_proc']:
            process.extend(res['biological_proc'])
        if res['pathway_class']:
            pathway.extend(res['pathway_class'])
        if res['tissue_exp']:
            tissue_exp.extend(res['tissue_exp'])
        if res['diseases']:
            disease.extend(res['diseases'])
        #print('this is before label',tissue_exp)
    #print('my process list',process)
    location=list(set(location))
    function=list(set(function))
    process=list(set(process))
    pathway=list(set(pathway))
    disease=list(set(disease))
    #print('my dis list',disease)
    tissue_exp=list(set(tissue_exp))

    options=[{'label': name.capitalize(), 'value': name} for name in location if not pd.isna(name)]
    options1=[{'label': name.capitalize(), 'value': name} for name in function if not pd.isna(name)]
    options2=[{'label': name.capitalize(), 'value': name} for name in process if not pd.isna(name)]
    options3=[{'label': name.capitalize(), 'value': name} for name in pathway if not pd.isna(name)]
    options4=[{'label': name.capitalize(), 'value': name} for name in disease if not pd.isna(name)]
    #print('my drop down',options4)
    options5=[{'label': str(name), 'value': name}  for name in tissue_exp if not pd.isna(name)]
    #print('this is expression',options5)
    return options,options1,options2,options3,options4,options5
def get_loc_net(el,compart):
    print('location',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'location':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    #print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return new_el
def get_fun_net(el,compart):
    print('function',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'molecular_func':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return new_el

def get_proc_net(el,compart):
    print('process',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'biological_proc':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    #print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return new_el

def get_path_net(el,compart):
    print('pathway',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'pathway_class':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    #print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return new_el
def get_dis_net(el,compart):
    print('disease',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'diseases':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    #print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return 
def get_tiss_net(el,compart):
    print('tissue',compart)
    my_data = db.database1
    compart1=[compart]
    my_res=my_data.find({'tissue_exp':{'$in':compart1}},{'name':1,'_id':0})
    cnt=0
    n_p=[]
    #print('old updated total',len(el))
    #print('old edges',cnt)
    for res in my_res:
        n_p.append(res['name'])
        cnt+=1
    #print('number in n',cnt)
    new_el=update_nodes(el,n_p)
    #print('now nodes are ',get_nodes(new_el))
    #print('new nodes',get_nodes(new_el))
    tmp_g=cyto_2_graph(new_el)
    print("updated_graph",tmp_g.number_of_edges()," and", tmp_g.number_of_nodes())
    cnt=0
    #print('new edges',cnt)
    #print(get_nodes(new_el))
    #print('number of updated',len(new_el))
    return new_el
def get_pdb_data(tap_node,pdb_ids):
    beg="""{
    entries(entry_ids:""" 
    #pdb_ids=my_res[0]['pdb_id']
    #pbs=["1STP", "2JEF", "1CDG"]
    #tap_node='cdk1'

    trail=  """) {
        rcsb_id
        struct {title}
        rcsb_entry_info{resolution_combined}
        exptl {method}
        rcsb_primary_citation{pdbx_database_id_PubMed}

      }
    }
    """
    query=beg+json.dumps(pdb_ids)+trail

    url='https://data.rcsb.org/graphql'
    r = requests.post(url, json={'query': query})
    print(r.status_code)
    my_query=r.json()
    #print(r.text)
    pdb_data=pd.DataFrame(columns=['Gene_ID','PDB_ID','Title','Experiment','Resolution','PMID'])
    my_pdbs=my_query['data']['entries']
    for pdb in my_pdbs:


        Title=pdb['struct']['title']
        pmid=pdb['rcsb_primary_citation']['pdbx_database_id_PubMed']
        struc_id=pdb['rcsb_id']
        try:
            pdb_res=str(pdb['rcsb_entry_info']['resolution_combined'][0])+' A'
        except Exception as e:
            print("exception is ",e)
            print("this is the pdb")
            pdb_res=pd.NA

        exp_met=pdb['exptl'][0]['method']
        pdb_data=pdb_data.append({'Gene_ID':tap_node,'PDB_ID':struc_id,'Title':Title,'Experiment':exp_met,'Resolution':pdb_res,'PMID':pmid},ignore_index=True)
    pdb_data
    return pdb_data
def get_top_tissue(top_prots):
    my_data = db.database1
    my_res=my_data.find({ 'name':{'$in':top_prots}},{'tissue_exp':1,'_id':0})
    all_tissues=[]
    for exp in my_res:
        #high_exp = list(filter(lambda x: '(High)' in x, exp['tissue_exp'])
        try:
            high_exp= [i for i in exp['tissue_exp'] if '(High)' in i]
            temp=[s.strip(' (High)') for s in high_exp]
            all_tissues.extend(temp)
        except:
            continue            
        #break
    all_tissues=list(set(all_tissues))
    my_exp_df=pd.DataFrame(index=top_prots,columns=all_tissues)
    my_exp_df=my_exp_df.fillna(0)
    my_res=my_data.find({ 'name':{'$in':top_prots}},{'tissue_exp':1,'name':1,'_id':0})
    for exp in my_res:
        #high_exp = list(filter(lambda x: '(High)' in x, exp['tissue_exp'])
        try:
            high_exp= [i for i in exp['tissue_exp'] if '(High)' in i]
            temp=[s.strip(' (High)') for s in high_exp]
            #all_tissues.extend(temp)
            my_exp_df.loc[exp['name'],temp]=1 
        except:
            continue
    #tiss_ = px.imshow(my_exp_df) 
    return my_exp_df

def get_path_cluster(top_prots):
    my_data = db.database1
    my_res=my_data.find({ 'name':{'$in':top_prots}},{'name':1,'pathways':1,'_id':0})

    all_tissues=[]
    for exp in my_res:
        #high_exp = list(filter(lambda x: '(High)' in x, exp['tissue_exp'])
        #path_way= [i for i in exp['pathways']]
        try:
            #path_ls=exp['pathways']
            #path_way= [i for i in path_ls]
            path_way= [i for i in exp['pathways']]
            #temp=[s.strip(' (High)') for s in high_exp]
            all_tissues.extend(path_way)
        except:
            continue            
        #break
    all_tissues=list(set(all_tissues))

    my_exp_df=pd.DataFrame(index=top_prots,columns=all_tissues)
    my_exp_df=my_exp_df.fillna(0)

    my_res=my_data.find({ 'name':{'$in':top_prots}},{'pathways':1,'name':1,'_id':0})
    for exp in my_res:
        #high_exp = list(filter(lambda x: '(High)' in x, exp['tissue_exp'])
        #high_exp= [i for i in exp['tissue_exp'] if '(High)' in i]
        try:
            temp=[i for i in exp['pathways']]
        #all_tissues.extend(temp)
            my_exp_df.loc[exp['name'],temp]=1 
        except:
            continue   
    #break
#all_tissues=list(set(all_tissues))
    df_to_return=my_exp_df.loc[:,my_exp_df.sum(axis=0)>3]
    return df_to_return

# New multiquery function
def multi_filter_query(loc,fun,proc,path,dis,exp):
    db=client.ppi
    my_db = db.database1
    #Updating location query
    if loc:
        locate=loc
        print('query',locate)
    else:
        locate={'$exists': True}
    #Updating function query
    if fun:
        mol_fun=fun
        print('query',mol_fun)
    else:
        mol_fun={'$exists': True}
    #Updating process query
    if proc:
        bio_proc=proc
        print('query',bio_proc)
    else:
        bio_proc={'$exists': True}
    #Updating pathway query
    if path:
        pathway=path
        print('query',pathway)
    else:
        pathway={'$exists': True}
    #Updating disease query
    if dis:
        disease=dis
        print('query',disease)
    else:
        disease={'$exists': True}
    #Updating expression query
    if exp:
        tiss_exp=exp
        print('query',tiss_exp)
    else:
        tiss_exp={'$exists': True}
    
        
    
    
    my_res=my_db.find(
        {
            '$and': [ 
                { 'location':locate },
                { 'molecular_func':mol_fun },
                { 'biological_proc':bio_proc },
                { 'pathway_class':pathway },
                { 'diseases':disease },
                { 'tissue_exp': tiss_exp }
            ]
        },
        {'_id':0,'name':1}
    )
    
    tmp_df=pd.DataFrame(list(my_res))
    #print('Cant you see',tmp_df)
    if tmp_df.empty:
        return []
    else:
        return tmp_df['name'].to_list()


def id_conversion(top_prots):
    my_data = db.database1
    my_res=my_data.find({ 'id':{'$in':top_prots}},{'name':1,'_id':0})
    conv_list=pd.DataFrame(my_res)['name'].to_list()
    return conv_list
# my callbacks

@app.callback(Output('Textarea Input', 'value'),
              Input('example_button', 'n_clicks'),prevent_initial_call=True)
def update_layout(n_clicks):
    
    ctx = dash.callback_context
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs,
        'state' : ctx.states
    }, indent=2)
    print('example button',ctx_msg)
    #print('states', ctx.states)
    trigger_source=ctx.triggered
    #if curr_zoom:
    if trigger_source[0]['prop_id']=='example_button.n_clicks':
        return example_prots
       

@app.callback(Output("cytoscape-update-layout", "generateImage"),
             Input("btn-get-png", "n_clicks"))
def get_image(get_png_clicks):

    # File type to output of 'svg, 'png', 'jpg', or 'jpeg' (alias of 'jpg')
    #if get_png_clicks>0:
    ftype = 'png'

    # 'store': Stores the image data in 'imageData' !only jpg/png are supported
    # 'download'`: Downloads the image as a file with all data handling
    # 'both'`: Stores image data and downloads image as file.
    action = 'store'

    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        print('Inside download',input_id)

        if input_id != "tabs":
            action = "download"
            ftype = input_id.split("-")[-1]

    return {
        'type': ftype,
        'action': action
        }
  


@app.callback(Output('cytoscape-update-layout', 'layout'),
              [Input('dropdown-update-layout', 'value')])
def update_layout(layout):
    #print('change layout')
    return {
        'name': layout,
        'animate': True
    }

@app.callback(Output('hallmark_network', 'layout'),
              [Input('hallmark-update-layout', 'value')])
def update_layout(layout):
    #print('change layout')
    return {
        'name': layout,
        'animate': True
    }
@app.callback(Output('signa_network', 'layout'),
              [Input('signa-update-layout', 'value')])
def update_layout(layout):
    #print('change layout')
    return {
        'name': layout,
        'animate': True
    }

@app.callback(Output('cytoscape-update-layout', 'zoom'),
              Input('rescale', 'n_clicks'),
              Input('zoom-in', 'n_clicks'),
              Input('zoom-out', 'n_clicks'),
              State('cytoscape-update-layout', 'zoom'),prevent_initial_call=True)
def update_layout(n_clicks,plus,minus,curr_zoom):
    print('Last zoom',curr_zoom)
    ctx = dash.callback_context
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs,
        'state' : ctx.states
    }, indent=2)
    print('zoom area',ctx_msg)
    #print('states', ctx.states)
    trigger_source=ctx.triggered
    #if curr_zoom:
    if trigger_source[0]['prop_id']=='rescale.n_clicks':
         return 0.75
    elif trigger_source[0]['prop_id']=='zoom-in.n_clicks':
         print('current zoom in value',curr_zoom+0.5)
         return curr_zoom+0.5
    elif trigger_source[0]['prop_id']=='zoom-out.n_clicks':
        if curr_zoom<1:
            print('current zoom out value lower',curr_zoom)
            return 0.75
        elif curr_zoom>=1:
            print('current zoom out value',curr_zoom-0.5)
            return curr_zoom-0.5
@app.callback(
   Output("location", "value"),
   Output("function", "value"),
   Output("process", "value"),
   Output("pathway", "value"),
   Output("disease", "value"),
   Output("tissue", "value"),
   Output('apply_fil', 'n_clicks'),
   Input('reset','n_clicks')
    )
def reset_filer(n_clicks):
    if n_clicks==0:
        raise PreventUpdate
    else:
        return None,None,None,None,None,None, 1

@app.callback(
              Output('intermediate-value','children'),
              Output('unmatch-value','children'),
              Input('save button', 'n_clicks'),
              State('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('Textarea Input', 'value'),
              State('query_type','value')
          #[State('Filename Input', 'value')]
          )
def storing_prots(n_clicks,list_of_contents, list_of_names, list_of_dates,inp_prot,qtype):


    ctx = dash.callback_context
    trigger_source=ctx.triggered
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs,
        'state' : ctx.states
    }, indent=2)
    #print('The entry click with id type',ctx_msg)
    #print('states', ctx.states.keys())
    #trigger_source=ctx.triggered
    qtype_chk=ctx.states['query_type.value']

    if n_clicks == 0:
        raise PreventUpdate
    else:
        my_data = db.database1
        if list_of_contents is not None:
                print('using file to fetch')
                div_children = parse_contents(list_of_contents, list_of_names) 
        elif inp_prot is not None:
                print('using text area')
                div_children = [x.upper() for x in inp_prot.split("\n") if x]
        if qtype_chk=='gene_symbol':
            my_res=my_data.find({},{'name':1,'_id':0})
            db_prots=pd.DataFrame(list(my_res))
            nf=list(set(div_children)-set(db_prots['name'].to_list()))


            return div_children,nf
        elif qtype_chk=='uniprot_id':
            my_res=my_data.find({},{'id':1,'_id':0})
            db_prots=pd.DataFrame(list(my_res))
            nf=list(set(div_children)-set(db_prots['id'].to_list()))
            new_div=id_conversion(div_children)
            return new_div,nf

@app.callback(Output("unmatch_prot", "data"),
            Input('unmatch-value', 'children'),
            prevent_initial_call=True)

def unmatch_prots(search_prot):
#def unmatch_prots(n_clicks):


    #part1
    #search_prot=['TACR1','F2R','YY1','HIF1','P53']
    print('Unmatch not called')
    ctx = dash.callback_context
    print('states', ctx.states)
    trigger_source=ctx.triggered
    if trigger_source[0]['prop_id']=='unmatch-value.children':
        #my_data = db.database1
        #qtype_chk=ctx.states['query_type.value']
        #my_res=my_data.find({},{'name':1,'_id':0})
        #db_prots=pd.DataFrame(list(my_res))
        #nf=list(set(search_prot)-set(db_prots['name'].to_list()))
        #print('This are unmatched',nf)
        if len(search_prot)>0:
            nf_df = pd.DataFrame({'Not Found':search_prot})
            #print('unmatched',nf_df)

            return dcc.send_data_frame(nf_df.to_csv, "unmatched_proteins.csv")
@app.callback(
       Output("location", "options"),
       Output("function", "options"),
       Output("process", "options"),
       Output("pathway", "options"),
       Output("disease", "options"),
       Output("tissue", "options"),
       Output('memory_net', 'data'),
       Input('intermediate-value','children')
       
    )
def drop_down_feed(div_children):

    ctx = dash.callback_context
    #print('states', ctx.states.keys())
    trigger_source=ctx.triggered
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs,
        'state' : ctx.states
    }, indent=2)
    #print('Trigger of cb for new drop down',ctx_msg)


    if div_children is None:
        print('No trigger for down')
        raise PreventUpdate
    else:
        query=div_children
        if trigger_source[0]['prop_id']=='intermediate-value.children':
            cy_edges,cy_nodes,nodes=query_db_net(query)
            #print('Today we found them',nodes)
            
            options,options1,options2,options3,options4,options5=fetch_dropdown(nodes)
            print(f'Number of nodes {len(cy_nodes)}and Number of edges {len(cy_edges)} and options{len(options)}')

            return  options, options1, options2, options3,options4,options5,cy_edges+cy_nodes



 

@app.callback(
                Output(component_id='cytoscape-update-layout', component_property ='elements'),
                Input('intermediate-value','children'),
                Input('apply_fil', 'n_clicks'),
                State('location', 'value'),
                State('function', 'value'),
                State('process', 'value'),
                State('pathway', 'value'),
                State('disease', 'value'),
                State('tissue', 'value'),
                State('memory_net', 'data')
          #[State('Filename Input', 'value')]
          )

#def storing_prots(n_clicks,sel_loc,sel_fun,sel_proc,sel_path,sel_dis,sel_tiss,list_of_contents, list_of_names, list_of_dates,session_net,inp_prot,curr_net):
def storing_prots(div_children,filters,sel_loc,sel_fun,sel_proc,sel_path,sel_dis,sel_tiss,sess_net):

    #part1
    ctx = dash.callback_context
    #print('states', ctx.states.keys())
    trigger_source=ctx.triggered
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs
    }, indent=2)
    #print('Trigger of cb for network generation',ctx_msg)

    if div_children is None and filters == 0:
        raise PreventUpdate
    else:
        

        query=div_children
        #query=prots
        #print('user input',prots)
        #data = db.database1#check that after making entry this line shud be re-runned or not ?
        if trigger_source[0]['prop_id']=='intermediate-value.children':
            cy_edges,cy_nodes,nodes=query_db_net(query)
            #print('Today we found them',nodes)
            print(f'Network info: Number of nodes {len(cy_nodes)}and Number of edges {len(cy_edges)}')
            #options,options1,options2,options3,options4,options5=fetch_dropdown(nodes)
            return  cy_edges+cy_nodes


        elif trigger_source[0]['prop_id']=='apply_fil.n_clicks':
            ctx = dash.callback_context
            call_state=ctx.states


            loc_fil=call_state["location.value"]
            fun_fil=call_state["function.value"]
            proc_fil=call_state["process.value"]
            path_fil=call_state["pathway.value"]
            dis_fil=call_state["disease.value"]
            exp_fil=call_state["tissue.value"]

            filter_ls=multi_filter_query(loc_fil,fun_fil,proc_fil,path_fil,dis_fil,exp_fil)
            print(f'Network Query {len(filter_ls)}')
            new_el=update_nodes(sess_net,filter_ls)
            return new_el

    
    

    #print(div_children)
    

@app.callback([Output(component_id='complex_para', component_property ='data'),
              Output('network_para_graph', 'figure'),
              Output('location_graph', 'figure'),
              Output('sub_network_para_graph', 'figure'),
              #Output('Does_effect_graph', 'figure'),
              Output(component_id='hallmark_network', component_property ='elements'),
              #Output('Gets_effect_graph', 'figure'),

              Output(component_id='signa_network', component_property ='elements'),
              Output('top_stats','data'),
              Output('top_pathway','figure'),
              Output('net_info','children'),
              Output('analyse_status','children')
              ],
          [Input('cp_calculate', 'n_clicks')],
          [State('cytoscape-update-layout', 'elements')])
def calculate_network_para(n_clicks,curr_elements):
    fig2=get_dummy_fig()
    disp_img=imread("G:/PPI/website/website(konnect2prot) v4.5.10/assets/error_message.png")
    fig3=px.imshow(disp_img)
    fig3.update_xaxes(showticklabels=False)
    fig3.update_yaxes(showticklabels=False)

    disp_img=imread("G:/PPI/website/website(konnect2prot) v4.5.10/assets/err_msg_size.png")
    fig4=px.imshow(disp_img)
    fig4.update_xaxes(showticklabels=False)
    fig4.update_yaxes(showticklabels=False)
    if n_clicks>0:
        print('7.Analysis')

        g=cyto_2_graph(curr_elements)# Getting the network

        # Basic statistics
        node_num=g.number_of_nodes()
        edge_num=g.number_of_edges()
        print(f'Inside analyis with node {node_num} and edge {edge_num}')
        a=dict(g.degree())
        ai=dict(g.in_degree())
        ao=dict(g.out_degree())
        d_list=np.array(list(a.values()))
        p_l=d_list[d_list!=0]
        

        if len(p_l)==0:
            avg=0
            clus_coeff=0
            b=0
            c=0
            d=0
            return [],fig4,fig3,fig3,[],[],[],fig3,[],['Unable to analyse, network size too small.']
            #return [],[],[],[],[],[],[],[],[],['Unable to analyse, network size too small.']

        else:
            avg=sum(p_l)/len(p_l)
            clus_coeff=nx.average_clustering(g)
            b=nx.betweenness_centrality(g)
            c=nx.clustering(g)
            d=nx.closeness_centrality(g)

            print('Done so far')
            #perco=nx.katz_centrality(g,max_iter=10000,tol=1e-02)
            top_prots=nx.voterank(g,15)

        
        cy_edges,cy_nodes,nodes=query_signa_net(top_prots)
        cy_edges2,cy_nodes2,nodes2=query_hallmark_net(top_prots)



        #e=nx.eigenvector_centrality(g)
        #final=[a,ai,ao,b,c,d,perco]# Just remove katz
        final=[a,ai,ao,b,c,d]
        #complex_para=pd.DataFrame(final,index=['Degree','InDegree','OutDegree','Betweenness','Clustering','Closeness','Katz']).transpose()
        complex_para=pd.DataFrame(final,index=['Degree','InDegree','OutDegree','Betweenness','Clustering','Closeness']).transpose()
        
        #deg_dist=gen_graph(complex_para)
        #complex_para['Name']=complex_para.index
        complex_para.reset_index(level=0, inplace=True)
        top_complex_para=complex_para[complex_para['index'].isin(top_prots)]
        top_complex_para.set_index('index', inplace=True)

        top_prot_graph=px.bar(top_complex_para.iloc[:,1:],barmode='group',title="Topological parameters of top proteins")
        top_prot_graph.update_layout( xaxis_title="Top proteins", yaxis_title="Parameter value" )
        top_complex_para.reset_index(level=0,inplace=True)
        top_complex_para=top_complex_para.rename(columns={'index':'Name'})
        
        ####################
        db=client.ppi
        my_data = db.database1
        my_res=my_data.find({'name':{'$in':top_prots}},{'name':1,'location':1,'pclass':1,'pathways':1,'biological_proc':1,'_id':0})
        df=pd.DataFrame(columns=['Name','Location'])
        df_path=pd.DataFrame(columns=['Name','Pathways'])
        #df_temp=pd.DataFrame(columns=['Name','Location'])
        #df_class=pd.DataFrame(columns=['Name','Protein Class','Location','Pathways','Bio_Process'])
        df_class=pd.DataFrame(columns=['Name','Protein Class','Location'])
        #locs=itm['location']
        #print('Not iteratble',locs)
        for itm in my_res:
            print('not iterable',type(itm['location']),itm['name'])
            locs=itm['location']
            my_loc=",".join(locs)
            try:

                path_way=itm['pathways']
            except:
                path_way=[]
                continue
            my_path=",".join(path_way)
            #df_temp = df_temp.append({'Name': itm['name'], 'Location':my_loc}, ignore_index=True)
            df_class = df_class.append({'Name': itm['name'], 'Protein Class':itm['pclass'],'Location':my_loc}, ignore_index=True)
            
            for loc in locs:
                df = df.append({'Name': itm['name'], 'Location':loc}, ignore_index=True)

            for path in path_way:
                df_path = df_path.append({'Name': itm['name'], 'Pathways':path}, ignore_index=True)


        print('My_first_df')

        loc_graph = px.bar(df, x="Location", y="Name", color="Name", title="Location of top spreaders")
        loc_graph.update_yaxes(visible=False, showticklabels=False)

        #path_graph = px.bar(df_path, x="Pathways", y="Name", color="Name", title="Pathways of top proteins")
        #path_graph.update_yaxes(visible=False, showticklabels=False)
        path_clus=get_path_cluster(top_prots)
        #print('This is pathways cluster',path_clus)
        if path_clus.empty:
            path_graph=get_dummy_fig('Spreaders pathway not found')
        else:
            columns = list(path_clus.columns.values)
            rows = list(path_clus.index)
            path_graph=dashbio.Clustergram(
            data=path_clus.loc[rows].values,
            #title="Pathway clustergram of the triggers",
            column_labels=columns,
            row_labels=rows,
            # color_threshold={
            #     'row': 250,
            #     'col': 700
            # },
            # color_map= [
            # [0.0, '#636EFA'],
            # [0.25, '#AB63FA'],
            # [0.5, '#FFFFFF'],
            # [0.75, '#E763FA'],
            # [1.0, '#EF553B']],
            color_map= [(0.00, "#EF553B"),   (0.5, "#EF553B"),
                        (0.5, "#636EFA"),  (1.00, "#636EFA")],
            line_width=2,
            #hidden_labels='row',
            #cluster='column',
            height=800,
            width=1200
            )
            #path_graph.update_layout(showlegend=True)




        ##################
        tissue_df=get_top_tissue(top_prots)
        #print(tissue_df)
        tissue_fig=px.imshow(   tissue_df,
                                title="High tissue specificity of the spreaders",
                                color_continuous_scale=[(0.00, "blue"),
                                                        (0.5, "blue"),
                                                        (0.5, "yellow"),
                                                        (1.00, "yellow")]
                                                        )
        # tissue_fig.update_layout(
        #     showlegend=True,
        #     coloraxis_showscale=False,
            
        #     xaxis=dict(tickmode='linear'),
        #     yaxis=dict(tickmode='linear')
        #     )

        tissue_fig.update_layout(
                xaxis=dict(tickmode='linear'),
                yaxis=dict(tickmode='linear'),
                coloraxis_colorbar=dict(
                title="Specificity",
                tickvals=[0,1],
                ticktext=["Not High","High"]))
        #sub_complex_para=pd.DataFrame()
        #sub_complex_para['Betweenness']=complex_para['Betweenness']
        #sub_complex_para['Degree']=complex_para['InDegree']+complex_para['OutDegree']
                #html.H5('Complex Network paramters'),
        fig = px.scatter(complex_para, x="Degree", y="Betweenness",title="Degree vs Betweenness", hover_data=['index'],color="Degree")
        #fig = px.scatter(sub_complex_para, x="Degree", y="Betweenness",title="Degree vs Betweenness",color="Degree")
        #print("Index names",complex_para.index.name)
        complex_para = complex_para.rename(columns = {'index':'Name'})
        d_table=complex_para.to_dict('rows')

        
        my_data = db.database1
        my_res=my_data.find({ 'name':{'$in':top_prots}},{'name':1,'pdb_id':1,'ligands':1,'_id':0})
        temp=list(my_res)
        df=pd.DataFrame(temp)
        my_struct_df=pd.DataFrame(columns=['Name','Inhibitors','PDB complex(Count)'])
        for id_,item in df.iterrows():
            prot_name=item['name']
            if item['ligands']!='NA':
                temp=pd.DataFrame(item['ligands'])
                lig_cnt=len(temp[temp == True].index)
                temp = temp.apply(lambda x : True if x['interaction_types'] == 'inhibitor' else False, axis = 1)
            else:
                lig_cnt=0
            if item['pdb_id']!='NA':
                pdb_cnt=len(item['pdb_id'])
            else:
                pdb_cnt=0
            my_struct_df=my_struct_df.append({'Name':prot_name,'Inhibitors':lig_cnt,'PDB complex(Count)':pdb_cnt},ignore_index=True) 
        result_1 = reduce(lambda x,y: pd.merge(x,y, on='Name', how='outer'), [top_complex_para,df_class,my_struct_df])

        #############################
        top_prots_stat=result_1.to_dict('rows')
        #print('sub_hallmark',cy_edges2+cy_nodes2)
        row1=f'No. of nodes: {node_num}'
        row2=f'No. of edges: {edge_num}'
        row3=f'Average degree: {avg:.3f}'
        row4=f'Clustering Coeff. {clus_coeff:.3f}'
        #row5='Network efficiency'+net_eff
        
        
        out_div=html.Div(
                    [
                        html.H5("Network statistics"),
                        html.P([
                                row1,
                                html.Br(),
                                row2,
                                html.Br(),
                                row3,
                                html.Br(),
                                row4]
                        )
                    ],
                    style={
                    'padding':'10px',
                    'margin':'10px',
                    'box-shadow': '0 3px 5px rgba(57, 63, 72, 0.3)'
                    }
                )


        #return d_table,fig,tissue_fig,loc_graph,does_graph,gets_graph, top_prots_stat,
        msg=['Scroll down to global properties panel for results']
        return d_table,fig,tissue_fig,loc_graph,cy_edges2+cy_nodes2,cy_edges+cy_nodes, top_prots_stat,path_graph,out_div,msg
    else:
        
        return [],fig2,fig2,fig2,[],[],[],fig2,[],[]



    
@app.callback(Output("hallmark_dwnload", "data"),
            [Input('hall_d_button', 'n_clicks')],
            [State('hallmark_network', 'elements')],
            prevent_initial_call=True,)

def hallmarks_prots(n_clicks,hall_net):

    #part1
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_source=ctx.triggered
        print('In download button')
        if trigger_source:
            if trigger_source[0]['prop_id']=='hall_d_button.n_clicks':
                hall_df=pd.DataFrame(get_edges(hall_net))
                
                #print('unmatched',hall_df)

                return dcc.send_data_frame(hall_df.to_csv, "protein_with_hallmarks.csv")

@app.callback(Output("signa_dwnload", "data"),
            [Input('signa_d_button', 'n_clicks')],
            [State('signa_network', 'elements')],
            prevent_initial_call=True,)

def signa_prots(n_clicks,hall_net):

    #part1
    ctx = dash.callback_context
    #print('In signa dwnload',ctx)
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs
    }, indent=2)
    #print('Trigger of cb',ctx_msg)
    if ctx.triggered:
        trigger_source=ctx.triggered

        if trigger_source:

            if trigger_source[0]['prop_id']=='signa_d_button.n_clicks':
                #print('download init')
                hall_df=pd.DataFrame(get_edges(hall_net))
                
                #print('unmatched',hall_df)

                return dcc.send_data_frame(hall_df.to_csv, "protein_with_signalink.csv")
    
    

@app.callback(Output('process_graph', 'figure'),
              #[Input('save button', 'n_clicks'),Input('proc_plot', 'value')],
              Input('cp_calculate', 'n_clicks'),
               [State('cytoscape-update-layout', 'elements')])
def make_process_graph(clicked,sess_net):
        #total_prot=list(set(total_prot))
        if clicked>0:
                numbs='not_all'
                total_prot=get_nodes(sess_net)
                print('4.process')
                #if not prots:
                    #print('here')
                    #pval=[1,2,3,4]
                    #rank=[1,2,3,4]
                    #name=['dummy1','dummy2','dummy3','dummy4']
                    #fig = px.bar( x=pval, y=rank,title="Enriched process of interactome", orientation='h' , text=name,labels=dict(x="P values of dummy processes", y="Rank dummy"))
                    #return get_dummy_fig()
                #my_data=db.edge_lists2
                #my_res=my_data.find({ '$and': [ { 'ENTITYA':{'$in':total_prot }}, { 'ENTITYB':{'$in':total_prot} } ] },{'ENTITYA':1,'ENTITYB':1,'EFFECT':1,'PMID':1,'_id':0})
                #my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':total_prot }},{ "ENTITYA": {'$in':total_prot }}]},{'ENTITYA':1,'ENTITYB':1})
                
                #my_prots=[]
                #for el in my_res:
                    #my_prots.append(el['ENTITYA'])
                    #my_prots.append(el['ENTITYB'])
                #my_prots=list(set(my_prots))
                my_prots=get_nodes(sess_net)
                data_name='GO_Biological_Process_2018'
                ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/addList'
                genes_str='\n'.join(my_prots)
                description = 'Example gene list'
                payload = {
                    'list': (None, genes_str),
                    'description': (None, description)
                }

                response = requests.post(ENRICHR_URL, files=payload)
                if not response.ok:
                    raise Exception('Error analyzing gene list')

                data = json.loads(response.text)
                


                ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/enrich'
                query_string = '?userListId=%s&backgroundType=%s'
                user_list_id = data['userListId']
                gene_set_library = data_name
                response = requests.get(
                    ENRICHR_URL + query_string % (user_list_id, gene_set_library)
                 )
                if not response.ok:
                    raise Exception('Error fetching enrichment results')

                data = json.loads(response.text)
                paths=data[data_name]
                

                rank=[]
                name=[]
                pval=[]
                for path in paths:
                  
                  rank.append(path[0])
                  name.append(path[1])
                  pval.append(path[2])
                if numbs=='not_all':
                    
                    fig = px.bar( x=-np.log(pval[0:10]), y=rank[0:10],title="Enriched processes of interactome", orientation='h' , text=name[0:10],labels=dict(x="-log(P value)", y="Processes"))
                    fig.update_yaxes(autorange="reversed",showticklabels=False)
                    fig.update_traces(textposition="inside")
                else:
                    fig = px.bar( x=pval, y=rank,title="Enriched processes of interactome", orientation='h' , text=name,labels=dict(x="P values of Enriched processes", y="Rank"))


                return fig
        else:
            #pval=[1,2,3,4]
            #rank=[1,2,3,4]
            #name=['dummy1','dummy2','dummy3','dummy4']
            #fig = px.bar( x=pval, y=rank,title="Enriched process of interactome", orientation='h' , text=name,labels=dict(x="P values of dummy processes", y="Rank dummy"))
            return get_dummy_fig()
@app.callback(Output('pclass_graph', 'figure'),
                [Input('cp_calculate', 'n_clicks')],
                [State('cytoscape-update-layout', 'elements')])
def make_protein_class_graph(n_clicks,sess_net):
    total_prot=get_nodes(sess_net)
    #print('5.protein class==>',total_prot)
    if n_clicks>0:
        db=client.ppi_test
        my_data=db.edge_lists2
        #my_res=my_data.find({ '$and': [ { 'ENTITYA':{'$in':total_prot }}, { 'ENTITYB':{'$in':total_prot} } ] },{'ENTITYA':1,'ENTITYB':1,'EFFECT':1,'PMID':1,'_id':0})
        my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':total_prot }},{ "ENTITYA": {'$in':total_prot }}]},{'ENTITYA':1,'ENTITYB':1})
        
        my_prots=[]
        for el in my_res:
            my_prots.append(el['ENTITYA'])
            my_prots.append(el['ENTITYB'])
        my_prots=list(set(my_prots))
        db=client.ppi
        my_data=db.database1
        #total_prot=['ADORA2A','CDK1']
        #my_res=my_data.find({ 'name':{'$in':my_prots }},{'pclass':1})
        my_res=my_data.find({ 'name':{'$in':total_prot }},{'pclass':1})

        p_class=[]
        for res in my_res:
            #print(res)
            try:
                p_class.extend(res['pclass'])
            except Exception as e:
                continue
                
        frequency = collections.Counter(p_class)
        fig = px.bar( x=list(frequency.keys()), y=list(frequency.values()),title="Protein class abundance of interactome" ,labels=dict(x="Protein classes", y="Abundance"))
        
        return fig
    else:
        fig=get_dummy_fig()
        return fig

@app.callback(Output('pathway_graph', 'figure'),
              [Input('cp_calculate', 'n_clicks')],
               [State('cytoscape-update-layout', 'elements')])
def make_pathway_graph(clicked,sess_net):

        numbs='not_all'
        if clicked>0:
        # total_prot=prots
        # print('1.pathway')
        # if clicked>0:
        #     if not prots:
        #         #print('here')
        #         #pval=[1,2,3,4]
        #         #rank=[1,2,3,4]
        #         #name=['dummy1','dummy2','dummy3','dummy4']
        #         #fig = px.bar( x=pval, y=rank,title="Enriched pathways of interactome", orientation='h' , text=name,labels=dict(x="P values of dummy pathways", y="Rank dummy"))
        #         return get_dummy_fig()
        #     my_data=db.edge_lists2
        #     #my_res=my_data.find({ '$and': [ { 'ENTITYA':{'$in':total_prot }}, { 'ENTITYB':{'$in':total_prot} } ] },{'ENTITYA':1,'ENTITYB':1,'EFFECT':1,'PMID':1,'_id':0})
        #     my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':total_prot }},{ "ENTITYA": {'$in':total_prot }}]},{'ENTITYA':1,'ENTITYB':1})
            
        #     my_prots=[]
        #     for el in my_res:
        #         my_prots.append(el['ENTITYA'])
        #         my_prots.append(el['ENTITYB'])
            #my_prots=list(set(my_prots))
            my_prots=get_nodes(sess_net)
            data_name='KEGG_2019_Human'
            ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/addList'
            genes_str='\n'.join(my_prots)
            description = 'Example gene list'
            payload = {
                'list': (None, genes_str),
                'description': (None, description)
            }

            response = requests.post(ENRICHR_URL, files=payload)
            if not response.ok:
                raise Exception('Error analyzing gene list')

            data = json.loads(response.text)
            


            ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/enrich'
            query_string = '?userListId=%s&backgroundType=%s'
            user_list_id = data['userListId']
            gene_set_library = data_name
            response = requests.get(
                ENRICHR_URL + query_string % (user_list_id, gene_set_library)
             )
            if not response.ok:
                raise Exception('Error fetching enrichment results')

            data = json.loads(response.text)
            paths=data[data_name]

            

            rank=[]
            name=[]
            pval=[]
            #print('type pf paval',type(pval))
            for path in paths:
              
              rank.append(path[0])
              name.append(path[1])
              pval.append(path[2])
            if numbs=='not_all':
                
                fig = px.bar( x=-np.log10(pval[0:10]),title="Enriched pathways of interactome", orientation='h' , text=name[0:10],labels=dict(x="-log(P value)", y="Pathways"))
                fig.update_yaxes(autorange="reversed",showticklabels=False)
                fig.update_traces(textposition="inside")
                
                
        
            else:
                fig = px.bar( x=pval, y=rank,title="Enriched pathways of interactome", orientation='h' , text=name,labels=dict(x="P values of Enriched pathways", y="Rank"))


            return fig
        else:
            return get_dummy_fig()

@app.callback(Output('disease_graph', 'figure'),
              [Input('cp_calculate', 'n_clicks')],
                [State('cytoscape-update-layout', 'elements')])
def make_disease_graph(n_clicks,sess_net):
    numbs='not_all'
    #total_prot=prots
    print('6.Disease')
    if n_clicks>0:
        # if not total_prot:
        #     print('Should not be here')
        #     #pval=[1,2,3,4]
        #     #rank=[1,2,3,4]
        #     #name=['dummy1','dummy2','dummy3','dummy4']
        #     #fig = px.bar( x=pval, y=rank,title="Enriched dummy disease of interactome", orientation='h' , text=name,labels=dict(x="P values of dummy processes", y="Rank dummy"))
        #     return get_dummy_fig()
        # my_data=db.edge_lists2
        # #my_res=my_data.find({ '$and': [ { 'ENTITYA':{'$in':total_prot }}, { 'ENTITYB':{'$in':total_prot} } ] },{'ENTITYA':1,'ENTITYB':1,'EFFECT':1,'PMID':1,'_id':0})
        # my_res = my_data.find({'$and':[{ "ENTITYA": {'$in':total_prot }},{ "ENTITYA": {'$in':total_prot }}]},{'ENTITYA':1,'ENTITYB':1})
        
        # my_prots=[]
        # for el in my_res:
        #     my_prots.append(el['ENTITYA'])
        #     my_prots.append(el['ENTITYB'])
        #my_prots=list(set(my_prots))
        my_prots=get_nodes(sess_net)
        #print('to be search',my_prots)
        data_name='ClinVar_2019'
        ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/addList'
        genes_str='\n'.join(my_prots)
        description = 'Example gene list'
        payload = {
            'list': (None, genes_str),
            'description': (None, description)
        }

        response = requests.post(ENRICHR_URL, files=payload)
        if not response.ok:
            raise Exception('Error analyzing gene list')

        data = json.loads(response.text)
        


        ENRICHR_URL = 'http://maayanlab.cloud/Enrichr/enrich'
        query_string = '?userListId=%s&backgroundType=%s'
        user_list_id = data['userListId']
        gene_set_library = data_name
        response = requests.get(
            ENRICHR_URL + query_string % (user_list_id, gene_set_library)
         )
        if not response.ok:
            raise Exception('Error fetching enrichment results')

        data = json.loads(response.text)
        paths=data[data_name]
        if paths:
        

            rank=[]
            name=[]
            pval=[]
            for path in paths:
              
              rank.append(path[0])
              name.append(path[1])
              pval.append(path[2])
            #print('disease_prblem',paths)
            if numbs=='not_all':
                
                fig = px.bar( x=-np.log10(pval[0:10]), y=rank[0:10],title="Enriched diseases of interactome", orientation='h' , text=name[0:10],labels=dict(x="-log(P value)", y="Diseases"))
                fig.update_yaxes(autorange="reversed",showticklabels=False)
                fig.update_traces(textposition="inside")
            else:
                fig = px.bar( x=pval, y=rank,title="Enriched diseases of interactome", orientation='h' , text=name,labels=dict(x="P values of Enriched diseases", y="Rank"))

        else:
            disp_img=imread("G:/PPI/website/website(konnect2prot) v4.5.10/assets/err_msg_size.png")
            fig3=px.imshow(disp_img)
            fig3.update_xaxes(showticklabels=False)
            fig3.update_yaxes(showticklabels=False)
            return fig3

      
        return fig
    else:
        return get_dummy_fig()

#Retreiving indivvidual information

@app.callback(Output('ligand', 'children'),
                  Input('cytoscape-update-layout', 'tapNodeData'))
def displayTapNodeData(data):
    print('node_tap',data)
    ctx = dash.callback_context
    if ctx.triggered:
        my_db=db.database1
        query=list(my_db.find({'name':data['id']},{'_id':0,'ligands':1}))
        
        #print("strcut_debug",struct_detail)
        if query[0]['ligands']!='NA':
            col_order=['ligand_name','drug_concept_id','interaction_types','PMIDs']
            struct_detail=pd.DataFrame(query[0]['ligands'])
            struct_detail=struct_detail[col_order]
            #struct_detail.sort_index(axis=0,inplace=True)
            #print(struct_detail.head())
            #struct_detail=struct_detail.rename(columns={'Gene_ID':'Uniprot_ID'})
            #print('struct_detail is not empty')
        
        #print('dock cols',complex_para.columns)
            table_3 = html.Div([
            #html.H5('Complex Network paramters'),
                    dt.DataTable(
                    data=struct_detail.to_dict('rows'),
                   # data=docking,
                    columns=[{'name': i, 'id': i} for i in struct_detail.columns],
                    fixed_rows={ 'headers': True, 'data': 0 },
                    #style_table={'height':'300px' ,'overflowY': 'scroll'},
                    style_data={ 'border': '1px solid black' },
                    style_cell={'width': '150px'},
                    page_size=5,
                    export_format='xlsx'
                )
            ],style={'height':'100%','width':'100%'})
        else:
            #print('no struct detail')
            table_3 = html.Div(["No data found"],style={'height':'100%','width':'100%'})
    else:
        table_3 = html.Div(["Tap desired node"],style={'height':'100%','width':'100%'})


    #print("docking data sent ",table_3)
    return table_3
    
    

@app.callback(Output('docking', 'children'),
                  Input('cytoscape-update-layout', 'tapNodeData'))
def displayTapNodeData(data):
    print("tap node data for structure",data)
    ctx = dash.callback_context
    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs
    }, indent=2)
    #print('Trigger of cb',ctx_msg)
    if ctx.triggered:
        my_db=db.database1
        query=list(my_db.find({'name':data['id']},{'_id':0,'structure_info':1}))
        struct_detail=pd.DataFrame(query[0]['structure_info'])
        #print("strcut_debug",struct_detail)
        if query[0]['structure_info']:
            #struct_detail=struct_detail.rename(columns={'Gene_ID':'Uniprot_ID'})
            struct_detail.drop('Gene_ID',axis=1,inplace=True)
            #print('struct_detail is not empty')
        
        #print('dock cols',complex_para.columns)
            table_3 = html.Div([
            #html.H5('Complex Network paramters'),
                    dt.DataTable(
                    data=struct_detail.to_dict('rows'),
                   # data=docking,
                    columns=[{'name': i, 'id': i} for i in struct_detail.columns],
                    fixed_rows={ 'headers': True, 'data': 0 },
                    #style_table={'height':'300px' ,'overflowY': 'scroll'},
                    style_data={ 'border': '1px solid black' },
                    style_cell={'width': '150px'},
                    page_size=5,
                    export_format='xlsx'
                )
            ],style={'height':'100%','width':'100%'})
        else:
            #print('no struct detail')
            table_3 = html.Div(["No data found"],style={'height':'100%','width':'100%'})
    else:
        table_3 = html.Div(["Tap desired node"],style={'height':'100%','width':'100%'})


    #print("docking data sent ",table_3)
    return table_3


@app.callback(Output('disease_mutation', 'children'),
                  Input('cytoscape-update-layout', 'tapNodeData'))
def displayTapNodeData(data):
    print("tap node data for structure",data)
    ctx = dash.callback_context
    if ctx.triggered:
        my_db=db.database1
        query=list(my_db.find({'name':data['id']},{'_id':0,'disease_mut':1}))
        
        #print("strcut_debug",struct_detail)
        if query[0]['disease_mut']!='NA':
            struct_detail=pd.DataFrame(query[0]['disease_mut'])
            struct_detail.drop(['gene','uniprot'],axis=1,inplace=True)
            #struct_detail=struct_detail.rename(columns={'Gene_ID':'Uniprot_ID'})
            #print('struct_detail is not empty')
        
        #print('dock cols',complex_para.columns)
            table_3 = html.Div([
            #html.H5('Complex Network paramters'),
                    dt.DataTable(
                    data=struct_detail.to_dict('rows'),
                   # data=docking,
                    columns=[{'name': i, 'id': i} for i in struct_detail.columns],
                    fixed_rows={ 'headers': True, 'data': 0 },
                    #style_table={'height':'300px' ,'overflowY': 'scroll'},
                    style_data={ 'border': '1px solid black' },
                    style_cell={'width': '150px'},
                    page_size=5,
                    export_format='xlsx'
                )
            ],style={'height':'100%','width':'100%'})
        else:
            #print('no struct detail')
            table_3 = html.Div(["No data found"],style={'height':'100%','width':'100%'})
    else:
        table_3 = html.Div(["Tap desired node"],style={'height':'100%','width':'100%'})


    #print("docking data sent ",table_3)
    return table_3

@app.callback(Output('func_info', 'children'),
              Input('cytoscape-update-layout', 'tapNodeData'))
def displayTapNodeData(data):
    print("tap node data for function",data)
    ctx = dash.callback_context
    if ctx.triggered:
        gene,protein,func_txt=get_func_info(data['id'])
        label=f'Uniprot:{protein}, Gene:{gene}'

        out_div=html.Div(
                    [
                        html.H5(label),
                        html.P(
                            func_txt
                        )
                    ],
                    style={
                    'padding':'10px',
                    'margin':'10px',
                    #'box-shadow': '0 3px 5px rgba(57, 63, 72, 0.3)'
                    'border-color': '#dce8fc'
                    }
                )


        #return out_div
    else:
        out_div=html.Div(["Tap desired node"],style={'height':'100%','width':'100%'})
    return out_div



@app.callback(Output('click_info', 'children'),
                  Input('cytoscape-update-layout', 'tapEdgeData'))

def displayTapEdgeData(ed_data):
    ctx = dash.callback_context
    if ctx.triggered:
        print('edge_tap',ed_data)
        data=ed_data
        #print(data)
        #my_data=db.edge_lists2
        #my_res=my_data.find({ '$and': [ { 'ENTITYA':data['source'] }, { 'ENTITYB':data['target'] } ] },{'EFFECT':1,'PMID':1,'_id':0})
        my_data=db.edge_list_ref
        my_res=my_data.find({ '$and': [ { 'ENTITYA':data['source'] }, { 'ENTITYB':data['target'] } ] },\
                            {'ENTITYA':1,'IDA':1,\
                             'ENTITYB':1,'IDB':1,\
                             'EFFECT':1,'MECHANISM':1,'PMID':1,'_id':0})
        edges=list(my_res)
        complex_para=pd.DataFrame(edges)
        #deg_dist=gen_graph(complex_para)
        #complex_para['Name']=complex_para.index
        #complex_para.reset_index(level=0, inplace=True)

        table = html.Div([
                #html.H5('Complex Network paramters'),
                    dt.DataTable(
                    data=complex_para.to_dict('rows'),
                   # data=docking,
                    columns=[{'name': i, 'id': i} for i in complex_para.columns],
                    fixed_rows={ 'headers': True, 'data': 0 },
                    #style_table={'height':'300px' ,'overflowY': 'scroll'},
                    style_data={ 'border': '1px solid black' },
                    style_cell={'width': '150px'},
                    export_format='xlsx'
                )
            ],style={'height':'100%','width':'100%'})
        #my_res
        #return data['source']+" " + my_res[0]['EFFECT'].upper() +" "+ data['target'] +" " + " Reference:" +"PMID" +my_res[0]['PMID'].upper()
        
    else:
        table = html.Div(["Tap desired edge"],style={'height':'100%','width':'100%'})
    return table


        

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'),
              Input('func_info', 'children'),
              Input('click_info', 'children'),
              State('docking', 'children'),
              State('ligand', 'children'),
              State('disease_mutation', 'children'),
              State('click_info', 'children'),
              State('func_info', 'children')
              )
def render_content(tab,node_,edge_,dock,lig,dis_mut,ref,funcs):
    print('Tab init',tab)
    ctx = dash.callback_context

    ctx_msg = json.dumps({
        
        'triggered': ctx.triggered,
        'inputs': ctx.inputs,
        'state' : ctx.states
    }, indent=2)
   #print('callbacks',ctx_msg)
    
    if tab == 'tab-0':
        #print('Tab val',funcs)
        return funcs
    elif tab == 'tab-1':
        #print('Tab val',dock)
        return dock
    elif tab == 'tab-2':
        #print('Tab val',lig)
        return lig
    elif tab == 'tab-3':
        #print('Tab val',dis_mut)
        return dis_mut
    elif tab == 'tab-4':
        return ref


# Main
if __name__ == '__main__':
    context = ('ebe918fa63877c64.crt','ebe918fa63877c64.key')
    #app.run_server(debug=True)
    #app.run_server(host='10.0.0.37',port=80,debug=True)
    app.run_server(host='10.0.0.37',debug=True)
    # app.server.run(debug=True, threaded=True)
