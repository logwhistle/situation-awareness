import pickle
with open("adj.pickle","rb") as f:
    adj_info = pickle.load(f)
with open("node.pickle","rb") as f:
    node_info = pickle.load(f)
with open("level.pickle","rb") as f:
    level_info = pickle.load(f)
    print(0)