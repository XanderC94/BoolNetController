"""hbnac controller."""
import os, sys
import bncontroller.sim.robot.binarization as bin_strategies
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.utils import GLOBALS
from bncontroller.sim.robot.agent import EPuck
from bncontroller.sim.robot.utils import DeviceName
from bncontroller.sim.robot.core import BNController, HBNAController
from bncontroller.sim.logging.logger import FileLogger
from bncontroller.sim.logging.datadumper import SimulationDataDumper

print(os.getcwd())
print(GLOBALS.slct_behaviours_map)

logger = lambda *items: None

#-------------------------------------------

bnselector = SelectiveBooleanNetwork.from_json(
        read_json(GLOBALS.bn_slct_model_path)
    )

bn_pt = OpenBooleanNetwork.from_json(
        read_json(GLOBALS.slct_behaviours_map['0']),        
    ) 

bn_apt = OpenBooleanNetwork.from_json(
        read_json(GLOBALS.slct_behaviours_map['1']),        
    ) 

phototaxist = BNController(
    model=bn_pt,
    sensing_interval=int(GLOBALS.sim_sensing_interval_ms), 
    bin_thresholds=dict(**GLOBALS.sim_sensors_thresholds), 
    bin_strategies={
        DeviceName.LIGHT: bin_strategies.phototaxis,
    },
    led_color=0x00ff00
)

antiphototaxist = BNController(
    model=bn_apt,
    sensing_interval=int(GLOBALS.sim_sensing_interval_ms), 
    bin_thresholds=dict(**GLOBALS.sim_sensors_thresholds), 
    bin_strategies={
        DeviceName.LIGHT: bin_strategies.antiphototaxis,
    },
    led_color=0xff00ff
)

dhbnac = HBNAController(
    selector=bnselector,
    behaviours={
        bnselector.attractors_input_map['0']: phototaxist, 
        bnselector.attractors_input_map['1']: antiphototaxist
    },
    bin_thresholds=dict(**GLOBALS.sim_sensors_thresholds), 
    bin_strategies={
        DeviceName.LIGHT: bin_strategies.antiphototaxis,
    },
    noise_rho=float(GLOBALS.slct_noise_rho),
    sensing_interval=int(GLOBALS.sim_sensing_interval_ms),
    input_fixation_steps=int(GLOBALS.slct_fix_input_steps)
)

epuck = EPuck(
    GLOBALS.sim_run_time_s, 
    GLOBALS.sim_timestep_ms, 
    GLOBALS.sim_event_timer_s
)

epuck.position = GLOBALS.sim_agent_position
epuck.orientation = GLOBALS.sim_agent_yrot_rad

dumper = SimulationDataDumper(GLOBALS.sim_run_time_s, epuck.timestep)

epuck.run(
    dhbnac,
    lambda data: dumper.add_log_entry(data)
)

dumper.dump_data(GLOBALS.sim_data_path)

# Cleanup code.

epuck.cleanup()

dumper.clear()

if GLOBALS.webots_quit_on_termination:
    epuck.supervisor.simulationQuit(1)
else:
    epuck.supervisor.simulationReset()

# --------------------------------------------