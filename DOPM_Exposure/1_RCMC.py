import rasterio
import numpy as np
from scipy.stats import rv_discrete
import geopandas as gpd
from shapely.geometry import Point
from collections import defaultdict

input_path = './Sample data/raster/Respiratory_rates/'
output_path = './Sample data/shp/Respiratory_rates/'

number_points = [5815, 22715, 26590, 25350, 424898, 165447, 67974, 12271]
age_groups = ['1_25_40', '2_20_30', '3_18_25', '4_17_23', '5_15_18', '6_18_25', '7_12_28', '8_10_30']

for i in range(0, len(number_points)):

    raster_path = input_path + age_groups[i] + '.tif'
    with rasterio.open(raster_path) as src:
        raster = src.read(1)
        transform = src.transform
        crs = src.crs

    valid_mask = raster > 0
    valid_indices = np.nonzero(valid_mask)
    valid_values = raster[valid_mask]

    probabilities = valid_values / valid_values.sum()
    value_indices = np.arange(valid_values.size)
    distribution = rv_discrete(name='distribution', values=(value_indices, probabilities))

    num_points = number_points[i]
    num_simulations = 1000

    frequency_dict = defaultdict(int)

    for _ in range(num_simulations):
        num_points_per_simulation = num_points // num_simulations
        random_indices = distribution.rvs(size=num_points_per_simulation)

        for idx in random_indices:
            frequency_dict[idx] += 1

    remaining_points = num_points % num_simulations
    if remaining_points > 0:
        random_indices = distribution.rvs(size=remaining_points)
        for idx in random_indices:
            frequency_dict[idx] += 1

    geo_coords = []
    frequencies = []

    for idx, count in frequency_dict.items():
        row, col = valid_indices[0][idx], valid_indices[1][idx]
        x, y = transform * (col + 0.5, row + 0.5)
        for _ in range(count):
            geo_coords.append(Point(x, y))
            frequencies.append(count)

    gdf = gpd.GeoDataFrame({'frequency': frequencies}, geometry=geo_coords, crs=crs)
    gdf = gdf.head(num_points)

    shapefile_path = (output_path + age_groups[i].split('_')[0] +
                      '_random_points_monte_carlo.shp')
    gdf.to_file(shapefile_path, driver='ESRI Shapefile')

print("Age-guided virtual receptors finished!")
