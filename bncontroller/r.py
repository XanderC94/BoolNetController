from rpy2 import robjects as robjs
from rpy2.robjects.packages import importr

rBoolNet = importr('BoolNet')
rDiffeRenTES = importr('diffeRenTES')

if __name__ == "__main__":
    
    path = "D:/users/Xander/Downloads/bn.txt"

    n = 20

    attractor_n = r'Attractor (\d+)'
    attractor_states_n = r'consisting of (\d+) state(s)'
    attraction_basin_card = r'basin of (\d+) state(s)'
    attractor_state = r'\d{'+f'{{{n+1}}}'+'}'

    net = rBoolNet.loadNetwork(path)
    print('Net Loaded')
    attractors = rBoolNet.getAttractors(net)
    print('Attractors processed')
    ATM = rDiffeRenTES.getATM(net, attractors)
    print('TES processed')

    print(str(attractors).split('\n'))
    # print(attractors[1])
    # print(attractors[2])
    print(ATM[0])