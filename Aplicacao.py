import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# Substitua pelo ID do seu arquivo no Google Drive
GDRIVE_CSV_URL = "https://drive.google.com/uc?id=12zWDtYgLGE0-u_aXKmPFQJbYj5WTuq-k"

# Função para carregar despesas do Google Drive
def carregar_despesas():
    try:
        df = pd.read_csv(GDRIVE_CSV_URL)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação", "Usuário"])

# Função para salvar despesas no Google Drive (deve ser feita manualmente se usar link público)
def salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, usuario):
    df = pd.DataFrame([[data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, usuario]],
                      columns=["Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação", "Usuário"])
    
    historico = carregar_despesas()
    historico = pd.concat([historico, df], ignore_index=True)
    historico.to_csv("despesas.csv", index=False)
    st.warning("⚠️ Para atualizar no Google Drive, envie manualmente o novo arquivo despesas.csv!")

# Função para deletar uma despesa
def deletar_despesa(index):
    despesas = carregar_despesas()
    if 0 <= index < len(despesas):
        despesas = despesas.drop(index).reset_index(drop=True)
        despesas.to_csv("despesas.csv", index=False)
        st.warning("⚠️ Para atualizar no Google Drive, envie manualmente o novo arquivo despesas.csv!")

# Função para editar uma despesa
def editar_despesa(index):
    despesas = carregar_despesas()
    if 0 <= index < len(despesas):
        row = despesas.iloc[index]
        return row
    return None

# Função para página de gráficos
def pagina_graficos():
    st.title("Análise de Despesas")
    
    despesas = carregar_despesas()

    if not despesas.empty:
        # Criar gráfico de barras para despesas por categoria
        categoria_despesas = despesas.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        st.subheader("Despesas por Categoria")
        st.bar_chart(categoria_despesas)

        # Criar gráfico de linha para despesas ao longo do tempo
        despesas['Data'] = pd.to_datetime(despesas['Data'], format="%Y-%m-%d")
        despesas_por_data = despesas.groupby(despesas['Data'].dt.to_period('M'))['Valor'].sum()
        st.subheader("Despesas ao Longo do Tempo")
        st.line_chart(despesas_por_data)
    else:
        st.warning("Não há despesas registradas para análise.")

# Página de lançamento de despesas
def pagina_lancamento():
    st.title("Lançamento de Despesas")
    
    despesas = carregar_despesas()
    indices = ["Novo Lançamento"] + list(range(len(despesas)))
    index_editar = st.selectbox("Informe o índice da despesa a ser editada", indices)
    despesa_editar = editar_despesa(index_editar) if isinstance(index_editar, int) else None
    
    categorias = ["Uber/99", "Mercado", "Esportes", "Casa Utensilio", "Saúde", "Lazer", "Delivery Bebida", "Restaurante/Bar", "Entretenimento", "Diversos", "Nina", "Casa concerto", "Beleza", "Delivery Comida", "Vastuário"]
    
    data = st.date_input("Data da Despesa", format="DD/MM/YYYY", value=despesa_editar["Data"] if despesa_editar is not None else date.today())
    data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY", value=despesa_editar["Data de Vencimento"] if despesa_editar is not None else date.today())
    categoria = st.selectbox("Categoria", categorias, index=categorias.index(despesa_editar["Categoria"]) if despesa_editar is not None and despesa_editar["Categoria"] in categorias else 0)
    origem = st.selectbox("Origem", ["Suellen", "João", "Conjunto"], index=["Suellen", "João", "Conjunto"].index(despesa_editar["Origem"]) if despesa_editar is not None else 0)
    valor = st.number_input("Valor", min_value=0.0, format="%.2f", value=despesa_editar["Valor"] if despesa_editar is not None else 0.0)
    cartao = st.selectbox("Cartão", ["Crédito", "Débito"], index=["Crédito", "Débito"].index(despesa_editar["Cartão"]) if despesa_editar is not None else 0)
    
    parcelas = despesa_editar["Parcelas"] if despesa_editar is not None else "1"
    try:
        parcelas = int(str(parcelas).split()[0])
    except ValueError:
        parcelas = 1
    
    parcelas = st.number_input("Parcelas", min_value=1, step=1, value=parcelas)
    
    observacao = st.text_area("Observação", value=despesa_editar["Observação"] if despesa_editar is not None else "")
    usuario = st.session_state.get("usuario", "Desconhecido")
    
    if st.button("Salvar Despesa"):
        salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao, usuario)
        st.success("Despesa salva com sucesso!")
        st.rerun()
    
    st.subheader("Histórico de Despesas")
    st.dataframe(despesas)
    
    st.subheader("Deletar uma Despesa")
    index_deletar = st.number_input("Informe o índice da despesa a ser deletada", min_value=0, max_value=len(despesas)-1 if not despesas.empty else 0, step=1)
    if st.button("Deletar Despesa"):
        deletar_despesa(index_deletar)
        st.success("Despesa deletada com sucesso!")
        st.rerun()

# Controle principal
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
