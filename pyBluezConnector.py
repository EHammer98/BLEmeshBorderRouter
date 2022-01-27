#!/usr/bin/python
import sys, os, subprocess, json, time
import fileinput

version = "0.0.3"
git = "https://github.com/EHammer98/BLEmeshBorderRouter"

process = subprocess.Popen(['stdbuf', '-oL', '-i0', 'meshctl'], 
    bufsize=0, 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE
    # universal_newlines=True
)  

def connect():
    global process 
    process.stdin.write("back\n".encode())
    time.sleep(.5)
    process.stdin.write("power off\n".encode())
    time.sleep(0.5)
    process.stdin.write("power on\n".encode())
    time.sleep(0.5)
    process.stdin.write("connect 0\n".encode())
    time.sleep(10)

def init():
    try:
        global process
        # start meshctl process
        os.environ['PYTHONUNBUFFERED'] = '1'
        # read opening line
        process.stdout.readline()
        os.set_blocking(process.stdout.fileno(), False)
        connect()
    except:
        connect()




def refreshMesh():
    #global process
    #process.stdin.write("mesh-info\n".encode())
    #print("Response: " + str(process.stdout.readline().decode('utf8')) + "\n")
    with open("/home/pi/.config/meshctl/prov_db.json", 'r') as file:
        data = json.load(file)
        print(str(data)) 
       # for i, p in enumerate(data['nodes']):
       #     print(str(i) + ": " + p['deviceKey'])

def group(node, group, kind):
    global process
    if (kind == "light"):
        process.stdin.write("menu config\n".encode())
        time.sleep(0.5)
        process.stdin.write(("target " + str(node) + "\n").encode())
        time.sleep(0.5)
        process.stdin.write(("appkey-add 1\n").encode())
        time.sleep(0.5)
        process.stdin.write(("bind 0 1 1000\n").encode())
        time.sleep(0.5)
        process.stdin.write(("sub-add " + str(node) + " " + str(group) +  " 1000\n").encode())
        time.sleep(0.5)

    if (kind == "switch"):
        process.stdin.write("menu config\n".encode())
        time.sleep(0.5)
        process.stdin.write(("target " + str(node) + "\n").encode())
        time.sleep(0.5)
        process.stdin.write(("appkey-add 1\n").encode())
        time.sleep(0.5)
        process.stdin.write(("bind 0 1 1001\n").encode())
        time.sleep(0.5)
        process.stdin.write(("pub-set " + str(node) + " " + str(group) +  " 1 0 0 1001\n").encode())
        time.sleep(0.5)

    print("Response: " + str(process.stdout.readline().decode('utf8')) + "\n")
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            break

def switchOn(node):
    global process
    process.stdin.write("menu onoff\n".encode())
    time.sleep(0.5)
    process.stdin.write(("target " + str(node) + "\n").encode())
    time.sleep(0.5)
    process.stdin.write(("onoff 1\n").encode())
    time.sleep(0.5)
    print("Response: " + str(process.stdout.readline().decode('utf8')) + "\n")
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            break

def switchOff(node):
    global process
    process.stdin.write("menu onoff\n".encode())
    time.sleep(0.5)
    process.stdin.write(("target " + str(node) + "\n").encode())
    time.sleep(0.5)
    process.stdin.write(("onoff 0\n").encode())
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            break

def lightStat(node):
    global process
    process.stdin.write("menu onoff\n".encode())
    time.sleep(0.5)
    process.stdin.write(("target " + str(node) + "\n").encode())
    time.sleep(0.5)
    process.stdin.write(("get\n").encode())
    cnt = 0
    trgt = 0
    loop = 1
    while 1:
        try:
            cnt = cnt + 1
            response = process.stdout.readline().decode('utf8')
            #print("Response: " + response + "\n")
            if ("On Off Model Message received (1) opcode 8204" in response):
                #print("count: " + str(cnt) + "\n")
                trgt = cnt + 2
            if (cnt == trgt - 1):
                #print("Response: " + str(cnt) + response + "\n")  
                responseList = response.split()
                #print(responseList[5] + "\n")
                if ("1" in responseList[5]):
                    #print("ON \n")
                    return "On"
                else:
                    #print("OFF \n")
                    return "Off"
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            lightStat(node)

