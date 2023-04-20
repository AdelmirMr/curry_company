
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

st.set_page_config(page_title= "Visão Empresa", layout="wide")

#funções
def clean_code( df1 ):
    """ Esta função tem o objetivo de limpar o dataframe

        Tipo de limpeza:
        1. Remoção dos dados NaN
        2. Conversão de tipos
        3. Remoção dos espaços das variáveis de texto
        4. Formatação de coluna de datas
        5. Limpeza da coluna de tempo ( Remoção do texto da variável numérica)

        Imput: Dataframe
        Output: Dataframe

    """
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

def order_metric(df1):
            # definir colunas
            cols = ['ID', 'Order_Date']

            # seleção de colunas
            df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
            # desenhar o grafico de linhas
            fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')

            return fig

def traffic_order_share(df1):
         df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(
            ['Road_traffic_density']).count().reset_index()
         df_aux = df_aux[df_aux['Road_traffic_density'] != 'NaN']

         df_aux['entregas_perc'] = (df_aux['ID'] / df_aux['ID'].sum()) * 100

         fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
         return fig

def mean_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    df_aux = round(
        df1[['Delivery_person_Ratings', 'week_of_year']].groupby('week_of_year').mean().reset_index(), 3)
    df_aux.columns = ['semana', 'media']

    fig = px.bar(df_aux, x='semana', y='media', title='Delivery Ratings per Week', color='semana', text_auto=True)
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    df_aux = df1.loc[:, ['week_of_year', 'ID']].groupby(['week_of_year']).count().reset_index()

    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig


def delivery_by_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    # entregas por entregador unico
    df_aux['order_by_deliver'] = (df_aux['ID'] / df_aux['Delivery_person_ID'])

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps( df1):
        cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
        # Agrupando as localizações pela cidade e por tipo de tráfego, realizando o calculo da mediana, para capturar o ponto
        data_plot = (df1.loc[:, cols]
                     .groupby(['City', 'Road_traffic_density'])
                     .median()
                     .reset_index())
        # limpando os dados, removendo lixo
        data_plot = data_plot[data_plot['City'] != 'NaN']
        data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']

        # plotanto o gráfico
        map = folium.Map()

        # marcando o gráfico com os pontos de latitude e gongitude

        for index, location_info in data_plot.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],
                           location_info['Delivery_location_longitude']],
                          popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

        folium_static( map, width=1024, height=600)
        return None

df = pd.read_csv('dataset/train.csv')

# Limpando dados
df1 = clean_code(df)





# ======================
# VISÃO EMPRESA
# ======================


# ===============================
# Barra lateral Filtros
# ==============================

st.header('Marketplace - Visão Cliente')

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

st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS")

# Filtros de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas , :]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas , :]




# ======================
# Layout no Streamlit
# ======================
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', 'Visão Tática',
                              'Visão Geográfica'])

# 1.1 quantidade de pedidos por dia
with tab1:
    with st.container():
        st.markdown("# Quantidade de pedidos por dia")
        fig = order_metric(df1)
        # plotar o grafico dentro do streamlit
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            # Distribuição dos pedidos por tipo de tráfego
            # Seleciona as linhas e colunas, fazendo a contagem por Densidade de Tráfego
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # entregas por semana
            fig = mean_by_week(df1)
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown("# Pedidos por semana")
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("# Entregadores por semana")
        # Quantidade de pedidos por semana / numnero unico de entregadores por semana
        fig = delivery_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:

    st.markdown('# Country Maps')
    country_maps(df1)