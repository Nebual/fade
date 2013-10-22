GO = ("enter","go")
LOOK = ("examine", "look")
GET = ("pick", "grab", "get", "take")
USE = ("use",)

Areas = {}
States = {}
Inventory = {}

#def giveGlobals(StatesIn, InventoryIn, setAreaIn):
#	global States, Inventory, setArea
#	States, Inventory, setArea = StatesIn, InventoryIn, setAreaIn

def setArea(newArea):
	if newArea in Areas:
		States["area"] = Areas[newArea]
		States["area"].describe()

class Room(object):
	pass
	
class Lobby(Room):
	def describe(self):
		print "You're in the lobby of a hotel. The room is lavishly decorated."
		if "backpack" not in States: print "You see a backpack lying against the wall near the entrance."
		if "keyfloor" in States: print "There's a metal key on the floor near the wall."
		print "\nThere are doors marked 'Stairs', 'Washrooms', and 'Cafe'"

	def GO(self, cmd, cmds, msg):
		if "stair" in msg:
			if not "stairdoorunlocked" in States:
				print "The doorknob to the stairs refuses to turn. It is likely locked."
		elif "washroom" in msg:
			print "You enter the washrooms."
			setArea("washrooms")
		elif "cafe" in msg:
			print ("You peer through the window to the Cafe.\n"
				"Its far too dark to enter, you'd just be bumbling into furniture.")
		elif "entrance" in msg:
			print "You can't leave the hotel, you don't have the Core yet."
		else:
			print "Where to?"
	def LOOK(self, cmd, cmds, msg):
		if "pack" in msg:
			print ("You see a rugged looking leather backpack; old, but in good condition.\n"
				"A brief inspection reveals 4 pouches, all of which empty short of\n"
				"a single deck of Magic The Gathering cards.")
		else:
			print "Look at what?"	
	def GET(self, cmd, cmds, msg):
		if ("backpack" not in States) and "pack" in msg:
			print ("You pick up the rugged leather backpack.\n"
				"As you slide it onto your shoulders, you hear the clink of metal hitting\n"
				" the linolium floor.")
			States["keyfloor"] = True
			States["backpack"] = True
		elif "keyfloor" in States and "key" in msg:
			print ("You pick up the key. It has an 'S' scratched on it.")
			del States["keyfloor"]
			Inventory["stairkey"] = "A worn key. There is an 'S' scratched on it."
		else: 
			print "Get what?"
	def USE(self, cmd, cmds, msg):
		if len(cmds) > 3 and "stairkey" in Inventory and "key" in msg:
			#print "Which door do you want to use the key on?"
			resp = cmds[3] #raw_input("\t>").lower()
			if "stair" in resp:
				print ("You put the 'S' key into the Stairwell Door.\n"
					"\n"
					"For awhile, nothing happens. Then suddenly, you realize\n"
					"the architecture of the building precludes automatic doors,\n"
					"and that you'll likely have to turn the key manually.\n"
					"With a turn, the lock clicks open, though the key doesn't\n"
					"want to be removed without locking the door again.")
				States["stairdoor"] = True
				del Inventory["stairkey"]
			elif "cafe" in resp:
				print "The cafe door has no lock."
				if not "flashlight" in Inventory:
					print "Its just creepy in there without a light."
			elif "washroom" in resp:
				print "The keyhole for the washroom door takes a very large key."
			else:
				print "Keys are generally used to open locked things. Not much else."
		elif len(cmds) > 1:
			print "Use "+cmds[1]+" on what?"  
		else:
			print "Use what?"
Areas["lobby"] = Lobby()
	
class Washroom(Room):
	def describe(self):
		print ("You're in the first floor washrooms, Men's section.\n"
			"There is a row of water recepticles below a glass mirror,\n"
			"neither of which appear to be in functional condition.\n"
			"There is a wooden shelf, made of a low quality fibre that likely wasn't\n"
			"very attractive when it was new, either.\n\n" 
			"Behind you is the door to the lobby.")
	def GO(self, cmd, cmds, msg):
		if "lobby" in msg:
			setArea("lobby")
		else:
			print "Go where?"
	def LOOK(self, cmd, cmds, msg):
		if "shelf" in msg:
			print "An inspection of the contents of the shelf reveals a series of broken bottles,"
			if "wr_flashlight_taken" not in States:
				print "an old electronic flashlight at the end of the top shelf,"
			print "several unpleasant looking old fabrics, and that the shelf is quite unstable."
		elif "window" in msg:
			print ("You gaze out the window for a few minutes. You learn little.\n"
				"The window is opaque. This was largely why.")
		elif "sink" in msg:
			print "The sinks are most certainly not going to flow any time soon."
		elif "lobby" in msg: 
			print "The hotel lobby, main entrance room."
		elif "floor" in msg: 
			print "The floor is filthy, and thats all the time you want to spend looking at it."
		elif "mirror" in msg:
			print ("You barely recognize yourself in the mirror underneath all the layers of\n"
				"protective clothing. But its essential if you're to get the Core you're looking for.")
			
	def GET(self, cmd, cmds, msg):
		if "flashlight" in msg and "wr_flashlight_taken" not in States:
			if "backpack" in States:
				States["wr_flashlight_taken"] = True
				Inventory["flashlight"] = "An old portable electronic light source, Lithium Ion power source."
				print ("You pick up the flashlight off the shelf. The wood quivers a little,\n"
					"a shelf loses its integrity and tumbles to the floor, but theres no further\n"
					"cascading problems. The washroom window is bright enough, so you put\n"
					"the flashlight into your backpack.")
			else:
				print ("The room is plenty bright enough, and you don't have anywhere\n"
					"to store the flashlight, so you leave it behind.")
	def USE(self, cmd, cmds, msg):
		pass
Areas["washrooms"] = Washroom()
