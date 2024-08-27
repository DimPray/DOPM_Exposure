import pandas as pd
import numpy as np
import math
from scipy.optimize import curve_fit
import statsmodels.api as sm
from sklearn.metrics import r2_score

input_path = './Sample data/input/'
output_path = './Sample data/output/'

#  Step 1 ： acquire parameters in cubic function
df = pd.read_excel(input_path + "Fitting_data_age.xlsx", index_col='FID')

def cubic_func(X, a, b, c, d):
    return a * X**3 + b * X**2 + c * X + d

# Cubic regression
params_cubic, _ = curve_fit(cubic_func, df['R_age'], df['GT'])
cubic_fit = cubic_func(df['R_age'], *params_cubic)
cubic_r2 = r2_score(df['GT'], cubic_fit)
cubic_model = sm.OLS(df['GT'], sm.add_constant(np.column_stack([df['R_age']**3, df['R_age']**2, df['R_age']]))).fit()
cubic_f = cubic_model.fvalue
cubic_p = cubic_model.f_pvalue
cubic_eq = f"Y = {params_cubic[0]:.8f} * X^3 + {params_cubic[1]:.8f} * X^2 + {params_cubic[2]:.8f} * X + {params_cubic[3]:.8f}"

# Step 2 : prediction on Age-guided receptors
Age_receptor = pd.read_csv(input_path + "Age_guided_receptors.txt", sep=',', index_col='FID')
Emission = pd.read_excel(input_path + "Point_emission_sources.xlsx", index_col='FID')
Efficiency = pd.read_excel(input_path + "Emission_efficiency.xlsx", index_col='FID')

Distance = []
for i in range(0, len(Emission)):
    Dis_sum = []
    for j in range(0, len(Age_receptor)):
        Dis = math.sqrt((Emission.loc[i, 'X'] - Age_receptor.loc[j, 'X'])**2
                         + (Emission.loc[i, 'Y'] - Age_receptor.loc[j, 'Y'])**2)  # Euclidean distance
        Dis_sum.append(Dis)
    Distance.append(Dis_sum)
result_1 = pd.DataFrame(data=Distance, index=Emission.index, columns=Age_receptor.index.T)

result_2 = result_1.T
b = 9500.0
Results_b = pd.DataFrame()
Risk_sum = []
for i in range(0, len(result_2)):
    Risk_j = 0
    for j in range(0, len(result_2.columns)):
        if result_2.iloc[i, j] <= b:
            W_j = (1 - ((result_2.iloc[i, j]) / b) ** 2) ** 2
            Risk = Efficiency.loc[j, 'E'] * W_j * Age_receptor.loc[i, 'rate']
            Risk_j = Risk_j + Risk
    Risk_sum.append(Risk_j)

Risk_sum = pd.DataFrame(data=Risk_sum, index=Age_receptor.index, columns=['R_age'])
Results_b = pd.concat([Results_b, Risk_sum], axis=1)
Prediction = ((Results_b.loc[:, 'R_age'] ** 3) * params_cubic[0] + (Results_b.loc[:, 'R_age'] ** 2) * params_cubic[1] +
              Results_b.loc[:, 'R_age'] * params_cubic[2] + params_cubic[3])
DOPM_pre = pd.DataFrame(data=Prediction, index=Age_receptor.index)
DOPM_pre.to_excel(output_path + "R_DOPM_prediction.xlsx", index=True)

print("Prediction -- DOPM -- finished!")