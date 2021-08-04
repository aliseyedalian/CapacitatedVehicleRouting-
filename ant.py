import numpy

class Ant:
    def __init__(self,depot_position ,max_capacity):
        #print("*** an ant initialized in depot position ( node",position.index,") with capacity",max_capacity,"***")
        self.depot = depot_position
        self.position = depot_position  # ant position is a node number
        self.max_capacity = max_capacity
        self.capacity = max_capacity
        

    def start(self, nodes , visited_nodes , distances , feromones,alfa,beta):
        current_node = self.position
        path = [current_node]
        remain_nodes = [node for node in nodes if node not in visited_nodes] 
        while(len(remain_nodes)):  
            """ transition rule """
            prob = list(map(lambda x: ((feromones[min(x.index ,current_node.index)][max(x.index ,current_node.index)])**alfa)
            *((distances[min(x.index ,current_node.index)][max(x.index ,current_node.index)])**(-beta)), remain_nodes))
            prob = prob/numpy.sum(prob) 
            next_node = numpy.random.choice(remain_nodes, p=prob)
            if self.capacity - next_node.demand >= 0:
                self.capacity = self.capacity - next_node.demand
                path.append(next_node)
                current_node = next_node
                visited_nodes.append(current_node)
                remain_nodes.remove(current_node)
            else:# try agian ... , maybe another next_node exists with less demand
                next_node = numpy.random.choice(remain_nodes, p=prob)  
                if self.capacity - next_node.demand >= 0:
                    self.capacity = self.capacity - next_node.demand
                    path.append(next_node)
                    current_node = next_node
                    visited_nodes.append(current_node)
                    remain_nodes.remove(current_node)  
                else:
                    break
        self.position = self.depot
        path.append(self.depot)
        self.capacity = self.max_capacity
        return path, visited_nodes