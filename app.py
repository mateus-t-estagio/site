#Juntando a parte do código de produção e de acidentes
#Dados apresentados na forma gráfica e com opções de MultiSelect
import warnings

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

warnings.filterwarnings("ignore")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server
# Leitura dos arquivos em excel
#Leitura da base de dados para a Produção, tanto em TU quanto em TKU
Producao=pd.read_excel('Producao.xlsx')
#Leitura da base de dados para os Acidentes
Acidentes = pd.read_excel('Registro_de_Acidentes.xlsx')
#Leitura da base de dados para o Indice de Acidentes
Indice_Acidentes = pd.read_excel('Indice de Acidentes.xlsx')

# Listas para os callbacks e dropdowns
Ferrovias = ['EFC', 'EFVM', 'FTC', 'FTL', 'FCA', 'RMN', 'RMP', 'RMO', 'RMS', 'MRS', 'EFPO', 'FNSTN']
TU_TKU = ['TU', 'TKU']
esc_aci=['Total de Acidentes','Índice de Acidentes']

# Definição do layout da página
app.layout=html.Div([

    html.Label('Histórico de Produção de Transporte: '),
    dcc.Dropdown(
                id='id_dropdown_ferr',
                options=[{'label': i, 'value': i} for i in Ferrovias],
                value=['EFC'],
                multi=True),
    dcc.RadioItems(
                id='id_radio_TON',
                options=[{'label': i, 'value': i} for i in TU_TKU],
                value='TU',
                labelStyle={'display': 'inline-block'}
            ),
    html.Div([dcc.Graph(id='grafico_producao')]), 
  
    html.Label('Histórico de Acidentes e Índice de Acidentes: '),
    dcc.Dropdown(
                id='id_dropdown_acidente',
                options=[{'label': i, 'value': i} for i in Ferrovias],
                value=['EFC'],
                multi=True),
    dcc.RadioItems(
                id='id_radio_acidente',
                options=[{'label': i, 'value': i} for i in esc_aci],
                value='Total de Acidentes',
                labelStyle={'display': 'inline-block'}),
    
            html.Div([dcc.Graph(id='grafico_acidentes')]),

])
# Calbacks para os gráficos
@app.callback(dash.dependencies.Output('grafico_producao','figure'),[
        dash.dependencies.Input('id_dropdown_ferr','value'),
        dash.dependencies.Input('id_radio_TON','value')
    ])
def prod_transporte(x_ferr,y_tu):
    #Criando uma lista com as ferrovias escolhidas no dropdown 
    Ferr_Select=x_ferr
    #Criando dicionário onde serão salvos os DataFrames referentes a cada Ferrovia   
    Ferrovia_to_Analise= {}
    #Loop para filtrar os dados referentes a cada ferrovia 
    for val in Ferr_Select:
        #Filtrar os dados referente a Ferrovia na lista Ferr_Select
        iProducao=Producao['Ferrovia']==val
        Ferrovia_Escolhida=Producao[iProducao]
        Ferrovia_Escolhida['Mes/Ano']=pd.to_datetime(Ferrovia_Escolhida['Mes/Ano'])
        #Salvando no espaço val o DataFrame referente a Ferrovia em Ferr_Select
        Ferrovia_to_Analise[val]=Ferrovia_Escolhida    
    df=pd.DataFrame()
    trace={}
    tracado=[]
    #Loop para manipular e salvar os dados para a criação dos gráficos
    for val in Ferr_Select:
        #Base de dados para a Ferrovia em Ferr_Select 
        df=Ferrovia_to_Analise[val]
        #Lista de dados do eixo x
        x=df['Mes/Ano']
        #Lista de dados do eixo y
        y=df[y_tu]
        #Traçado referente a cada Ferrovia em Ferr_Select
        trace[val] = go.Scatter(x=x,
                            y=y,
                            mode='lines+markers',
                            name=val) 
        #Lista acumulando as informações de cada gráfico
        tracado.append(trace[val]) 
    data=tracado
    #Formatando a lista de Ferrovias para colocar no titulo do gráfico
    z=', '.join(x_ferr) 
    #Criação dos gráficos  
    return {
            'data': data,
            'layout': {
            'title':'Produção de Transporte- Ferrovia(s): ' + z,
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': y_tu + '/10³' },
            }}   

