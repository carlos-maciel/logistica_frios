import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.figure_factory as ff
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# url: str = st.secrets["SUPABASE_URL"]
# key: str = st.secrets["SUPABASE_KEY"]
# supabase: Client = create_client(url, key)

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

response = supabase.table("monitoramento").select("*").execute()

df = pd.DataFrame(response.data)
df["DataHora"] = pd.to_datetime(df["DataHora"])

st.title("Dashboard - Logística de Frios e Perecíveis ")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mapa", "Status", "Falhas", "Temperatura Interna", "Correlação"])

df_falha = df[df["StatusEquipamento"] == "falha"]

placas_remover = ["GBC1006", "EBC1004"]
df_falha = df_falha[~df_falha["PlacaVeiculo"].isin(placas_remover)]

with tab1:
    st.write("Localização dos caminhões quando apresentaram falha:")

    if not df_falha.empty:
        df_falha["TamanhoPonto"] = 20
        fig_falha = px.scatter_map(
            df_falha,
            lat="Latitude",
            lon="Longitude",
            hover_name="PlacaVeiculo",
            hover_data={
                "TemperaturaInterna": True,
                "NivelEnergia": True,
                "PlacaVeiculo": False,
                "Latitude": False,
                "Longitude": False,
            },
            color="PlacaVeiculo",
            size="TamanhoPonto",
            size_max=9,
            zoom=3,
            height=550,
            map_style="open-street-map"
        )
        fig_falha.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_falha)
    else:
        st.info("Nenhum caminhão apresentou falha.")
with tab2:
    status_counts = df['StatusEquipamento'].value_counts(normalize=True) * 100
    fig_status = px.pie(status_counts, values=status_counts.values, names=status_counts.index, 
                        title="Status Geral das Máquinas",
                        labels={"machine_status": "Status", "value": "Percentual"},
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_status.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_status, use_container_width=True)

    maquinas_baixa_bateria = df[df['NivelEnergia'] < 30]
    maquinas_baixa_bateria['Problema'] = 'Nivel de energia baixo'
    maquinas_baixa_bateria = maquinas_baixa_bateria.rename(columns={'NivelEnergia': 'Valor Atual'})
    maquinas_baixa_bateria['Valor Esperado'] = '> 30'

    st.dataframe(maquinas_baixa_bateria[['Problema', 'id', 'PlacaVeiculo', 'Valor Atual', 'Valor Esperado', ]],  use_container_width=True)

with tab3:
    # Quantidade de falhas por veículo
    falhas_por_veiculo = df[df["StatusEquipamento"] == "falha"]["PlacaVeiculo"].value_counts()
    fig_falhas = px.bar(
        falhas_por_veiculo,
        x=falhas_por_veiculo.index,
        y=falhas_por_veiculo.values,
        title="10 Veículos com Mais Falhas",
        labels={"x": "Veículo", "y": "Quantidade de Falhas"}
    )
    st.plotly_chart(fig_falhas, use_container_width=True)

with tab4:
    st.subheader("Evolução da Temperatura Interna com Falhas Destacadas")
    st.write("Todos os veículos")
    for placa in df['PlacaVeiculo'].unique():
        df_placa = df[df['PlacaVeiculo'] == placa]
        fig_temp = px.line(
            df_placa, x="DataHora", y="TemperaturaInterna",
            title=f"Evolução da Temperatura Interna - Caminhão {placa}",
            labels={"TemperaturaInterna": "Temperatura Interna (°C)", "DataHora": "Data/Hora"}
        )
        df_falha_placa = df_placa[df_placa["StatusEquipamento"] == "falha"]
        fig_temp.add_scatter(
            x=df_falha_placa["DataHora"], y=df_falha_placa["TemperaturaInterna"],
            mode='markers', marker=dict(color='red', size=10), name='Falha'
        )
        st.plotly_chart(fig_temp, use_container_width=True)

with tab5:
    st.subheader("Correlação entre Variáveis e Falha")
    df['Falha'] = (df['StatusEquipamento'] == 'falha').astype(int)
    corr = df[['TemperaturaInterna', 'TemperaturaExterna', 'Umidade', 'NivelEnergia', 'Falha']].corr()
    fig_corr = ff.create_annotated_heatmap(
        z=np.round(corr.values, 2),
        x=list(corr.columns),
        y=list(corr.index),
        colorscale='Viridis'
    )
    fig_corr.update_layout(title="Correlação entre Variáveis e Falha")
    st.plotly_chart(fig_corr, use_container_width=True)
