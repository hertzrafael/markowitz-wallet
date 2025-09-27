import streamlit as st

class Layout:

    def __init__(self):
        self.run()

    def run(self):
        st.set_page_config(page_title="Markowitz Otimização", layout="wide")

        st.sidebar.header("Carteira")
        objective = st.sidebar.selectbox(
            'Objetivo:',
            ('Minimizar risco', 'Maximizar retorno')
        )

        asset = st.sidebar.text_input(
            'Ativo:',
            placeholder='Insira aqui o ativo a ser adicionado...'
        )

        st.sidebar.divider()

        selected_assets = st.sidebar.multiselect(
            'Ativos adicionados:',
            options=[]
        )

        print(objective)