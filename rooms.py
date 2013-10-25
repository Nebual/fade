import os, sys, textwrap, re

GO = ("enter","go")
LOOK = ("examine", "look")
GET = ("pick", "grab", "get", "take")
USE = ("use",)

Areas = {}
States = {}
Inventory = {}

class SearchableString(str):
	def __contains__(self,y):
		if type(y) == str:
			return str.__contains__(self, y)
		else:
			return any(part in self for part in y)

wrapper = textwrap.TextWrapper(width=79)
splitSentance = re.compile(r'([^\.!?]*[\.!?])').split
def wrap(s):
	"""A function that applies wordwrap (to console width) to a string, and returns it.
	Tabs and newlines are automatically removed.
	Periods are always followed by a newline.
	Blank newlines are made of a period by itself.
	"""
	rows = [wrapper.fill(line.strip().replace("\t","")) for line in splitSentance(s) if line]
	if rows[-1] == "": del rows[-1]
	out = ""
	for row in rows:
		if row == ".": out += "\n"
		else: out += row + "\n"
	return out[:-1]
def say(s):
	print(wrap(s))

class SearchableString(str):
	"""A subclass of str, that lets you do
	("hello", "hi") in "hello there gentlemen"
	which returns True if any elements of the tuple are found in the second string"""
	def __contains__(self,y):
		if type(y) == str:
			return str.__contains__(self, y)
		else:
			return any(part in self for part in y)

def notFound(cmds):
	contents = "'" + (" ".join(cmds[1:])) + "'"
	if cmds[0] in GO:
		if len(cmds) == 1: say("As a 3 dimensional being, you can only go to places, you cannot just 'Go' in general.")
		else: 
			say("You attempt to "+cmds[0]+" "+contents+", but can't see how.")
	elif cmds[0] in LOOK:
		say("You look around feverently for this "+contents+", but find nothing of the sort.")
	elif cmds[0] in USE:
		if len(cmds) == 1: say("You cannot use the room at large, only things physically inside it.")
		else: 
			say("You don't see what using "+contents+" would accomplish.")
	elif cmds[0] in GET:
		if len(cmds) == 1: say("You just don't get 'it'. You'll have to settle for "+cmds[0]+"ing specific things.")
		else:
			say("You don't think you can "+cmds[0]+" "+contents+".")
	else:
		say("You're not sure what '"+cmds[0]+"' entails.")

def setArea(newArea):
	"""Takes a string, and sets States["area"] to the corresponding Room object."""
	if newArea in Areas:
		if "area" in States: States["lastarea"] = States["area"].name
		States["area"] = Areas[newArea]
		States["area"].describe()

class Room(object):
	def __init__(self):
		self.name = self.__class__.__name__.lower()
		Areas[self.name] = self

class Test(Room):
	"""Test is a developer room, for experimenting with inventory, states, etc. It also is connected to every room."""
	def describe(self):
		say("""This is an example of Speex. Newlines are auto added after periods, existing newlines/tabs are ignored.""")

	def GO(self, cmd, cmds, msg):
		setArea(cmds[1])
	def LOOK(self, cmd, cmds, msg):
		if "test2" in msg: print("Test message")
		elif "test" in msg: say("""Test message""")
	def GET(self, cmd, cmds, msg):
		if ("backpack" not in States) and "pack" in msg:
			say("""You pick up the rugged leather backpack.
				As you slide it onto your shoulders, you hear the clink of metal hitting the linolium floor.""")
			States["keyfloor"] = True
			States["backpack"] = True
	def USE(self, cmd, cmds, msg):
		if len(cmds) > 3 and "stairkey" in Inventory and "key" in msg:
			say("Use the key on what?")
		elif len(cmds) > 1:
			say("Use "+cmds[1]+" on what?")  
Test()

