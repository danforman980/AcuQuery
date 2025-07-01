#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 12:29:18 2025

@author: DanielForman
"""

from dash import Dash, html, callback, Output, Input, State, clientside_callback, dcc
import pandas as pd
import webbrowser
import dash_bootstrap_components as dbc
import sqlite3 as sql
import dash_ag_grid as dag
from pdf2image import convert_from_path
import os

#DO MORE TESTING WITH 10006

os.chdir('/Users/DanielForman/Documents/Database_work/AcuQuery')

#function to select data from the database using the HGNC id as the key

def sql_search(hgnc_id, db, file):
    conn = sql.connect(file)
    cur = conn.cursor()
    data = pd.read_sql_query("SELECT * FROM "+db+" where HGNC_id = (" + "'HGNC:" + str(hgnc_id) + "'" + ")", conn)
    return(data)

#intialising and setting up the theme for the app
    
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL, dbc_css], suppress_callback_exceptions=False)
server = app.server

imgURL = 'https://www.apconix.com/wp-content/uploads/2018/12/apconix-logo-wstrap.png'

#dark mode option (unused right now)
color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch( id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

#setting up the layout of the app

tsa_target = html.Div(dbc.FormFloating(
    [
        dbc.Input(id="tsa_target", placeholder="", type = 'text'),
        dbc.Label(children = "Enter HGNC ID") 
        ]
    )
)

file_path = html.Div(dbc.FormFloating(
    [
        dbc.Input(id="file_path", placeholder="", type = 'text'),
        dbc.Label(children = "Enter File Path") 
        ]
    )
)

target_button = dbc.Button("Search", id='target_button',className="me-1", n_clicks=0)
test_button = dbc.Button("Search", id='tb',className="me-1", n_clicks=0)

selection_column = dbc.Card(
    [ 
    dbc.Row([dbc.Col(tsa_target, width=8), dbc.Col(target_button, width=4)], align="center"),
    dbc.Row(dbc.Col(file_path, width=8)),
    dbc.Row(html.Br())
    ],
    className="border-0",
    
)
                    
gene_card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(id="gene_table_1"),
            html.Br(),
            html.Div(id="gene_table_2"),
            html.Br(),
            html.Div(id="gene_table_3"),
        ]
    ),
    className="border-0",
)

ID_card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(id="ID_table_1"),
            html.Br(),
            html.Div(id="ID_table_2"), 
            html.Br(),
            html.Div(id="ID_table_3")
        ]
    ),
    className="border-0",
)

ortho_card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(id="ortho_table"),
        ]
    ),
    className="border-0",
)

Plot_card = dbc.Card(
    dbc.CardBody(
        dbc.Tabs(
            children = 
            [
                dbc.Tab([html.Img(id="Protein_Expression_Plot", style={'width': '70%', 'height': '70%'})], label="Protein_Expression_Plot"),
                dbc.Tab([html.Img(id="SingleCell_RNAseq_Plot", style={'width': '70%', 'height': '70%'})], label="SingleCell_RNAseq_Plot"),
                dbc.Tab([html.Img(id="Human_Bulk_RNAseq_Plot", style={'width': '70%', 'height': '70%'})], label="Human_Bulk_RNAseq_Plot"),
                dbc.Tab([html.Img(id="Immune_Plot", style={'width': '70%', 'height': '70%'})], label="Immune_Plot"),
                dbc.Tab([html.Img(id="Cancer_Expression_Plot", style={'width': '70%', 'height': '70%'})], label="Cancer_Expression_Plot"),
            ]
    ),
        ),
    className="border-0",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P(children="This is tab 2!", className="card-text"),
        ]
    ),
    className="border-0",
)

protein_isoform_card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(id="protein_isoform_table"),
        ]
    ),
    className="border-0",
)

target_info = dbc.Tabs(
    children = [
        dbc.Tab(gene_card, tab_id='gene_card', label="Gene Overview", tab_style={"marginLeft": "auto"}),
        dbc.Tab(ID_card, tab_id='ID_card', label="DataBase IDs"),
        dbc.Tab(protein_isoform_card, tab_id='protein_isoform_card', label="Protein Isoforms"),
        dbc.Tab(ortho_card,  tab_id='ortho_card',label="Orthologues"),
        dbc.Tab(tab2_content, label="Paralogues"),
        dbc.Tab(tab2_content, label="Pharmacology"),
        dbc.Tab(tab2_content, label="Risk Association"),
        dbc.Tab(tab2_content, label="NeoSubstrate"),
        dbc.Tab(tab2_content, label="Chemical Info", tab_style={"marginLeft": "auto"}),
        dbc.Tab(Plot_card, tab_id='Plots', label="Plots"),
    ], id='target_info'
)
                      

columns = dbc.Row(
    [
        dbc.Col(selection_column, width=3),
        dbc.Col(target_info, width=9),
    ]
)

app.layout = dbc.Card(dbc.Col(
    [
     dbc.Row([dbc.Col(html.Div(html.H1(id='title', children='APP NAME', style={"text-decoration": "underline"})), md = 10), dbc.Col(html.Div(html.Img(src=imgURL)))]),
     dbc.Row(html.Br()),
     dbc.Row(columns)
     ],
    className="dbc"
    )
)

#dark mode?
#dbc.Row([dbc.Col(html.Div(html.H1(id='title', children='AcuQuery', style={"text-decoration": "underline"})), md = 10), dbc.Col([dbc.Row([color_mode_switch, "Dark Mode"]), dbc.Row(html.Div(html.Img(src=imgURL)))])]),

#function to get basic gene data from the database before generating the required tables

@callback(
    Output("gene_table_1", "children"),
    Output("gene_table_2", "children"),
    Output("gene_table_3", "children"),
    Output("ID_table_1", "children"),
    Output("ID_table_2", "children"),
    Output("ID_table_3", "children"),
    State("tsa_target", "value"),
    State("file_path", "value"),
    Input("target_button", "n_clicks"),
)
def gene_ID_Tables(tsa_target, file, n_clicks):
    if n_clicks:
        try:
            #getting the appropriate data from the database using the query functions
            gene_data = sql_search(tsa_target, 'gene_info', file)
            corpus_sizes = sql_search(tsa_target, 'corpus_sizes',file)
            corpus_sizes = corpus_sizes.drop(columns=['HGNC_id'])
            ID_data = sql_search(tsa_target, 'gene_IDs',file)
            
        except:
            return("No Data Found"," "," ","No Data Found"," ", " ")
        else:
            #check and display if data is not found
            if gene_data.empty:
                return("No Data Found"," "," ","No Data Found"," ", " ")
            else:
                
                #formatting the data into the correctly sized tables for display
                gene_data_1 = gene_data.iloc[:, 1:5]
                gene_data_2 = gene_data.iloc[:, 5:]
                corpus_sizes = corpus_sizes.iloc[:, 1:]
                gene_data_2 = gene_data_2.join(corpus_sizes)
                gene_data_3 = gene_data_2.iloc[:, 5:]
                gene_data_2 = gene_data_2.iloc[:, 1:5]
            
                gene_data_1 = gene_data_1.rename(columns=lambda name: name.replace('_', ' '))
                gene_data_2 = gene_data_2.rename(columns=lambda name: name.replace('_', ' '))
            
                ID_data_1 = ID_data.iloc[:, 1:7]
                ID_data_2 = ID_data.iloc[:, 7:13]
                ID_data_3 = ID_data.iloc[:, 13:]
                
                ID_data_1 = ID_data_1.rename(columns=lambda name: name.replace('_', ' '))
                ID_data_2 = ID_data_2.rename(columns=lambda name: name.replace('_', ' '))
                ID_data_3 = ID_data_3.rename(columns=lambda name: name.replace('_', ' '))
                
                #generating the tables with the data extracted from the database 
                
                gene_data_1 = dag.AgGrid(
                    rowData=gene_data_1.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 190} for i in gene_data_1.columns],
                    columnSize="autoSize", 
                    style={"height": 90},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
                    )
            
                gene_data_2 = dag.AgGrid(
                    rowData=gene_data_2.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 130} for i in gene_data_2.columns],
                    columnSize="autoSize", 
                    style={"height": 90},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True, "wrapText": True,}
                    )
            
                gene_data_3 = dag.AgGrid(
                    rowData=gene_data_3.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 130} for i in gene_data_3.columns],
                    columnSize="sizeToFit", 
                    style={"height": 90},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
                    )
            
                ID_data_1 = dag.AgGrid(
                    rowData=ID_data_1.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 154} for i in ID_data_1.columns],
                    columnSize="sizeToFit", 
                    style={"height": 90},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
                    )
            
                ID_data_2 = dag.AgGrid(
                    rowData=ID_data_2.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 200, "wrapText": True, "autoHeight":True} for i in ID_data_2.columns],
                    columnSize="autoSize", 
                    style={"height": 130},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
                    )
            
                ID_data_3 = dag.AgGrid(
                    rowData=ID_data_3.to_dict("records"),
                    columnDefs=[{"field": i, 'minWidth': 130} for i in ID_data_3.columns],
                    columnSize="sizeToFit", 
                    style={"height": 90},
                    dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
                    )
            
                #returning the full tables 
                
                return(gene_data_1, gene_data_2, gene_data_3, ID_data_1, ID_data_2, ID_data_3)
  

#function to get the orthologues, works in the same way as getting the basic gene data
@callback(
    Output("ortho_table", "children"), 
    State("tsa_target", "value"),
    State("file_path", "value"),
    Input("target_info", 'active_tab'),
    Input("target_button", "n_clicks"),
)

def orthologues_render(tsa_target, file, active_tab, n_clicks):
    if ((active_tab == 'ortho_card') or (active_tab == 'ortho_card' and n_clicks)):
        ortho_human = sql_search(tsa_target, 'ortho_human', file)
        ortho_human = ortho_human.iloc[:, 2:]
        
        ortho_sus_scrofa = sql_search(tsa_target, 'ortho_sus_scrofa', file)
        ortho_sus_scrofa = ortho_sus_scrofa.iloc[:, 2:]
        
        ortho_rattus_norvegicus = sql_search(tsa_target, 'ortho_rattus_norvegicus', file)
        ortho_rattus_norvegicus = ortho_rattus_norvegicus.iloc[:, 2:]
     
        ortho_oryctolagus_cuniculus = sql_search(tsa_target, 'ortho_oryctolagus_cuniculus', file)
        ortho_oryctolagus_cuniculus = ortho_oryctolagus_cuniculus.iloc[:, 2:]
      
        ortho_mus_musculus = sql_search(tsa_target, 'ortho_mus_musculus', file)
        ortho_mus_musculus = ortho_mus_musculus.iloc[:, 2:]
        
        ortho_macaca_mulatta = sql_search(tsa_target, 'ortho_macaca_mulatta', file)
        ortho_macaca_mulatta = ortho_macaca_mulatta.iloc[:, 2:]
       
        ortho_macaca_fascicularis = sql_search(tsa_target, 'ortho_macaca_fascicularis', file)
        ortho_macaca_fascicularis = ortho_macaca_fascicularis.iloc[:, 2:]
      
        ortho_danio_rerio = sql_search(tsa_target, 'ortho_danio_rerio', file)
        ortho_danio_rerio = ortho_danio_rerio.iloc[:, 2:]
        
        ortho_cavia_porcellus = sql_search(tsa_target, 'ortho_cavia_porcellus', file)
        ortho_cavia_porcellus = ortho_cavia_porcellus.iloc[:, 2:]
      
        ortho_canis_lupus_familiaris = sql_search(tsa_target, 'ortho_canis_lupus_familiaris', file)
        ortho_canis_lupus_familiaris = ortho_canis_lupus_familiaris.iloc[:, 2:]
       
        ortho_callithrix_jacchus = sql_search(tsa_target, 'ortho_callithrix_jacchus', file)
        ortho_callithrix_jacchus = ortho_callithrix_jacchus.iloc[:, 2:]
        
        ortho = []
        ortho_all = [ortho_human, ortho_sus_scrofa, ortho_rattus_norvegicus, ortho_oryctolagus_cuniculus, ortho_mus_musculus, ortho_macaca_mulatta, ortho_macaca_fascicularis, ortho_danio_rerio, ortho_cavia_porcellus, ortho_canis_lupus_familiaris, ortho_callithrix_jacchus]
        
        for i in ortho_all:
            if (i['Species'].values) != None:
                ortho.append(i)
                
        if len(ortho) == 0:
            return("No Orthologue Data Found")
        
        ortho=pd.concat(ortho)
        coldefs = [
            {'field': 'ensembl_id'},
            {'field': 'Species'},
            {'field': 'Type'},
            {'field': '%match', "width":100},
            {'field': '%query', "width":100},
            {'field': 'Link', "autoHeight":True, "cellRenderer": "markdown", "linkTarget":"_Blank", "width":300},
            ]
        
        ortho = ortho.to_dict('records')
        ortho = dag.AgGrid(
            columnDefs = coldefs,
            columnSize = "responsiveSizeToFit",
            rowData = ortho
            )
            
        #ortho = dbc.Table.from_dataframe(ortho, striped=True, bordered=True, hover=True)
        
        
        # ensembl_id', 'Species', 'Type', '%match', '%query', 'Link'
        #"cellRenderer": "markdown", "linkTarget":"_Blank"
        
        return(ortho)

#function to get the isoforms, works in the same was as the basic gene data    

@callback(
    Output("protein_isoform_table", "children"), 
    State("tsa_target", "value"),
    State("file_path", "value"),
    Input("target_info", 'active_tab'),
    Input("target_button", "n_clicks"),
)

def get_isoforms(tsa_target, file, active_tab, n_clicks):
    if ((active_tab == 'protein_isoform_card') or (active_tab == 'protein_isoform_card' and n_clicks)): 
        isoforms_txt = sql_search(tsa_target, 'protein_isoforms', file)
        
        if len(isoforms_txt) == 0:
            return("No Isoform Data Found")
        
        length = isoforms_txt['Length'].to_list()[0][1:-1].split("', '")
        Uniprot_Entry = isoforms_txt['Uniprot_Entry'].to_list()[0][1:-1].split("', '")
        Tissue_Specificity = isoforms_txt['Tissue_Specificity'].to_list()[0][21:-1].split("', '")
        GO_BP = isoforms_txt['Gene Ontology (biological process)'].to_list()[0][1:-1].replace("]", "]. ").split("', '")
        GO_CC = isoforms_txt['Gene Ontology (cellular component)'].to_list()[0][1:-1].replace("]", "]. ").split("', '")
        GO_MF = isoforms_txt['Gene Ontology (molecular function)'].to_list()[0][1:-1].replace("]", "]. ").split("', '")
        
        iso_dict = {'length': length, 
                'Uniprot Entry': Uniprot_Entry,
                'Tissue Specificity': Tissue_Specificity,
                'Biological Process': GO_BP,
                'Cellular Component': GO_CC,
                'Molecular Function': GO_MF} 
        
        isoforms = pd.DataFrame(iso_dict)
        
        
        coldefs = [
            {'field': 'length', "width":90},
            {'field': 'Uniprot Entry', "width":130},
            {'field': 'Tissue Specificity', "wrapText": True, "autoHeight":True, "width":235, "cellStyle": {"wordBreak": "normal", "lineHeight":"20px"},},
            {'field': 'Biological Process', "wrapText": True, "autoHeight":True, "width":235, "cellStyle": {"wordBreak": "normal", "lineHeight":"20px"},},
            {'field': 'Cellular Component', "wrapText": True, "autoHeight":True, "width":230, "cellStyle": {"wordBreak": "normal", "lineHeight":"20px"},},
            {'field': 'Molecular Function', "wrapText": True, "autoHeight":True, "width":230, "cellStyle": {"wordBreak": "normal", "lineHeight":"20px"},},
            ]
        
        isoforms = dag.AgGrid(
            id="get-started-example-basic-df",
            rowData=isoforms.to_dict("records"),
            columnDefs=coldefs,
            style={"height": 600},
            dashGridOptions = { "enableCellTextSelection": True, "suppressCellFocus": True}
            )
        
        return(isoforms)
   
#@callback(
#    Output("Protein_Expression_Plot", "src"),
#    Output("Immune_Plot", "src"),
#    Output("SingleCell_RNAseq_Plot", "src"),
#    Output("Human_Bulk_RNAseq_Plot", "src"), 
#    Output("Cancer_Expression_Plot", "src"), 
#    State("tsa_target", "value"),
#    Input("target_button", "n_clicks"),
#)
#def get_plots(tsa_target, n_clicks):
#    PEP = convert_from_path('/Users/DanielForman/Downloads/Plots_testing/HGNC_20_AARS1/AARS1/AARS1_IHC_protein_expression_plot.pdf')
#    IP = convert_from_path('/Users/DanielForman/Downloads/Plots_testing/HGNC_20_AARS1/AARS1/AARS1_immune_plot.pdf')
#    SCRP = convert_from_path('/Users/DanielForman/Downloads/Plots_testing/HGNC_20_AARS1/AARS1/AARS1_scRNAseq_plot.pdf')
#    CEP = convert_from_path('/Users/DanielForman/Downloads/Plots_testing/HGNC_20_AARS1/AARS1/cancer_expression_plot_ENSG00000090861.pdf')
#    HBRP = convert_from_path('/Users/DanielForman/Downloads/Plots_testing/HGNC_20_AARS1/AARS1/Human_Bulk_RNAseq_plot_AARS1.pdf')
        
#    return(PEP, IP, SCRP, CEP, HBRP)
    
clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)

if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:9801/')
    app.run(debug=False, port=9801)
