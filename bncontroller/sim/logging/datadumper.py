from pathlib import Path
from bncontroller.jsonlib.utils import write_json

class SimulationDataDumper(object):
    
    def __init__(self, runtime:int, timestep: int):
        
        self.sim_timestep = timestep
        self.sim_runtime = runtime
        self.data = []

    def add_log_entry(self, entry):
        self.data.append(entry)

    def dump_data(self, path: str or Path) -> str:
        
        write_json(vars(self), path)

        self.clear()
    
    def clear(self):
        self.data.clear()
