# This file stores the class CalcSocket for the project 'Calculus'.

import socket

class CalcSocket:
    def __init__(self, serverIP, serverPort):
        self.msgLen = 256 + 1

        self.serverIP = serverIP
        self.serverPort = serverPort

        self.rocksPerStack = 0
        self.maxTakable = 0

        self.stacks = []

        # Create a socket and connect to it
        self.createSocket()
        self.connectToServer()

        # Get the server rules
        self.getRules()

        # Run the main loop
        self.mainLoop()

        # Close the socket
        self.closeSocket()

    def createSocket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket created...")
        except socket.error as err:
            print("Socket failed to create! Message: " + str(err))
            exit(1)

    def connectToServer(self):
        try:
            self.s.connect((self.serverIP, self.serverPort))
            print("Connected to " + str(self.serverIP) + ":" + str(self.serverPort))
            print(self.receiveMsg())
        except socket.error as err:
            print("Failed to connect! Message: " + str(err))
            exit(1)

    def getRules(self):
        print("Requesting rules from the server...")
        self.sendMsg("rules")
        reply = self.receiveMsg()
        self.maxTakable = int(reply.split('max_takable')[1])
        print("Setting maxTakable to", self.maxTakable)

    def mainLoop(self):
        while(True):
            received = self.receiveMsg()

            if len(received) == 0:
                break
                self.closeSocket()
                raise RuntimeError("Socket connection broken!")

            print(received)

            if "SURRENDER" in received:
                print("The other party has surrendered so you win this game!")
                exit(1)


            if "LOST" in received:
                print("You lost this game!")
                self.closeSocket()
                exit(1)

            if "WON" in received:
                print("You won the game! Congratulations!")
                self.closeSocket()
                exit(1)

            if "NEXT" in received:
                self.getStats()
                self.printStats()
                (whichOne, howMany) = self.prompt()
                self.sendMsg("take " + str(whichOne) + " " + str(howMany))
                print("Waiting for the other player...")

    def getStats(self):
        self.sendMsg("stats")
        reply = self.receiveMsg()

        # DEBUG
        # print(reply)

        reply = reply.rstrip('\n').split('|')

        del self.stacks
        self.stacks = []

        self.stacks.append(int(reply[0].strip().split(' ')[2]))
        self.stacks.append(int(reply[1].strip().split(' ')[2]))
        self.stacks.append(int(reply[2].strip().split(' ')[2]))

    def printStats(self):
        print("> The first stack has", self.stacks[0], "rocks.")
        print("> The second stack has", self.stacks[1], "rocks.")
        print("> The third stack has", self.stacks[2], "rocks.")

    def resign(self):
        print("You've resigned so you've lost this game!")
        self.sendMsg("resign")
        self.closeSocket()
        exit(0)

    def prompt(self):
        whichOne = howMany = -1

        whichOneIn = input("Which stack do you want to take rocks from? (1-3): ")

        if "feladom" in whichOneIn or "resign" in whichOneIn:
            self.resign()

        howManyIn = input("How many rocks do you want to take? (1-"+str(min(self.maxTakable, self.stacks[whichOne-1]))+"): ")

        if "feladom" in howManyIn or "resign" in howManyIn:
            self.resign()

        try:
            whichOne = int(whichOneIn)
            howMany = int(howManyIn)
        except ValueError:
            return self.prompt()

        if not (1 <= whichOne <= 3):
            return self.prompt()

        if not (1 <= howMany <= self.maxTakable):
            return self.prompt()

        return (whichOne, howMany)

    def sendMsg(self, msg):
        msg = msg.encode()
        sent = self.s.sendall(msg)
        if sent != None:
            raise RuntimeError("socket connection broken")

    def receiveMsg(self):
        return self.s.recv(self.msgLen).decode()

        """
        chunks = []
        bytes_recd = 0
        while bytes_recd < (self.msgLen - bytes_recd):
            chunk = self.s.recv(self.msgLen)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        all_recd = b''.join(chunks)
        return all_recd
        """

    def closeSocket(self):
        print("Exiting now...")
        self.s.close()
