#!/usr/bin/python
import sys, os, subprocess, json, time

version = "0.0.1"
git = "https://github.com/EHammer98/BLEmeshBorderRouter"

process = subprocess.Popen(['stdbuf', '-oL', '-i0', 'meshctl'], 
    bufsize=0, 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE
    # universal_newlines=True
)  

def init():
    global process
    # start meshctl process
    os.environ['PYTHONUNBUFFERED'] = '1'
    # read opening line
    process.stdout.readline()
    os.set_blocking(process.stdout.fileno(), False)

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


def refreshMesh():
    #global process
    #process.stdin.write("mesh-info\n".encode())
    #print("Response: " + str(process.stdout.readline().decode('utf8')) + "\n")
    with open("/home/pi/.config/meshctl/prov_db.json", 'r') as file:
        data = json.load(file)
        
        for i, p in enumerate(data['nodes']):
            print(str(i) + ": " + p['deviceKey'])

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
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            break

def addDev(uuid):
    global process
    process.stdin.write("provision " + uuid + "\n".encode())
    time.sleep(0.5)
    process.stdin.write(("get\n").encode())
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
        except:
            break

def removeDev(uuid, node0, node1, node2, node3):
    global process
    process.stdin.write("menu config\n".encode())
    time.sleep(0.5)
    nodes = [node0, node1, node2, node3]
    
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
    process.stdin.write(("disconnect " + uuid + "\n").encode())
    while 1:
        try:
            response = process.stdout.readline().decode('utf8')
            print("Response: " + response + "\n")
            if (response == 'Failed to AcquireWrite\n'):
                print("Not able to reach node, reconnecting now...")
                connect()
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
            print("Enter node0: \n")
            n0 = input()
            print("Enter node1: \n")
            n1 = input()
            print("Enter node2: \n")
            n2 = input()
            print("Enter node3: \n")
            n3 = input()
            removeDev(u,n0,n1,n2,n3)
        elif (x == "exit"):
            print("Bye!!")
            quit()
        else:
            print("Invalid cmd\n")
            
init()           
main()