import os, sys, textwrap, re, time, random, inspect

import lockpick

GO = ("enter", "go", "goto")
LOOK = ("examine", "look")
GET = ("pick", "grab", "get", "take")
USE = ("use",)
LOCKPICK = ("lockpick",)

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

try: import winsound
except ImportError:
	import subprocess
	def playSound(filepath):
		subprocess.Popen(["paplay",filepath])
else:
	def playSound(filepath):
		winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

notFounds = (
	("You attempt to %s %s, but can't see how.","Despite how great it might be to %s %s, you don't see it.", "%s %s, you cannot."),
	("You look around feverently for this %s, but find nothing of the sort.","Your attempts to find %s have been entirely unfruitful.","Your %s viewing abilities are quite compromised.","As insightful as looking at %s may be, you don't see it.", "See %s, you cannot."),
	("You don't see what using %s would accomplish.","You failed in your attempt to use %s. Good job!", "Use %s, you cannot."),
	("You don't think you can %s %s.","%s %s, you cannot.", "You would seriously want to %s %s?"),
	("You're not sure what '%s' entails.", "You try your best to '%s', but nothing happens.", "You don't think you were ever trained to '%s'"),
)
def notFound(cmds):
	contents = "'" + (" ".join(cmds[1:])) + "'"
	if cmds[0] in GO:
		if len(cmds) == 1: say("As a 3 dimensional being, you can only go to places, you cannot just 'Go' in general.")
		else: 
			say(random.choice(notFounds[0]) % (cmds[0], contents))
	elif cmds[0] in LOOK:
		say(random.choice(notFounds[1]) % (contents))
	elif cmds[0] in USE:
		if len(cmds) == 1: say("You cannot use the room at large, only things physically inside it.")
		else: 
			say(random.choice(notFounds[2]) % (contents))
	elif cmds[0] in GET:
		if len(cmds) == 1: say("You just don't get 'it'. You'll have to settle for "+cmds[0]+"ing specific things.")
		else:
			say(random.choice(notFounds[3]) % (cmds[0], contents))
	elif cmds[0] in LOCKPICK:
		say("You use your Booker's scanner on %s, but there's too much interference; you can't get a 3D model." % (contents))
	else:
		say(random.choice(notFounds[4]) % (cmds[0]))

def getTime():
	T=States["time"]
	return "%d:%.2d%s" % (((T-60)%720)//60 + 1, T%60, (T%1440) > 720 and "PM" or "AM")
		
def setArea(newArea):
	"""Takes a string, and sets States["area"] to the corresponding Room object."""
	if newArea in Areas:
		if "area" in States: States["lastarea"] = States["area"].name
		States["area"] = Areas[newArea]
		States["area"].describe()

class Room(object):
	def describe(self): say(""" """)
	def GO(self, cmd, cmds, msg): pass
	def LOOK(self, cmd, cmds, msg): pass
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg): pass
	def LOCKPICK(self, cmd, cmds, msg): pass


class Test(Room):
	"""Test is a developer room, for experimenting with inventory, states, etc. It also is connected to every room."""
	def describe(self):
		say("""This is the developer hax room. `go room` runs setArea(room). `get itemname` runs Inventory[itemname] = 'Free item'. `use state' runs States[state] = True. `use state false` runs States[state] = False.""")

	def GO(self, cmd, cmds, msg):
		setArea(cmds[1])
	def LOOK(self, cmd, cmds, msg):
		if "test2" in msg: print("Test message")
		elif "test" in msg: say("""Test message""")
	def GET(self, cmd, cmds, msg):
		Inventory[cmds[1]] = cmds[1]+": You hacked this item in."
		say("Added '"+cmds[1]+"' to inventory.")
	def USE(self, cmd, cmds, msg):
		States[cmds[1]] = ("false" not in msg)
		say("Set States['"+cmds[1]+"'] to "+("false" not in msg and "True" or "False"))

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
	
