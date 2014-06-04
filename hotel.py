import os, sys, time, random
import lockpick, consolelib
from roomCommon import say, Areas, States, Inventory, SearchableString, playSound, getTime, setArea, Room, loadRoomModule

	
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
				say("You open the freshly unlocked Management door. Or at least, you tried, but theres too much rubble on the other side to get past. At least you still have the key, maybe there'll be another office?")
		elif "entrance" in msg:
			say("You can't leave the hotel, you don't have the Core yet.")
		elif "suppli" in msg:
			if "suppliesdoor" not in States:
				say("The Supplies door is closed, and you can't seem to make it open. It is likely locked.")
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
		if ("backpack" not in States) and "ack" in msg:
			say("""You pick up the rugged leather backpack.
				As you slide it onto your shoulders, you hear the clink of metal hitting the linolium floor.""")
			States["keyfloor"] = True
			States["backpack"] = True
		elif "keyfloor" in States and "key" in msg:
			say("You pick up the key. It has an 'S' scratched on it.")
			del States["keyfloor"]
			Inventory["stairkey"] = "A worn key. There is an 'S' scratched on it."
	def USE(self, cmd, cmds, msg):
		if "key" in msg:
			if len(cmds) > 3:
				resp = cmds[3]
				if "stair" in resp:
					if "stairkey" in Inventory:
						say("""You put the 'S' key into the Stairwell Door.""")
						raw_input("...")
						say("""For awhile, nothing happens. Then suddenly, you realize the architecture of the building precludes 
							automatic doors, and that you'll likely have to turn the key manually to get anywhere with it.""")
						raw_input("...")
						say("""With a turn, the lock clicks open, though the key doesn't want to be removed without locking the door again.""")
						States["stairdoor"] = True
						del Inventory["stairkey"]
					else: say("You don't seem to have a key that matches the stairs door.")
				elif "cafe" in resp:
					say("The cafe door has no lock.")
					if not "flashlight" in Inventory:
						say("it's just creepy in there without a light.")
				elif "washroom" in resp:
					say("The washroom door is already proped open.")
				elif "manage" in resp:
					if "managementkey" in Inventory:
						say("You carefully insert the large key into the lock, and to your delight, it unlocks!")
						States["managedoor"] = True
					else: say("The keyhole for the Management door takes a very large key.")
				elif "suppl" in resp:
					if "suppliesdoorkey" in Inventory:
						say("You unlock the door labeled Supplies. Progress!")
						States["suppliesdoor"] = True
						del Inventory["suppliesdoorkey"]
					else: say("The keyhole for the Supplies door takes a different key.")
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
				Inventory["flashlight"] = "An old portable electronic light, with a Lithium Ion power source."
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
				It's pitch black inside, since the power cut out long ago and the walls are, shockingly, not punctuated by
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
				The far wall once had huge windows, but rubble now entirely covers them.
				A jacket is half buried in the debris. """ + 
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
			say("You can't see anything; it's pitch black.")
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
		elif "jacket" in msg:
			if "cafe_key_pickup" not in States: say("A nice jacket. Though you don't think you can remove it from the debris, a quick rummage in the pockets reveals a small key.")
			else: say("The jacket looks dejected, and is stuck in the debris.")
		elif "key" in msg and "cafe_key_pickup" not in States:
			say("""The jacket's key has "SUPLISE" carved into the metal.""")
		elif ("window", "rubble") in msg:
			say("There's a ton of rubble blocking the windows; you'd need explosives to move much of it.")
		elif ("computer", "laptop", "terminal") in msg and "laptop_cafe_obtained" not in States:
			say("""You walk over to the computer terminal. It doesn't quite look like the pictures you've seen of this era, the display is far
				too close to the input device to be comfortable. However, given that you don't see an electrical line into it, perhaps it was
				one of the early internally powered models: a portable version. You might be able to turn it on.""")
	def GET(self, cmd, cmds, msg):
		if "flashlighton" not in States:
			say("You can't see anything; it's pitch black.")
			return
		if ("box", "wood", "toothpick") in msg and "toothpicks_obtained" not in States:
			say("""You pick up the box of julienned wood; might be handy.""")
			Inventory["toothpicks"] = "A box of julienned wood."
			States["toothpicks_obtained"] = True
		elif "key" in msg and "cafe_key_pickup" not in States:
			say("""You take the "SUPLISE" key from the jacket.""")
			Inventory["suppliesdoorkey"] = """A key found in the Cafe, it has "SUPLISE" carved into it."""
			States["cafe_key_pickup"] = True
		elif ("computer", "laptop", "terminal") in msg:
			if "laptop_cafe_powered" not in States:
				say("""The portable terminal would probably fit in your backpack, but it wouldn't be any use without power. You're quite thankful
					your Booker is more reliable, even if the thermoelectric makes it a little cool around the arm.
					Old tech required much more power.""")
			else: say("""You're unsure what use the heavy terminal would be to you at this point, as the interface seems to be stuck.""")
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
			say("You can't see anything; it's pitch black.")
		elif ("chair", "table") in msg:
			say("You really don't want to sit down in those chairs.")
		elif ("charge", "black", "cable") in msg and "charger" in Inventory:
			if ("computer", "laptop", "terminal") in msg:
				States["laptop_cafe_powered"] = True
				self.USE("","",SearchableString("computer"))
			else: say("Use the cable with what?")
		elif ("computer", "laptop", "terminal") in msg:
			if "laptop_cafe_powered" not in States:
				say("""Glancing over the input device, you recognize the familar power symbol, and try depressing it.
				A red light blinks on a few pulses, then disappears. Either the power symbol had a different etimology than you've been taught,
				or the unit's low on power. Not of much use then.""")
			else:
				say("""The Core can wait. One of the 5 tips of the cable seems to fit into the portable terminal, and when you plug the other end into a socket on the side of the table, the device lights up. A picture of a wheel spins in the center of the display for a few moments, followed by an interface you're actually familiar with. """)
				raw_input("...")
				print("""\
========================================================================
===/      Gmail /=======================================================
==                                                                    ==
= <     Place is Heating Up                                            =
=  From: wclark@marylandwaterworks.com           Oct 11th 2014         =
=---------------------------------------------                         =
=     Okay so you know we got that government contract to redo an      =
= office's sinks? Turns out it was actually the Whitehouse itself, and =
= people are really freaking out around here today. Something about    =
= a navy ship, possibly a submarine, being seized by extremists. I'd   =
= have thought that'd be standard fare for this place, but they've     =
= sent home quite a few of the non-essential staff early, and that     =
= can't be a good sign. My train doesn't leave for another few hours,  =
= so I figured I'd keep working, but the atmosphere was too weird for  =
= me to not send it your way, so let me know if you can find anything  =
= about it in the usual places. I can't imagine what they'd have on    =
= the boat that would threaten us here, I mean we have jets that can   =
= stop nuclear missiles, right? What could be worse than that?         =
=                                        ------------------------------=
==                                       - Reply -   - Fwd-           ==
========================================================================""")
				raw_input("...")
				say("""Amazing! An email from before the Collapse! After copying the contents into your Booker for perpetuity, you hit the keyboard's Back button to return to the list of emails.""")
				raw_input("...")
				say("""Nothing changes. The computer seems to have frozen. A shame, but you don't have time to try fixing it this trip.
				.
				The power cable could be useful for other things, so you take it with you.""")


