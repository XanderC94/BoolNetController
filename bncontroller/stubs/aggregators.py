import pandas
from bncontroller.sim.data import Point3D

def phototaxis(sim_data: dict) -> (float, Point3D):

    df = pandas.DataFrame(sim_data['data'])

    df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))

    score = df['aggr_light_values'].sum(axis=0, skipna=True) 

    max_step = df['n_step'].max()

    final_pos = df[df['n_step'] == max_step]['position'].T.values[0]

    return (1 / score if score > 0 else float('+inf')), Point3D.from_json(final_pos)

def antiphototaxis(sim_data: dict) -> (float, Point3D):

    score, position = phototaxis(sim_data)
    return 1 / score, position 

def hbns(sim_data: dict) -> (float, Point3D):
    return phototaxis(sim_data)
