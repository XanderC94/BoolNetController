"""daca controller."""

from bncontroller.sim.robot.agent import EPuck
from bncontroller.sim.robot.core import BNController
from bncontroller.sim.config import parse_args_to_config
from bncontroller.sim.robot.utils import DeviceName
from bncontroller.sim.robot.binarization import light_sensor_binarization
from bncontroller.sim.logging.logger import FileLogger
from bncontroller.sim.logging.datadumper import SimulationDataDumper

config = parse_args_to_config()

print(str(config.bn_model_path))

logger = FileLogger('BoolNetControl', path = config.sim_log_path)

logger.suppress(config.sim_suppress_logging)

#-------------------------------------------

controller = BNController(config, binarization_strategies={
    DeviceName.LIGHT : light_sensor_binarization,
})

epuck = EPuck(config)

epuck.position = config.sim_agent_position
epuck.orientation = config.sim_agent_yrot_rad

dumper = SimulationDataDumper(config.sim_run_time_s, epuck.timestep)


epuck.run(
    controller, 
    lambda string: logger.info(string), 
    lambda data: dumper.add_log_entry(data)
)

dumper.dump_data(config.sim_data_path)

# Cleanup code.

dumper.clear()
logger.flush()
epuck.cleanup()

# --------------------------------------------