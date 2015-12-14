'''
Created on 20 Nov 2015

@author: Jurie
'''

import queue
from collections import deque
import socket
import select
import threading
import json
import time

class Comms(object):
	'''
	classdocs
	Base class implementation TCP socket communication
	'''


	def __init__(self, tcpIP, tcpPort):
		'''
		Constructor
		'''
		self.ipAddress = tcpIP
		self.portNumber = tcpPort
		self.transQ = queue.Queue()
		self.recvQ = queue.Queue()
		
		self.BUFFER_SIZE = 1024

		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		self.terminate = False
		self.transmitCV = threading.Condition()
		
	def startServer(self):
		try:
			self.socket.bind((self.ipAddress, self.portNumber))
			self.socket.listen(1)
		except socket.error as err:
			print(err)
			exit()
			return False
		
		if( self.socket is None):
			print('Socket is none!!')
		else:
			self.conn, adrr = self.socket.accept()
			self.fdw = self.conn.makefile('w') #writing filedescriptor
			self.fdr = self.conn.makefile('r') #reading file descriptor
		
		return True
		
	def transmit(self):
		#This method will wait on condition variable, notified by a msg added to the Q. It will however only send a single msg.  It is the caller responsibility to add the loop.  Allowing expansion of the method.
		with self.transmitCV:
			print ('Entered transmit threaed of tester') 
			while (self.transQ.empty() == True and not self.terminate):
				self.transmitCV.wait()
				
			if(self.transQ.empty() == False):
				msg = self.transQ.get_nowait()
				if(type(msg) is not str):
					msg = msg.decode("utf-8")
				
				msg = msg.strip() + '\n'	#Ensures messages ends with a newline.
				self.fdw.write(msg)
				self.fdw.flush()
	
	def receive(self):
		#This method waits for 1 second to receive a msg and adds it to the queue if there is.  It is the caller's responsibility to implement a loop.  This allows for expansion of the method.
		ready = select.select([self.fdr],[],[self.fdr,self.fdw],1)
		if(len(ready[0])!=0):
			data = self.fdr.readline().strip()
			self.recvQ.put(data)
			return True
		else:
			return False
			
	def pushTransMsg(self, msg):
		#This method adds a msg to the transmit Q and notifies the thread.
		if(self.terminate == True):
			return False
		
		with self.transmitCV:
			self.transQ.put(msg)
			self.transmitCV.notify()
			
		return True
		

	def popRecvMsg(self):
		#Will raise Empty exception if there is no message in the Q
		return self.recvQ.get_nowait()
	
	def terminateComms(self):
		with self.transmitCV:
			self.terminate = True
			self.fdr.close()
			self.fdw.close()
			self.transmitCV.notify()


class UIServerComms(Comms):
	'''
	classdocs
	'''


	def __init__(self, tcpIP, tcpPort):
		'''
		Constructor
		'''
		Comms.__init__(self,tcpIP, tcpPort)
		#self.recvQ = Deque()	#Override recvQ to be a deque, allowing to peek at the first element.
		self.status = {}
		self.appStatus = {}
		self.incomingQ = queue.Queue()
		self.ID = 0
		self.rigID = -1
		
		self.recvLock = threading.Lock()
		

		
	def stop(self):
		self.terminateComms()
		self.t_recv.join()
		self.t_trans.join()
	
	def receive(self):
		silenceCounter = 0
		while(self.terminate == False):			
			try:
				received = Comms.receive(self)

				if(received == True):
					
					try:
						msgString = self.recvQ.get()
						if(not msgString):
							silenceCounter+=1
							if(silenceCounter>=10):
								self.terminate = True
						else:
							silenceCounter = 0
							msg = json.loads(msgString)
							key = next(iter(msg.keys()))
							if(key == 'update'):
								self.status = msg['update']
							elif(key == 'appStatus'):
								self.appStatus = msg['appStatus']
							else:
								self.incomingQ.put(msg)
								print("Msg in Q")
					except ValueError as e:
						#Log invalid msg
						print("Invalid msg",msgString)
			except select.error:
				self.terminate = True
				
		print("Exeting receive thread")
			
	'''def popRecvMsg(self):
		if(self.recvLock.acquire(blocking = False)==True):
			Comms.popRecvMsg(self)
			self.recvLock.release()
		else:
			raise ValueError'''
	
	def getStatus(self):
		return (self.status,self.appStatus)
	
	def sendUICmd(self, cmd): #Command is a dict of the JSON to be sent.  Excludes the ID and msg keyword
		cmd['id'] = self.ID
		self.ID +=1 #increment ID
		obj = {}
		obj['cmd'] = cmd
		msg = json.dumps(obj) + '\n'
		self.pushTransMsg(msg)

		return self.ID-1 #Return ID-1 since ID has already been incremented.

	def sendRigCmd(self, cmd): #Command is a dict of the JSON to be sent.  Excludes the ID and msg keyword
		cmd['id'] = self.rigID
		self.rigID +=1 #increment ID
		obj = {}
		obj['msg'] = cmd
		msg = json.dumps(obj) + '\n'
		self.pushTransMsg(msg)

		return self.rigID-1 #Return ID-1 since ID has already been incremented.
	
	def getIncoming(self):
		if (self.incomingQ.empty() == False):
			return self.incomingQ.get_nowait()
		else:
			return None
	
	def start(self):
		self.startServer()
		print('SErver started')
		self.t_recv = threading.Thread(target=self.receive)
		self.t_trans = threading.Thread(target=self.transmit)
		self.t_recv.start()
		self.t_trans.start()
		print('Start done')
		
	def transmit(self):
		while(self.terminate != True):
			Comms.transmit(self)
			
	def terminateComms(self):
		Comms.terminateComms(self)
		self.t_trans.join()
		self.t_recv.join()
