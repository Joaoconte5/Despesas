import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Controle de Despesas")

# Caminho do arquivo de dados (CSV)
arquivo_csv = "gestao_despesas.csv"

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(arquivo_csv):
        try:
            # Tentando carregar o arquivo CSV com encoding e separador
            return pd.read_csv(arquivo_csv, encoding="ISO-8859-1", sep=";", header=0)
        except pd.errors.ParserError:
            # Se houver erro ao ler, exibe uma mensagem no Streamlit
            st.error("Erro ao ler o arquivo CSV. Verifique o formato e o separador.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    else:
        return pd.DataFrame(columns=["Data", "Data Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas"])

# Carregar dados e exibir na Streamlit
df = carregar_dados()

# Menu de navegação
menu = st.sidebar.selectbox("Escolha a página", ["Lançamentos de Despesas", "Resumo de Despesas"])

# Página 1: Lançamentos de Despesas
if menu == "Lançamentos de Despesas":
    st.title("Lançamentos de Despesas")
    
    with st.container():
        st.header("Adicionar Nova Despesa")
        
        data = st.date_input("Data da Despesa")
        data_vencimento = st.date_input("Data de Vencimento")
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Saúde", "Lazer", "Outros"])
        origem = st.text_input("Origem da Despesa")
        valor = st.number_input("Valor", min_value=0.0)
        cartao = st.selectbox("Cartão", ["Crédito", "Débito"])
        parcelas = st.number_input("Parcelas", min_value=1, step=1)

        if st.button("Salvar Despesa"):
            nova_despesa = pd.DataFrame(
                [[data, data_vencimento, categoria, origem, valor, cartao, parcelas]],
                columns=["Data", "Data Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas"]
            )

            # Carregar dados existentes
            df_existente = carregar_dados()

            # Adicionar a nova despesa aos dados existentes
            df_final = pd.concat([df_existente, nova_despesa], ignore_index=True)

            # Salvar no CSV
            df_final.to_csv(arquivo_csv, index=False)
            st.success("Despesa salva com sucesso!")
            st.rerun()

        # Exibir a tabela de todos os lançamentos de despesas
        st.subheader("Todos os Lançamentos de Despesas")
        df = carregar_dados()  # Carregar os dados novamente
        st.dataframe(df)  # Exibe os dados em formato de tabela interativa

# Página 2: Resumo de Despesas
elif menu == "Resumo de Despesas":
    st.title("Resumo de Despesas")
    
    # Carregar os dados
    df = carregar_dados()

    # Garantir que a coluna 'Valor' seja numérica, forçando a conversão
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')  # Converte para numérico, substituindo erros por NaN

    # Garantir que a coluna 'Data Vencimento' seja datetime
    df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], errors='coerce')

    # KPI: Gasto total
    gasto_total = df['Valor'].sum()
    st.metric("Gasto Total", f"R$ {gasto_total:,.2f}")

    # KPI: Gasto realizado neste mês
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    df_mes_atual = df[(df["Data Vencimento"].dt.month == mes_atual) & (df["Data Vencimento"].dt.year == ano_atual)]
    gasto_mes_atual = df_mes_atual['Valor'].sum()
    st.metric("Gasto neste mês", f"R$ {gasto_mes_atual:,.2f}")

    # Gráfico de barras: Valor por categoria
    st.subheader("Valor por Categoria")
    categoria_gasto = df.groupby("Categoria")["Valor"].sum().reset_index()

    # Gráfico de barras
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Valor", y="Categoria", data=categoria_gasto, palette="viridis")
    plt.title("Valor por Categoria", fontsize=16)
    plt.xlabel("Valor", fontsize=12)
    plt.ylabel("Categoria", fontsize=12)
    st.pyplot(plt)

    # Tabela: Resumo por Categoria
    st.subheader("Resumo por Categoria")
    categoria_gasto = df.groupby("Categoria")["Valor"].sum().reset_index()
    st.table(categoria_gasto)
