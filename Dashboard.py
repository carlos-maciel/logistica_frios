import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

response = supabase.table("monitoramento").select("*").execute()

df = pd.DataFrame(response.data)
st.write("Dados da tabela:")
st.dataframe(df)

st.title("Dashboard")

status_counts = df['StatusEquipamento'].value_counts(normalize=True) * 100
fig_status = px.pie(status_counts, values=status_counts.values, names=status_counts.index, 
                    title="Status Geral das Máquinas",
                    labels={"machine_status": "Status", "value": "Percentual"},
                    color_discrete_sequence=px.colors.qualitative.Pastel)
fig_status.update_traces(textinfo='percent+label')
st.plotly_chart(fig_status, use_container_width=True)

