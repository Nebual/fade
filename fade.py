import os, sys, pickle, time, random
from optparse import OptionParser
try: import readline #Importing this enables up/down arrows in Linux
except ImportError: pass

sys.path.append("..")
import consolelib

from roomCommon import say, SearchableString, playSound, getTime, setArea, notFound, GO, LOOK, GET, USE, LOCKPICK, Areas, States, Inventory
import hotel

def parseCMD(msg):
	cmds = msg.split(); cmd = SearchableString(len(cmds) > 0 and cmds[0] or "")
	if cmd == "load":
		SaveName = len(cmds) > 1 and cmds[1] or raw_input("Save name: >")
		if SaveName:
			NewStates, NewInventory = pickle.load(open(SaveName+".sav","rb"))
			States.clear(); Inventory.clear()
			States.update(NewStates); Inventory.update(NewInventory)
			print("== Progress loaded from '"+SaveName+".sav' ==")
	elif cmd == "save":
		SaveName = len(cmds) > 1 and cmds[1] or raw_input("Save name: >")
		if SaveName:
			pickle.dump((States, Inventory), open(SaveName+".sav","wb"))
			print("== Progress saved to '"+SaveName+".sav' ==")
	elif cmd in ("clear", "cls"):
		consolelib.clear()
		print " "
	elif cmd == "help":
		print ("You consider for a moment the verbs you've learned:\n"
			"go (enter) [room]\n"
			"back (return, last) goes to previous room\n"
			"examine (look) [object]\n"
			"grab (pick, get, take) [object]\n"
			"use [object] on [object]\n"
			"lockpick [object]\n"
			"time\n"
			"i (inventory)\n"
			"save/load [savename]")
	elif cmd in ("i", "inventory"):
		if "backpack" in States:
			print("You stop and look at the contents of your leather backpack:")
			for item in Inventory.values():
				print("\t- "+item)
			print "\t- Lockpicking pins: "+str(States["pins"])
			print "\t- Money: $%.2f" % States["money"]
		else:
			say("There isn't anything in your pockets. You try to start missions light.")
	elif cmd in ("time", "watch"):
		if "watch" in States: say("You glance at your Booker's display of the current local time: "+getTime())
		else: say("Your booker's internal clock hasn't been configured for this locale, and is still displaying your home time: " + str(int(States["time"]/1.44)))
	elif cmd == "" or (cmd in LOOK and len(cmds) == 1):
		States["area"].describe()
	elif cmd in ("back", "return", "last") or "go back" in msg:
		if "lastarea" in States: setArea(States["lastarea"])
		else: say("You just walked into the building, you can't leave yet.")
	elif cmd in GO:
		States["area"].GO(cmd, cmds, msg)
	elif cmd in LOOK:
		if ("booker", "arm") in msg:
			say("The Booker on your arm is an advanced Personal Information Processor. The 2000 model premiered in the year 8AA, and is primarily built from salvaged Old world components modified to support an MF power core. Its many features include a watch, 3D scanner, 1w laser pointer (doubles as a microwelder), journal logging, and flying toasters screensaver.")
		else:
			States["area"].LOOK(cmd, cmds, msg)
	elif cmd in GET:
		States["area"].GET(cmd, cmds, msg)
	elif cmd in USE:
		if "magazine" in Inventory and "magazine" in msg:
			say("Is now the best time to be doing that?")
		elif "crochetagebook" in Inventory and "crochet" in msg:
			say("You flip through the booklet, but you can't understand the wording. The diagrams detail the basics of picking locks.")
		else:
			States["area"].USE(cmd, cmds, msg)
	elif cmd in LOCKPICK:
		if len(cmds) == 1:
			say("What locked object do you want to pick?")
		else:
			States["area"].LOCKPICK(cmd, cmds, msg)
	elif "bumbl" in cmd:
		say("Bumbling around into furniture isn't really productive."
			"Besides, you're supposed to follow 'leave no trace' when Seeking.")
	elif ("break", "kick", "smash") in cmd:
		say("Seekers can't just go around breaking things, especially not in old ruins.")

def main():
	while True:
		msg = SearchableString(raw_input("\n["+States["area"].__class__.__name__+"]--> ").lower())
		print("")
		
		with consolelib.listenPrints() as printedString:
			parseCMD(msg)

		if printedString[0]:
			States["time"] += 5 #Successful actions take 5 minutes
		else:
			#Nothing was printed, so the command/args pair wasn't found
			notFound(msg.split())

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-s", "--skip-intro", action="store_false", dest="showintro", default=True, help="skip the intro cinematic")
	parser.add_option("-l", "--load", action="store", type="string", dest="load", help="load a save")
	
	options, args = parser.parse_args()
	if options.load:
		parseCMD("load "+options.load.rsplit(".", 1)[0])
	elif options.showintro:
		raw_input("""\
==========================================

`7MMMMMMMM  db      `7MMMMMYb. `7MMMMMMMM  
  MM    `7 ;MM:       MM    `Yb. MM    `7  
  MM   d  ,V^MM.      MM     `Mb MM   d    
  MM""MM ,M  `MM      MM      MM MMmmMM    
  MM   Y AbmmmqMA     MM     ,MP MM   Y  , 
  MM    A'     VML    MM    ,dP' MM     ,M 
.JMML..AMA.   .AMMA..JMMmmmdP' .JMMmmmmMMM

=============== The Search ===============
----- Stumbling through the darkness -----
==========================================

               [Start Game]
""")
		playSound("sounds/ps1start.wav")

		greyscale = [
			".,-",
			"_ivc=!/|\\~",
			"gjez2]/(YL)t[+T7Vf",
			"mdk4zgbjDXY7p*O",
			"mdK4ZGbNDXY5P*Q",
			"W8KMA",
			"W8KMA",
			"#%$"
			]
		for t in range(1,5*5):
			width = (t//5)*3 #Every 4 ticks, increase doorframe width by 3
			s = ""
			for y in range(-17,13): #Offset from -15,-15 so the door ends at the bottom of the screen
				for x in range(-39,39):
					picked = 5
					for i in range(5):
						if abs(x) < (width+4*i) and abs(y) < (width+3*i):
							picked = i
							break
					s += random.choice(greyscale[picked])
				s+="\n"
			consolelib.clear()
			print(s)
			time.sleep(0.18)
		time.sleep(0.8)
		consolelib.clear()
		time.sleep(0.3)
		
	if "area" not in States:
		#New game!
		States["time"] = 9*60
		States["pins"] = 0
		States["money"] = 3
		setArea("lobby")
	
	WasKBInterrupt = False
	try:
		main()
	except KeyboardInterrupt:
		WasKBInterrupt = True
	finally:
		if not WasKBInterrupt:
			print("Eeek we crashed! Emergency saving to crash.sav")
			pickle.dump((States, Inventory), open("crash.sav","wb"))
