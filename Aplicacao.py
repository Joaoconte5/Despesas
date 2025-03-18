import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import requests
from io import StringIO

# URL do arquivo CSV no Google Drive
GDRIVE_CSV_URL = "https://drive.google.com/uc?id=12zWDtYgLGE0-u_aXKmPFQJbYj5WTuq-k"

def autenticar_usuario():
    # Verifica se o usuário já está autenticado
    if "autenticado" in st.session_state and st.session_state["autenticado"]:
        return  # Se já estiver autenticado, não faz nada
    
    st.sidebar.title("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    
    if st.sidebar.button("Entrar"):
        # Condição de login para os dois usuários
        if (usuario == "Suellen" and senha == "1234") or (usuario == "João" and senha == "5678"):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.experimental_rerun()  # Rerun para reiniciar a aplicação com o estado atualizado
        else:
            st.sidebar.error("Usuário ou senha incorretos")

def carregar_despesas():
    try:
        response = requests.get(GDRIVE_CSV_URL)
        response.raise_for_status()  # Verifica se houve erro de conexão
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar o Google Drive: {e}")
        return pd.DataFrame(columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação"])

def salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao):
    df = pd.DataFrame([[data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao]],
                      columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação"])
    try:
        historico = carregar_despesas()
        historico = pd.concat([historico, df], ignore_index=True)
        # Placeholder para salvar despesas no Google Drive:
        st.warning("Para salvar no Google Drive, configure a API do Google Drive.")
    except Exception as e:
        st.error(f"Erro ao salvar despesa: {e}")

def deletar_despesa(index):
    despesas = carregar_despesas()
    if 0 <= index < len(despesas):
        despesas = despesas.drop(index).reset_index(drop=True)
        # Placeholder para salvar despesas após deletar:
        st.warning("Para salvar no Google Drive, configure a API do Google Drive.")

def editar_despesa(index, data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao):
    despesas = carregar_despesas()
    if 0 <= index < len(despesas):
        despesas.at[index, "Data"] = data
        despesas.at[index, "Data de Vencimento"] = data_vencimento
        despesas.at[index, "Categoria"] = categoria
        despesas.at[index, "Origem"] = origem
        despesas.at[index, "Valor"] = valor
        despesas.at[index, "Cartão"] = cartao
        despesas.at[index, "Parcelas"] = parcelas
        despesas.at[index, "Observação"] = observacao
        # Placeholder para salvar despesas após editar:
        st.warning("Para salvar no Google Drive, configure a API do Google Drive.")

def pagina_lancamento():
    st.title("Lançamento de Despesas")
    
    despesas = carregar_despesas()
    despesa_editar = None
    index_editar = st.number_input("Informe o índice da despesa a ser editada", min_value=0, max_value=len(despesas)-1 if not despesas.empty else 0, step=1)
    
    if not despesas.empty:
        despesa_editar = despesas.iloc[index_editar]
    
    data = st.date_input("Data da Despesa", format="DD/MM/YYYY", value=date.today() if despesa_editar is None else despesa_editar["Data"])
    data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY", value=date.today() if despesa_editar is None else despesa_editar["Data de Vencimento"])
    categoria = st.selectbox("Categoria", ["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "Viagem", "Casa Utensílio", "Casa Concerto", "Diversos", "Carro",
                                          "Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza", "Vestuário", "Cursos e Treinamentos"],
                            index=["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "Viagem", "Casa Utensílio", "Casa Concerto", "Diversos", "Carro",
                                   "Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza", "Vestuário", "Cursos e Treinamentos"].index(despesa_editar["Categoria"]) if despesa_editar is not None else 0)
    origem = st.selectbox("Origem", ["Suellen", "João", "Conjunto"], index=["Suellen", "João", "Conjunto"].index(despesa_editar["Origem"]) if despesa_editar is not None else 0)
    valor = st.number_input("Valor", min_value=0.0, format="%.2f", value=despesa_editar["Valor"] if despesa_editar is not None else 0.0)
    cartao = st.selectbox("Cartão", ["Crédito", "Débito"], index=["Crédito", "Débito"].index(despesa_editar["Cartão"]) if despesa_editar is not None else 0)
    parcelas = st.number_input("Parcelas", min_value=1, step=1, value=int(despesa_editar["Parcelas"]) if despesa_editar is not None else 1, key="input_parcelas_edit")
    observacao = st.text_area("Observação", value=despesa_editar["Observação"] if despesa_editar is not None else "")
    
    if st.button("Salvar Despesa"):
        if despesa_editar is None:  # Novo lançamento
            salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao)
            st.success("Despesa salva com sucesso!")
        else:  # Editando lançamento existente
            editar_despesa(index_editar, data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao)
            st.success("Despesa editada com sucesso!")
        st.rerun()

    st.subheader("Histórico de Despesas")
    st.dataframe(despesas)

    st.subheader("Deletar uma Despesa")
    index = st.number_input("Informe o índice da despesa a ser deletada", min_value=0, max_value=len(despesas)-1 if not despesas.empty else 0, step=1)
    if st.button("Deletar Despesa"):
        deletar_despesa(index)
        st.success("Despesa deletada com sucesso!")
        st.rerun()

def pagina_graficos():
    st.title("Análise de Despesas")
    despesas = carregar_despesas()
    if despesas.empty:
        st.warning("Nenhuma despesa registrada.")
        return
    
    st.subheader("Total gasto por categoria")
    df_categoria = despesas.groupby("Categoria")["Valor"].sum().reset_index()
    fig, ax = plt.subplots()
    bars = ax.barh(df_categoria["Categoria"], df_categoria["Valor"], color='skyblue')
    ax.set_xlabel("Valor Total")
    ax.set_ylabel("Categoria")
    ax.set_title("Gastos por Categoria")
    for bar in bars:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'R${bar.get_width():,.2f}', va='center')
    st.pyplot(fig)
    
    st.subheader("Total gasto por mês de vencimento")
    despesas["Data de Vencimento"] = pd.to_datetime(despesas["Data de Vencimento"], errors='coerce')
    despesas["Mês de Vencimento"] = despesas["Data de Vencimento"].dt.to_period("M")
    df_vencimento = despesas.groupby("Mês de Vencimento")["Valor"].sum().reset_index()
    df_vencimento["Mês de Vencimento"] = df_vencimento["Mês de Vencimento"].astype(str)
    fig, ax = plt.subplots()
    bars = ax.bar(df_vencimento["Mês de Vencimento"], df_vencimento["Valor"], color='lightcoral')
    ax.set_xlabel("Mês de Vencimento")
    ax.set_ylabel("Valor Total")
    ax.set_title("Gastos por Mês de Vencimento")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'R${bar.get_height():,.2f}', ha='center', va='bottom')
    st.pyplot(fig)

def main():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        autenticar_usuario()
    else:
        st.sidebar.title(f"Bem-vindo, {st.session_state['usuario']}")
        if st.sidebar.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()
        
        st.sidebar.title("Menu")
        pagina = st.sidebar.radio("Navegação", ["Lançamento de Despesas", "Análise de Despesas"])
        
        if pagina == "Lançamento de Despesas":
            pagina_lancamento()
        else:
            pagina_graficos()

if __name__ == "__main__":
    main()
