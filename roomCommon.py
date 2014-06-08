import sys, time, random, inspect

import lockpick, consolelib

Areas = {}
States = {"area": "lobby"}
Inventory = {}


import re, textwrap
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

if sys.version_info >= (3,):
	def raw_input(s): return input(s)
else:
	raw_input = raw_input
	

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


GO = ("enter", "go", "goto")
LOOK = ("examine", "look", "view")
GET = ("pick", "grab", "get", "take", "pickup")
USE = ("use", "open", "turn")
LOCKPICK = ("lockpick",)

notFounds = (
	("You attempt to %s %s, but can't see how.","Despite how great it might be to %s %s, you don't see it.", "%s %s, you cannot."),
	("You look around feverently for this %s, but find nothing of the sort.","Your attempts to find anything interesting about %s have been entirely unfruitful.","Your %s viewing abilities are quite compromised.","As insightful as looking at %s may be, you don't see it.", "See %s, you cannot."),
	("You don't see what using %s would accomplish.","You failed in your attempt to use %s. Good job!", "Use %s, you cannot."),
	("You don't think you can %s %s.","%s %s, you cannot.", "You would seriously want to %s %s?"),
	("You're not sure what '%s' entails.", "You try your best to '%s', but nothing happens.", "You don't think you were ever trained to '%s'", "You're pretty sure someone once told you how to '%s', but it escapes you at the moment.", "You '%s', but its not very effective."),
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
	"""Changes the current room"""
	if newArea in Areas:
		if "area" in States: States["lastarea"] = States["area"]
		States["area"] = newArea
		if ("visited_" + newArea) in States:
			with consolelib.charByChar(0.0033):
				Areas[States["area"]].describe()
		else:
			States["visited_" + newArea] = True
			with consolelib.charByLine(0.0125):
				Areas[States["area"]].describe()

Maps = {
"hotel" : ((80, 32), {
	"visited_lobby" : ((20, 22), """\
=======||=======
[              ||
|              ]
[              ]
[     Main     ]
[     Lobby    ||
[              ]
/              ||
[              ]
=======||=======\
"""),
	"visited_washroom" : ((11, 22), """\
========
[      ]
[ Wash ||
[ room ]
[      ]
========\
"""),
	"visited_cafe" : ((37, 20), """\
=====================
[            =     =]
[            =       ]
|    Cafe            ]
[            =       ]
[            =     =]
=====================\
"""),
	"visited_supplies" : ((37, 28), """\
============
| Supplies ]
[ Closet   ]
============\
"""),
	"visited_stairs" : ((24, 5), """\
========
|      ]
[------]
[-     ]
[ -    ]
[Stairs]
[   -  ]
[    - ]
[     -||
[------]
[-     ]
[ -    ]
[  -   ]
[   -  ]
[    - ]
/     -]
===||===\
"""),
	"visited_floor2" : ((33, 11), """\
===||=====||=====//====
[                 ====]
|     Floor 2       ==]
[     Hallway     ====]
=======================\
"""),
	"visited_room201" : ((33, 7), """\
===//===
[ Room ]
[ 201  ]
[      ]\
"""),
	"visited_room202" : ((40, 7), """\
===  ===
[ Room ]
[ 202  ]
[      ]\
"""),
	"visited_room203" : ((47, 7), """\
===||===
[ Room ]
[ 203  ]
[      ]\
"""),
	"visited_floor2balcony" : ((33, 4), """\
======================
[      -Floor2-      ]
[      -Balcony      ]\
"""),
	"visited_floor3" : ((5, 5), """\
=============||===
[     ==  ====   ||
[ Floor3 = ==    ]
[ Hallway =      ]
==========//======\
"""),
	"visited_room301" : ((12, 1), """\
========
[ Room ]
[ 301  ]
[  X   ]\
"""),
	"visited_rooftop" : ((21, 0), """\
===========
[ Rooftop ]
[         ]
[  X      ]
===========\
""")
})}

def openMap(mapname):
	if mapname not in Maps:
		print("It doesn't seem to have enough data for the current area yet.")
		return
	(mapSizeX, mapSizeY), layouts = Maps[mapname]
	Map = [[" " for x in range(mapSizeX)] for y in range(mapSizeY)]
	for y, line in enumerate(Map):
		if y % 5 == 0 and y != 0:
			for x, char in enumerate(str(y)): line[x] = char
	for place in layouts:
		if place in States:
			(layoutX, layoutY), layout = layouts[place]
			for liney, line in enumerate(layout.split("\n")):
				for linex, char in enumerate(line):
					Map[liney + layoutY][linex + layoutX] = char
	print " " + "".join([x % 10 == 0 and str(x).ljust(10) or "" for x in range(mapSizeX)])
	for line in Map:
		print "".join(line)

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
		say("""This is the developer hax room. `go room` runs setArea(room). A hot tub steams in the corner.
		.
		`get itemname` runs Inventory[itemname] = 'Free item'. `use state' runs States[state] = True. `use state false` runs States[state] = False.""")

	def GO(self, cmd, cmds, msg):
		setArea(cmds[1])
	def LOOK(self, cmd, cmds, msg):
		if "test2" in msg: print("Test message")
		elif "test" in msg: say("""Test message""")
	def GET(self, cmd, cmds, msg):
		Inventory[cmds[1]] = cmds[1]+": You hacked this item in."
		say("Added '"+cmds[1]+"' to inventory.")
	def USE(self, cmd, cmds, msg):
		if ("false", "del") in msg:
			del States[cmds[1]]
			say("Deleted States['"+cmds[1]+"']")
		else:
			States[cmds[1]] = True
			say("Set States['"+cmds[1]+"'] to True")

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

def loadRoomModule(module):
	for name, cls in inspect.getmembers(module, inspect.isclass):
		if Room in cls.__bases__:
			#Create a new instance of each room, and throw it in Areas 
			Instance = cls()
			Instance.name = name.lower()
			Instance.zone = module.__name__.lower()
			Areas[Instance.name] = Instance
loadRoomModule(sys.modules[__name__])
