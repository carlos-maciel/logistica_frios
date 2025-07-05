import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

@st.cache_data
def converte_csv(data):
  return data.to_csv(index=False).encode('utf-8')

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

st.write("Dados da tabela:")

with st.expander('Colunas'):
  colunas = st.multiselect('Selecione as colunas', list(df.columns), default=list(df.columns))

colunas_selecionadas = df[colunas]

st.dataframe(colunas_selecionadas)

st.download_button(
  label="Baixar Arquivo CSV",
  data = converte_csv(df),
  file_name='dados.csv',
  mime='text/csv',
  icon=":material/download:",
)