"""demiurge controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import Supervisor
from bncontroller.parse.utils import parse_args_to_config

config = parse_args_to_config()

#-------------------------------------------

demiurge = Supervisor()

timestep = int(demiurge.getBasicTimeStep())

try:
    ls = demiurge.getFromDef(config.webots_nodes_defs['PointLight'])
    ls.getField('location').setSFVec3f(list(config.sim_light_position))
    # print(ls.getField('location').getSFVec3f())

    # hyperuranium = demiurge.getFromDef(config.webots_nodes_defs['WorldInfo'])
    # hyperuranium.getField('basicTimeStep').setSFFloat(config.sim_timestep_ms)
    # print(hyperuranium.getField('basicTimeStep').getSFFloat())
except Exception as ex:
    print(ex)

n_steps = 0
max_steps = int((config.sim_run_time_s * 1000) / timestep)
trigger_step = int((config.sim_event_timer_s * 1000) / timestep) # step @ which the event should be triggered

# -------------------------------------------------

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while demiurge.step(timestep) != -1 and n_steps != max_steps:
    
    # -------------------- PERFORM SIMULATION STEP ------------------------
    
    if n_steps == trigger_step:
        # trigger event modifying the simulation world
        try:
            ls = demiurge.getFromDef(config.webots_nodes_defs['PointLight'])
            ls.getField('intensity').setSFFloat(0.0)
            # print('Event Triggered')
        except Exception as ex:
            print(ex)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
    n_steps += 1

    pass

# Cleanup code.

# --------------------------------------------