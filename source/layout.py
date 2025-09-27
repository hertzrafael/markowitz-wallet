import streamlit as st

class Layout:

    def __init__(self):
        if "assets" not in st.session_state:
            st.session_state["assets"] = []
        
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
        
        if st.sidebar.button('Adicionar ativo', type='primary') and asset:
            st.session_state["assets"].append(asset.upper())

        st.sidebar.divider()

        selected_assets = st.sidebar.multiselect(
            'Ativos adicionados:',
            default=st.session_state["assets"],
            options=st.session_state["assets"]
        )

        print(st.session_state["assets"])