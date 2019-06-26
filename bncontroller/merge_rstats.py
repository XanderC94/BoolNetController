from pandas import DataFrame
import argparse
from pathlib import Path
from bncontroller.json.utils import read_json


'''
Add robot behaviour test suite

CHANGES:        
    * Improved Logging with singleton and factory patterns and subtitued to stdout prints calls.
    * Added rtest.py as entry point to the test suite.
    * Increased Configuration Options for include testing ones.

        * test_agent_y_rot_step_rad -- min variation of robot rotation in testing.
        * sd_save_suboptimal_models -- If true then save each suboptimal model found 
        (that is, models which have been considered optimal for at least 1 iteration).
        * test_positives_threshold -- Used in test to specify a target value over or 
        under which model are considered "good".
        * test_n_agent_spawn_points, test_n_light_spawn_points -- Number of agent and light spawn
        points. Coupled with <sim_agent_y_rot_step_rad> the number of tested configuration are
                        test_n_agent__spawn_points * (2PI / sim_agent_y_rot_step_rad)

        * test_data_path -- Path where to store test data
    
    * Renamed app.py to rtrain.py to match the test suite rtest.py
    * Added test data merge utility
'''

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser('Test Data Merger.')

    parser.add_argument('-dps', '--data_paths', nargs='+')
    parser.add_argument('-sp', '--save_path', type=Path)

    args = parser.parse_args()

    data = DataFrame()

    for p in args.data_paths:
        df = DataFrame.from_dict(read_json(p))

        data = data.append(df, ignore_index=True)

    data.to_json(args.save_path)