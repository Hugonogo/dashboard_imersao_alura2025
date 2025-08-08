import streamlit as st
import pandas as pd
import plotly.express as px

import copy

st.set_page_config(
    page_title="DashBoard interativo de dados",
    layout='wide'
)

df = pd.read_csv('https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv')
colunas_renomeadas = {


    'work_year': 'Ano',
    'experience_level': "Experiência",
    'employment_type': 'Contrato',
    'job_title': 'Cargo',
    'salary': 'Salário',
    'salary_currency': 'Moeda',
    'salary_in_usd': 'USD',
    'employee_residence': 'Residência',
    'remote_ratio': 'Remoto',
    'company_location': 'Empresa',
    'company_size': 'Tamanho da empresa'


}
df_inputed = copy.deepcopy(df)
df_inputed.rename(columns=colunas_renomeadas, inplace=True)




renomear_siglas_exp = {
    'EN': 'Junior',
    'MI': 'Pleno',
    'SE': 'Sênior',
    'EX': 'Executivo'
}

df_inputed['Experiência'] = df_inputed['Experiência'].replace(renomear_siglas_exp)

renomear_siglas_contrato = {
    'FT': 'Tempo Integral',
    'PT': 'Tempo Parcial',
    'FL': 'Freelancer',
    'CT': 'Contrato'
}

df_inputed['Contrato'] = df_inputed['Contrato'].replace(renomear_siglas_contrato)

renomear_siglas_empresa = {
    "M": "Médio",
    "L": "Grande",
    "S": "Pequeno"

}

df_inputed["Tamanho da empresa"] = df_inputed['Tamanho da empresa'].replace(renomear_siglas_empresa)

renomerar_remoto = {
    0: "Presencial",
    50: "Híbrido",
    100: "Remoto"
}

df_inputed['Remoto'] = df_inputed['Remoto'].replace(renomerar_remoto)
df_inputed = df_inputed.dropna()
df_inputed = df_inputed.assign(Ano = df_inputed["Ano"].astype("int64"))
# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

anos_disponiveis = sorted(df_inputed['Ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

exp_disponiveis = sorted(df_inputed["Experiência"].unique())
exp_selecionados = st.sidebar.multiselect('Experiência', exp_disponiveis, default=exp_disponiveis)

contratos_disponiveis = sorted(df_inputed['Contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Contratos", contratos_disponiveis, default=contratos_disponiveis)


tamanhos_empresas_disponiveis = sorted(df_inputed['Tamanho da empresa'].unique())
tamanhos_empresas_selecionada = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_empresas_disponiveis, default=tamanhos_empresas_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df_inputed[
    (df_inputed['Ano'].isin(anos_selecionados)) &
    (df_inputed['Experiência'].isin(exp_selecionados)) &
    (df_inputed['Contrato'].isin(contratos_selecionados)) &
    (df_inputed['Tamanho da empresa'].isin(tamanhos_empresas_selecionada))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['USD'].mean()
    salario_maximo = df_filtrado['USD'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["Cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"$ {salario_maximo:,.0f}")
col3.metric("Total de Registros", f"{total_registros:,}")
col4.metric("Cargo mais Frequente", f"{cargo_mais_frequente}")

st.markdown("---")

st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby("Cargo")["USD"].mean().nlargest(10).sort_values().reset_index()
        fig = px.bar(
            top_cargos,
            x='USD',
            y="Cargo",
            title="Top 10 Cargos com Maior Salário",
            labels={"USD": "Média Salarial em dolar", "Cargo": ""}

        )
        fig.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado enconrado para exibir gráfico")

with col_graf2:
    if not df_filtrado.empty:
        fig = px.histogram(
            df_filtrado,
            x="USD",
            nbins=30,
            title="Distribuição de Salários anuais em dolar",
            labels={'USD': "Faixa salarial anual em dolar", "count": ''}
        )
        fig.update_layout(title_x=0.1)
        st.plotly_chart(fig, use_container_width=True )
    else:
        st.warning("Nenhum dado enconrado para exibir gráfico")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado["Remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["Tipo de trabalho", "Quantidade"]
        fig = px.pie(
            remoto_contagem,
            names="Tipo de trabalho",
            values="Quantidade",
            title="Proporção do tipo de trabalho",
            hole=0.5
        )
        
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(title_x=0.1)
        st.plotly_chart(fig, use_container_width=True)
    else:

        st.warning("Nenhum dado enconrado para exibir gráfico")
with col_graf4:
    if not df_filtrado.empty:
        top_paises = df_filtrado.groupby("Residência")['USD'].mean().nlargest(10).sort_values().reset_index()
        fig = px.bar(
            top_paises,
            x='Residência',
            y='USD',
            title='Paises que mais pagam',
            labels={'Residência': "", "USD": "Média Salarial em dolar"}
        )
        fig.update_layout(title_x=0.1, xaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True   )
    else:
        st.warning("Nenhum dado enconrado para exibir gráfico")

st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)