#Test here is an example room, ideal to copypaste to add more rooms
class Example(Room):
	def describe(self):
		say("""
		""")

	def GO(self, cmd, cmds, msg):
		if "stair" in msg:
			if not "stairdoorunlocked" in States:
				say("The doorknob to the stairs refuses to turn. It is likely locked.")
	def LOOK(self, cmd, cmds, msg):
		if "test2" in msg: print("Test message")
		elif "test" in msg: say("""Test message""")
	def GET(self, cmd, cmds, msg):
		if ("backpack" not in States) and "pack" in msg:
			say("""You pick up the rugged leather backpack.
				As you slide it onto your shoulders, you hear the clink of metal hitting the linolium floor.""")
			States["keyfloor"] = True
			States["backpack"] = True
	def USE(self, cmd, cmds, msg):
		if len(cmds) > 3 and "stairkey" in Inventory and "key" in msg:
			say("Use the key on what?")
		elif len(cmds) > 1:
			say("Use "+cmds[1]+" on what?")  
Example()
	
class Lobby(Room):
	def describe(self):
		say("You're in the lobby of a hotel. The room is lavishly decorated." +
			("backpack" not in States and "You see a backpack lying against the wall near the entrance." or "") +
			("keyfloor" in States and "There's a metal key on the floor near the wall." or "") +
			".Besides the Entrance, there are doors marked 'Stairs', 'Washrooms', and 'Cafe'")
	def GO(self, cmd, cmds, msg):
		if "stair" in msg:
			if not "stairdoor" in States:
				say("The doorknob to the stairs refuses to turn. It is likely locked.")
			else:
				setArea("stairs")
		elif "washroom" in msg:
			setArea("washroom")
		elif "cafe" in msg:
			setArea("cafe")
		elif "entrance" in msg:
			say("You can't leave the hotel, you don't have the Core yet.")
		elif "test" in msg: setArea("test")
	def LOOK(self, cmd, cmds, msg):
		if "pack" in msg:
			say("""You see a rugged looking leather backpack; old, but in good condition.
					A brief inspection reveals 4 pouches, all of which empty short of
					a single deck of Magic The Gathering cards.""")
		elif "cafe" in msg:
			say("""You peer through the window to the Cafe.
				It's far too dark to enter, you'd just be bumbling into the furniture.""")
		elif "washroom" in msg:
			say("""There are two washroom doors, labeled Mars and Venus. While the latter is entirely inaccessible,  
				the doorframe to Mars has caved in slightly, leaving the door proped open.""")
		elif "stair" in msg:
			say("""You see the door to the main stairwell. There is a small keyhole on it""")
		elif ("floor", "ceiling", "walls") in msg:
			say("The lobby likely looked quite respectable in its time. It doesn't anymore.")
	def GET(self, cmd, cmds, msg):
		if ("backpack" not in States) and "pack" in msg:
			say("""You pick up the rugged leather backpack.
				As you slide it onto your shoulders, you hear the clink of metal hitting the linolium floor.""")
			States["keyfloor"] = True
			States["backpack"] = True
		elif "keyfloor" in States and "key" in msg:
			say("You pick up the key. It has an 'S' scratched on it.")
			del States["keyfloor"]
			Inventory["stairkey"] = "A worn key. There is an 'S' scratched on it."
	def USE(self, cmd, cmds, msg):
		if "stairkey" in Inventory and "key" in msg:
			if len(cmds) > 3:
				resp = cmds[3]
				if "stair" in resp:
					say("""You put the 'S' key into the Stairwell Door.
						For awhile, nothing happens. Then suddenly, you realize the architecture of the building precludes 
						automatic doors, and that you'll likely have to turn the key manually to get anywhere with it.
						With a turn, the lock clicks open, though the key doesn't want to be removed without locking the door again.""")
					States["stairdoor"] = True
					del Inventory["stairkey"]
				elif "cafe" in resp:
					say("The cafe door has no lock.")
					if not "flashlight" in Inventory:
						say("it's just creepy in there without a light.")
				elif "washroom" in resp:
					say("The washroom door is already proped open.")
				elif "manage" in resp:
					say("The keyhole for the Management door takes a very large key.")
				elif "door" in resp:
					print("Which door?")
				else:
					say("Keys are generally used to open locked things. Not much else.")
			else:
				say("Use the key on what?")
Lobby()
	
