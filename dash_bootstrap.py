import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


# Inputs
df_humsavar = pd.read_csv("Tier1_2_3_CGI_humsavar.csv", usecols= ['uniprot', 'position', 'AA_orig', 'AA_targ', 'label'])
df_other = pd.read_csv("Tier1_2_3_CGI_Other.csv", usecols= ['uniprot', 'position', 'AA_orig', 'AA_targ', 'label'])
# modify the label from (0,1) to (benign, pathogenic)
df_humsavar["label"] = np.where(df_humsavar["label"] == 0, 'Benign', 'Pathogenic')
df_other["label"] = np.where(df_other["label"] == 0, 'Benign', 'Pathogenic')

app =dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE],
               meta_tags=[{'name': 'viewport',
                           'content': 'width=device-width, initial-scale=1.0'}]
               )

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Choose Dataset:",
                        className='text-left text-primary mb-4'),
                width=12)
    ),
    dbc.Row(
        dbc.Row(
            dcc.Dropdown(id='dataset', multi=False, value='Tier1_2_3_CGI_humsavar',
                         options=[{'label': x, 'value': x}
                                  for x in ['Tier1_2_3_CGI_humsavar', 'Tier1_2_3_CGI_Other']],
                         className='mb-5 center',
                         ),
            style = {'width': '40%',  'align-items': 'center'}),
    align='center'),
    dbc.Row([
        dbc.Col(html.H4(f"Choose Protein for:",
                        className='text-left text-warning mb-4'),
                width=5),
        dbc.Col(
            html.H4(id='my_output', className='text-left text-warning mb-4'),
        )
    ],align='center') ,

    dbc.Row(
        dbc.Row(
            dcc.Dropdown(id='selected_protein', multi=True, value=['Q9BXY4-1', 'P10398-1'],
                         )
        )
    ),
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='hist-fig2', figure={}),
            )
        ),
        dbc.Col(
            html.Div(
                dcc.Graph(id='hist-fig1', figure={}, className = 'mb-4')
            )
        ),

    ]),
    dbc.Col(
        html.Div(
            [
                html.Button("Download Tier1_2_3_CGI_humsavar", id="humsavar_csv", className='mb-4 btn-outline-success'),
                dcc.Download(id="download-dataframe-csv1"),
            ]
        )
    ),
    dbc.Col(
        html.Div(
            [
                html.Button("Download Tier1_2_3_CGI_other", id="other_csv", className='btn-outline-success'),
                dcc.Download(id="download-dataframe-csv2"),
            ]
        )
    )
], fluid=True)

 # Callback section: connecting the components
# # ************************************************************************
# Multiple histogram, color: uniprot id
@app.callback(
    Output('hist-fig2', 'figure'),
    Input('selected_protein', 'value'),
    Input('my_output', 'children')
)
def update_graph2(selected_protein, my_output):

    if my_output == 'Tier1_2_3_CGI_Other':
        df = df_other
    else:
        df = df_humsavar
    dff = df[df['uniprot'].isin(selected_protein)]
    figln2 = px.histogram(dff, x='position',color='uniprot', nbins=100, marginal="rug",opacity=0.75,hover_data=dff.columns)
    return figln2

# Multiple histogram, color: pathogenicity
@app.callback(
    Output('hist-fig1', 'figure'),
    Input('selected_protein', 'value'),
    Input('my_output', 'children')
)
def update_graph1(selected_protein, my_output):

    if my_output == 'Tier1_2_3_CGI_Other':
        df = df_other
    else:
        df = df_humsavar
    dff = df[df['uniprot'].isin(selected_protein)]
    figln2 = px.histogram(dff, x='position',color='label', nbins=100, marginal="rug",hover_data=dff.columns,
                          opacity=0.75, color_discrete_map = {'Benign':'green','Pathogenic':'purple'})

    return figln2


@app.callback(
    Output(component_id='my_output', component_property='children'),
    Input(component_id='dataset', component_property='value')
)
def update_output_div(input_value):
    return input_value

@app.callback(
    Output("selected_protein", "options"),
    [Input("my_output", "children")],
)

def update_dropdown(my_output):
    if my_output == 'Tier1_2_3_CGI_Other':
        df = df_other
    else:
        df = df_humsavar

    options = [{'label': x, 'value': x}
               for x in sorted(df['uniprot'].unique())]
    return options


@app.callback(
    Output("download-dataframe-csv1", "data"),
    Input("humsavar_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func_humsavar( n_clicks):
    return dcc.send_data_frame(df_humsavar.to_csv, "Tier1_2_3_CGI_humsavar.csv")


@app.callback(
    Output("download-dataframe-csv2", "data"),
    Input("other_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func_other(n_clicks):
    return dcc.send_data_frame(df_humsavar.to_csv, "Tier1_2_3_CGI_other.csv")

if __name__=='__main__':
    app.run_server(debug=True, port=8000)
