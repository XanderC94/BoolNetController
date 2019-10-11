# Boolean Network Behavioural (re)Differentiation

Master Thesis in Intelligent Robotic System for Computer Science and Engineering Master Course -- Alma Mater Studiorum

## Abstract

The design of control software for robots that are required to face different and unpredictable environmental conditions is of paramount importance in current robotic research. A viable solution to attain such a control software consists in exploiting the rich dynamics of biological cell models; indeed, cells are capable of differentiating into specific types, each characterized by peculiar behavioural traits suited to the particular environmental condition in which the cell acts. Moreover,if properly triggered, cells can also undergo type changes. Inspired by this phenomenon, in this work we have devised a method to support the automatic design of robots controlled by Boolean networks (BNs), which are a notable model of genetic regulatory networks. The initial behaviour of the robot is not specific, i.e. its BN is in an undifferentiated state. When specific environmental conditions appear, the BN changes its dynamics that in turn induces a specific behaviour in the robot. If, subsequently, the environmental signals change, the robot is able to return to the initial, undifferentiated behaviour and then differentiate again into a different behaviour, according to the external signals. This method is shown in detail, along with a thorough experimental analysis, in a case study involving taxis behaviours.

## Install

Requires Python (3.7), R (3.6) with this https://github.com/mbraccini/diffeRenTES library (recursively follow required libraries), and Webots 2019a v1+.

Run "python setup.py"

## Usage

* gbehaviour.py -- generates a new behavioural bn based on the given parameters (configuration file)

* gselector.py -- generates a new selective bn based on the given parameters (configuration file)

To know what a config file options are run "python bncontroller/sim/config.py". This will generate a "blank" config file with placeholder options to fill. The file is generated in the current working directory.

* generate_n.py --  generates N networks (which type you choose, by expressing the core function in config file) saving their ebnf repr and ATM (csv) on files.

* sbnstats.py -- Random space exploration of selective networks

* check_constr.py -- Check constraints on generated networks

* rtest.py -- Test single behavioural networks or complete controllers (sbn + M * bbn) or whatever else you want since custom code can be injected.

* webots.py -- Run a chosen controller on Webots