class Lobby(Room):
	def describe(self):
		say("""You're in the lobby of a hotel; the room is lavishly decorated.
			.
			There's an old grandfather clock, its 3m cabinet towering over the rest of the room, still ticking away after all these years.""" + 
			("backpack" not in States and "You see a backpack lying against the wall near the entrance." or "") +
			("keyfloor" in States and "There's a metal key on the floor near the wall." or "") +
			".Besides the Entrance, there are doors marked 'Stairs', 'Washrooms', 'Cafe', 'Supplies', and 'Management'")
	def GO(self, cmd, cmds, msg):
		if "stair" in msg:
			if not "stairdoor" in States:
				say("The doorknob to the stairs refuses to turn. It is likely locked.")
			else:
				setArea("stairs")
		elif ("bathroom", "washroom") in msg:
			setArea("washroom")
		elif "cafe" in msg:
			setArea("cafe")
		elif "manage" in msg:
			if "managedoor" not in States:
				say("The Management door does not wish to be opened. It is likely locked.")
			else:
				setArea("management")
		elif "entrance" in msg:
			say("You can't leave the hotel, you don't have the Core yet.")
		elif "suppli" in msg:
			if "suppliesdoor" not in States:
				say("The Supplies door is closed, and you can't make it open. It is likely locked.")
			else:
				setArea("supplies")
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
			say("The lobby likely looked quite respectable in its time. It doesn't anymore." +
				("keyfloor" in States and "There's a metal key on the floor near the wall." or ""))
		elif ("clock", "grandf") in msg:
			say("""You study the old grandfather clock behind the receptionist's desk. The clockface is divided into twelve sections, each representing 1/24th of a day. A second arm further divides the time into 12ths of an hour, though you were fairly certain this era considered there to be 60 minutes to an hour. You synchronize your Booker's clock with your best interpretation of the current local time: """+getTime())
			States["watch"] = True
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
				elif "suppl" in resp:
					say("The keyhole for the Supplies door takes a different key.")
				elif "door" in resp:
					print("Which door?")
				else:
					say("Keys are generally used to open locked things. Not much else.")
			else:
				say("Use the key on what?")
	def LOCKPICK(self, cmd, cmds, msg):
		if "stair" in msg and "stairdoor" not in States:
			ret, States["pins"] = lockpick.main(1, States["pins"])
			if ret:
				States["stairdoor"] = True
		elif "suppl" in msg and "suppliesdoor" not in States:
			ret, States["pins"] = lockpick.main(3, States["pins"])
			if ret:
				States["suppliesdoor"] = True
			
	
