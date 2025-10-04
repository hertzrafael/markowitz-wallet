# markowitz-wallet
Trabalho para a disciplina de Otimização Aplicada a Negócios, usando otimização aplicada a uma carteira de ativos visando minimizar o risco ou maximizar o lucro.

## Como usar?

### 1. Instalação das bibliotecas

Você precisará instalar as dependências que estão no `requirements.txt` e também instalar, através do `conda` e não do `pip`, a biblioteca `ipopt`, que será utilizada para realizar as otimizações necessárias para o objetivo do projeto.

```python
conda install -c conda-forge ipopt
```

### 2. Download dos ativos

Na aba `ATIVOS`, você deverá inserir os tickets dos ativos que você tem interesse e, logo após, realizar o download do histórico de mudança percentual diária dos ativos selecionados.

### 3. Minimização de Risco

Com os dados dos ativos instalados, basta você escolher a opção `Minimizar risco` em `Objetivo`, para que a aplicação já funcione quando você abra a seção `RESULTADOS` da aplicação. Dessa forma, você pode escolher um retorno anual alvo para que a diversificação da carteira de ativos atinja o seu objetivo.

### 4. Maximização de Lucro

De forma semelhante à Minimização de risco, mude a opção em `Objetivo` para `Maximizar retorno`. Assim, a aplicação já estará funcionando com o objetivo de retornar o máximo de lucro dentro da situação analisada. Você tem a opção de escolher um `CAP` também.
