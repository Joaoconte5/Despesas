import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt  # Certifique-se de que está importado aqui
from datetime import date
from supabase import create_client, Client


# Configuração do Supabase
SUPABASE_URL = "https://kmnrrqwgawojqntixfsf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImttbnJycXdnYXdvanFudGl4ZnNmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI1MDc5OTAsImV4cCI6MjA1ODA4Mzk5MH0.u8wxqBqJ1QI6zvSA74uvoQhxJBRoAOPeDLy_PqGgpuA"  # Substitua pela sua chave de API
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constantes para login
USUARIOS_VALIDOS = {
    "Suellen": "1234",
    "João": "5678"
}

def autenticar_usuario():
    """Função para autenticar o usuário"""
    if "autenticado" in st.session_state and st.session_state["autenticado"]:
        return
    st.sidebar.title("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if USUARIOS_VALIDOS.get(usuario) == senha:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.experimental_rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos")

def carregar_despesas():
    """Função para carregar as despesas do banco de dados"""
    response = supabase.table("despesas").select("*").execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame(columns=["id", "Data", "Data de Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas", "Observação"])

def salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao):
    """Função para salvar uma nova despesa"""
    supabase.table("despesas").insert({
        "Data": str(data),
        "Data de Vencimento": str(data_vencimento),
        "Categoria": categoria,
        "Origem": origem,
        "Valor": valor,
        "Cartão": cartao,
        "Parcelas": parcelas,
        "Observação": observacao
    }).execute()

def deletar_despesa(index):
    """Função para deletar uma despesa"""
    supabase.table("despesas").delete().eq("id", index).execute()

def pagina_lancamento():
    """Página para lançamento ou exclusão de despesas"""
    st.title("Lançamento de Despesas")
    
    despesas = carregar_despesas()  # Carregar todas as despesas
    opcao_edicao = st.radio("Você quer adicionar uma nova despesa ou excluir uma despesa?", ("Adicionar Nova Despesa", "Excluir Despesa"))

    # Exibição da tabela com todos os lançamentos
    st.subheader("Lançamentos Realizados")
    if not despesas.empty:
        st.dataframe(despesas)  # Exibe a tabela com todas as despesas
    else:
        st.warning("Não há despesas registradas.")

    if opcao_edicao == "Adicionar Nova Despesa":
        st.subheader("Novo Lançamento com Dados de Despesa Existente")

        # Opção de selecionar ID existente para pré-preencher os dados
        id_existente = st.selectbox("Escolher uma despesa existente", ["Nenhum"] + list(despesas["id"].astype(str)))

        # Se um ID for selecionado, preenche os campos com os dados existentes
        if id_existente != "Nenhum":
            despesa_existente = despesas[despesas["id"] == int(id_existente)].iloc[0]
            data = st.date_input("Data da Despesa", format="DD/MM/YYYY", value=pd.to_datetime(despesa_existente["Data"]))
            data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY", value=pd.to_datetime(despesa_existente["Data de Vencimento"]))
            categoria = st.selectbox("Categoria", ["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "Viagem", "Casa Utensílio", "Casa Concerto", "Diversos", "Carro", "Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza", "Vestuário", "Cursos e Treinamentos"], index=["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "Viagem", "Casa Utensílio", "Casa Concerto", "Diversos", "Carro", "Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza", "Vestuário", "Cursos e Treinamentos"].index(despesa_existente["Categoria"]))
            origem = st.selectbox("Origem", ["Suellen", "João", "Conjunto"], index=["Suellen", "João", "Conjunto"].index(despesa_existente["Origem"]))
            valor = st.number_input("Valor", min_value=0.0, format="%.2f", value=despesa_existente["Valor"])
            cartao = st.selectbox("Cartão", ["Crédito", "Débito"], index=["Crédito", "Débito"].index(despesa_existente["Cartão"]))
            parcelas = st.text_input("Parcelas", value=str(despesa_existente.get("Parcelas", "")))
            observacao = st.text_area("Observação", value=despesa_existente["Observação"])
        else:
            data = st.date_input("Data da Despesa", format="DD/MM/YYYY", value=date.today())
            data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY", value=date.today())
            categoria = st.selectbox("Categoria", ["Mercado", "Delivery Comida", "Delivery Bebida", "Restaurante/Bar", "Saúde", "Lazer", "Viagem", "Casa Utensílio", "Casa Concerto", "Diversos", "Carro", "Esportes", "Uber/99", "Entretenimento", "Nina", "Beleza", "Vestuário", "Cursos e Treinamentos"])
            origem = st.selectbox("Origem", ["Suellen", "João", "Conjunto"])
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            cartao = st.selectbox("Cartão", ["Crédito", "Débito"])
            parcelas = st.text_input("Parcelas", value=str(""))
            observacao = st.text_area("Observação")
        
        if st.button("Salvar Despesa"):
            salvar_despesa(data, data_vencimento, categoria, origem, valor, cartao, parcelas, observacao)
            st.success("Despesa salva com sucesso!")
            st.rerun()

    elif opcao_edicao == "Excluir Despesa":
        id_excluir = st.number_input("Informe o ID da despesa a ser excluída", min_value=0, step=1)
        if st.button("Excluir Despesa"):
            deletar_despesa(id_excluir)
            st.success(f"Despesa com ID {id_excluir} excluída com sucesso!")
            st.rerun()