class Supplies(Room):
	def describe(self): say("""You're in the lobby's supplies closet. There are shelves of clean towels, sheets, and headrest envelopes. There are several large electronic metal appliances of unknown purpose. """
	+ ("managementkey" not in Inventory and "There's a key hanging by the door." or "") + """
	There is a dish containing some small metal discs, """ + ("suppliesroom_lockpicks" in States and ", " or "several paperclips, ") + """small pieces of polymer, """ + ("suppliesroom_money" in States and ", " or """a paper with "5 IN GOD WE TRUST 5" written on it, """) + """and some metal screws.
	Sunk into the wall is a mahogany cupboard labeled 'LOST TREBLECLEF FOUND'; it looks like it might be locked. 
	.
	Behind you is the door to the lobby.""")
	def GO(self, cmd, cmds, msg):
		if "lobby" in msg: setArea("lobby")
	def LOOK(self, cmd, cmds, msg):
		if ("large", "metal", "applia") in msg: say("You find many of the metal boxes are filled with clothing, left behind by their original owners. You do not find the Core in any of them.")
		elif "key" in msg and "managementkey" not in Inventory: say("""Theres a large key hanging from a post. It has a tag on it reading "Mngnt".""")
		elif ("screw", "poly", "disc") in msg: say("Just some junk, probably.")
		elif ("paper", "5", "god", "money") in msg and "suppliesroom_money" not in States:
			say("If your memory serves you correctly, these papers were used to anonymously transfer credits, as part of business.")
		elif ("lockpi", "clip") in msg and "suppliesroom_lockpicks" not in States:
			say("Hey sweet some paperclips! More lockpicks means less hunting down keys.")
		elif "treble" in msg: say("This is a really badly drawn trebleclef.")
		elif ("mahog", "cupbo", "lost", "found") in msg:
			if "supplyLAFcupboardunlocked" in States:
				say("On a shelf inside the cupboard is a small pair of children's shoes" + ("supplyLAFbottletaken" not in States and " and a hydration bottle." or ".") + ("supplyLAFchargertaken" not in States and "There is a length of black cable with metal pins on both ends." or ""))
			else: say("Its a nice cabinet, but its locked.")
		elif ("black", "cable", "plug") in msg and "supplyLAFcupboardunlocked" in States:
			say("One end of the cable has a plug with 3 metal pins, the other end splits into 5 smaller wires, each with a differently shaped single metal pin. Versatile?")
		elif ("shoe") in msg: say("How the parents didn't notice the missing shoes is beyond you.")
		elif ("hydra", "water", "bottle") in msg and "supplyLAFcupboardunlocked" in States: say("The bottle looks like it'd hold about 1000 cubic cm, and since you lost your hydrater when that school collapsed, it'd probably be a good thing to take along.")
	def GET(self, cmd, cmds, msg):
		if "key" in msg and "managementkey" not in Inventory:
			say("""You pickup the "Mngnt" key and toss it haphazardly into your backpack.""")
			Inventory["managementkey"] = """A large key with a tag reading "Mngnt" """
		elif ("paper", "5", "god", "money") in msg and "suppliesroom_money" not in States:
			say("You pickup the 5 credits bill. Or 5 dollars, you should say.")
			States["money"] += 5
			States["suppliesroom_money"] = True
		elif ("lockpi", "clip") in msg and "suppliesroom_lockpicks" not in States:
			say("You snap the 3 paperclips in half, and somehow end up with 5 more lockpicks!")
			States["pins"] += 5
			States["suppliesroom_lockpicks"] = True
		elif ("shoe") in msg: say("The shoes are, by a large margin, too small for your feet.")
		elif ("hydra", "water", "bottle") in msg and "supplyLAFcupboardunlocked" in States and "supplyLAFbottletaken" not in States:
			States["supplyLAFbottletaken"] = True
			Inventory["waterbottle"] = "A 1000 cubic cm hydration bottle, full of water."
			say("You pickup the bottle, and place it in your backpack.")
		elif ("black", "cable", "plug") in msg and "supplyLAFcupboardunlocked" in States and "supplyLAFchargertaken" not in States:
			States["supplyLAFchargertaken"] = True
			Inventory["charger"] = "A power cable with 5 tips."
			say("You pickup the cable, and place it in your backpack.")
	def USE(self, cmd, cmds, msg):
		if "key" in msg:
			if len(cmds) > 3:
				if ("mahog", "cupbo", "lost", "found") in msg and "supplyLAFcupboardunlocked" not in States and "managementkey" in Inventory:
					States["supplyLAFcupboardunlocked"] = True
					say("Using the key that you found an arms length away, you unlock the cupboard.")
				else:
					say("Keys are generally used to open locked things. Not much else.")
			else:
				say("Use the key on what?")
	def LOCKPICK(self, cmd, cmds, msg): pass

