import pandas as pd
import numpy as np
import math
from scipy.optimize import curve_fit
import statsmodels.api as sm
from sklearn.metrics import r2_score

input_path = "./Sample data/input/"
output_path = "./Sample data/output/"

Emission = pd.read_excel(input_path + "Point_emission_sources.xlsx", index_col='FID')
Sites_receptor = pd.read_excel(input_path + "Monitoring_sites.xlsx", index_col='FID')
Efficiency = pd.read_excel(input_path + "Emission_efficiency.xlsx", index_col='FID')

# Gaussian weighting function-aided Proximity Model
# 1. calculate Euclidean distance from each Pes to each Vr
Distance = []
for i in range(0, len(Emission)):
    Dis_sum = []
    for j in range(0, len(Sites_receptor)):
        Dis = math.sqrt((Emission.loc[i, 'X'] - Sites_receptor.loc[j, 'X'])**2
                         + (Emission.loc[i, 'Y'] - Sites_receptor.loc[j, 'Y'])**2)  # Euclidean distance
        Dis_sum.append(Dis)
    Distance.append(Dis_sum)
result_1 = pd.DataFrame(data=Distance, index=Emission.index, columns=Sites_receptor.index.T)

# 2. extract the minimum distance points which distance <= 50km
result_2 = result_1.T
b = 9500.0
Results_b = pd.DataFrame()
Risk_sum = []
for i in range(0, len(result_2)):
    Risk_j = 0
    for j in range(0, len(result_2.columns)):
        if result_2.iloc[i, j] <= b:
            W_j = (1 - ((result_2.iloc[i, j]) / b) ** 2) ** 2
            Risk = Efficiency.loc[j, 'E'] * W_j
            Risk_j = Risk_j + Risk
    Risk_sum.append(Risk_j)
Risk_sum = pd.DataFrame(data=Risk_sum, index=Sites_receptor.index, columns=['R_pop'])
Results_b = pd.concat([Results_b, Risk_sum], axis=1)
df = pd.concat([Sites_receptor.loc[:, 'GT'], Results_b.loc[:, 'R_pop']], axis=1)

# 3. define fitting process
def linear_func(X, a, b):
    return a * X + b

def quadratic_func(X, a, b, c):
    return a * X**2 + b * X + c

def cubic_func(X, a, b, c, d):
    return a * X**3 + b * X**2 + c * X + d

def exponential_func(X, a, b):
    return a * np.exp(b * X)

# Linear regression
X_linear = sm.add_constant(df['R_pop'])
linear_model = sm.OLS(df['GT'], X_linear).fit()
linear_r2 = linear_model.rsquared
linear_f = linear_model.fvalue
linear_p = linear_model.f_pvalue
linear_eq = f"Y = {linear_model.params[1]:.8f} * X + {linear_model.params[0]:.8f}"

# Quadratic regression
params_quadratic, _ = curve_fit(quadratic_func, df['R_pop'], df['GT'])
quadratic_fit = quadratic_func(df['R_pop'], *params_quadratic)
quadratic_r2 = r2_score(df['GT'], quadratic_fit)
quadratic_model = sm.OLS(df['GT'], sm.add_constant(np.column_stack([df['R_pop']**2, df['R_pop']]))).fit()
quadratic_f = quadratic_model.fvalue
quadratic_p = quadratic_model.f_pvalue
quadratic_eq = f"Y = {params_quadratic[0]:.8f} * X^2 + {params_quadratic[1]:.8f} * X + {params_quadratic[2]:.8f}"
print(params_quadratic)

# Cubic regression
params_cubic, _ = curve_fit(cubic_func, df['R_pop'], df['GT'])
cubic_fit = cubic_func(df['R_pop'], *params_cubic)
cubic_r2 = r2_score(df['GT'], cubic_fit)
cubic_model = sm.OLS(df['GT'], sm.add_constant(np.column_stack([df['R_pop']**3, df['R_pop']**2, df['R_pop']]))).fit()
cubic_f = cubic_model.fvalue
cubic_p = cubic_model.f_pvalue
cubic_eq = f"Y = {params_cubic[0]:.8f} * X^3 + {params_cubic[1]:.8f} * X^2 + {params_cubic[2]:.8f} * X + {params_cubic[3]:.8f}"

results = {
    'Model': ['Linear', 'Quadratic', 'Cubic'],
    'Equation': [linear_eq, quadratic_eq, cubic_eq],
    'R2': [linear_r2, quadratic_r2, cubic_r2],
    'F': [linear_f, quadratic_f, cubic_f],
    'Sig': [linear_p, quadratic_p, cubic_p]
}
results_df = pd.DataFrame(results)
results_df.to_excel(output_path + 'model_fitting_results.xlsx', index=False)

print("Validation -- GWFPM -- finished!")
