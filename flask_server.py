from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import queue
import random
import json
import argparse
import socket,pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

TAKEOFF_SIZE = 10
LANDING_SIZE = 10

takeoff_q = queue.Queue(TAKEOFF_SIZE)
landing_q = queue.PriorityQueue(LANDING_SIZE)

start = time.time()
lock = threading.Lock()
cost = 10

s = None
def writeToFile(plane,action,action_start_time,action_complete_time,strip):
    fo = open(str("atc1") + ".js","a+")
    dict_obj = dict(plane = plane,action = action,action_start_time = action_start_time,action_complete_time = action_complete_time,strip = strip)
    json.dump(dict_obj,fo)
    socketio.emit('my response', str(dict_obj).replace("\'","\""))
    fo.write(',')
    fo.close()
    return

def createRunwayThreads(numberRunways):
    r = [0] * numberRunways
    senThread = threading.Thread(target = sendWeight)

    for i in range(numberRunways):
        r[i] = threading.Thread(target = runway,args = (i+1,))

    for i in range(numberRunways):
        r[i].start()

    senThread.start()

    for i in range(numberRunways):
        r[i].join()

    recThread.join()

def sendWeight():
    try:
        while True :
            weight = landing_q.qsize() + takeoff_q.qsize()
            weightpickle = pickle.dumps(weight)
            lock.acquire()
            s.send(weightpickle)
            lock.release()
            time.sleep(1)
    except:
        print("All airplanes handled")

def runway(strip):
    while True:
        global s
        d = landing_q.queue
        if(landing_q.empty() and takeoff_q.empty()):
            pass
        if(not landing_q.empty() and d[0][0] == 1):
            plane = landing_q.get()
            if(takeoff_q.full()):
                print(plane[1] + " sent to another ATC emergency ")
                data_string = pickle.dumps(plane)
                lock.acquire()
                s.send(data_string)
                lock.release()
            else:
                print("Emergency :: " + plane[1] +  " Landing on strip " + format(strip))
                t = time.time()
                writeToFile(plane[1],"Emergency Land",int(t-start),int(t-start)+3,strip)
                time.sleep(3)
                takeoff_q.put(plane[1])
                landing_q_update(cost)
        elif(not takeoff_q.empty()):
            plane = takeoff_q.get()
            print(plane  + " Taking off from strip " + format(strip))
            t = time.time()
            writeToFile(plane,"Take Off",int(t-start),int(t-start)+6,strip)
            landing_q_update(cost)
            time.sleep(6)
        else:
            plane = landing_q.get()
            print(plane[1] +  " Landing on strip " + format(strip))
            t = time.time()
            writeToFile(plane[1],"Normal Land",int(t-start),int(t-start)+1,strip)
            time.sleep(1)
            takeoff_q.put(plane[1])
            landing_q_update(cost)
    return

def recieve():
    try:
        while True:
            if(landing_q.empty() and takeoff_q.empty()):
                break
            data = s.recv(1024)
            data_arr = pickle.loads(data)
            print(data_arr)
            landing_q_insert(data_arr[1],int(data_arr[2]))
    except:
        print("")

def landing_q_insert(name, fuel):
    if(fuel < (cost*3)) :
        landing_q.put((1, name, fuel))
    else :
        landing_q.put((2, name, fuel))
    return

def landing_q_update(cost) :
    landing_q_temp = queue.Queue(LANDING_SIZE)
    l = landing_q.qsize()
    for i in range(l):
        plane = landing_q.get()
        landing_q_temp.put((plane[0], plane[1], plane[2]))
    for i in range(l):
        plane = landing_q_temp.get()
        fuel = plane[2] - cost
        if(fuel < (cost*3)) :
            landing_q.put((1, plane[1], fuel))
        else :
            landing_q.put((2, plane[1], fuel))

#if __name__ == "__main__":
def start_ATC(name,runways,neighbourATC,port):
    takeoff_q.put("a66")
    takeoff_q.put("a67")
    takeoff_q.put("a68")
    takeoff_q.put("a69")
    takeoff_q.put("a610")
    landing_q_insert("a611", 320)
    landing_q_insert("a612", 510)
    landing_q_insert("a613", 700)
    landing_q_insert("a614", 120)
    landing_q_insert("a615", 130)
    landing_q_insert("a616", 150)
    landing_q_insert("a617", 40)
    landing_q_insert("a618", 700)
    landing_q_insert("a619", 100)

    server = '127.0.0.1'
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server,port))

    weight = landing_q.qsize() + takeoff_q.qsize()
    distance = neighbourATC
    weightName = (name,weight,distance)
    weightNameMessage = pickle.dumps(weightName)

    s.send(weightNameMessage)
    input()
    recThread = threading.Thread(target = recieve)
    recThread.start()
    createRunwayThreads(runways)

@app.route('/')
def radarSession():
    return render_template('table.html')

@app.route('/radar')
def tableSession():
    return render_template('radar.html')

@socketio.on('callATC')
def sessions1(methods=['GET','POST']):
    start_ATC('atc1',3,[('atc2',30),('atc3',40)],9000)

@app.route('/input')
def sessionsInput():
    return render_template('input.html',callback=handle_my_custom_event11)

@socketio.on('get inputPlane')
def handle_my_custom_event11(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    print(json["airplane"])
    if(json["process"]=='t'):
    	takeoff_q.put(json["airplane"])
    else:
    	landing_q_insert(json["airplane"],int(json["fuel"]))

def runFlask():
    socketio.run(app)

if __name__ == '__main__':
    runFlask()
