from pandas import DataFrame
import argparse
from pathlib import Path
from bncontroller.json.utils import read_json

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