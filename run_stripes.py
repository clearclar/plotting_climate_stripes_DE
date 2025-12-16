import plotting_climate_stripes_function
print(plotting_climate_stripes_function.__file__)


station_ids = [5705, 1766, 1420, 1262, 15526]
for station_id in station_ids:
    plotting_climate_stripes_function.main(station_id)