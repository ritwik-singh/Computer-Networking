import json
from simulator.node import Node

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)


        # created a routing table that contians own linked cost dict() neight dv dict() and ows dv()
        self.routing_table = {
            "neighbor_seq_num":{},
            "costs": {},
            "node_distance_vector": {},
            "neighbor_distance_vector":{}
            }
        self.seq_num = 0

    def __str__(self):
        # sending message in the form of list with dv and seq number as their elements.
        message = [self.seq_num, self.routing_table["node_distance_vector"]]
        self.seq_num += 1
        return json.dumps(message)

    def link_has_been_updated(self, neighbor, latency):

        # check  latency and discard it if its -1
        if latency != -1:
            self.routing_table["costs"][neighbor] = latency
        else:
            if neighbor in self.routing_table["costs"]:
                tmp = self.routing_table["costs"].pop(neighbor)
            if neighbor in self.routing_table["neighbor_distance_vector"]:
                tmp = self.routing_table["neighbor_distance_vector"].pop(neighbor)
        self.compute_ditance_vector()
        
    def process_incoming_routing_message(self, m):
        
        # load the message
        seq_num,_neighbor_distance_vector = json.loads(m)
        flag = False
        key_set = iter(_neighbor_distance_vector)
        neighbor = int(_neighbor_distance_vector[next(key_set)]['path'][0])
        to_delete = []
        # check whether its in the neighbor dv
        if neighbor not in self.routing_table["neighbor_distance_vector"]:
            self.routing_table["neighbor_distance_vector"][neighbor] = {}
        # if recived seq num is less dicard it by returning
        if neighbor in self.routing_table["neighbor_seq_num"] and seq_num < self.routing_table["neighbor_seq_num"][neighbor]:
            return

        for destination, value in (self.routing_table["neighbor_distance_vector"][neighbor]).items():
            to_delete.append(destination)

        for destination_str, value in _neighbor_distance_vector.items():
            destination = int(destination_str)
            if destination in to_delete:
                to_delete.remove(destination)

            link = {"cost":value['cost'], "path":value['path']}
            new_change  = False
            source = neighbor
            destination = destination
            distanceVector = link
            seq_num = seq_num
            if destination not in self.routing_table["neighbor_distance_vector"][source]:

                if self.id not in distanceVector["path"]:
                    self.routing_table["neighbor_distance_vector"][source][destination] = distanceVector
                    new_change  =  True
                    
                else:
                    new_change  =  False
            else:
                if self.id in distanceVector["path"]:
                        del self.routing_table["neighbor_distance_vector"][source][destination]
                        new_change  =  True

                self.routing_table["neighbor_distance_vector"][source][destination] = distanceVector
                new_change  =  True

            flag = new_change or flag

        for destination in to_delete:
            del self.routing_table["neighbor_distance_vector"][neighbor][destination]
            flag = True

        self.routing_table["neighbor_seq_num"][neighbor] = seq_num

        if flag:
            #if something has change recomute all the distance vector.
            self.compute_ditance_vector()

    def compute_ditance_vector(self):
        
        # store orignial dv
        original_distance_vector = self.routing_table["node_distance_vector"]
        self.routing_table["node_distance_vector"] = {}

        # recompute it by clearing everything
        for neighbor, cost in self.routing_table["costs"].items():
            self.routing_table["node_distance_vector"][neighbor] = {"cost":cost, "path":[self.id, neighbor]}
        # check if any value should be updated or not
        for source, distanceVectors in self.routing_table["neighbor_distance_vector"].items():
            for destination, distanceVector in distanceVectors.items():
                source=source 
                destination=destination 
                distanceVector=distanceVector
                if source in self.routing_table["costs"]:
                    if destination not in self.routing_table["node_distance_vector"] or (destination in self.routing_table["node_distance_vector"] and distanceVector["cost"] + self.routing_table["costs"][source] < self.routing_table["node_distance_vector"][destination]["cost"]):
                        new_path = [self.id] + (distanceVector["path"])
                        self.routing_table["node_distance_vector"][destination] = {"cost":distanceVector["cost"] + self.routing_table["costs"][source], "path":new_path}
        #if something changes send it to all the neighbours.
        if self.routing_table["node_distance_vector"] != original_distance_vector:          
            self.send_to_neighbors(str(self))
    
    def get_next_hop(self, destination):
        
        if destination in self.routing_table["node_distance_vector"]:
            if self.routing_table["node_distance_vector"][destination]["cost"] < float('inf'):
                return (self.routing_table["node_distance_vector"][destination]["path"])[1]

        return -1
