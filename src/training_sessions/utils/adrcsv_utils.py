import pandas as pd
import typing
import re

def split_df_in_series(df):
    # First split based on exercises:
    df_filtered = df[df['SERIE']!='-']
    list_of_exercises = [group for name, group in df_filtered.groupby(['Ejer.'])]
    list_of_exercises = sorted(list_of_exercises, key = lambda x: min(x['R']))

    # Now we split based on series
    series_list = []
    group_of_series = [[group for name, group in exercise_df.groupby(exercise_df['SERIE'].str.split().str[0])] for exercise_df in list_of_exercises]

    for series in group_of_series:
        series_list.extend(series)
        
    return  series_list


def from_adr_pandas_to_json(df: pd.DataFrame):
    
    list_of_series_dataframes = split_df_in_series(df)
    list_of_processed_series = []
    for serie in list_of_series_dataframes:
        serie_dict = {'exercise': serie['Ejer.'].iloc[0], 'repetitions':[]}
        for _, row in serie.iterrows():
            rep_dict = {}
            if row["SERIE"] != "-":
                rep_dict['number'] = int( re.search(r'R(\d+)', row['SERIE']).group(1) ) 
                rep_dict['kg']=float(row['KG'])
                rep_dict['distance']=float(row['D'])
                rep_dict['mean_velocity']=float(row['VM'])
                rep_dict['peak_velocity']=float(row['VMP'])
                rep_dict['power']=float(row['P(W)'])    
                serie_dict['repetitions'].append(rep_dict)
        serie_dict['repetitions'] = serie_dict['repetitions'][::-1]
        list_of_processed_series.append(serie_dict)
    
    return list_of_processed_series

