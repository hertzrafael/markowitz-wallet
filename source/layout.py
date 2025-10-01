from source.assets import Assets
from source.markowitz import Markowitz
from pandas import to_datetime, read_csv

import streamlit as st
import os

class Layout:

    def __init__(self, config):
        if "assets" not in st.session_state:
            st.session_state["assets"] = []
        
        self.config = config
        self.run()

    def run(self):
        st.set_page_config(page_title="Markowitz Otimização", layout="wide")

        map = self.__make_sidebar__()

        tab_result, tab_assets = st.tabs([
            "RESULTADOS", 
            "ATIVOS"
        ])

        with tab_result:
            self.__tab_results__(map['objective'], map['assets'])

        with tab_assets:
            self.__tab_assets__()

        print(map['assets'])

    def __make_sidebar__(self):
        st.sidebar.header("Carteira")
        objective = st.sidebar.selectbox(
            'Objetivo:',
            ('Minimizar risco', 'Maximizar retorno')
        )

        files = [file for file in os.listdir(os.path.join(os.getcwd(), self.config.tmp_name)) if file.endswith('.csv')]
        assets = st.sidebar.selectbox(
            'Escolha o arquivo com os ativos para análise:',
            options=files
        )

        return {
            'assets': assets,
            'objective': objective
        }
    
    def __tab_results__(self, objective, file_name):

        if file_name is None:
            st.error('Selecione um arquivo válido para obter os resultados.')
            return

        folder = os.path.join(os.getcwd(), self.config.tmp_name)
        file = read_csv(os.path.join(folder, f'{file_name}'), index_col=0, parse_dates=True)
        markowitz = Markowitz(file)

        with st.expander('Informações'):
            st.write(f'''
                Você está selecionando o objetivo '{objective}' dos ativos:

                {", ".join([column for column in file.columns])}.
            ''')

        st.header(f'Objetivo: {objective}')

        if objective == 'Minimizar risco':
            self.__result_minimize_risk__(markowitz)
        else:
            self.__result_maximize_profit__(markowitz)

        
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
            assets = Assets(tickers=selected_assets)
            download = assets.download(
                '2025-01-01', 
                to_datetime('today').strftime('%Y-%m-%d'), 
                save=True, 
                save_path=f'{self.config.tmp_name}/{file_name}'
            )

            if download is not None:
                st.sidebar.success('O arquivo foi baixado com sucesso.')
    
    def __result_minimize_risk__(self, markowitz):
        target_annual_return = st.number_input(
            'Insira o retorno alvo anual:', 
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            format="%.2f"
        )

        optimize_markowitz = markowitz.minimize_risk(target_annual_return)
        st.subheader('Resultado:')

        _, first_metric, second_metric, _ = st.columns(4)

        with first_metric:
            st.metric('Retorno final', optimize_markowitz['final_return'], border=True)

        with second_metric:
            st.metric('Risco final', optimize_markowitz['final_risk'], border=True)
        
        st.dataframe(optimize_markowitz['weights'])

    def __result_maximize_profit__(self, markowitz):
        st.subheader('Resultado:')

        cap = st.number_input(
            'Insira o CAP:', 
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            format="%.2f"
        )

        with st.expander('O que é CAP?'):
            st.write('''
                    CAP é a alocação (porcentagem) máxima que cada ativo poderá ter. Ou seja, quanto menor, mais diversificada a
                    carteira deve ser.
            ''')

        optimize_markowitz = markowitz.maximize_profit(cap)

        _, first_metric, second_metric, third_metric, _ = st.columns(5)

        with first_metric:
            st.metric('Retorno anual', optimize_markowitz['annual_return'], border=True)

        with second_metric:
            st.metric('Risco final', optimize_markowitz['final_wallet_risk'], border=True)

        with third_metric:
            st.metric('Risco alvo', optimize_markowitz['target_risk'], border=True)
        
        st.dataframe(optimize_markowitz['weights'])