class Washroom(Room):
	def describe(self):
		say("""You're in the first floor washrooms, Men's section.
			There is a row of water recepticles below a glass mirror, neither of which appear to be in functional condition.
			There is a wooden shelf, made of a low quality fibre that likely wasn't very attractive when it was new, either.
			.
			Behind you is the door to the lobby.""")
	def GO(self, cmd, cmds, msg):
		if "lobby" in msg:
			setArea("lobby")
	def LOOK(self, cmd, cmds, msg):
		if "shelf" in msg:
			say("An inspection of the contents of the shelf reveals a series of broken bottles, " +
				("wr_flashlight_taken" not in States and "an old electronic flashlight at the end of the top shelf, " or "") +
				"several unpleasant looking old fabrics, and that the shelf is quite unstable.")
		elif "window" in msg:
			print("You gaze out the window for a few minutes. You learn little.\n"
				"The window is opaque. This was largely why.")
		elif ("sink", "water", "recepticle") in msg:
			say("The sinks are most certainly not going to flow any time soon.")
		elif "lobby" in msg: 
			say("The hotel lobby, main entrance room.")
		elif "floor" in msg:
			say("The floor is filthy, and thats all the time you want to spend looking at it.")
		elif "mirror" in msg:
			say("""You barely recognize yourself in the mirror underneath all the layers of
				protective clothing, the sight of it nearly causing you to collapse in exhaustion. 
				Without it though, you'd never get the Core you're looking for.""")
	def GET(self, cmd, cmds, msg):
		if "flashlight" in msg and "wr_flashlight_taken" not in States:
			if "backpack" in States:
				States["wr_flashlight_taken"] = True
				Inventory["flashlight"] = "An old portable electronic light source, Lithium Ion power source."
				say("""You pick up the flashlight off the shelf. With a crash that echoes into the lobby,
					a shelf loses its integrity and tumbles to the floor. Petrified, you pause for a moment to listen, but there's 
					no further disturbences. The light coming from the washroom window is bright enough, so you put
					the flashlight into your backpack for now.""")
			else:
				say("The room is plenty bright enough, and you don't have anywhere to store the flashlight, so you leave it behind.")
	def USE(self, cmd, cmds, msg):
		pass
Washroom()

