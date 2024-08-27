import pandas as pd
from scipy.stats import pearsonr
import math

input_path = "./Sample data/input/"
output_path = "./Sample data/output/"

Emission = pd.read_excel(input_path + "Point_emission_sources.xlsx", index_col='FID')
Sites_receptor = pd.read_excel(input_path + "Monitoring_sites.xlsx", index_col='FID')
Efficiency = pd.read_excel(input_path + "Emission_efficiency.xlsx", index_col='FID')

# 1. calculate Euclidean distance from each emission source to each receptor
Distance = []
for i in range(0, len(Emission)):
    Dis_sum = []
    for j in range(0, len(Sites_receptor)):
        Dis = math.sqrt((Emission.loc[i, 'X'] - Sites_receptor.loc[j, 'X'])**2
                         + (Emission.loc[i, 'Y'] - Sites_receptor.loc[j, 'Y'])**2)  # Euclidean distance
        Dis_sum.append(Dis)
    Distance.append(Dis_sum)
result_1 = pd.DataFrame(data=Distance, index=Emission.index, columns=Sites_receptor.index.T)

# 2. examine the optimal bandwidth
result_2 = result_1.T
bandwidth = [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12]
Results_b = pd.DataFrame()
for b in bandwidth:
    Risk_sum = []
    for i in range(0, len(result_2)):
        Risk_j = 0
        for j in range(0, len(result_2.columns)):
            if result_2.iloc[i, j] <= b * 1000.0:
                W_j = (1 - ((result_2.iloc[i, j]) / (b * 1000.0)) ** 2) ** 2
                Risk = Efficiency.loc[j, 'E'] * W_j
                Risk_j = Risk_j + Risk
        Risk_sum.append(Risk_j)
    Risk_sum = pd.DataFrame(data=Risk_sum, index=Sites_receptor.index, columns=['R_' + str(b) + 'km'])
    Results_b = pd.concat([Results_b, Risk_sum], axis=1)

pearson_corr_sum = []
for r in range(0, len(Results_b.columns)):
    Y = Sites_receptor.loc[:, 'GT']
    X_r = Results_b.iloc[:, r]
    pearson_corr, _ = pearsonr(Y, X_r)
    pearson_corr_sum.append(pearson_corr)
Pearson = pd.DataFrame(data=pearson_corr_sum, index=Results_b.columns, columns=['R'])
Pearson.to_excel(output_path + "Sensitivity_analysis.xlsx", index=True)

print("Bandwidth -- sensitivity analysis -- finish!")