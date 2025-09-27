from source.assets import Assets
from pandas import to_datetime

import streamlit as st
import os

class Layout:

    def __init__(self):
        if "assets" not in st.session_state:
            st.session_state["assets"] = []
        
        self.run()

    def run(self):
        st.set_page_config(page_title="Markowitz Otimização", layout="wide")

        self.__make_sidebar__()

        tab_result, tab_assets = st.tabs([
            "RESULTADOS", 
            "ATIVOS"
        ])

        with tab_assets:
            self.__tab_assets__()

        print(st.session_state["assets"])

    def __make_sidebar__(self):
        st.sidebar.header("Carteira")
        objective = st.sidebar.selectbox(
            'Objetivo:',
            ('Minimizar risco', 'Maximizar retorno')
        )

        files = [file for file in os.listdir(os.path.join(os.getcwd(), 'tmp')) if file.endswith('.csv')]
        assets = st.sidebar.multiselect(
            'Escolha o arquivo com os ativos para análise.',
            options=files
        )
    
    def __tab_assets__(self):
        asset = st.text_input(
            'Ativo:',
            placeholder='Insira aqui o ativo a ser adicionado...'
        ).upper()
        
        if st.button('Adicionar ativo', type='primary') and asset and asset not in st.session_state['assets']:
            st.session_state["assets"].append(asset)

        selected_assets = st.multiselect(
            'Ativos adicionados:',
            default=st.session_state["assets"],
            options=st.session_state["assets"]
        )

        file_name = st.text_input('Insira o nome do arquivo a ser criado:')

        if st.button('Baixar retorno dos ativos'):
            assets = Assets(tickers=st.session_state["assets"])
            download = assets.download(
                '2025-01-01', 
                to_datetime('today').strftime('%Y-%m-%d'), 
                save=True, 
                save_path=f'tmp/{file_name}'
            )

            if download is not None:
                st.sidebar.success('O arquivo foi baixado com sucesso.')