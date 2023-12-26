from matplotlib import pyplot as plt
import networkx as nx
from collections import defaultdict
import random



def parse_co():
    with open(r"E:\态势感知\code\map\Points.co", 'r') as f:
        node_info = {node: (lo, la) for node, lo, la in (map(
            lambda args: (int(args[0]), float(args[1]), float(args[2])),
            [line.strip().split(" ") for line in f.readlines()]))}
    return node_info
    
def parse_gr():
    with open(r"E:\态势感知\code\map\real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])) if (int(args[0])<int(args[1])) else (int(args[1]), int(args[0])),
                        [line.strip().split(" ") for line in f.readlines()]))
    
    adj_info = set(adj_info)
    adj = defaultdict(list)
    for e1,e2 in adj_info:
        assert e1<e2
        adj[e1].append(e2)
        adj[e2].append(e1)
    return adj

def gen_level(NUM_PEOPLE, new_point):
    level = {}
    for i in range(new_point,new_point+NUM_PEOPLE):
        theta = random.random()
        if theta<0.2:
            level[i]=1
        elif theta<0.4:
            level[i]=2
        elif theta<0.6:
            level[i]=3
        elif theta<0.8:
            level[i]=4
        else:
            level[i]=5
    import pickle
    with open("map/level.pickle","wb") as f:
        pickle.dump(level, f)
    print(level)

if __name__=="__main__":
    NUM_PEOPLE = 500

    new_point = 10000

    node_info = parse_co()
    adj = parse_gr()
    nodes = list(adj.keys())
    random.shuffle(nodes)
    for node in nodes[:NUM_PEOPLE]:
        next_node = random.choice(adj[node])
        theta = random.random()
        x0,y0 = node_info[node]
        x1,y1 = node_info[next_node]
        x = (x1-x0)*theta+x0
        y = (y1-y0)*theta+y0 

        #add node
        node_info[new_point] = (x,y)
        
        # del edge
        adj[node].remove(next_node)
        adj[next_node].remove(node)
        #add edge
        adj[node].append(new_point)
        adj[new_point].append(node)
        adj[new_point].append(next_node)
        adj[next_node].append(new_point)

        new_point+=1
    import pickle
    with open("map/adj.pickle","wb") as f:
        pickle.dump(adj,f)
    with open("map/node.pickle","wb") as f:
        pickle.dump(node_info,f)
    gen_level(NUM_PEOPLE, 10000)




