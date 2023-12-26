with open(r"E:\态势感知\code\map\real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])),
                        [line.strip().split(" ") for line in f.readlines()]))
with open(r"E:\态势感知\code\map\Points.co", 'r') as f:
    node_info = {node: (lo, la) for node, lo, la in (map(
        lambda args: (int(args[0]), float(args[1]), float(args[2])),
        [line.strip().split(" ") for line in f.readlines()]))}

adj_nodes_list = []
for adj in adj_info:
    adj_nodes_list+=adj
adj_nodes_set = set(adj_nodes_list)
for node in adj_nodes_set:
    del node_info[node]
import json
with open("unadj_nodes.json","w") as f:
    json.dump(node_info,f)