import sys
import numpy as np
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import median
from node import Node
from ant import Ant
import matplotlib.pyplot as plt

tao = 1 # init feremones value on links
alfa = 3   # feremones power in transition rule
dynamic_alfa = True  # alfa = i/250 
beta = 7   # distances power in transition rule
rho = 0.6  # rate of feremones evaporation
C = 300   # coefficient of feremones increment if link also exist in best solution

def getData(path):
    nodes = list()
    with open(path) as f:
            line1 = f.readline()
            ant_num = int(line1.split()[0] )
            max_capacity = int(line1.split()[1] )
            for line in f.readlines():
                index = line.split()[0]
                x = line.split()[1]
                y = line.split()[2]
                demand = line.split()[3]
                node = Node(index = index , x = x , y = y , demand = demand)
                nodes.append(node)
            f.close() 
    return ant_num , max_capacity , nodes

def init_ants():
    ants = list()
    for i in range(ant_num):
        # ants are initially on depot
        ant = Ant(depot_position = nodes[0] , max_capacity = max_capacity)
        ants.append(ant)
    return ants

def init_links():
    feromones = dict() 
    distances = dict() 
    for node_i in nodes:
        for node_j in nodes:
            if node_i.index < node_j.index:
                if node_i.index not in feromones:
                    feromones[node_i.index] = dict()
                feromones[node_i.index][node_j.index] = tao
                if node_i.index not in distances:
                    distances[node_i.index] = dict()
                distances[node_i.index][node_j.index] = ((node_i.x - node_j.x)**2 + (node_i.y - node_j.y)**2 )**0.5
    return feromones , distances

def paths_length(ants_paths):
    L = list() # is a list that contains lenght of each path
    for path in ants_paths:
        l_path = 0
        for i in range(len(path)-1):
            l_path += distances[min(path[i].index,path[i+1].index)][max(path[i].index,path[i+1].index)]
        L.append(round(l_path,2))
    return L 

def has_best_solution(n1,n2,best_solution):
    ants_best_paths = best_solution[0]
    for path in ants_best_paths:
        if n1 in path and n2 in path:
            if (path.index(n2) - path.index(n1))**2 == 1:
                return C
    return 1

def update_feromones(best_solution):
    ants_paths = solution[0]
    Lsolution = solution[1]
    L = paths_length(ants_paths)
    '''  update best_solution so far:  '''
    if best_solution == None:
        best_solution = solution
    else:
        if Lsolution < best_solution[1] and len(visited_nodes)==len(nodes):
            best_solution = solution
    Lbestsolution = best_solution[1] # length of best solution so ever
    '''  feromones update rule: '''
    if len(visited_nodes)==len(nodes):
        for path in range(len(ants_paths)):
            Lpath = L[path]
            path = ants_paths[path]
            for i in range(len(path)-1):
                n1 , n2 = path[i] , path[i+1] 
                feromones[min(n1.index,n2.index)][max(n1.index,n2.index)]= has_best_solution(n1,n2,best_solution)*(Lbestsolution/Lsolution)*(Lsolution-Lpath)/Lsolution +feromones[min(n1.index,n2.index)][max(n1.index,n2.index)]
    '''  evaporate feremones:  '''
    for index_i in feromones:
        for index_j in feromones[index_i]:
            f = rho * feromones[index_i][index_j] 
            if f < 1 : f = 1 # floor of feremones 
            feromones[index_i][index_j] = round(f,3) 
    return best_solution
    
def plot_nodes():
    if plot:
        x = list()
        y = list()
        for node in nodes[1:]:
            x.append(node.x)
            y.append(node.y)
        plt.scatter(nodes[0].x,nodes[0].y,c="red",label = "Depot")
        plt.scatter(x,y,c="black",label="Custumer")
        for node in nodes:
            text = " n"+str(node.index)+",d="+str(node.demand)
            plt.annotate(text, (node.x, node.y))
        plt.legend(bbox_to_anchor=(1, 1), loc='upper left')
        title = "Information of Nodes"
        plt.title(title)
        plt.show()
    
def plot_solution(solution,iteration, best = False):
    if plot:
        ants_paths = solution[0]
        length = solution[1]
        ant_count = 0
        for path in ants_paths:
            ant_count+=1
            x = [node.x for node in path]
            y = [node.y for node in path]
            label = "Ant "+str(ant_count)
            plt.plot(x, y, 'o-',label=label)
            plt.legend()
            u = np.diff(x)
            v = np.diff(y)
            pos_x = x[:-1] + u/2
            pos_y = y[:-1] + v/2
            norm = np.sqrt(u**2+v**2) 
            plt.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy", pivot="mid",scale = 50)     
        plt.scatter([node.x for node in nodes],[node.y for node in nodes],c='black')
        title = "The Ants Paths\nThe Solution in Iteration "+str(iteration)+",\nSum of Ants Paths lenght = "+str(round(length,2))
        if best:
            title = "The Ants Paths\nThe Best Solution that all Cunsumers were Served, Sum of Ants Paths lenght = "+str(round(length,2))
        plt.title(title)
        plt.show() 

def plot_progress(progress , best = False):
    plt.plot(progress)
    plt.xlabel("Iteration")
    plt.ylabel("Distance")
    if best:
        title = 'Progress in The Best Solutions'
    else:
        title = 'Progress in The Solutions'
    plt.title(label = title)
    plt.show()
    #progress = progress[:int(len(progress)/10)]
    #plt.plot(progress)
    #plt.show()

if __name__ == "__main__":
    plot = True
    iterations = 1000
    best_solution = None
    best_solutions_lenght = [] # has best solutions' lenghts, for plotting the fitness progress.
    solutions_lenght = [] # has best solutions' lenghts, for plotting the fitness progress.
    ant_num , max_capacity, nodes = getData("data.txt")
    plot_nodes()
    ants = init_ants()
    feromones , distances = init_links()
    for i in range(iterations+1):
        if dynamic_alfa: alfa = i/250
        visited_nodes = [nodes[0]] # first just depot is visited
        ants_paths = [] # paths of ants
        for ant in ants:
            path , visited_nodes = ant.start(nodes , visited_nodes , distances , feromones , alfa , beta)
            ants_paths.append(path)
        solution = (ants_paths , round(sum(paths_length(ants_paths)),2)) # a solution has paths of ants and sum of these paths
        best_solution = update_feromones(best_solution)   
        if i % (iterations/2) ==0 :   
            plot_solution(solution = solution,iteration = i, best = False)
        best_solutions_lenght.append(best_solution[1])
        solutions_lenght.append(solution[1])
        print("*** iteration ",i ,",best solution:",best_solution[1])

    plot_progress(progress = solutions_lenght , best = False)
    plot_progress(progress = best_solutions_lenght , best = True)
    plot_solution(solution = best_solution,iteration = i , best = True)