class Stairs(Room):
	def describe(self):
		say("""You're in the Hotel's central stairwell. Though the stairs look pretty rough, you should be okay provided you walk along the edge of the wooden steps.
		. """ + 
		("stairs_fish" not in States and "Halfway up the first flight is a remarkably well preserved small fish. " or "") +
		("stairs_mattress_cut" not in States and "A mattress is blocking the stairwell above the second floor. " or "A mattress has a hole cut through it, allowing passage past the second floor. ") + 
		"""The stairs have entirely broken down below the lobby, preventing access to the basement door.
		.
		The first floor door leads to the Lobby.
		The second""" + ("stairs_mattress_cut" not in States and " floor door appears" or " and third floor doors appear")+" to be unlocked.")

	def GO(self, cmd, cmds, msg):
		if ("lobby", "first", "1") in msg:
			setArea("lobby")
		elif ("second", "2") in msg:
			setArea("floor2")
		elif ("third", "3") in msg:
			if "stairs_mattress_cut" in States:
				del States["flashlighton"]
				setArea("floor3")
			else: say("There remains a large mattress between you and the third floor door.")
	def LOOK(self, cmd, cmds, msg):
		if "fish" in msg and "stairs_fish" not in States: say("The fish appears to be dead. More relevently, it was never alive. You're unsure why anyone would make such a useless facsimile, perhaps it was once a children's toy. You consider that it wouldn't take up much space in your backpack, before shaking your head at the very thought.")
		elif "stair" in msg: say("The stairs look quite decrepit, and after a few steps, your feet agree.")
		elif "mattress" in msg: 
			say("There's a large monarch sized mattress blocking the way past the second floor.")
			print("""
    ___________
   /         /|
 /_________/ /
|_________|/\n""")
			say("It is firmly wedged in the stair railing; you won't be able to move it, though if you still had your plasma cutter you could easily cut a hole through it.")
		elif ("basement", "below") in msg: say("You could go down there, but you wouldn't be able to get back up. On the plus side, its pretty unlikely the Core is down there.")
	def GET(self, cmd, cmds, msg):
		if ("stairs_fish" not in States) and "fish" in msg:
			say("You pick up the fish, turn it over a few times, and drop it in your backpack. You're not sure what to make of yourself.")
			States["stairs_fish"] = True
			Inventory["redherring"] = "A true facsimile of a red herring. Likely a children's toy."
		elif "mattress" in msg:
			say("You start cramming the large mattress into your backpack, but nothing physically occurs.")
	def USE(self, cmd, cmds, msg):
		if ("red", "blade", "knife") in msg and "stairs_mattress_cut" not in States and "redblade" in Inventory:
			say("You begin cutting a hole through the mattress.")
			playSound("sounds/mattress.wav")
			for x in range(3): print("..."); time.sleep(1)
			say("It's considerably slower work than you'd prefer, but before long there's enough of a hole for you to squeeze through to the other side. The knife is covered in mattress lint and won't be able to cut much.")
			raw_input("...")
			say("You clean off the knife. Good as new!")
			Inventory["redblade"] += " There are traces of lint stuck to it."
			States["stairs_mattress_cut"] = True

