from pandas import read_csv

from pyomo.environ import ConcreteModel, Var, Objective, Set, NonNegativeReals, SolverFactory, Constraint, minimize

class Markowitz:

    def __init__(self, frame):
        self.frame = frame

    def minimize_risk(self):
        daily_returns = self.frame
        assets = daily_returns.columns.tolist()

        mean_daily_returns = daily_returns.mean()
        cov_daily_matrix = daily_returns.cov()

        retorno_alvo = 15

        model = ConcreteModel()
        model.A = Set(initialize=assets)
        model.w = Var(model.A, domain=NonNegativeReals, bounds=(0,1))
        
        def weight_restriction(model):
            return sum(model.w[asset] for asset in model.A) == 1
        
        def return_rule(model):
            return sum(model.w[asset] * mean_daily_returns[asset] for asset in model.A) == retorno_alvo

        model.weight_restriction = Constraint(rule=weight_restriction)
        model.return_restriction = Constraint(rule=return_rule)

        def objective_variance(model):
            return sum(model.w[i] * model.w[j] * cov_daily_matrix.loc[i, j] for i in model.A for j in model.A)
        
        model.objective = Objective(rule=objective_variance, sense=minimize)

        ipopt_solver = SolverFactory('ipopt')
        print(f"Ipopt disponível para Pyomo: {ipopt_solver.available()}")