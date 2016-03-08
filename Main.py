'''
Created on 11 Dec 2015

@author: Jurie
'''

from tkinter import *
from tkinter.tix import COLUMN
from tkinter.ttk import Combobox
import tkinter.messagebox
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
		
	def sendPerc(self,event):
		print('perc:' + str(self.varPerc.get()))
		self.sendRigCmd({'type':'setCMD','instr':'setPumpPerc','percentage':self.varPerc.get()})
	
	def sendDataDump(self,activate):
		print('DataDump ' + str(activate))
		if (activate==True):
			self.sendRigCmd({'type':'testerCMD','instr':'activateDataDump'})
		elif(activate==False):
			self.sendRigCmd({'type':'testerCMD','instr':'deactivateDataDump'})
			
	def sendManual(self,instr):
		print('Send manual ' + instr)
		self.sendRigCmd({'type':'manualCMD','instr':instr})
			
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
		self.lstStates = ["clearError","prime","fill","forceFill","idle","pump","setPressure","error","override","leakageTest","continue", "preempt", "waitIsolate","isolationTest"]
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
		
		self.lblPerc = Label(text='Pump percentage:')
		self.lblPerc.grid(row=rowC, column=0)
		self.varPerc = DoubleVar()
		self.entPerc = Entry(textvariable = self.varPerc)
		self.entPerc.grid(row=rowC, column =1)
		self.entPerc.bind('<FocusOut>',self.sendPerc)
		
		self.btnActivateDump = Button(text = "Activate data dump",command = lambda:self.sendDataDump(True))
		self.btnActivateDump.grid(row=rowC, column=2)

		self.btnActivateDump = Button(text = "Deactivate data dump",command = lambda:self.sendDataDump(False))
		self.btnActivateDump.grid(row=rowC, column=3)
		
		rowC+=1
		self.btnStartPump = Button(text = 'startPump',command = lambda:self.sendManual('startPump'))
		self.btnStartPump.grid(row=rowC,column=0)
		self.btnStartPump = Button(text = 'stopPump',command = lambda:self.sendManual('stopPump'))
		self.btnStartPump.grid(row=rowC,column=1)
		
		self.btnStartPump = Button(text = 'openInflow',command = lambda:self.sendManual('openInflowValve'))
		self.btnStartPump.grid(row=rowC,column=2)
		self.btnStartPump = Button(text = 'closeInflow',command = lambda:self.sendManual('closeInflowValve'))
		self.btnStartPump.grid(row=rowC,column=3)
		
		self.btnStartPump = Button(text = 'openOut',command = lambda:self.sendManual('openOutflowValve'))
		self.btnStartPump.grid(row=rowC,column=4)
		self.btnStartPump = Button(text = 'closeOut',command = lambda:self.sendManual('closeOutflowValve'))
		self.btnStartPump.grid(row=rowC,column=5)
		
		self.btnStartPump = Button(text = 'openRelease',command = lambda:self.sendManual('openReleaseValve'))
		self.btnStartPump.grid(row=rowC,column=6)
		self.btnStartPump = Button(text = 'closeRelease',command = lambda:self.sendManual('closeReleaseValve'))
		self.btnStartPump.grid(row=rowC,column=7)
		
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
	
	def __init__(self,sendCmd,sendRigCmd,master=None):
		Frame.__init__(self, master)
		self.grid(row=0,column = 0)
		self.createWidgets()
		self.sendCmd = sendCmd
		self.sendRigCmd = sendRigCmd

def prompt(incomming):
	#print( incomming)
	reply = tkinter.messagebox.askyesno('Prompt', incomming['prompt']['msg'])
	print("reply:",reply)
	if (reply):
		comms.sendPromptReply({'reply':'yes','id':incomming['prompt']['id']})
	else:
		comms.sendPromptReply({'reply':'no','id':incomming['prompt']['id']})
	

def updateUI(comms, app):
	stepStrings = ['start pump', 'start pump','Initial pumprun','Set pressure','Set pressure', 'start settle', 'wait settle','reset counters', 'measuring','Take measure','Send idle', 'Save results']
	
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
			if (appStatus['state']=='LEAKAGE_TEST'):
				app.varFbStep.set(stepStrings[appStatus['step']-1])
			else:
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
			elif(key == 'prompt'):
				print(incoming)
				prmt_t = threading.Thread(target=prompt,args=(incoming,))
				prmt_t.start()
				
				
					
		#time.sleep(0.1)
		
	print('TerminateComms init')	
	comms.terminateComms()
	print('TerminateComms done')	
	

comms = UIServerComms('jurie-masters.local',5001)

comms.start()
		
root = Tk()
app = ButtonsFrame(master = root,sendCmd = comms.sendUICmd, sendRigCmd = comms.sendRigCmd)

update = threading.Thread(target=updateUI, args=(comms, app))
update.start()

app.mainloop()
root.destroy()
comms.terminateComms()