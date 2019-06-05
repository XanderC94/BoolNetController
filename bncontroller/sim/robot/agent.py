import sys, math, operator
from controller import Supervisor, Robot
from bncontroller.sim.robot.core import Controller
from bncontroller.sim.robot.morphology import EPuckMorphology
from bncontroller.sim.data import Point3D
from bncontroller.sim.config import SimulationConfig

# -------------------------------------------------------------------------------------------

class RoboticAgent(object):

    def __init__(self, options: SimulationConfig):
        # create the Robot instance.
        # robot = Robot()
        # Supervisor extends Robot but has access to all the world info. 
        # Useful for automating the simulation.
        self.__robot = Supervisor() 
        # get the time step (ms) of the current world.
        self.__sim_timestep = int(self.__robot.getBasicTimeStep())
        self.__config = options
        self.__morphology = None

    ##############################################

    @property
    def supervisor(self) -> Supervisor:
        return self.__robot

    @property
    def position(self) -> Point3D:
        return Point3D.from_tuple(
            tuple(self.supervisor.getSelf().getField('translation').getSFVec3f())
        )

    @position.setter
    def position(self, value : Point3D):
        self.supervisor.getSelf().getField('translation').setSFVec3f(list(value))

    @property
    def orientation(self):
        return self.supervisor.getSelf().getField('rotation').getSFRotation()

    @orientation.setter
    def orientation(self, orientation):
        self.supervisor.getSelf().getField('rotation').setSFRotation([0,-1, 0, orientation])
    
    @property
    def morphology(self):
        return self.__morphology
    
    @morphology.setter
    def morphology(self, new_morphology):
        self.__morphology = new_morphology

    @property
    def timestep(self) -> int:
        return self.__sim_timestep

    def run(self, controller : Controller, logging_hook = lambda string: None, data_hook = lambda data: None):
        # initialize simulation
        n_steps = 0
        max_steps = int((self.__config.sim_run_time * 1000) / self.timestep)

        trigger_step = int((self.__config.sim_event_timer * 1000) / self.timestep) # step @ which the event should be triggered

        logging_hook(
            f"TIME:{self.__config.sim_run_time} min | STEP-TIME:{self.timestep} ms => MAX-STEPS: {max_steps}"
        )

        # -------------------------------------------------

        # Main loop:
        # - perform simulation steps until Webots is stopping the controller
        while self.supervisor.step(self.timestep) != -1 and n_steps != max_steps:
            
            # -------------------- PERFORM SIMULATION STEP ------------------------

            logging_hook(f"step:{n_steps}")
            
            if n_steps == trigger_step:
                # trigger event modifying the simulation world
                pass

            data = controller(self.morphology, n_steps, self.timestep)

            data_hook(data)

            # ~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                   
            n_steps += 1

            pass
    
    def cleanup(self):
        self.supervisor.simulationSetMode(self.supervisor.SIMULATION_MODE_PAUSE)

        if self.__config.webots_quit_on_termination:
            self.supervisor.simulationQuit(1)
        else:
            self.supervisor.simulationReset()

###############################################################################################

class EPuck(RoboticAgent):

    def __init__(self, options: SimulationConfig):
        
        super().__init__(options)

        self.morphology = EPuckMorphology(self.timestep, self.supervisor)

        for wheel in self.morphology.wheel_actuators.values():
            wheel.device.setPosition(float('+inf'))
            wheel.device.setVelocity(0.0)
    
    ##############################################
    
    def cleanup(self):

        # Cleanup code.
        self.morphology.wheel_actuators[self.morphology.LEFT].device.setVelocity(0.0)
        self.morphology.wheel_actuators[self.morphology.RIGHT].device.setVelocity(0.0)

        super().cleanup()