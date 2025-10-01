from pandas import read_csv, Series, DataFrame
from pyomo.environ import ConcreteModel, Var, Objective, Set, NonNegativeReals, SolverFactory, Constraint, minimize, maximize, value

import numpy as np

class Markowitz:

    def __init__(self, frame):
        self.frame = frame
        self.assets = frame.columns.tolist()

    def minimize_risk(self, target_annual_return):
        daily_returns = self.frame

        mean_daily_returns = daily_returns.mean()
        cov_daily_matrix = daily_returns.cov()

        # Model Config
        target_return = (target_annual_return / 100) / 252

        model = ConcreteModel()
        model.A = Set(initialize=self.assets)
        model.w = Var(model.A, domain=NonNegativeReals, bounds=(0,1))
        
        def weight_restriction(model):
            return sum(model.w[asset] for asset in model.A) == 1
        
        def return_rule(model):
            return sum(model.w[asset] * mean_daily_returns[asset] for asset in model.A) >= target_return

        model.weight_restriction = Constraint(rule=weight_restriction)
        model.return_restriction = Constraint(rule=return_rule)

        def objective_variance(model):
            return sum(model.w[i] * model.w[j] * cov_daily_matrix.loc[i, j] for i in model.A for j in model.A)
        
        model.objective = Objective(rule=objective_variance, sense=minimize)

        solver = SolverFactory('ipopt')
        solver.solve(model, tee=True)

        optimized_weights = (DataFrame(Series({a: value(model.w[a]) for a in model.A}) * 100)
                .rename(columns={0: 'Porcentagem'})
        )
        optimized_weights['Porcentagem'] = optimized_weights['Porcentagem'].round(2)
        
        final_return = np.dot(mean_daily_returns, optimized_weights) * 252
        final_risk = np.sqrt(np.dot(optimized_weights.T, np.dot(cov_daily_matrix, optimized_weights))) * np.sqrt(252)

        return {
            'weights': optimized_weights,
            'final_return': np.round(final_return, 2),
            'final_risk': np.round(final_risk, 2)
        }

    def maximize_profit(self, cap):
        model = ConcreteModel()
        model.A = Set(initialize=self.assets)

        # --- Estatísticas ---
        mu_d = self.frame.mean()        # média diária
        Sigma_d = self.frame.cov()      # cov diária
        n = len(self.assets)

        # Risco alvo = média dos desvios-padrão anuais individuais
        std_ind_anu = self.frame.std() * np.sqrt(252.0)
        sigma_alvo = float(std_ind_anu.mean())
        var_alvo = (sigma_alvo**2)/4

        ANUAL = 252.0
        cap = cap / 100

        # --- Modelo Pyomo: max retorno, risco <= alvo, long-only, cap por ativo ---
        m = ConcreteModel()
        m.A = Set(initialize=self.assets)

        def bounds_w(m, a):
            return (0.0, cap)   # long-only e teto de 8%
        
        m.w = Var(m.A, bounds=bounds_w)

        # orçamento
        m.budget = Constraint(expr=sum(m.w[a] for a in m.A) == 1.0)

        # risco anual da carteira <= alvo: (w' Σ_d w)*252 <= sigma_alvo^2
        Sigma_np = Sigma_d.values
        idx = {a:i for i,a in enumerate(self.assets)}
        m.risk = Constraint(
            expr = ANUAL * sum(m.w[i]*Sigma_np[idx[i], idx[j]]*m.w[j] for i in m.A for j in m.A) == var_alvo
        )

        # objetivo: maximizar retorno anual esperado
        mu_np = mu_d.values
        m.obj = Objective(
            expr = ANUAL * sum(m.w[a]*mu_d[a] for a in m.A),
            sense = maximize
        )

        # --- Resolver com Ipopt e tolerâncias mais rígidas ---
        solver = SolverFactory('ipopt')
        solver.options.update({
            'tol': 1e-9,
            'constr_viol_tol': 1e-9,
            'compl_inf_tol': 1e-9,
            'bound_relax_factor': 0.0,   # não relaxar bounds
            'print_level': 3
        })
        res = solver.solve(m, tee=True)

        # --- Extração dos pesos ---
        w = Series({a: value(m.w[a]) for a in m.A})

        # Limpeza numérica: zera negativos muito pequenos e renormaliza
        w[w < 0] = np.where(w[w < 0] > -1e-10, 0.0, w[w < 0])  # só zera “-0.00%”
        if (w < -1e-8).any():
            print("Aviso: bounds violados numericamente. Ajustando e renormalizando.")
        w = w.clip(lower=0.0)          # garante long-only
        w = w / w.sum()                # renormaliza para somar 1

        # --- Estatísticas finais ---
        ret_anu = float(mu_d @ w) * ANUAL
        var_anu = float(w.values @ Sigma_np @ w.values) * ANUAL
        vol_anu = np.sqrt(var_anu)

        print("\n--- Otimização de Carteira (Max Retorno, risco <= alvo) ---")
        print(f"Risco alvo (média dos ativos): {sigma_alvo:.2%}")
        print(f"Risco final da carteira:       {vol_anu:.2%}")
        print(f"Retorno anualizado:            {ret_anu:.2%}\n")

        print("Pesos (top 15):")
        print((w.sort_values(ascending=False).head(40)*100).round(2).astype(str) + "%")

        return {
            'weights': w.sort_values(ascending=False),
            'annual_return': np.round(ret_anu, 2),
            'final_wallet_risk': np.round(vol_anu, 2),
            'target_risk': np.round(sigma_alvo, 2)
        }