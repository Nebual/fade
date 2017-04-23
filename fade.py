import os, sys, time, random
from optparse import OptionParser
try: import readline #Importing this enables up/down arrows in Linux
except ImportError: pass

import consolelib, dson
import roomCommon
from roomCommon import say, SearchableString, playSound, getTime, setArea, openMap, notFound, GO, LOOK, GET, USE, LOCKPICK, Areas, States, Inventory
import hotel, resolution

def parseCMD(msg):
	cmds = msg.split(); cmd = SearchableString(len(cmds) > 0 and cmds[0] or "")
	curArea = Areas[States["area"]]
	if cmd == "load":
		SaveName = len(cmds) > 1 and cmds[1] or input("Save name: >")
		if SaveName:
			NewStates, NewInventory = dson.load(open(SaveName+".dson","r"))
			States.clear(); Inventory.clear()
			States.update(NewStates); Inventory.update(NewInventory)
			print("== Progress loaded from '"+SaveName+".dson' ==")
	elif cmd == "save":
		SaveName = len(cmds) > 1 and cmds[1] or input("Save name: >")
		if SaveName:
			dson.dump((States, Inventory), open(SaveName+".dson","w"), indent=2)
			print("== Progress saved to '"+SaveName+".dson' ==")
	elif cmd in ("clear", "cls"):
		consolelib.clear()
		print(" ")
	elif cmd in ("h", "help"):
		print ("You consider for a moment the verbs you've learned:\n"
			"go/enter [room]\n"
			"back/return/last goes to previous room\n"
			"look/examine/view [object]\n"
			"grab/pick/get/take [object]\n"
			"use [object] on [object]\n"
			"lockpick [object]\n"
			"time\n"
			"map\n"
			"i/inventory\n"
			"save [filename]\n"
			"load [filename]")
	elif cmd in ("i", "inventory"):
		if "backpack" in States:
			print("You stop and look at the contents of your leather backpack:")
			for item in Inventory.values():
				print("\t- "+item)
			print("\t- Lockpicking pins: "+str(States["pins"]))
			print("\t- Money: $%.2f" % States["money"])
		else:
			say("There isn't anything in your pockets. You try to start missions light.")
	elif cmd in ("time", "watch"):
		if "watch" in States: say("You glance at your Booker's display of the current local time: "+getTime())
		else: say("Your booker's internal clock hasn't been configured for this locale, and is still displaying your home time: " + str(int(States["time"]/1.44)))
	elif cmd in ("map",):
		say("You review your Booker's spatial layouting program.")
		with consolelib.lineByLine(0.03):
			openMap(curArea.zone)
	elif cmd == "" or (cmd in LOOK and len(cmds) == 1):
		curArea.describe()
	elif cmd in ("back", "return", "last") or "go back" in msg:
		if "lastarea" in States: setArea(States["lastarea"])
		else: say("You just walked into the building, you can't leave yet.")
	elif cmd in GO:
		curArea.GO(cmd, cmds, msg)
	elif cmd in LOOK:
		if ("booker", "arm") in msg:
			say("The Booker on your arm is an advanced Personal Information Processor. The 2000 model premiered in the year 8AA, and is primarily built from salvaged Old world components modified to support an MF power core. Its many features include a watch, 3D scanner, 1w laser pointer (doubles as a microwelder), journal logging, and flying toasters screensaver.")
		elif ("keyhole") in msg: say("You peer through the door's keyhole, but can't see anything, since there's a lock in the way.")
		else:
			curArea.LOOK(cmd, cmds, msg)
	elif cmd in GET:
		curArea.GET(cmd, cmds, msg)
	elif cmd in USE:
		with consolelib.listenPrints() as printedString:
			curArea.USE(cmd, cmds, msg)
		if printedString[0]: pass
		elif "magazines" in Inventory and ("maga", "zine") in msg:
			say("Is now the best time to be doing that?")
		elif "crochetagebook" in Inventory and "crochet" in msg:
			say("You flip through the booklet, but you can't understand the language. The diagrams detail the basics of picking locks.")
		elif ("water", "hydra", "bottle") in msg and "waterbottle" in Inventory:
			say("You're not thirsty at the moment.")
	elif cmd in LOCKPICK:
		if len(cmds) == 1:
			say("What locked object do you want to pick?")
		else:
			curArea.LOCKPICK(cmd, cmds, msg)
	elif "bumbl" in cmd:
		say("Bumbling around into furniture isn't really productive."
			"Besides, you're supposed to follow 'leave no trace' when Seeking.")
	elif ("break", "kick", "smash") in cmd:
		say("Seekers can't just go around breaking things, especially not in old ruins.")
	elif ("hello", "hi", "hey") in cmd: say("Ello.")
	elif ("yes") in cmd: say("Nope.")
	elif ("no") in cmd: say("Yep.")

def main():
	while True:
		msg = SearchableString(input("\n["+Areas[States["area"]].__class__.__name__+"]--> ").lower())
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
	parser.add_option("-f", "--fast", action="store_true", dest="fasttext", default=False, help="disables slow text printing")
	parser.add_option("-w", "--web", action="store_true", dest="web", default=False, help="enables sending helper commands to a javascript frontend")
	
	options, args = parser.parse_args()
	if options.fasttext:
		consolelib.setTextSpeed(True)
	if options.web:
		consolelib.setWebMode(True)
	if options.load:
		parseCMD("load "+options.load.rsplit(".", 1)[0])
		options.showintro = False
	else: input("""\
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

                                [Press Enter]\
""")
	if options.showintro:
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
		
	if "time" not in States:
		#New game!
		States["time"] = 9*60
		States["pins"] = 0
		States["money"] = 3
		consolelib.clear()
		if(input("""\n\n\n\n\n\n\n\n\n\n\n
                      There is much to see in this world,
                  take care to `look` at everything you find.
\n\n\n\n\n\n
                          [Press Enter to Start Game]
                   [Type 'help' at any time to list commands]
\n""") == "help"): parseCMD("help")
		setArea("lobby")
	
	WasKBInterrupt = False
	try:
		main()
	except KeyboardInterrupt:
		WasKBInterrupt = True
	finally:
		if not WasKBInterrupt:
			print("Eeek we crashed! Emergency saving to crash.dson...")
			dson.dump((States, Inventory), open("crash.dson","w"))
			print("Save successful! Printing stacktrace:\n")
