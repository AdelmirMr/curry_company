# Libraries
from haversine import haversine
import plotly.express as px
#import plotly.graph_objetcs as go

# Bibliotecas necessárias

import pandas as pd
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= "Visão Entregadores", layout="wide")

def clean_code(df1):
    # convertenta a coluna AGE para int
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '
    df1 = df.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1 = df.loc[linhas_selecionadas, :].copy()
    # convertenta objeto em Inteiro
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    # convertenta o objeto em float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    # convertenta data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # convertendo multiple_deliveries de texto para numero inteiro

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df1 = df1[df1['City'] != 'NaN']

    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1 = df1.reset_index(drop=True)

    # Removendo espaço em branco dentro de Strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df1 = df1[df1['City'] != 'NaN']

    # Limpando a coluna de time taken
    # a função apply permite que seja utilizada uma nova função para cada elemento da coluna.
    # desta forma x é o elemento de interação.

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
           .groupby(['City', 'Delivery_person_ID'])
           .min()
           .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
           .reset_index()
           )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3

df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)
# ===============================
# Barra lateral Filtros
# ==============================

st.header('Marketplace - Visão Entregadores')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width= 240)
st.sidebar.markdown("""___""")

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime( 2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY'
)


st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium', 'High', 'Jam'],
    default = ['Low','Medium', 'High', 'Jam'])

tipos_clima = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy',
     'conditions Sunny', 'conditions Windy'],
    default = ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy',
     'conditions Sunny', 'conditions Windy'])


st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS")

# Filtros de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas , :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas , :]

#filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(tipos_clima)
df1 = df1.loc[linhas_selecionadas, :]





# ======================
# Layout no Streamlit
# ======================

tab1, tab2, tab3, = st.tabs( ['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        # A maior idade dos entregadores
        with col1:
             maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
             col1.metric('Maior idade', maior_idade)

        # A menor idade dos entregadores
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade ', menor_idade )

        # Melhor condição de veículo
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor_condicao)

        # Pior condição de veículo
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao)

    with st.container():
        st.markdown('''___''')

        st.header('AVALIAÇÕES')
        col1, col2 =  st.columns(2, gap = 'large')
        # Quantidade de entregas por entregador
        with col1:
            st.markdown('Por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)


        with col2:
            st.markdown('Avaliação média por trânsito')

            # Quantidade de entregas por tipo de fráfego
            avaliacao_media_desvio = (
                            df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                               .groupby('Road_traffic_density')
                               .agg({'Delivery_person_Ratings': ['mean', 'std']})
            )
            #muda o nome das colunas
            avaliacao_media_desvio.columns =['delivery_mean', 'delivery_std']

            #reset do index
            avaliacao_media_desvio = avaliacao_media_desvio.reset_index()
            st.dataframe(avaliacao_media_desvio)


            # Quantidade de entregas por tipo de clima
            st.markdown('Avaliação média por clima')
            avaliacao_media_desvio_clima = (
                                df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                   .groupby('Weatherconditions')
                                   .agg({'Delivery_person_Ratings': ['mean', 'std']})
                )

            avaliacao_media_desvio_clima.columns = ['media', 'desvio_padrao']
            avaliacao_media_desvio_clima = avaliacao_media_desvio_clima.reset_index()

            st.dataframe(avaliacao_media_desvio_clima)

    with st.container():
        st.markdown('''___''')
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)

        #Os 10 mais rápidos
        with col1:

            st.subheader('TOP 10 entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)

        with col2:
            st.subheader('TOP 10 entregadores mais lentos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)









