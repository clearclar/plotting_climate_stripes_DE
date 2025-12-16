import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from datetime import datetime

import wetterdienst
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest
from wetterdienst.metadata.period import Period

from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

#from run_stripes import station_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def get_climate_data(resolution, station_id=None, start_date=None, end_date=None, variables:list=None, subset='climate_summary', shape='long'):
    settings = Settings(
        ts_shape=shape,
        ts_humanize=True,
        ts_convert_units=True
    )

    if (variables == None) or (len(variables) == 0):
        parameters = [(resolution, subset)]
    elif len(variables) == 1:
        parameters = [(resolution, subset, variables[0])]
    elif len(variables) > 1:
        parameters = []
        for variable in variables:
            parameters.append((resolution, subset, variable))
    
    if (start_date != None) and (end_date!=None):
        request = DwdObservationRequest(
            parameters=parameters,
            start_date=start_date,
            end_date=end_date,
            settings=settings
        )
    
    else:
        request = DwdObservationRequest(
            parameters=parameters,
            periods = Period.HISTORICAL,
            settings=settings
        )
    
    if station_id != None:
        request = request.filter_by_station_id(station_id=(station_id,))#.all()
    else:
        request = request.all()
    
    meta = request.df.to_pandas()
    values = request.values.all().df.to_pandas()
    
    cols_to_use = list(meta.columns.difference(values.columns))+['station_id']
    data_complete = pd.merge(
        values, meta[cols_to_use], on="station_id"
    ).drop(columns=['end_date', 'start_date', 'dataset'])

    return data_complete

def plot_climate_stripes(station_id):
    meantemp = get_climate_data('annual', station_id, variables=['temperature_air_mean_2m'], shape='wide')#.dropna().reset_index()
    meantemp['date'] = pd.to_datetime(meantemp['date']).dt.normalize()

    fig,ax = plt.subplots(figsize=(14, 4))
        
    cmap = 'RdBu_r'

    year = meantemp.date.dt.year
    temp = meantemp['temperature_air_mean_2m']

    start_year = min(year)
    end_year = max(year)

    rect_coll = PatchCollection([Rectangle((y, 0), 1, 1) for y in range(start_year, end_year + 1)], zorder=2)
    rect_coll.set_array(temp)
    rect_coll.set_cmap(cmap)
    ax.add_collection(rect_coll)

    ax.set_ylim(0, 1)
    ax.set_xlim(start_year, end_year + 1)
    ax.yaxis.set_visible(False)
    
    ax.set_title(meantemp.name[0], fontsize=20, loc='left', y=1.03)

    ax2 = ax.twinx()
    ax2.plot(year, temp, color='black', linewidth=1.5, )
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position('left')
    ax2.set_ylabel('temperature')

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.yaxis.set_visible(False)

    coef = np.polyfit(year, temp, 1)
    trend = np.poly1d(coef)

    ax3.plot(year, trend(year), linestyle='--', color='black', linewidth=1, )

    plt.figtext(0.856, 0.087, '© Clara Vydra', fontsize=6)
    plt.figtext(0.907, 0.15, 'Data source: Deutscher Wetterdienst',
                rotation=270, fontsize=6)

    plotfile = f'plots/{station_id}_warming_stripes_plus_timeseries_and_trend.png'
    plt.savefig(plotfile, bbox_inches='tight', facecolor='white')
    logging.info('Saved plots')
    plt.close() 

def main(station_id):
    plot_climate_stripes(station_id)


if __name__=='__main__':
    main(station_id)