def addDev(uuid):
    global process
    process.stdin.write(("provision " + str(uuid) + "\n").encode())
    time.sleep(0.5)
    cnt = 0
    trgt = 0
    loop = 1
    while 1:
        try:
            cnt = cnt + 1
            response = process.stdout.readline().decode('utf8')
            #print("Response: " + response + "\n")
            time.sleep(0.1)
            if ("Trying to connect Device" in response):
                print("count: " + str(cnt) + "\n")
                trgt = cnt + 39
            if (cnt == trgt - 1):
                #print("Response: " + str(cnt) + response + "\n")  
                responseList = response.split()
                print("List: " + str(responseList) + "\n")
                print("Item : " + responseList[6] + "\n")
                return responseList[6]
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            addDev(uuid)

def removeDev(uuid, devKey, node0, node1, node2, node3):

    global process
    items = []
    jsonFile = {
  "$schema":"file:\/\/\/BlueZ\/Mesh\/schema\/mesh.jsonschema",
  "meshName":"BT Mesh",
  "netKeys":[
    {
      "index":0,
      "keyRefresh":0,
      "key":"18eed9c2a56add85049ffc3c59ad0e12"
    }
  ],
  "appKeys":[
    {
      "index":0,
      "boundNetKey":0,
      "key":"4f68ad85d9f48ac8589df665b6b49b8a"
    },
    {
      "index":1,
      "boundNetKey":0,
      "key":"2aa2a6ded5a0798ceab5787ca3ae39fc"
    }
  ],
  "provisioners":[
    {
      "provisionerName":"BT Mesh Provisioner",
      "unicastAddress":"0077",
      "allocatedUnicastRange":[
        {
          "lowAddress":"0100",
          "highAddress":"7fff"
        }
      ]
    }
  ],
  "nodes":[],
  "IVindex":5,
  "IVupdate":0
}

    process.stdin.write("menu config\n".encode())
    time.sleep(0.5)
    nodes = [node0, node1, node2, node3]
    
    data = ""
    with open("/home/pi/.config/meshctl/prov_db.json", 'r') as file:
        data = json.load(file)
        for i, p in enumerate(data['nodes']):
            print(str(i) + ": " + p['deviceKey'])
            if not p['deviceKey'] == devKey:
                items.append(p)   
        file.close()

    jsonFile["nodes"].extend(items)

    with open('/home/pi/.config/meshctl/prov_db.json', 'w') as outfile:      
        json.dump(jsonFile, outfile)
        outfile.close()

    for n in nodes:
        process.stdin.write(("target " + str(n) + "\n").encode())
        time.sleep(0.5)
        process.stdin.write(("node-reset\n").encode())
        while 1:
            try:
                response = process.stdout.readline().decode('utf8')
                print("Response: " + response + "\n")
                if (response == 'Failed to AcquireWrite\n'):
                    print("Not able to reach node, reconnecting now...")
                    connect()
            except:
                break
    process.stdin.write("back\n".encode())
    time.sleep(0.5)
    process.stdin.write((str("disconnect " + uuid + "\n")).encode())
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
            refreshMesh()
        except:
            break


def main():
    print("pyBluezConnector | By E. Hammer | V.: " + version)
    print("Visit: " + git + " for more info \n")
    while (1):
        print('Enter cmd: \n')
        x = input()
        if (x == "connect"):
            print('CONNECTING... \n')
            connect() 
        elif (x == "switchOn"):
            print("Enter target: \n")
            t = input()
            switchOn(t)
        elif (x == "switchOff"):
            print("Enter target: \n")
            t = input()
            switchOff(t)
        elif (x == "lightStat"):
            print("Enter target: \n")
            t = input()
            lightStat(t)
        elif (x == "refreshMesh"):
            refreshMesh()
        elif (x == "addDev"):
            print("Enter UUID: \n")
            u = input()
            addDev(u)
        elif (x == "removeDev"):
            print('REMOVING DEVICE FROM MESH... \n')
            print("Enter UUID: \n")
            u = input()
            print("Enter devKey: \n")
            dev = input()
            print("Enter node0: \n")
            n0 = input()
            print("Enter node1: \n")
            n1 = input()
            print("Enter node2: \n")
            n2 = input()
            print("Enter node3: \n")
            n3 = input()
            removeDev(u,dev,n0,n1,n2,n3)
        elif (x == "groupDev"):
            print('GROUPING DEVICE... \n')
            print("Enter node: \n")
            n = input()
            print("Enter group: \n")
            g = input()
            print("Enter type: \n")
            t = input()
            group(n,g,t)
        elif (x == "exit"):
            print("Bye!!")
            quit()
        else:
            print("Invalid cmd\n")
            
#init()           
#main()