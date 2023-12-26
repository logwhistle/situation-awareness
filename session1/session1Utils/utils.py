from collections import namedtuple


class Edge:
    __slots__ = ("v1", "v2", 'parsed')

    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
        self.parsed = (v1, v2) if v1 < v2 else (v2, v1)

    def __str__(self):
        return "({}, {})".format(self.v1, self.v2)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.parsed)

    def __eq__(self, o):
        if isinstance(o, Edge):
            return self.parsed == o.parsed
        else:
            raise TypeError

    def __iter__(self):
        return iter(self.parsed)


class Search_Node(namedtuple("Search_Node", ["nodeID", "g", "time_info", "edgeID"])):
    def __hash__(self) -> int:
        return hash(self.nodeID)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Search_Node):
            return self.nodeID == o.nodeID
        elif isinstance(o, int):
            return self.nodeID == o
        else:
            raise TypeError

    # def __lt__(self,o):
    #     if isinstance(o,Search_Node):
    #         return self.g<o.g
    #     else:
    #         raise TypeError


class PATH(namedtuple("PATH", ["nodes", "edges", "time_info"])):
    def __repr__(self):
        return "PATH(nodes={}, total_nodes={}, edges={}, total_time= {})".format(self.nodes, len(self.nodes),
                                                                                 self.edges, self.time_info[-1])

    def __hash__(self) -> int:
        return hash(self.nodes)

    def __eq__(self, o: object) -> bool:
        return self.nodes == o.nodes


class Prioritized_Edge:
    __slots__ = ("priority", "edge", "idx", "rank")

    def __init__(self, priority, edge, idx, rank=0):
        self.priority = priority

        e1, e2 = edge
        e1, e2 = (e1, e2) if e1 < e2 else (e2, e1)
        self.edge = (e1, e2)

        self.idx = idx
        self.rank = rank

    def __hash__(self) -> int:
        return hash(self.edge)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Prioritized_Edge):
            return self.edge == o.edge or self.edge == o.edge[::-1]
        elif isinstance(o, tuple):
            return self.edge == o or self.edge == o[::-1]
        else:
            raise TypeError

    def __lt__(self, x) -> bool:
        if isinstance(x, Prioritized_Edge):
            if self.rank == x.rank:
                return self.priority < x.priority
            else:
                # rank大的后选
                return self.rank > x.rank
        else:
            raise TypeError


class Init_State(namedtuple("Init_State", ["paths"])):
    def __hash__(self) -> int:
        hash_value = 0
        for path in self.paths:
            hash_value = hash(hash_value + hash(path))
        return hash_value

    def __eq__(self, o: object) -> bool:
        if len(self.paths) != len(o.paths):
            return False
        for a, b in zip(self.paths, o.paths):
            if a != b:
                return False
        return True