def main():
    """Função principal de controle da aplicação"""
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        autenticar_usuario()
    else:
        st.sidebar.title(f"Bem-vindo, Guerreiro(a) {st.session_state['usuario']}")
        if st.sidebar.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()
        
        st.sidebar.title("Menu")
        pagina = st.sidebar.radio("Navegação", ["Lançamento de Despesas", "Gráficos"])
        
        if pagina == "Lançamento de Despesas":
            pagina_lancamento()
        elif pagina == "Gráficos":
            pagina_graficos()

def pagina_graficos():
    """Página para exibir gráficos de despesas"""
    st.title("Gráficos de Despesas")

    # Filtro de origem
    origem_filtro = st.selectbox("Filtrar por Origem", ["Todos", "Suellen", "João", "Conjunto"])
    
    despesas = carregar_despesas()
    
    if origem_filtro != "Todos":
        despesas = despesas[despesas["Origem"] == origem_filtro]

    # gráfico de despesas por categoria
    despesas_categoria = despesas.groupby("Categoria")["Valor"].sum().reset_index()

    st.subheader("Despesas por Categoria")
    fig, ax = plt.subplots()
    ax.bar(despesas_categoria["Categoria"], despesas_categoria["Valor"], color='skyblue')
    ax.set_xlabel('Categoria')
    ax.set_ylabel('Valor Total (R$)')
    ax.set_title('Despesas por Categoria')

    # Adicionando rótulos de dados com o símbolo R$
    for i, v in enumerate(despesas_categoria["Valor"]):
        ax.text(i, v + 10, f"R${v:,.2f}", ha='center', va='bottom', fontweight='bold')

    st.pyplot(fig)

def pagina_graficos():
    """Página para exibir gráficos de despesas"""
    st.title("Gráficos de Despesas")

    # Filtro de origem
    origem_filtro = st.selectbox("Filtrar por Origem", ["Todos", "Suellen", "João", "Conjunto"])
    
    # Carregar as despesas
    despesas = carregar_despesas()
    
    if origem_filtro != "Todos":
        despesas = despesas[despesas["Origem"] == origem_filtro]

    # Gráfico de despesas por categoria (com a categoria no eixo Y)
    despesas_categoria = despesas.groupby("Categoria")["Valor"].sum().reset_index()

    st.subheader("Despesas por Categoria")
    fig1, ax1 = plt.subplots()
    ax1.barh(despesas_categoria["Categoria"], despesas_categoria["Valor"], color='skyblue')  # Usando barh para gráfico horizontal
    ax1.set_xlabel('Valor Total (R$)')
    ax1.set_ylabel('Categoria')
    ax1.set_title('Despesas por Categoria')

    # Adicionando rótulos de dados com o símbolo R$
    for i, v in enumerate(despesas_categoria["Valor"]):
        ax1.text(v + 10, i, f"R${v:,.2f}", va='center', fontweight='bold')  # Ajustando a posição do rótulo para gráfico horizontal

    st.pyplot(fig1)


    # Garantir que 'Data de Vencimento' esteja no formato datetime
    despesas["Data de Vencimento"] = pd.to_datetime(despesas["Data de Vencimento"], errors='coerce')

    # Gráfico de despesas por mês de vencimento (apenas mês/ano)
    despesas_vencimento = despesas.groupby(despesas["Data de Vencimento"].dt.to_period("M"))["Valor"].sum().reset_index()

    st.subheader("Despesas por Mês de Vencimento")
    fig2, ax2 = plt.subplots()
    ax2.bar(despesas_vencimento["Data de Vencimento"].astype(str), despesas_vencimento["Valor"], color='skyblue')
    ax2.set_xlabel('Mês/Ano')
    ax2.set_ylabel('Valor Total (R$)')
    ax2.set_title('Despesas por Mês de Vencimento')

    # Adicionando rótulos de dados com o símbolo R$
    for i, v in enumerate(despesas_vencimento["Valor"]):
        ax2.text(i, v + 10, f"R${v:,.2f}", ha='center', va='bottom', fontweight='bold')

    st.pyplot(fig2)






if __name__ == "__main__":
    main()