class Cafe(Room):
	def describe(self):
		if "flashlighton" not in States:
			say("""Against all caution, you walk into the cafe.
				it's pitch black inside, since the power cut out long ago and the walls are, shockingly, not punctuated by
				sunlight. You can't do much in here without a flashlight.""")
		else:
			say("""Using your flashlight, you look around the old Cafe.
				The tables were obviously in use just prior to the fall, as evidenced by the plates and what appears to have once
				been food on them; some of the chairs were knocked over by the patrons' rush to get outside. Not that it would have helped them.
				.
				In the food preparation area, there are several electronic food coolers, heaters, cutters, and a box that looks
				strikingly like a modern MF Heater, but sure enough, it still has the familiar electrical umbilical cord all the others share.
				Some of the appliances may be useful as electrical scrap, but you wouldn't want to bring any of them with you unless
				you had a reason to.
				.
				The far wall once had huge windows, but rubble now entirely covers them.""" + 
				("toothpicks_obtained" not in States and "There's a small box on the countertop, with a label indicating it contains 'Strong Wood Products, Inc'." or "") + 
				("laptop_cafe_obtained" not in States and "A computer terminal sits behind a desk near the entrance." or "") +
				".The lobby is behind you.")
	def GO(self, cmd, cmds, msg):
		if "lobby" in msg:
			setArea("lobby")
		elif ("food", "prep") in msg:
			say("The food preparation area is part of the Cafe; clearly the architect was a fan of open room design ethos.")
	def LOOK(self, cmd, cmds, msg):
		if "flashlighton" not in States:
			say("You can't see anything. it's pitch black.")
		elif ("box", "wood", "toothpick") in msg and "toothpicks_obtained" not in States:
			say("""Upon closer inspection, you see the box contains a large quantity of long, julienned pieces of wood.
				They could be useful, and wouldn't weigh much anyways.""")
		elif "table" in msg:
			say("The tables look fancy, yet utilitarian, as if they were meant to represent upper class furnishings without actually having quality materials or craftsmanship.")  
		elif "floor" in msg:
			say("The floor's filthy, and covered in rubble. You're not sure why you even shined the light there.")
		elif "chair" in msg:
			say("The chairs are centered around the tables, 4 to each. They don't look comfortable.")
		elif ("cooler", "heater", "cutter", "fridge", "stove") in msg:
			say("""You're not really sure what to make of the appliances. They're in various states of decay, but you have plenty
			of bars in your jacket, so you won't need to rely on them for awhile yet. No sign of the Core.""")
		elif ("window", "rubble") in msg:
			say("There's a ton of rubble blocking the windows; you'd need explosives to move much of it.")
		elif ("computer", "laptop", "terminal") in msg and "laptop_cafe_obtained" not in States:
			say("""You walk over to the computer terminal. It doesn't quite look like the pictures you've seen of this era, the display is far
				too close to the input device to be comfortable. However, given that you don't see an electrical line into it, perhaps it was
				one of the early internally powered models: a portable version. You might be able to turn it on.""")
	def GET(self, cmd, cmds, msg):
		if "flashlighton" not in States:
			say("You can't see anything. it's pitch black.")
			return
		if ("box", "wood", "toothpick") in msg and "toothpicks_obtained" not in States:
			say("""You pick up the box of julienned wood; might be handy.""")
			Inventory["toothpicks"] = "A box of julienned wood."
			States["toothpicks_obtained"] = True
		elif ("computer", "laptop", "terminal") in msg and "laptop_cafe_obtained" not in States:
			if "laptop_cafe_powered" not in States:
				say("""The portable terminal would probably fit in your backpack, but it wouldn't be any use without power. You're quite thankful
					your Booker is more reliable, even if the thermoelectric makes it a little cool around the arm.
					Old tech required much more power.""")
	def USE(self, cmd, cmds, msg):
		if "flashlight" in msg:
			if "flashlight" in Inventory:
				if "flashlighton" in States:
					say("You turn off the flashlight, deciding that conserving battery power is likely more important than being able to do anything at all in the Cafe.")
					del States["flashlighton"]
				else:
					say("""You pull the old Lithium Ion flashlight out of your backpack and turn it on.
					The room becomes moderately illuminated, at least enough for a casual look around.
					It's no MF cell, so you should probably keep the idling to a minimum.""")
					States["flashlighton"] = True
			else:
				say("You charade out the actions involved in turning on your hand, but if anything, the room gets darker. You'll probably need an actual flashlight.")
		elif "flashlighton" not in States:
			say("You can't see anything. it's pitch black.")
		elif ("chair", "table") in msg:
			say("You really don't want to sit down in those chairs.")
		elif ("computer", "laptop", "terminal") in msg and "laptop_cafe_obtained" not in States:
			say("""Glancing over the input device, you recognize the familar power symbol, and try depressing it.
				A red light blinks on a few pulses, then disappears. Either the power symbol had a different etimology than you've been taught,
				or the unit's low on power. Not of much use then.""")
Cafe()

class Stairs(Room):
	def describe(self):
		say("""AREA INCOMPLETE, GRATS ON GETTING THIS FAR, TYPE 'back'!
		
		The first floor door leads to the Lobby.
		""")

	def GO(self, cmd, cmds, msg):
		if "lobby" in msg:
			setArea("lobby")
	def LOOK(self, cmd, cmds, msg):
		if "test2" in msg: pass
	def GET(self, cmd, cmds, msg):
		if ("backpack" not in States) and "pack" in msg:
			say("""You pick up the rugged leather backpack.
				As you slide it onto your shoulders, you hear the clink of metal hitting the linolium floor.""")
			States["keyfloor"] = True
			States["backpack"] = True
	def USE(self, cmd, cmds, msg):
		if len(cmds) > 3 and "stairkey" in Inventory and "key" in msg:
			say("Use the key on what?")
		elif len(cmds) > 1:
			say("Use "+cmds[1]+" on what?")  
Stairs()