class Washroom(Room):
	def describe(self):
		say("""You're in the first floor washrooms, Men's section.
			There is a row of water recepticles below a glass mirror, neither of which appear to be in functional condition.
			There is a wooden shelf, made of a low quality fibre that likely wasn't very attractive when it was new, either.
			A clipboard is on the wall near the door.
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
			say("Many of the sinks are most certainly not going to flow any time soon, but surprisingly, one on the end still produces a thin stream of polluted water. You wouldn't want to drink it.")
		elif "clipboard" in msg:
			say("The ink has faded to illegibility on the papers" + ("wr_paperclip" not in States and ", but the paperclips may be of use." or ""))
		elif "paperclip" and "wr_paperclip" not in States in msg:
			say("The paperclips could be quite handy as lockpicks.")
		elif "lobby" in msg: 
			say("The hotel lobby, main entrance room.")
		elif "floor" in msg:
			say("The floor is filthy, and that's all the time you want to spend looking at it.")
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
		elif "clip" in msg and "wr_paperclip" not in States:
			if "backpack" in States:
				States["wr_paperclip"] = True
				States["pins"] += 6
				say("You take the paperclips from the clipboard, and break them of them in half. You now have "+str(States["pins"])+" lockpicking pins.")
			else:
				say("You don't have anywhere to put the paperclips. What, you think they'd fit in your pockets or something?")
	def USE(self, cmd, cmds, msg):
		pass

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

class Management(Room):
	def describe(self): say("""You're in the lobby's Management office. Theres extraordinarily little described in this room. TODO
	.
	Behind you is the door to the lobby.""")
	def GO(self, cmd, cmds, msg): 
		if "lobby" in msg: setArea("lobby")
	def LOOK(self, cmd, cmds, msg): pass
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg): pass

class Supplies(Room):
	def describe(self): say("""You're in the lobby's supplies closet. There are shelves of clean towels, sheets, and headrest envelopes. There are several large electronic metal appliances of unknown purpose.
	.
	Behind you is the door to the lobby.""")
	def GO(self, cmd, cmds, msg):
		if "lobby" in msg: setArea("lobby")
	def LOOK(self, cmd, cmds, msg): pass
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg): pass
	def LOCKPICK(self, cmd, cmds, msg): pass

class Stairs(Room):
	def describe(self):
		say("""You're in the Hotel's central stairwell. Though the stairs look pretty rough, you should be okay provided you walk along the edge of the wooden steps.
		. """ + 
		("stairs_fish" not in States and "Halfway up the first flight is a remarkably well preserved small fish. " or "") +
		("stairs_mattress_cut" not in States and "A mattress is blocking the stairwell above the third floor. " or "A mattress has a hole cut through it, allowing passage past the third floor. ") + 
		"""The stairs have entirely broken down below the lobby, preventing access to the basement door.
		.
		The first floor door leads to the Lobby.
		The second""" + ("stairs_mattress_cut" not in States and " and third" or ", third, and fourth")+" floor doors appears to be unlocked. ")

	def GO(self, cmd, cmds, msg):
		if ("lobby", "first", "1") in msg:
			setArea("lobby")
		elif ("second", "2") in msg:
			setArea("floor2")
		elif ("third", "3") in msg:
			setArea("floor3")
	def LOOK(self, cmd, cmds, msg):
		if "fish" in msg and "stairs_fish" not in States: say("The fish appears to be dead. More relevently, it was never alive. You're unsure why anyone would make such a useless facsimile, perhaps it was once a children's toy. You consider that it wouldn't take up much space in your backpack, before shaking your head at the very thought.")
		elif "stair" in msg: say("The stairs look quite decrepit, and after a few steps, your feet agree.")
		elif "mattress" in msg: 
			say("There's a large monarch sized mattress blocking the way past the third floor.")
			print("""
    ___________
   /         /|
 /_________/ /
|_________|/\n""")
			say("It is firmly wedged in the stair railing; you won't be able to move it, though if you still had your plasma cutter you could easily cut a hole through it.")
	def GET(self, cmd, cmds, msg):
		if ("stairs_fish" not in States) and "fish" in msg:
			say("You pick up the fish, turn it over a few times, and drop it in your backpack. You're not sure what to make of yourself.")
			States["stairs_fish"] = True
			Inventory["redherring"] = "A true facsimile of a red herring. Likely a children's toy."
		elif "mattress" in msg:
			say("You start cramming the large mattress into your backpack, but nothing physically occurs.")
	def USE(self, cmd, cmds, msg):
		if "knife" in msg and "stairs_mattress_cut" not in States and "knife" in Inventory:
			say("You begin cutting a hole through the mattress.")
			playSound("sounds/mattress.wav")
			for x in range(3): print("..."); time.sleep(1)
			say("It's considerably slower work than you'd prefer, but before long there's enough of a hole for you to squeeze through to the other side. The knife is covered in mattress lint and won't be able to cut much.")
			raw_input("...")
			say("You clean off the knife. Good as new!")
			States["stairs_mattress_cut"] = True

class Floor2(Room):
	def describe(self):
		say("""Beneath you is an expensive looking rug; dusty, but relatively untouched by the years. You almost feel bad tracking dirt onto it. A small window illuminates the hall. The far end of the hallway is blocked by rubble, but you can reach the first three rooms.
		.
		An arrangement of dried out flowers used to decorate the area by the elevator door. In front of them is a trolley with a trash bin and used linens. 
		.
		The room doors read '201', '202', and '203', each with a matching keycard reader. Behind you is the stairwell door.
		""")

	def GO(self, cmd, cmds, msg):
		if ("stair") in msg:
			setArea("stairs")
		elif ("201") in msg:
			setArea("room201")
		elif ("202") in msg:
			setArea("room202")
	def LOOK(self, cmd, cmds, msg):
		if ("trash","bin") in msg: 
			say("""You dig through the trash bin thoroughly. The Core definitely isn't in here. 
			.
			You convince yourself that it was worth a try anyway.""")
		elif ("supplieskey_taken" not in States) and ("troll","linen","towel") in msg:
			say("""A bin on the front of the trolley holds some assorted janitorial tools and a key with a plastic grip reading 'Supplies'.
			.
			The pile of folded white towels are greyed with dust. You think them better undisturbed.
			""")
		elif ("supplieskey_taken" in States) and ("troll","linen","towel") in msg:
			say("""A bin on the front of the trolley holds some assorted janitorial tools.
			.
			The pile of folded white towels are greyed with dust. You think them better undisturbed.
			""")
		elif ("tools") in msg:
			say("You can't see any use for these tools right now.")
		elif ("supplieskey_taken" not in States) and ("key") in msg:
			print("The key has a yellow plastic grip that says 'Supplies'. It must be a janitor's key.")
		elif ("rug","floor") in msg:
			say("The huge floor rug is slightly faded with age. This cost someone a lot of money.")
		elif ("door") in msg:
			say("Which door?")
		elif ("201") in msg:
			say("It reads '201' in large gold letters. A crumpled shirt on the floor is holding the door slightly ajar.")
		elif ("202") in msg:
			say("The door is surprisingly unlocked.")
		elif ("203") in msg:
			say("You turn the handle to no avail. Locked.")
		elif ("elevator") in msg:
			say("You wouldn't trust the elevator even if it was powered.")
		elif ("shirt") in msg:
			say("The shirt is keeping room 201 open. Better not move it incase the door locks itself.")
		elif ("window") in msg:
			say("The window is quite small. There are probably more further along the hallway, blocked by the rubble.")
		elif ("flower") in msg:
			say("One touch and these flowers would crumble to dust.")
		elif ("stair") in msg:
			say("You stare down into the stairwell.")
		elif ("rubble") in msg:
			say("The rubble fills the hallway. Maybe if you had some Rubble-B-Gone.")
	def GET(self, cmd, cmds, msg):
		if ("rug","carpet") in msg:
			say("You begin rolling up the rug. After realizing there's no physical way you could take this with you, you lay it back on the floor.")
		elif ("supplieskey_taken" not in States) and ("key") in msg:
			say("You pocket the 'Supplies' key.")
			States["supplieskey_taken"] = True
			Inventory["supplieskey"] = "A key found on the second floor labled 'Supplies'."
		elif ("tool") in msg:
			say("You can't see any use for these tools right now.")
		elif ("troll") in msg:
			say("What would you even do with this?")
		elif ("linen","towel") in msg:
			say("As infinitely useful as towels are, you really don't want to raise the dust.")
		elif ("trash") in msg:
			say("You decide to leave the trash bin alone, else you'd be picking up debris for hours.")
		elif ("shirt") in msg:
			say("You decide to leave the shirt where it is to prevent the door from locking shut.")
		elif ("flower") in msg:
			say("The flowers are so dried, a stiff breeze might be enough to obliterate them. You decide against touching them.")
	def USE(self, cmd, cmds, msg):
		if ("troll") in msg:
			say("You drive the trolley around the room, accomplishing nothing. You park it back by the elevator door.")
		elif ("door") in msg:
			say("You use the doorknob, spinning it right and then left. You're quite impressed at the craftsmanship.")

class Room201(Room):
	def describe(self):
		say("""The curtains are pulled aside, flooding the room with light. The centerpiece of the small room is the unmade bed with an open luggage case on top. Some articles of clothing are strewn on the bed and around the floor. 
		.
		Beside the bed is a basic 1-drawer night stand. There isn't much else of particular interest in the room.
		.
		The door to the hallway is held ajar with a shirt.
		""")
	def GO(self, cmd, cmds, msg):
		if "hallway" in msg: setArea("floor2")
	def LOOK(self, cmd, cmds, msg):
		if ("drawer","stand") in msg:
			say("The one night stand in the room is empty. It feels like they were in the middle of either packing up or settling in. An old incandescent lamp sits on top aside an unpowered clock.")
		elif ("clock") in msg:
			say("The clock doesn't seem to be recieving power.")
		elif ("lamp","light") in msg:
			say("You fiddle with the lamp for a few moments before finding the awkward twist switch just below the bulb. A quick turn in either direction gives no result.")
		elif ("bed") in msg:
			say("The bedding is messy but looks comfortable enough. A small open suitcase sits on top with clothing and personal effects spilling from it.")
		elif ("luggage","suitcase") in msg:
			say("Clothing and personal effects are spilling from the luggage.")
		elif ("clothing") in msg:
			say("None of the clothing is particularly interesting to you.")
		elif ("magazines_taken" not in States) and ("effects") in msg:
			say("Specifically you spot a comb, a nutritional bar far beyond its best before date, and some dirty magazines.")
		elif ("magazines_taken" in States) and ("effects") in msg:
			say("A comb and an expired nutritional bar lay amongst the clothes. You dig around a bit in case you missed one of those magazines. You were trained to be thorough.")
		elif ("shirt") in msg:
			say("The shirt is keeping room 201 open. Better not move it incase the door locks itself.")
	def GET(self, cmd, cmds, msg):
		if ("lamp","light") in msg:
			say("You follow the lamp's cord to the wall and unplug it. However, all attempts to fit the lamp in your knapsack end in failure due to its massive, opulent lampshade.")
		elif ("luggage","suitcase") in msg:
			say("You consider taking the suitcase, but it's too full to close. How did they pack this in the first place?")
		elif ("magazines_taken" not in States) and ("magazine") in msg:
			say("Hanging onto these magazines seems like a great idea. You slip them into your knapsack for later.")
			States["magazines_taken"] = True
			Inventory["magazines"] = "Some naughty 'zines from someone's luggage."
		elif ("magazines_taken" not in States) and ("effects") in msg:
			print("You don't really want any of these things.\n\nWait, you might be able to find a use for these magazines. You stash them in \nyour backpack for later.")
			States["magazines_taken"] = True
			Inventory["magazines"] = "Some naughty 'zines from someone's luggage."
		elif ("magazines_taken" in States) and ("effects") in msg:
			say("You don't really want any of these things.")
		elif ("shirt") in msg:
			say("You leave the shirt where it is to prevent the door from locking shut.")
	def USE(self, cmd, cmds, msg):
		if ("lamp") in msg:
			say("You fiddle with the lamp for a few moments before finding the awkward twist switch just below the bulb. A quick turn in either direction gives no result.")

class Room202(Room):
	def describe(self):
		say("""The room is empty.
		.
		Like, particularly so.
		.
		There are stains covering every square centimeter of the faded wallpaper, and soot stains suggesting a fire was once burning in the middle of the room, but not a trace of any furnishings or decorations remain. Its as if all the damage that should've occured across the second floor was instead concentrated in obliterating this one room in particular.
		.
		Behind you is the hallway, and a large hole in the far wall leads to the balcony.
		""")
	def GO(self, cmd, cmds, msg):
		if "hallway" in msg: setArea("floor2")
		elif ("hole", "balc") in msg: setArea("floor2balcony")
	def LOOK(self, cmd, cmds, msg):
		if ("wallpaper", "stains", "soot", "fire"): say("This place is totally wrecked.")
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg): pass

class Floor2Balcony(Room):
	def describe(self):
		say("""You're standing on a balcony on the second floor of the Hotel.
		.
		The desolated landscape spreads out wide before you. The hotel stands at the top edge of a tall escarpment, a testiment to old world egotistical architects.
		""")
	def GO(self, cmd, cmds, msg):
		if ("hole", "202") in msg: setArea("room202")
	def LOOK(self, cmd, cmds, msg):
		if ("view"): self.describe()
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg): pass

for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
	if Room in cls.__bases__:
		#Create a new instance of each room, and throw it in Areas 
		Instance = cls()
		Instance.name = name.lower()
		Areas[Instance.name] = Instance
