import socket,pickle,threading
import os
import time

all_atcs = []
all_connections = []
all_address = []
all_weights = []
all_distances = []
fuel_per_dist = 1

lock = threading.Lock()
server = '127.0.0.1'

def selectTarget(distances):
    minDs = 9999
    for distance in distances:
        if(distance[1] <= minDs):
            if(distance[1] == minDs):
                weight1 = all_weights[all_atcs.index(distance[0])]
                weight2 = all_weights[all_atcs.index(atcMin)]
                if(weight1 < weight2):
                    minDs = distance[1]
                    atcMin = distance[0]
            else:
                minDs = distance[1]
                atcMin = distance[0]
    return atcMin

def makeconnection(port):
    s = socket.socket()
    s.bind((server,int(port)))
    s.listen(5)
    c, addr = s.accept()

    nameWeightMessage = c.recv(1024)
    nameWeight = pickle.loads(nameWeightMessage)

    name = nameWeight[0]
    weight = nameWeight[1]
    distances = nameWeight[2]
    print(str(name) + 'connected' + 'neighbourATCs' + str(distances))

    lock.acquire()
    all_atcs.append(name)
    all_weights.append(weight)
    all_distances.append(distances)
    all_connections.append(c)
    all_address.append(addr)
    lock.release()

    index = all_address.index(addr)
    while True:
        data = c.recv(1024)
        try:
            data_arr = pickle.loads(data)
        except:
            break
        else:
            if(type(data_arr)==int):
                all_weights[index] = data_arr
            else:
                target = selectTarget(distances)
                print(str(name) + ' -> ' + data_arr + ' -> ' + str(target))
                target = all_atcs.index(target)
                target_conn = all_connections[target]
                sendData = pickle.dumps(data_arr)
                target_conn.send(sendData)
    c.close()

if __name__ == "__main__":
    p1 = threading.Thread(target = makeconnection,args = ('9000',))
    p2 = threading.Thread(target = makeconnection,args = ('7000',))
    p3 = threading.Thread(target = makeconnection,args = ('8000',))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
