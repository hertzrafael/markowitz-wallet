from pandas import read_csv, Series, DataFrame
from pyomo.environ import ConcreteModel, Var, Objective, Set, NonNegativeReals, SolverFactory, Constraint, minimize, value

import numpy as np

class Markowitz:

    def __init__(self, frame):
        self.frame = frame

    def minimize_risk(self, target_annual_return):
        daily_returns = self.frame
        assets = daily_returns.columns.tolist()

        mean_daily_returns = daily_returns.mean()
        cov_daily_matrix = daily_returns.cov()

        # Model Config
        target_return = (target_annual_return / 100) / 252

        model = ConcreteModel()
        model.A = Set(initialize=assets)
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