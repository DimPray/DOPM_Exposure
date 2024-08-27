import pandas as pd
import math

input_path = "./Sample data/input/"
output_path = "./Sample data/output/"

Emission = pd.read_excel(input_path + "Point_emission_sources.xlsx", index_col='FID')
Pop_receptor = pd.read_csv(input_path + "Pop_virtual_receptors.txt", sep=',', index_col='FID')
Efficiency = pd.read_excel(input_path + "Emission_efficiency.xlsx", index_col='FID')

# Gaussian weighting function-aided Proximity Model
# 1. calculate Euclidean distance from emission source to each receptor
Distance = []
for i in range(0, len(Emission)):
    Dis_sum = []
    for j in range(0, len(Pop_receptor)):
        Dis = math.sqrt((Emission.loc[i, 'X'] - Pop_receptor.loc[j, 'X'])**2
                         + (Emission.loc[i, 'Y'] - Pop_receptor.loc[j, 'Y'])**2)  # Euclidean distance
        Dis_sum.append(Dis)
    Distance.append(Dis_sum)
result_1 = pd.DataFrame(data=Distance, index=Emission.index, columns=Pop_receptor.index.T)

# 2. extract the minimum distance points which distance <= bandwidth
b = 9500.0
result_2 = result_1.T

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

Risk_sum = pd.DataFrame(data=Risk_sum, index=Pop_receptor.index, columns=['R_pop'])
Results_b = pd.concat([Results_b, Risk_sum], axis=1)
# Results_b.to_excel(output_path + "R_GWFPM_pop.xlsx", index=True)

print("Model -- GWFPM -- finish!")