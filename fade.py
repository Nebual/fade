import os, sys, pickle, time
from cStringIO import StringIO
from optparse import OptionParser
try: import readline #Importing this enables up/down arrows in Linux
except ImportError: pass

import rooms
from rooms import GO, LOOK, GET, USE, Areas, States, Inventory, say, SearchableString
stdout_backup = sys.stdout

class mystdout(object):
	def __init__(self, suppress=False):
		self.file = StringIO()
		self.stdout = sys.stdout
		sys.stdout = self
		self.suppress = suppress
	def write(self, data):
		self.file.write(data)
		if not self.suppress: self.stdout.write(data)
	def close(self):
		s = self.file.getvalue()
		sys.stdout = self.stdout
		self.file.close()
		return s

import contextlib
#backup_print = print
@contextlib.contextmanager
def listenPrints(suppress=False):
	"""Creates a context that saves all prints to a string, while optionally suppressing them.
	returns a list containing the string at index 0.
	with listenPrints() as out: print("lol")
	"""
	out = [""]
	myout = mystdout(suppress=suppress)
	try:
		yield out
	finally:
		out[0] = myout.close()
@contextlib.contextmanager
def charByChar(speed=0.05):
	"""Creates a context that saves all prints to a string, suppressing them.
	When context is left, it prints the string char by char.
	with charByChar(speed=0.1): print("lol")
	"""
	with listenPrints(suppress=True) as out:
		yield out
	for char in out[0]:
		sys.stdout.write(char)
		sys.stdout.flush()
		time.sleep(speed)

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
	elif cmd == "help":
		print ("You consider for a moment the verbs you've learned:\n"
			"go (enter) [room]\n"
			"back (return, last) goes to previous room\n"
			"examine (look) [object]\n"
			"grab (pick, get, take) [object]\n"
			"use [object] on [object]\n"
			"save/load [savename]\n"
			"i (inventory)")
	elif cmd in ("i", "inventory"):
		if "backpack" in States:
			print("You stop and look at the contents of your leather backpack:")
			for item in Inventory.values():
				print("\t["+item+"]")
		else:
			say("There isn't anything in your pockets. You try to start missions light.")
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
	elif cmd in ("back", "return", "last"):
		if "lastarea" in States: rooms.setArea(States["lastarea"])
		else: say("You just walked into the building, you can't leave yet.")
	elif "bumbl" in cmd:
		say("Bumbling around into furniture isn't really productive."
			"Besides, you're supposed to follow leave no trace when Seeking.")
	elif "break" in cmd:
		say("Seekers can't just go around breaking things, especially not in old ruins.")

def main():
	while True:
		msg = SearchableString(raw_input("\n["+States["area"].__class__.__name__+"]--> ").lower())
		print("")
		
		with listenPrints() as out:
			parseCMD(msg)

		if not out[0]:
			rooms.notFound(msg.split())

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
		import time, os, random
		for t in range(1,4*5):
			width = (t//4)*3
			s = ""
			for y in range(-17,13):
				for x in range(-40,40):
					picked = 5
					for i in range(5):
						if abs(x) < (width+4*i) and abs(y) < (width+3*i):
							picked = i
							break
					s += random.choice(greyscale[picked])
					
					#s+=random.choice(greyscale[min(7,max(0, int((abs(x/2.0)+abs(y/1.5))*(7.0/20.0) - t//10)))])
				s+="\n"
			os.system(os.name == "nt" and "cls" or "clear")
			print(s)
			time.sleep(0.18)
		time.sleep(0.6)
		os.system(os.name == "nt" and "cls" or "clear")
		time.sleep(0.4)
		
		with charByChar(speed=0.04):
			rooms.setArea("lobby")
		
	if "area" not in States:
		rooms.setArea("lobby")
	
	WasKBInterrupt = False
	try:
		main()
	except KeyboardInterrupt:
		WasKBInterrupt = True
	finally:
		if not WasKBInterrupt:
			print("Eeek we crashed! Emergency saving to crash.sav")
			pickle.dump((States, Inventory), open("crash.sav","wb"))
