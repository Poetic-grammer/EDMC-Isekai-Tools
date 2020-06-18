import sys
try:
    import tkinter as tk
    from tkinter import ttk
except:
    import Tkinter as tk
    import ttk
import requests

import myNotebook as nb
from config import config

this = sys.modules[__name__]

def plugin_start(plugin_dir):
   """
   Load this plugin into EDMC
   """
   this.webhooks = tk.StringVar(value=config.get("IsekaiWebHooks"))
   this.currentCarrier = None
   this.webhookLimit = 6
   return "Isekai Plugin"

def plugin_stop():
    """
    EDMC is closing
    """
    print "Farewell cruel world!"

def plugin_app(parent):
    this.parent = parent
    frame = tk.Frame(parent, width=100, height=10)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    label = tk.Label(frame, text="Carrier:")
    label.grid(row=0, column=0)
    this.currentCarrierLabel = tk.Label(frame, text="not")
    this.currentCarrierLabel.grid(row=0, column=1)
    return frame

def updateCarrier():
    this.currentCarrierLabel['text'] = this.currentCarrier["Name"]


def getWebHooks():
    result = this.config.get("IsekaiWebHooks")
    if result == None:
        return []
    return result.splitlines()

def handle_CarrierStats(data):
    eventData = data["entry"]
    if this.currentCarrier == None:
        this.currentCarrier = {}
    fields = ["CarrierID", "Callsign", "Name"]
    for i in fields:
        this.currentCarrier[i] = eventData[i]
    updateCarrier()



def handle_CarrierJumpRequest(data):
    allWebHooks = getWebHooks()
    print "Current Carrier"
    print this.currentCarrier
    currentName = "Some carrier" if not "Name" in this.currentCarrier else this.currentCarrier["Name"] 
    destination = data["entry"]['SystemName']
    callsign = None if not "Callsign" in this.currentCarrier  else this.currentCarrier["Callsign"]
    content = "{carrierName} heading to {destination} in 15 minutes".format(carrierName  = currentName, destination = destination)
    username = "Isekai bridge officer"

    if callsign is not None:
        content += "\n https://fleetcarrier.space/carrier/{callsign}".format(callsign = callsign)
    # create post
    post = {
        "content" : content,
        "username" : username
    }

    for i in allWebHooks:
        r = requests.post(i.strip(), data=post )

def handle_CarrierJumpCancelled(data):
    allWebHooks = getWebHooks()
    print "Current Carrier"
    print this.currentCarrier
    currentName = "Some carrier" if not "Name" in this.currentCarrier else this.currentCarrier["Name"] 
    callsign = None if not "Callsign" in this.currentCarrier  else this.currentCarrier["Callsign"]
    content = "{carrierName}'s jump is canceled ".format(carrierName  = currentName)
    username = "Isekai bridge officer"

    if callsign is not None:
        content += "\n https://fleetcarrier.space/carrier/{callsign}".format(callsign = callsign)
    # create post
    post = {
        "content" : content,
        "username" : username
    }

    for i in allWebHooks:
        r = requests.post(i.strip(), data=post )



def journal_entry(cmdr, is_beta, system, station, entry, state):

    dataPack = { "commander" : cmdr,"system": system, "station": station, "entry": entry }

    handlers = {
        'CarrierJumpRequest': handle_CarrierJumpRequest,
        'CarrierJumpCancelled': handle_CarrierJumpCancelled,
        'CarrierStats': handle_CarrierStats
    }

    if entry['event'] in handlers:
        handlers[entry['event']](dataPack)

def plugin_prefs(parent, cmdr, is_beta):
    webHooks = getWebHooks()
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1) 
    this.webHooksUi = []
    nb.Label(frame, text="discord webhooks")
    for i in xrange(this.webhookLimit):
        tempEntry =nb.Entry(frame)
        row =8+(i*2)
        tempEntry.grid(padx=10, row= row)
        this.webHooksUi.append(tempEntry)
        if i < len(webHooks):
            this.webHooksUi[i].delete(0, tk.END)
            this.webHooksUi[i].insert(0, webHooks[i])

    return frame

def prefs_changed():
    temp = ""
    for i in this.webHooksUi:
        temp += i.get() + "\n"
    config.set("IsekaiWebHooks", temp)




