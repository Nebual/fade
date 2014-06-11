import sys, time, random
import lockpick, consolelib
from roomCommon import *

class US97(Room):
	def describe(self): say("""You're on a black stone riverway, which runs into the horizon in two directions. You're completely exposed out here, so you should hurry along.
	.
	Occasional metal wrecks lie dormant along the riverside.   
	There is a large barrel tower in one of the fields, sitting high atop 4 wooden posts. There is a collection of animals idling near it.
	.
	To the South is the Grand Luxury Hotel, and the town you saw from the hotel is to the North. There is a hydrocarbon shop near the fork in the river, with the Resolution resting behind it.""")
	def GO(self, cmd, cmds, msg):
		if ("hotel", "south") in msg: setArea("hotelground")
		elif ("town", "north") in msg:
			say("You're still carrying the heavy core, and you're nearing your time limit, so you don't think the town is a good idea just now.")
		elif ("hydro", "carbon", "gas", "station", "shop") in msg:
			setArea("station97")
	def LOOK(self, cmd, cmds, msg):
		if ("town", "north") in msg: say("Another deserted town, most likely. A sign by the riverside reads 'Wapato Welcomes You'")
		elif ("hydro", "carbon", "gas", "station", "shop") in msg: say("A small store targetting travellers, sitting atop the largest reservoir of hydrocarbons you've ever encountered. It's crazy how common the stuff used to be here, and it explains a lot of the culture. You parked the Resolution behind the shop for repairs.")
		elif ("barrel", "tower", "water") in msg: say("The wooden structure looks rather old, though there's a path leading to its base. Looking closer, you see an iron tube snaking down one of the posts. At the bottom there's a socket with a wheel on it.")
		elif ("animal") in msg: say("The animals are... quadrupedal, about 2m long, and have horns. They look fairly docile. This isn't your department; you're not an xenobiologist.")
		elif ("horizon") in msg: say("It's a horizon, a visual seam between land and sky.")
		elif ("metal", "wreck", "car", "machine") in msg: say("These were the machines the riverways were built for. A rather impractical design, with an inefficient motor, poor drivetrain, and an interior space barely large enough to sit in, let alone work on anything. The heavy steel frame leads to such a poor fuel to payload ratio, and doesn't even offer reasonable protection.")
		else: Areas["hotelground"].LOOK(cmd, cmds, msg)
	def GET(self, cmd, cmds, msg):
		if ("metal", "wreck", "car", "machine") in msg: self.USE(cmd, cmds, msg)
		elif ("water") in msg: say("How might you get the water out of the tower?")
	def USE(self, cmd, cmds, msg):
		if ("wheel") in msg:
			say("As you approach the tower, the animal herd drifts away. You attempt to twist the wheel, and a deluge of clean looking water pours out of the socket.")
			if "waterbottle" in Inventory and "waterbottle_full" not in States:
				say("You fill up your hydration bottle, in case you might need it later.")
				States["waterbottle_full"] = True
			else: say("You don't have anything to store water in, so you turn the wheel off.")
			say("The animals gradually return to the base of the tower after you leave.")
		elif ("water", "tower", "barrel", "socket") in msg: say("You're not quite certain how to utilize the tower.")
		elif ("metal", "wreck", "car", "machine") in msg: say("It would take you at least as long to get one of these machines up to working order as it would the Resolution, what'd be the point?")

class Station97(Room):
	def describe(self): say("""Hey, a station! Too bad it's [EOF]""")
	def GO(self, cmd, cmds, msg):
		pass
	def LOOK(self, cmd, cmds, msg):
		pass


loadRoomModule(sys.modules[__name__])
