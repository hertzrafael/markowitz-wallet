import yfinance as yf

import os

class Assets:

    def __init__(self, tickers):
        self.tickers = tickers

    def download(self, start, end, save=True, save_path=None):
        print(f'Iniciando download de {self.tickers}...')
        
        try:
            assets = yf.download(self.tickers, start=start, end=end)['Close']
            print(assets)

            if not save:
                return assets

            daily_return = assets.pct_change().dropna()
            daily_return.columns = [column.replace('.SA', '') for column in daily_return.columns]

            if daily_return.empty:
                print('Verifique se os dados foram baixados corretamente.')
                return None

            print('Iniciando salvamento do arquivo...')
            path = os.path.join(os.getcwd(), save_path)
            if os.path.exists(path):
                print('Já existe um arquivo com este path, delete-o ou altere o nome/caminho.')
                return
            
            if not path.endswith('.csv'):
                path = f'{path}.csv'
            
            daily_return.to_csv(path)
            print('Arquivo criado com sucesso.')

        except Exception as ex:
            print(f'Erro ao baixar os ativos: {ex}')
            assets = None

        return assets
    
    
        
