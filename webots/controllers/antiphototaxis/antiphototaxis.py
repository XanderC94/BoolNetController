"""antiphototaxis controller."""

import bncontroller.sim.robot.binarization as bin_strategies
from bncontroller.sim.robot.agent import EPuck
from bncontroller.sim.robot.core import BNController
from bncontroller.sim.utils import GLOBALS
from bncontroller.sim.robot.utils import DeviceName
from bncontroller.sim.logging.logger import FileLogger
from bncontroller.sim.logging.datadumper import SimulationDataDumper

print(str(GLOBALS.bn_ctrl_model_path))

logger = lambda *items: None

if not GLOBALS.sim_suppress_logging:
    logger = FileLogger('BoolNetControl', path = GLOBALS.sim_log_path)
    logger.suppress(GLOBALS.sim_suppress_logging)

#-------------------------------------------

antiphototaxist = BNController(
    model=GLOBALS.bn_ctrl_model_path,
    sensing_interval=GLOBALS.sim_sensing_interval_ms, 
    bin_thresholds=GLOBALS.sim_sensors_thresholds, 
    bin_strategies={
        DeviceName.LIGHT: bin_strategies.antiphototaxis,
    }
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
    antiphototaxist, 
    lambda string: logger(string), 
    lambda data: dumper.add_log_entry(data)
)

dumper.dump_data(GLOBALS.sim_data_path)

# Cleanup code.

epuck.cleanup()

dumper.clear()

if not GLOBALS.sim_suppress_logging:
    logger.flush()

if GLOBALS.webots_quit_on_termination:
    epuck.supervisor.simulationQuit(1)
else:
    epuck.supervisor.simulationReset()

# --------------------------------------------