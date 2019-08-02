import pandas
# import statistics
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

    return 1 / score, position 


def hbnac(sim_data: dict, lpos: Point3D) -> (float, float):

    df = pandas.DataFrame(sim_data['data'])

    def get_attr_ratio(df):
        if 'a0' in df and 'a1' in df and df['a1'] > 0:
            return df['a0'] / df['a1']
        elif 'a0' not in df:
            return 0.0
        else:
            return float('inf')


    noise_phase_data = df[df['noise'] == True]
    phase_l = int(len(noise_phase_data)/2)

    pt_data = df[(df['input'] == 0) & (df['noise'] == False)]
    apt_data = df[(df['input'] == 1) & (df['noise'] == False)]

    ##################################################################

    noise_a01_count = noise_phase_data[:phase_l]['attr'].value_counts()

    noise_score1 = get_attr_ratio(noise_a01_count)

    ##################################################################

    noise_a01_count = noise_phase_data[phase_l:]['attr'].value_counts()

    noise_score2 = get_attr_ratio(noise_a01_count)

    ##################################################################

    pt_score, pt_dist = __pt_stub(pt_data, lpos) # minimize
    
    pt_a01_count = pt_data['attr'].value_counts()
    pt_a01_ratio = get_attr_ratio(pt_a01_count)

    ##################################################################

    apt_score, apt_dist = __pt_stub(apt_data, lpos) # maximize
    
    apt_a01_count = apt_data['attr'].value_counts()
    apt_a01_ratio = get_attr_ratio(apt_a01_count)

    ##################################################################

    pt_apos = pt_data['position'].iloc[0]
    apt_apos = apt_data['position'].iloc[0]

    apt_yrot = list(apt_data['light_values'].iloc[0].values())
    pt_yrot = list(pt_data['light_values'].iloc[0].values())
    
    apt_yrot_idx = apt_yrot.index(max(apt_yrot))

    apt_yrot = EPuckMorphology.LIGHT_SENSORS_POSITION[apt_yrot_idx]

    pt_yrot_idx = pt_yrot.index(max(pt_yrot))

    pt_yrot = EPuckMorphology.LIGHT_SENSORS_POSITION[pt_yrot_idx]

    return (
            {
                'noise_score1': noise_score1, 
                'pt_score': pt_score, 
                'pt_a01_ratio': pt_a01_ratio, 
                'apt_score': apt_score, 
                'apt_a01_ratio': apt_a01_ratio, 
                'noise_score2': noise_score2
            }, {
                # 'lpos': lpos.to_json(),
                'pt_apos': pt_apos,
                'pt_yrot': pt_yrot,
                'pt_idist': lpos.dist(pt_apos),
                'apt_apos': apt_apos,
                'apt_yrot': apt_yrot,
                'apt_idist': lpos.dist(apt_apos),
                'pt_fdist': pt_dist, 
                'apt_fdist': apt_dist
            }
        )

############################################################################

if __name__ == "__main__":
    
    from bncontroller.jsonlib.utils import read_json

    data = read_json(
        'D:\\Xander\\Documenti\\Projects\\BoolNetController\\res\\data\\sim\\handcheck_sim_data_20190730T145525281.json'
    )

    print(hbnac(data, Point3D.from_json({
        "x": 0.0,
        "y": 0.3,
        "z": -0.0
    })))
