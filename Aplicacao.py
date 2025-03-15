import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Controle de Despesas")

st.title("Lançamentos de Despesas")

# Definir o caminho do arquivo dentro do app
arquivo_excel = "gestao_despesas.xlsx"

with st.container():
    st.header("Adicionar Nova Despesa")
    
    data = st.date_input("Data da Despesa")
    data_vencimento = st.date_input("Data de Vencimento")
    categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Saúde", "Lazer", "Outros"])
    origem = st.text_input("Origem da Despesa")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    cartao = st.selectbox("Cartão", ["Crédito", "Débito"])
    parcelas = st.number_input("Parcelas", min_value=1, step=1)

    if st.button("Salvar Despesa"):
        # Criar um DataFrame com os dados inseridos
        nova_despesa = pd.DataFrame(
            [[data, data_vencimento, categoria, origem, valor, cartao, parcelas]],
            columns=["Data", "Data Vencimento", "Categoria", "Origem", "Valor", "Cartão", "Parcelas"]
        )
        
        # Verificar se o arquivo já existe dentro do app
        if os.path.exists(arquivo_excel):
            df_existente = pd.read_excel(arquivo_excel)
            df_final = pd.concat([df_existente, nova_despesa], ignore_index=True)
        else:
            df_final = nova_despesa
        
        # Salvar dentro do app
        df_final.to_excel(arquivo_excel, index=False)
        st.success("Despesa salva com sucesso!")
        st.rerun()  # Atualiza a página para exibir a nova despesa imediatamente

# Criar uma tabela para exibir os lançamentos salvos
st.header("Histórico de Despesas")

if os.path.exists(arquivo_excel):
    df = pd.read_excel(arquivo_excel)

    # Criar botões de exclusão para cada linha
    df["Excluir"] = [f"Excluir {i}" for i in range(len(df))]

    # Exibir a tabela formatada
    st.dataframe(df, height=400)

    # Criar uma opção para excluir uma linha específica
    excluir_index = st.selectbox("Selecione um lançamento para excluir:", df.index)

    if st.button("Excluir Lançamento"):
        df = df.drop(index=excluir_index).reset_index(drop=True)  # Remove a linha selecionada
        df.to_excel(arquivo_excel, index=False)  # Salva a planilha atualizada
        st.success("Despesa removida com sucesso!")
        st.rerun()  # Atualiza a página imediatamente

else:
    st.info("Nenhuma despesa cadastrada ainda.")
