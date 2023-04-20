# Libraries
from haversine import haversine
import plotly.express as px
#import plotly.graph_objetcs as go

# Bibliotecas necessárias


import pandas as pd
import streamlit as st
import folium
import numpy as np
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
st.set_page_config(page_title= "Visão Restaurantes", layout="wide")

def clean_code(df1):
    #convertenta a coluna AGE para int
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '
    df1 = df.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1 = df.loc[linhas_selecionadas, :].copy()
    #convertenta objeto em Inteiro
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    #convertenta o objeto em float
    df1['Delivery_person_Ratings'] = df1[ 'Delivery_person_Ratings'].astype(float)
    #convertenta data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')

    #convertendo multiple_deliveries de texto para numero inteiro

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df1 = df1[df1['City'] != 'NaN']

    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    df1 = df1.reset_index(drop = True)

    #Removendo espaço em branco dentro de Strings/texto/object
    df1.loc[: , 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[: , 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[: , 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df1 = df1[df1['City'] != 'NaN']




    # Limpando a coluna de time taken
    # a função apply permite que seja utilizada uma nova função para cada elemento da coluna.
    # desta forma x é o elemento de interação.

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1
def avg_std_time_delivery(df1, festival, op):
    '''
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    :param df: Dataframe com os dados necessários para o calculo
    :param op: Tipo de operação que precisa ser calculado,
            'avg_time': Calcula o tempo médio'
            'std_time': Calcula o desvio padrão
    :return: df: Dataframe calculado
    '''

    df_aux = df1[df1['Festival'] == festival]
    df_aux01 = (df_aux.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux01.columns = ['avg_time', 'std_time']
    df_aux01 = df_aux01.reset_index()
    df_aux01 = np.round(df_aux01.loc[:, op], 2)

    return df_aux01
def avg_city(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux['City'],
                         y=df_aux['avg_time'],
                         error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig
def mean_time_city(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude',
            'Restaurant_longitude']

    df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                             haversine(
                                                 (x['Delivery_location_latitude'],
                                                  x['Delivery_location_longitude']),
                                                 (x['Restaurant_latitude'], x['Restaurant_longitude'])), axis=1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

    fig = go.Figure(
        data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.09, 0])])

    return fig
def std_delivery_city(df1):
    cols = ['City', 'Road_traffic_density', 'Time_taken(min)']

    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg(
        {'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['tempo_medio', 'desvio_padrao']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='tempo_medio',
                      color='desvio_padrao', color_continuous_scale='Bluered',
                      color_continuous_midpoint=np.average(df_aux['desvio_padrao']))
    return fig
df = pd.read_csv('dataset/train.csv')
df1 = clean_code(df)

# ===============================
# Barra lateral Filtros
# ==============================

st.header('Marketplace - Visão Restaurantes')

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
        st.subheader("Overal Metrics")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:

            num = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', num)
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude',
                    'Restaurant_longitude']

            df1['distancia'] = df1.loc[:, cols].apply(lambda x:
                                                      haversine(
                                                          (x['Delivery_location_latitude'],
                                                           x['Delivery_location_longitude']),
                                                          (x['Restaurant_latitude'], x['Restaurant_longitude'])),
                                                      axis=1)
            avg_distance = np.round(df1['distancia'].mean(), 2)

            col2.metric('Dist. Média', avg_distance)

        with col3:
            df_aux01 = avg_std_time_delivery(df1,'Yes', 'avg_time')
            col3.metric('tempo medio de entrega', df_aux01)

        with col4:
            df_aux01 = avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric('Desvio padrao entrega', df_aux01)

        with col5:
            df_aux01 = avg_std_time_delivery(df1, 'No', 'std_time')
            col5.metric('Tempo médio fora de festival', df_aux01)

        with col6:
            df_aux01 = avg_std_time_delivery(df1, 'No', 'avg_time')
            col6.metric('Desvio fora de festival', df_aux01)

    with st.container():
        col1, col2 = st.columns(2)

        st.markdown('''---''')
        with col1:
            st.subheader("Desvio padrão das entregas por cidade")
            fig = avg_city(df1)

            st.plotly_chart(fig)

        with col2:
            st.subheader("tempo médio por tipo de didade e tipo de pedido")

            cols = ['City', 'Type_of_order', 'Time_taken(min)']
            df_aux = df1.loc[:, cols] \
                .groupby(['City', 'Type_of_order']) \
                .agg({'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['tempo_medio', 'desvio_padrao']
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux)

    with st.container():


        col1, col2 = st.columns(2, gap = 'large')
        with col1:

            st.subheader("Tempo médio de entrega por cidade")
            fig = mean_time_city(df1)

            st.plotly_chart(fig)

        with col2:
            st.subheader("Desvio padrão de entrega por cidade")
            fig = std_delivery_city(df1)

            st.plotly_chart(fig)


    st.markdown('''___''')


