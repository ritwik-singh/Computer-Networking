from simulator.node import Node
import json

class Link_State_Node(Node):


    def __init__(self, id):
        super().__init__(id)
        self.edges = dict()

    def make_edge(self,cost,time):
        return {"cost" :cost, "time" : time}

    def create_message(self):
        message = dict()
        for key, val in self.edges.items():
            if(key[0] != self.id):
                message[str(key)] = self.make_edge(val["cost"],val["time"])
            else:
                new_key = key[::-1]
                message[str(new_key)] = self.make_edge(val["cost"],val["time"])

        return message

    def __str__(self):
        return json.dumps(self.create_message())


    def link_has_been_updated(self, neighbor, latency):
        self.edges[tuple((self.id,neighbor))] = self.make_edge(latency,self.get_time())
        self.edges[tuple((neighbor,self.id))] = self.make_edge(latency,self.get_time())
        self.send_to_neighbors(str(self))

    def split_msg(self,key):      
        new_key = key.replace('(',"")
        new_key = new_key.replace(')',"")
        new_key = new_key.split(",")
       
        return tuple(map(int, new_key ))

    def process_incoming_routing_message(self, m): 
        _edges = json.loads(m)
        flag = False
        for key, value in _edges.items():
            key = self.split_msg(key)
            change = False
            new_edge = self.make_edge(int(value["cost"]),int(value["time"]))

            source = key[0]
            dst = key[1]

            if ((tuple((source,dst)) in self.edges) and (int(new_edge["time"]) > int(self.edges[tuple((source,dst))]["time"]))) or (tuple((source,dst)) not in self.edges):
                self.edges[tuple((source,dst))] = new_edge
                self.edges[tuple((dst,source))] = new_edge
                change = True
            flag = change or flag
            
        if flag :
            self.send_to_neighbors(str(self))

    def get_next_hop(self, destination):
    
        dist = dict()
        q = []
        node = {"node_id" : self.id, "cost" : 0,"prev" :[]}
        q.append(node)
        q.sort(key=lambda x:x["cost"])
        dist[self.id] = 0
        while len(q)>0:
            
            v = q.pop(0)
            q.sort(key=lambda x:x["cost"])
            if v["node_id"] == destination:
                return v["prev"][0]
    

            for key_tmp, val in self.edges.items():
                
                key = tuple(key_tmp)
                
                if val["cost"] > 0:

                    neigh = None
                    if key[0] == v["node_id"]:
                        neigh = key[1]
                    elif key[1] == v["node_id"]:
                        neigh = key[0]
                    
                    if neigh is not None:
                        if neigh not in dist or ((val["cost"]) + (v["cost"])) < dist[neigh]:
                            node  = {"node_id" : neigh, "cost": ((val["cost"]) + (v["cost"])), "prev": v["prev"] + [neigh]}
                            
                            q.append(node)
                            q.sort(key=lambda x:x["cost"])
                            dist[neigh] = (val["cost"]) + (v["cost"])
        
        return -1
