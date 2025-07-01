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