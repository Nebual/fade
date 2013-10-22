import os, sys, pickle
try: import readline
except ImportError: pass

import rooms
from rooms import GO, LOOK, GET, USE, Areas, States, Inventory

def main():
	rooms.setArea("lobby")

	while True:
		msg = raw_input("fade> ").lower()
		cmds = msg.split(); cmd = len(cmds) > 0 and cmds[0] or ""
		
		if cmd == "load":
			SaveName = len(cmds) > 1 and cmds[1] or raw_input("Save name: >")
			if SaveName:
				NewStates, NewInventory = pickle.load(open(SaveName+".sav","rb"))
				States.clear(); Inventory.clear()
				States.update(NewStates); Inventory.update(NewInventory)
				print "== Progress loaded from '"+SaveName+".sav' =="
		elif cmd == "save":
			SaveName = len(cmds) > 1 and cmds[1] or raw_input("Save name: >")
			if SaveName:
				pickle.dump((States, Inventory), open(SaveName+".sav","wb"))
				print "== Progress saved to '"+SaveName+".sav' =="
		elif cmd == "help":
			print ("You consider for a moment the verbs you've learned:\n"
				"go (enter) [room]\n"
				"examine (look) [object]\n"
				"grab (pick, get, take) [object]\n"
				"use [object] on [object]\n"
				"save/load [savename]\n"
				"i (inventory)\n")
		elif cmd in ("i", "inventory"):
			if "backpack" in States:
				print "You stop and look at the contents of your leather backpack:\n"
				for item in Inventory.values():
					print "\t["+item+"]"
			else:
				print "There isn't anything in your pockets. You try to start missions light."
		elif cmd == "" or (cmd in LOOK and len(cmds) == 1):
			States["area"].describe()
		elif cmd in GO:
			States["area"].GO(cmd, cmds, msg)
		elif cmd in LOOK:
			States["area"].LOOK(cmd, cmds, msg)
		elif cmd in GET:
			States["area"].GET(cmd, cmds, msg)
		elif cmd in USE:
			States["area"].USE(cmd, cmds, msg)
		else:
			print "Do what?"

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		WasKBInterrupt = True
	finally:
		if not WasKBInterrupt:
			print "Eeek we crashed! Emergency saving to crash.sav"
			pickle.dump((States, Inventory), open("crash.sav","wb"))