@app.callback(dash.dependencies.Output('grafico_acidentes','figure'),[
        dash.dependencies.Input('id_dropdown_acidente','value'),
        dash.dependencies.Input('id_radio_acidente','value')
    ])
def numero_acidentes(x_ferr,y_tu):
    #Condição para a seleção do tipo de informação, referente ou ao total de acidentes ou aos indices de acidentes
    if y_tu == 'Total de Acidentes':
        #Criando a lista com as informações escolhidas pelo usuário no dropdown
        Ferr_Select=x_ferr
        Ferrovia_to_Analise = {}
        #Loop para filtrar os dados referentes a cada ferrovia 
        for val in Ferr_Select:
        #Filtrar os dados referente a Ferrovia na lista Ferr_Select
            Ferrovia=Acidentes
            iFerrovia=Ferrovia['Ferrovia']==val
            Ferrovia_Escolhida=Ferrovia[iFerrovia]
            Ferrovia_to_Analise[val]=Ferrovia_Escolhida
        df=pd.DataFrame()
        trace={}
        tracado=[]
        for val in Ferr_Select:
            #Criando DataFrame referente aos dados de cada Ferrovia
            df=Ferrovia_to_Analise[val]
            #Definindo os parâmetros x e y do gráfifo 
            x=df['Ano']
            y=df['Acidentes']
            #Criando o gráfico da Ferrovia "val"
            trace[val]=go.Bar(x=x,
                                y=y,
                                text='Número de Acidentes',
                                name=val)
            #Agrupando um conjunto de base de dados referente a cada Ferrovia em Ferr_Select
            #Uma lista salvando cada conjunto de traçados de gráficos em "trace[val]"
            tracado.append(trace[val])
        data=tracado
        #Formatando a lista de Ferrovias para colocar no titulo do gráfico
        z=', '.join(x_ferr) 
        #Criação dos gráficos 
        return {
                'data': data,
                'layout': {
                'title':'Acidentes - Ferrovia(s): '+ z,
                'xaxis':{'title': 'Ano'},
                'yaxis':{'title': 'N° de Acidentes'},
                }}
    else:
        #Criando a lista com as informações escolhidas pelo usuário no dropdown
        Ferr_Select=x_ferr
        #Criando as listas e dicionários que serão utilizado no decorrer do código
        Ferrovia_to_Analise = {}
        Ferrovia=pd.DataFrame()
        trace={}
        tracado=[]
        for val in Ferr_Select:
            #Escolhendo a base de dados a partir da qual serão realizadas as manipulações e criações de gráfico
            Ferrovia=Indice_Acidentes
            iFerrovia=Ferrovia['Concessionária']==val
            Ferrovia=Ferrovia[iFerrovia]
            #Definindo os parâmetros x e y do gráfifo
            x=Ferrovia['Ano']
            y=Ferrovia['Realizado']
            #Criando o gráfico da Ferrovia "val"
            trace[val]=go.Bar(x=x,
                                y=y,
                                text='Índice de Acidentes',
                                name=val)
            tracado.append(trace[val])
        #Agrupando um conjunto de base de dados referente a cada Ferrovia em Ferr_Select
        #Uma lista salvando cada conjunto de traçados de gráficos em "trace[val]"
        data=tracado

        #Formatando a lista de Ferrovias para colocar no titulo do gráfico
        z=', '.join(x_ferr) 
        #Criação dos gráficos  
        return {
                'data': data,
                'layout': {
                'title':'Índice de Acidentes - Ferrovia(s): ' + z,
                'xaxis':{'title': 'Ano'},
                'yaxis':{'title': 'Indice de Acidentes'},
                }}

if __name__ == '__main__':
    app.run_server()
