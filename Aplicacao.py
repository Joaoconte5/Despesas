import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

def autenticar_usuario():
    st.sidebar.title("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if (usuario == "Suellen" and senha == "1234") or (usuario == "João" and senha == "5678"):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos")

def salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, usuario):
    df = pd.DataFrame([[data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, usuario]],
                      columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação", "Usuário"])
    try:
        historico = pd.read_csv("despesas.csv")
        historico = pd.concat([historico, df], ignore_index=True)
    except FileNotFoundError:
        historico = df
    
    historico.to_csv("despesas.csv", index=False)

def carregar_despesas():
    try:
        return pd.read_csv("despesas.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação", "Usuário"])

def deletar_despesa(index):
    despesas = carregar_despesas()
    if 0 <= index < len(despesas):
        despesas = despesas.drop(index).reset_index(drop=True)
        despesas.to_csv("despesas.csv", index=False)

def pagina_lancamento():
    st.title("Lançamento de Despesas")
    
    data = st.date_input("Data da Despesa", format="DD/MM/YYYY", value=date.today())
    data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY", value=date.today())
    categoria = st.selectbox("Categoria", ["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "viagem", "Casa Utensilio", "Casa concerto", "Diversos", "Carro",
"Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza","Vestuário", "Cursos e treinamentos"])
    origem = st.selectbox("Origem", ["Suellen", "João", "Conjunto"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    cartao = st.selectbox("Cartão", ["Crédito", "Débito"])
    parcelas = st.number_input("Parcelas", min_value=1, step=1, value=1)
    observacao = st.text_area("Observação")
    
    if st.button("Salvar Despesa"):
        salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, st.session_state["usuario"])
        st.success("Despesa salva com sucesso!")
        st.rerun()
    
    st.subheader("Histórico de Despesas")
    despesas = carregar_despesas()
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
        st.sidebar.title(f"Bem-vindo Guerreiro(a), {st.session_state['usuario']}")
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