class Floor2(Room):
	def describe(self):
		say("""Beneath you is an expensive looking rug; dusty, but relatively untouched by the years. You almost feel bad tracking dirt onto it. A small window illuminates the hall. The far end of the hallway is blocked by rubble, but you can reach the first three rooms.
		.
		An arrangement of dried out flowers used to decorate the area by the elevator door; in front of them is a trolley with a trash bin and used linens. 
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
		elif ("203") in msg:
			say("The door to Room203 won't open. Tsk tsk.")
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
	def LOCKPICK(self, cmd, cmds, msg):
		say("""The rooms all use a keycard reader; you can't lockpick that.""")

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
			say("Clothing and personal effects are spilling from the luggage. It's not like there's going to be a portable power generator just sitting in a suitcase.")
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
	def GET(self, cmd, cmds, msg):
		if "soot" in msg: say("You're not going to pick up soot. It is, by definition, devoid of energy.")
	def USE(self, cmd, cmds, msg): pass

class Floor2Balcony(Room):
	def describe(self):
		say("""You're standing on a balcony on the second floor of the Hotel.
		.
		The desolated landscape spreads out wide before you. The hotel stands at the top edge of a tall escarpment, a testiment to old world egotistical architects. Theres the ruins of a small town 1km North of you, but the buildings are in considerably worse condition than the Hotel, and besides, the Core isn't there.
		.
		If you climb across the balconies, you can reach the door to Room203, and the hole to Room202.
		""")
	def GO(self, cmd, cmds, msg):
		if ("hole", "202") in msg: setArea("room202")
		elif ("door", "203") in msg:
			if "room203_balconyunlocked" in States: setArea("room203")
			else: say("The door to Room203 is most certainly, without a doubt, probably locked. Or stuck. You're leaning towards locked.")
	def LOOK(self, cmd, cmds, msg):
		if ("view") in msg: say("The view is bleak.")
		elif "hotel" in msg: say("You turn away from the interesting view to look at the boring side of the building. Theres at least one floor above you, judging by the next balcony up, but beyond that nothing stands out. Doesn't mean the Core isn't up there though.")
		elif "town" in msg: say("You spy a large sign by the road leading into the town. Squinting through the dust clouds, you read 'Wapato Welcomes You!'")
		elif "balcon" in msg: say("The balcony of Room203")
		elif ("hole","202") in msg: say("The hole leads to the barren wasteland that is Room202. Its almost nicer than the barren wasteland that is outside.")
		elif ("door","203") in msg:
			if "room203_balconyunlocked" in States: say("You see the unlocked door to Room203")
			else: say("You see a fairly simple lock on the door to Room203. You could probably pick the lock, but theres probably a key downstairs for it.")
	def GET(self, cmd, cmds, msg): pass
	def USE(self, cmd, cmds, msg):
		if ("key", "manag") in msg and "managementkey" in Inventory and "room203_balconyunlocked" not in States:
			say("Using the Mgmnt key, you unlock the balcony door to Room203.")
			States["room203_balconyunlocked"] = True
	def LOCKPICK(self, cmd, cmds, msg):
		if ("door", "203") and "room203_balconyunlocked" not in States: 
			ret, States["pins"] = lockpick.main(2, States["pins"])
			if ret: States["room203_balconyunlocked"] = True

class Room203(Room):
	def describe(self):
		say("""You're in the room of a guest who was, you're hoping, a kitchen knife salesman.
		.
		There is an open crate with a sticker stating 'Sell By 03/2014' by what used to be the bed.
		A black glass cube sits on a table at the foot of the bed, alongside a leather case with a padlock sealing it.
		A box labeled 'Pro Lockpicks' sits open by the door.
		.
		There is a door leading to the balcony, and the hallway door.
		""")
	def GO(self, cmd, cmds, msg):
		if "hall" in msg: say("The lock on the door to the hallway is smashed beyond use, and unlike in the tapes, this means the door is actually unopenable.")
		elif ("balcon") in msg: setArea("floor2balcony")
	def LOOK(self, cmd, cmds, msg):
		if ("black", "glass", "cube") in msg: say("The cube is actually a composite, mostly synthetic polymers, with a plate of curved glass on one side. There is an array of buttons and knobs, one of which you recognize as the power switch.")
		elif "crate" in msg: say("""You peer into the crate.
		Its filled with individually packaged kitchen knives, there must be at least a hundred.""")
		elif ("box", "lockp") in msg: say("""A box of lockpicks! That sounds really useful!""")
		elif ("leather", "case", "padlock") in msg: say("""A deluxe looking small case, labeled "Display Model". There is a padlock on the zipper.""")
	def GET(self, cmd, cmds, msg):
		if ("kniv", "knife", "crate") in msg: say("""You pick up one of the knives from the crate, but as you turn it over to inspect it, the metal crumbles into a myriad of pieces.
		Terrible craftsmanship!
		The handle says, "Packaged On Made In Mexic".""")
		if ("box", "lockp") in msg:
			if "crochetagebook" not in States:
				say("""You pickup the box of lockpicks, but its nearly empty. All that remains is a small paper booklet titled "Crochetage pour des Idiots".""")
				Inventory["crochetagebook"] = "A book on the art of Crochetage."
				States["crochetagebook"] = True
			else: say("You pickup the box of lockpicks, but its empty.")
		if ("red", "blade") in msg and "bladecaseopen" in States and "redblade" not in Inventory:
			say("""You pickup the red blade from the case, and place it in your pack's sleeve.""")
			Inventory["redblade"] = "A red blade with a nice handle. Still sharp."
	def USE(self, cmd, cmds, msg):
		if ("black", "glass", "cube", "power", "switch") in msg: say("""You flick the power switch on the cube, and hear a small pop, followed by an unpleasent buzz.
		The glass plate appears to house a display, which is gradually fading into visible brightness. A complicated binary signal is displayed, as an oscilating array of black and white buzzing squares. You watch it for awhile, but are unable to discern anything useful.
		The buzz is quite obnoxious, and might attract problems, so you switch the cube off. Not like you had anything to parse the signal with anyway.""")
		if ("leather", "case", "padlock") in msg:
			say("""You fumble with the padlock, and realize the owner must've forgotten to actually close the lock!"""
			+ ("redblade" not in Inventory and "Inside the case is a red handled blade styled similarly to the ones in the crate, but of noticably higher quality." or ""))
			States["bladecaseopen"] = True
		if "blade" in msg and "redblade" in Inventory: say("""You swing the red blade around. It has a nice grip to it, though it seems like an awfully manual way to cut food.""")

class Floor3(Room):
	def describe(self):
		if "flashlighton" not in States: say("""You're in a dark hallway.
			You're pretty sure the stairs door is still behind you.""")
		else:
			say("""You're in a hallway that ends abruptly. Where you expected to see numerous dark and potentially loot filled guest rooms instead lies a large chunk of the ceiling.
			.
			Besides the stairs, the only door accessible is Room301. There is also """ + ("3f_manage_unlocked" in States and "an unlocked " or "a locked ") + "inaccessible door marked 'SYAFF'.")
	def GO(self, cmd, cmds, msg):
		if "flashlighton" not in States: say("You can't see anything, but feel your way to the door.")
		if "stair" in msg:
			setArea("stairs")
		elif ("staff", "syaff") in msg:
			if "3f_manage_unlocked" in States: say("It may be unlocked, but you still can't reach it.")
			else: say("You cannot reach that door, and besides, its locked anyway.")
		elif ("room", "301") in msg:
			setArea("room301")
	def LOOK(self, cmd, cmds, msg):
		if "flashlighton" not in States: say("You can't see anything; it's pitch black.")
		elif ("staff", "syaff", "accessibl") in msg: say("You peer closer at the lettering on the door, and conclude that it probably says 'Staff', but maintain that T's should not be that heavily stylized.")
		elif ("room", "301") in msg: say("A thin veneer of cedar glued over a cheap mesh of wood and glue; all that seperates a room's occupants from the outside world. Also it isn't locked.")
		elif ("debris", "ceiling", "chunk"): say("The building must've taken a heavy hit just above you, judging from this mess.")
	def GET(self, cmd, cmds, msg):
		if ("debris", "ceiling", "chunk") in msg: say("You can't pick up the ceiling; what.")
	def USE(self, cmd, cmds, msg):
		if "light" in msg:
			if "flashlight" in Inventory:
				if "flashlighton" in States:
					say("You turn off the flashlight, deciding that conserving battery power is likely more important than being able to do anything at all.")
					del States["flashlighton"]
				else:
					say("""You pull the old Lithium Ion flashlight out of your backpack and turn it on. The hall becomes well illuminated.""")
					States["flashlighton"] = True
			else:
				say("You charade out the actions involved in turning on your hand, but if anything, the room gets darker. You'll probably need an actual flashlight.")
		elif "flashlighton" not in States:
			say("You can't see anything; it's pitch black.")
		elif "key" in msg and "managementkey" in Inventory and ("staff", "syaff", "door") in msg:
			say("Reaching around the debris from the ceiling, you unlock the 'SYAFF' door using the Mgmnt key.")
			States["3f_manage_unlocked"] = True

class Room301(Room):
	def describe(self):
		say("""This room appears to have suffered similar damage to the hallway. A large metal support beam has fallen through from above, exposing a bright hole to the roof. There's a clipboard amongst the debris.
		.
		Behind you is the hallway door.""")
	def GO(self, cmd, cmds, msg):
		if ("hall", "door") in msg:
			if "core_obtained" not in States: setArea("floor3")
			else: say("The door won't budge; the crater's collapse must have blocked it.")
		elif ("hole", "beam", "roof", "metal") in msg: setArea("rooftop")
	def LOOK(self, cmd, cmds, msg):
		if ("hole", "roof") in msg: say("The hole means this room is effectively exposed to the outside air, so you shouldn't stay here long.") 
		elif ("beam", "metal") in msg: say("A sturdy metal girder, with associated roof debris still attached. You can probably climb up it to the roof.")
		elif ("clip") in msg: say("Where there's a clipboard, there's paperclips! Or sometimes a metal clasp. But in this case paperclips!") 
	def GET(self, cmd, cmds, msg):
		if ("clip", "pick") in msg and "room301_clips" not in States:
			say("Exposure to outside air or not, you pause to pickup the paperclips, snapping them to yield 6 lockpicks.")
			States["pins"] += 6
			States["room301_clips"] = True
	def USE(self, cmd, cmds, msg): pass

class Rooftop(Room):
	def describe(self):
		if "core_obtained" not in States:
			say("""You're on the rooftop of the hotel. The cause of the damage on the lower floors is clear: the building was hit, and with enough velocity to collapse the cafe and leave a crater on the roof. You see the remains of the communications tower, obviously hit during the impact, whose central column provided your ramp up. Though the town's remains sparkle in the distance, the biting wind reminds you of the urgency of your work. The less time spent up here, the better.
			.
			The crater draws your attention.
			.
			The hole to Room301 is behind you.""")
		else: say("""The rooftop of the hotel has collapsed further, and theres a widening crater in the center where the Core hit. You don't think you'll be able to get back down through the hotel, so there must be another way.
		.
		There's a north, east, south, and west edge to consider, but you don't have a lot of time, both structurally and respiratorily, you may just need to jump.""")
	def GO(self, cmd, cmds, msg):
		if ("hole", "room", "301") in msg: setArea("room301")
		elif "ladder" in msg: setArea("hotelground")
		elif ("jump", "bush") in msg:
			raw_input("Alright, you're going to jump...")
			raw_input("You take a deep breath, and run towards the south edge...")
			say("And chicken out; what if the core gets damaged?")
	def LOOK(self, cmd, cmds, msg):
		if ("core") in msg: say("Finally, the core! Now you can finally get the Resolution back up to speed.")
		elif ("commun", "tower") in msg: say("Pretty pathetic tech, considering the radiation leakage and high power consumption, but it revolutionized the culture of the time.")
		elif ("town") in msg: say("Though the town is enticing, you find it hard to concentrate through gasping for breaths.")
		elif ("wind", "air") in msg: say("Dusty, radioactively decaying debris fills the air.") 
		if "core_obtained" not in States:
			if ("crater") in msg: say("You lean over the hole left by the speeding projectile, and are so used to disappointment that you almost don't notice that you've finally found it. It cost you weeks of exposure, but you've been timing your trips, so it should work out. Now just to grab it and get out of here. The thing weighs a fair bit, and probably won't fit in your pack, so you'll need to hold onto it.")
			elif ("it") in msg: say("There's a lot of it's in the world, you're going to need to be more specific.")
			elif ("thing") in msg: say("Sure its a thing, but what type of thing is it?")
		else:
			if ("crater") in msg: say("The crater is getting wider; this building is likely no longer up to the fire code.")
			elif "north" in msg: say("The north face leans over the escarpment, not a nice height. The second floor balconys would be hard to reach from here, and might not even support your fall.")
			elif "east" in msg: say("The east face overlooks the hotel's exercise basin, but the water has long since drained. Not looking good.")
			elif "south" in msg: say("To the south is the front entrance's parking lot. There is a large bush that might break your fall to some degree were you to jump, and that might be your only option.")
			elif "west" in msg: say("The west side has several balconys, but theres no telling which of them are blocked. There's also a maintenance ladder that extends most of the way down. Cool!")
			elif "ladder" in msg: say("The ladder goes to 2m off the ground, seems ideal.")
	def GET(self, cmd, cmds, msg):
		if "core_obtained" not in States:
			if ("it") in msg: say("There's a lot of it's in the world, you're going to need to be more specific.")
			elif ("project") in msg: say("Its not a projectile anymore, that was just a temporary state brought on by the rapid unplanned disassembly earlier.")
			elif ("thing") in msg: say("Sure its a thing, but what type of thing is it?")
			elif ("core") in msg:
				say("You get down on your stomach, and reach into the crater. You manage to grab the installation handle, and with a firm yank, it breaks loose. With a loud grind, the crater collapses further, and you just barely back out as the ledge falls apart.")
				States["core_obtained"] = True
		else: say("There's nothing to get up here, besides respiratory problems.")
	def USE(self, cmd, cmds, msg):
		if "ladder" in msg: self.GO("","",SearchableString("ladder"))
		elif "jump" in msg: self.GO("","",SearchableString("jump"))

class HotelGround(Room):
	def describe(self): say("You're outside the Grand Luxury Hotel. With the Core in hand, you're ready to restore the Resolution and hopefully get out of this red zone. [EOF]")

loadRoomModule(sys.modules[__name__])
