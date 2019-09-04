from pathlib import Path
from bncontroller.jsonlib.utils import write_json
from bncontroller.filelib.utils import check_path

class SimulationDataDumper(object):
    
    def __init__(self, model_path: Path, runtime:int, timestep: int):
        
        self.model_path = model_path
        self.sim_timestep = timestep
        self.sim_runtime = runtime
        self.data = []

    def add_log_entry(self, entry):
        self.data.append(entry)

    def dump_data(self, path: str or Path) -> str:
        
        if check_path(path, create_if_file=True) != 0:
            raise Exception(f"Invalid simulation data dump path:\n\t{path}...")

        write_json(vars(self), path)

        self.clear()
    
    def clear(self):
        self.data.clear()
