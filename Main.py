'''
Created on 11 Dec 2015

@author: Jurie
'''

from tkinter import *
from tkinter.tix import COLUMN
from tkinter.ttk import Combobox
import json
import time
import threading

from Comms import UIServerComms

class ButtonsFrame(Frame):
	def print_hi(self):
		print('hi')
	
	def print_content(self,event):
		print(self.content.get())
		
	def sendState(self):
		print(self.varState.get())
		self.sendCmd({'type':'stateCMD','instr':self.varState.get()})
	
	def sendMode(self,event):
		print(self.varMode.get())
		self.sendCmd({'type':'modeCMD','instr':self.varMode.get()})
	
	def createWidgets(self):
		rowC =0
		self.lblMode = Label(text='Mode:')
		self.lblMode.grid(row=rowC,column=0)
		self.varMode = StringVar()
		self.cmbMode = Combobox(values = ['auto_continue','stepthrough','singlestate'],textvariable = self.varMode)
		self.cmbMode.grid(row=rowC,column = 1)
		self.cmbMode.bind('<<ComboboxSelected>>',self.sendMode)
		
		self.lblState = Label(text='State:')
		self.lblState.grid(row=rowC,column = 2)
		self.varState = StringVar()
		self.lstStates = ["clearError","prime","fill","forceFill","idle","pump","setPressure","error","override","leakageTest","continue", "preempt"]
		self.cmbState = Combobox(values = self.lstStates,textvariable = self.varState)
		self.cmbState.grid(row=rowC,column = 3)
		self.btnState = Button(text='Send state',command=self.sendState)
		self.btnState.grid(row=rowC,column = 4)
		
		rowC +=1
		
		self.lblFbMode = Label(text = 'Mode:')
		self.lblFbMode.grid(row=rowC,column=0)
		self.varFbMode = StringVar()
		self.entMode = Entry(state = 'readonly',textvariable = self.varFbMode)
		self.entMode.grid(row=rowC,column=1)
		
		self.lblFbState = Label(text = 'State:')
		self.lblFbState.grid(row=rowC,column=2)
		self.varFbState = StringVar()
		self.entState = Entry(state = 'readonly',textvariable = self.varFbState)
		self.entState.grid(row=rowC,column=3)
		
		self.lblFbStep = Label(text = 'Step:')
		self.lblFbStep.grid(row=rowC,column=4)
		self.varFbStep = StringVar()
		self.entStep = Entry(state = 'readonly',textvariable = self.varFbStep)
		self.entStep.grid(row=rowC,column=5)
		
		rowC+=1

		self.lblReply = Label(text='Reply:')
		self.lblReply.grid(row=rowC,column=0,sticky='w')
		rowC+=1
		self.txtReply = Text(wrap=WORD, height = 1)
		self.txtReply.grid(row=rowC,column = 0,columnspan=4)

		rowC+=1
		self.lblWarning = Label(text='Warnings:')
		self.lblWarning.grid(row=rowC,column=0,sticky='w')
		self.scrlWarning = Scrollbar()
		rowC+=1
		self.scrlWarning.grid(row=rowC,column = 4,sticky = 'nsw')
		self.txtWarning = Text(wrap=WORD, height = 5, state=DISABLED)
		self.txtWarning.grid(row=rowC,column = 0,columnspan=4)
		self.txtWarning['yscrollcommand'] = self.scrlWarning.set
		self.scrlWarning['command'] = self.txtWarning.yview
		
		rowC+=1
		self.lblError = Label(text='Errors:')
		self.lblError.grid(row=rowC,column=0,sticky='w')
		self.scrlError = Scrollbar()
		rowC+=1
		self.scrlError.grid(row=rowC,column = 4,sticky = 'nsw')
		self.txtError = Text(wrap=WORD, height = 5, state=DISABLED)
		self.txtError.grid(row=rowC,column = 0,columnspan=4)
		self.txtError['yscrollcommand'] = self.scrlError.set
		self.scrlError['command'] = self.txtError.yview
		
		rowC+=1
		self.lblRigStatus = Label(text='Rig status:')
		self.lblRigStatus.grid(row=rowC,column=0,sticky='w')
		rowC+=1
		self.txtRigStatus = Text(wrap=WORD, height = 30, width =40, state=DISABLED)
		self.txtRigStatus.grid(row=rowC,column = 0,columnspan=2)
		
		rowC-=1
		self.lblAppStatus = Label(text='Main status:')
		self.lblAppStatus.grid(row=rowC,column=3,sticky='w')
		rowC+=1
		self.txtAppStatus = Text(wrap=WORD, height = 30, width =40, state=DISABLED)
		self.txtAppStatus.grid(row=rowC,column = 3,columnspan=2)
		
	def addWarningMsg(self,msg):
		self.txtWarning.config(state=NORMAL)
		self.txtWarning.insert(END, "\n"+json.dumps(msg))
		self.txtWarning.config(state=DISABLED)
		
	def addErrorMsg(self,msg):
		self.txtError.config(state=NORMAL)
		self.txtError.insert(END, "\n"+json.dumps(msg))
		self.txtError.config(state=DISABLED)
		
	def addReply(self,msg):
		self.txtReply.config(state=NORMAL)
		self.txtReply.delete(0.0,END)
		self.txtReply.insert(INSERT, json.dumps(msg))
		self.txtReply.config(state=DISABLED)
	
	def __init__(self,sendCmd,master=None):
		Frame.__init__(self, master)
		self.grid(row=0,column = 0)
		self.createWidgets()
		self.sendCmd = sendCmd
		
def updateUI(comms, app):
	while (comms.terminate ==False):
		rigStatus, appStatus = comms.getStatus()
		app.txtAppStatus.config(state=NORMAL)
		app.txtAppStatus.delete(0.0,END)
		app.txtAppStatus.insert(INSERT,json.dumps(appStatus,indent=4))
		app.txtAppStatus.config(state=DISABLED)
		app.txtRigStatus.config(state=NORMAL)
		app.txtRigStatus.delete(0.0,END)
		app.txtRigStatus.insert(INSERT,json.dumps(rigStatus,indent=4))
		app.txtRigStatus.config(state=DISABLED)
		try:
			app.varFbMode.set(appStatus['mode'])
			app.varFbState.set(appStatus['state'])
			app.varFbStep.set(appStatus['step'])
		except:
			pass
			#print("App status not according to convention")
		
		incoming = comms.getIncoming()
		if(incoming):
			
			key = list(incoming.keys())[0]
			print("Key", key)
			if(key == 'warningMsg'):
				app.addWarningMsg(incoming['warningMsg'])
			elif(key == 'errorMsg'):
				app.addErrorMsg(incoming['errorMsg'])
			elif(key == 'reply'):
				app.addReply(incoming['reply'])
				print("Got reply")
					
		time.sleep(0.4)
		
	print('TerminateComms init')	
	comms.terminateComms()
	print('TerminateComms done')	
	

comms = UIServerComms('10.42.0.77',5001)

comms.start()
		
root = Tk()
app = ButtonsFrame(master = root,sendCmd = comms.sendUICmd)

update = threading.Thread(target=updateUI, args=(comms, app))
update.start()

app.mainloop()
root.destroy()
comms.terminateComms()