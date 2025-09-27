from source.assets import Assets
from pandas import to_datetime

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
        ).upper()
        
        if st.sidebar.button('Adicionar ativo', type='primary') and asset and asset not in st.session_state['assets']:
            st.session_state["assets"].append(asset)

        st.sidebar.divider()

        selected_assets = st.sidebar.multiselect(
            'Ativos adicionados:',
            default=st.session_state["assets"],
            options=st.session_state["assets"]
        )

        if st.sidebar.button('Baixar retorno dos ativos'):
            assets = Assets(tickers=st.session_state["assets"])
            download = assets.download(
                '2025-01-01', 
                to_datetime('today').strftime('%Y-%m-%d'), 
                save=True, 
                save_path='tmp/ativos'
            )

            if download is not None:
                st.sidebar.success('O arquivo foi baixado com sucesso.')

        print(st.session_state["assets"])