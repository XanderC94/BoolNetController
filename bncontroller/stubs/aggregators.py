import pandas
import math
import numpy as np
from bncontroller.sim.data import Point3D
from bncontroller.sim.robot.morphology import EPuckMorphology

pandas.options.mode.chained_assignment = None

def __pt_stub(df: pandas.DataFrame, lpos: Point3D):

    df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))

    score = df['aggr_light_values'].sum(axis=0, skipna=True) 

    max_step = df['n_step'].max()

    fpos = df[df['n_step'] == max_step]['position'].T.values[0]

    return (1 / score if score > 0 else float('+inf')),  round(lpos.dist(fpos), 5)

def phototaxis(sim_data: dict, lpos: Point3D) -> (float, float):

    df = pandas.DataFrame(sim_data['data'])

    return __pt_stub(df, lpos)

def antiphototaxis(sim_data: dict, lpos: Point3D) -> (float, float):

    score, position = phototaxis(sim_data, lpos)

    return score, position 

def antiphototaxis_min(sim_data: dict, lpos: Point3D) -> (float, float):

    score, position = phototaxis(sim_data, lpos)

    return 1 / score, position 

######################################################################################

def sbnc(sim_data: dict, lpos: Point3D) -> (float, float):

    df = pandas.DataFrame(sim_data['data'])

    def get_attr(df, attr, default):
        return df[attr] if attr in df else default

    def get_attr_ratio(df, a1, a2):

        v1 = get_attr(df, a1, 0)
        v2 = get_attr(df, a2, 0)

        if v2 > 0:
            return  v1 / v2
        else:
            return math.inf
       
    noise_phase_data = df[df['noise'] == True]
    phase_l = int(len(noise_phase_data)/2)

    pt_data = df[(df['input'] == 0) & (df['noise'] == False)]
    apt_data = df[(df['input'] == 1) & (df['noise'] == False)]

    ##################################################################

    noise1_a01_count = noise_phase_data[:phase_l]['attr'].value_counts()
    noise1_a0_count = get_attr(noise1_a01_count, 'a0', 0)
    noise1_a1_count = get_attr(noise1_a01_count, 'a1', 0)

    # print(noise1_a0_count, noise1_a1_count)

    # noise1_score = get_attr_ratio(noise1_a01_count)

    ##################################################################

    noise2_a01_count = noise_phase_data[phase_l:]['attr'].value_counts()
    noise2_a0_count = get_attr(noise2_a01_count, 'a0', 0)
    noise2_a1_count = get_attr(noise2_a01_count, 'a1', 0)

    # print(noise2_a0_count, noise2_a1_count)

    # noise2_score = get_attr_ratio(noise2_a01_count)

    ##################################################################

    pt_score, pt_fdist = __pt_stub(pt_data, lpos) # minimize+
    
    pt_a01_count = pt_data['attr'].value_counts()
    pt_a01_ratio = get_attr_ratio(pt_a01_count, 'a0', 'a1')

    # print(pt_a01_ratio)

    ##################################################################

    apt_score, apt_fdist = __pt_stub(apt_data, lpos) # maximize
    
    apt_a01_count = apt_data['attr'].value_counts()
    apt_a01_ratio = get_attr_ratio(apt_a01_count, 'a0', 'a1')

    # print(apt_a01_ratio)

    ##################################################################

    pt_apos = pt_data.iloc[0]['position']
    pt_fapos = pt_data.iloc[-1]['position']
    apt_apos = apt_data.iloc[0]['position']
    apt_fapos = apt_data.iloc[-1]['position']

    apt_ilv = [*apt_data.iloc[0]['light_values'].values()]
    apt_flv = [*apt_data.iloc[-1]['light_values'].values()]
    pt_ilv = [*pt_data.iloc[0]['light_values'].values()]
    
    apt_yrot_idx = apt_ilv.index(max(apt_ilv))
    apt_yrot = EPuckMorphology.LIGHT_SENSORS_POSITION[apt_yrot_idx]
    
    apt_fyrot_idx = apt_flv.index(max(apt_flv))
    apt_fyrot = EPuckMorphology.LIGHT_SENSORS_POSITION[apt_fyrot_idx]

    pt_yrot_idx = pt_ilv.index(max(pt_ilv))

    pt_yrot = EPuckMorphology.LIGHT_SENSORS_POSITION[pt_yrot_idx]

    return (
        {
            # 'noise1_score': noise1_score, 
            'noise1_a0_count': noise1_a0_count, 
            'noise1_a1_count': noise1_a1_count,

            'pt_score': pt_score, 
            # 'wpt_score': pt_score * pt_fdist / lpos.dist(pt_apos), 
            'pt_a01_ratio': pt_a01_ratio,

            # 'wapt_score': apt_score * apt_fdist / lpos.dist(apt_apos), 
            'apt_score': apt_score, 
            'apt_a01_ratio': apt_a01_ratio,

            # 'noise2_score': noise2_score,
            'noise2_a0_count': noise2_a0_count,
            'noise2_a1_count': noise2_a1_count,
        }, {
            # 'lpos': lpos.to_json(),
            'pt_apos': pt_apos,
            'pt_idist': lpos.dist(pt_apos),
            'pt_yrot': pt_yrot,
            'pt_fapos': pt_fapos, 
            'pt_fdist': pt_fdist, 

            'apt_apos': apt_apos,
            'apt_idist': lpos.dist(apt_apos),
            'apt_yrot': apt_yrot,
            'apt_fapos': apt_fapos,
            'apt_fdist': apt_fdist,
            'apt_fyrot': apt_fyrot,
        }
    )

############################################################################

def weighted_pt(s, i, f):

    return s * f / i

def weighted_apt(s, i, f):
    
    return s * f / i

#############################################################################

if __name__ == "__main__":
    
    from bncontroller.jsonlib.utils import read_json

    data = read_json(
        'D:\\Xander\\Documenti\\Projects\\BoolNetController\\res\\data\\sim\\handcheck_sim_data_20190730T145525281.json'
    )

    print(sbnc(data, Point3D.from_json({
        "x": 0.0,
        "y": 0.3,
        "z": -0.0
    })))
