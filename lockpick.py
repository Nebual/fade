import random, sys

sys.path.append("..")
import consolelib

class Pick(object):
	def __init__(self, s):
		self.s = s
		rows = s.split("\n")
		self.width = len(max(rows, key=len))
		self.height = len(rows)

picks = [
"""\
====""",
"""\
==
==""",
"""\
=
===""",
"""\
==
 ==""",
"""\
 ==
==""",
"""\
 =
===""",
]
for i, s in enumerate(picks):
	picks[i] = Pick(s)

locks = [[
"""\
 =
====
==="""
],[
"""\
=  =
====
  ==""",
"""\
= =
===
  =
  =""",
"""\
==
===
====
  ===""",
],[
"""\
 ==
====
 = ==
 ===""",
"""\
 ===
=====
  =
====
===""",
]]
for diff, difftab in enumerate(locks):
	for i, lock in enumerate(difftab):
		difftab[i] = [" "]*25
		for y, line in enumerate(lock.split("\n")):
			for x, val in enumerate(line):
				difftab[i][y*5 + x] = val #(val=="=") and 1 or 0
		
helptext = """Help :
wasd : Move current pin
q e  : Change current pin
space: Weld current pin
enter: Attempt to unlock
z    : Start over
ctl-c: Give up
Pins Remaining: \
"""

def main(difficulty, pins):
	"""Engages the lockpicking minigame.
	
	returns 0 (player gave up with ctrl-c), False (fail), True (success)
	"""
	
	#Draw the lock (left hand side)
	lock = random.choice(locks[difficulty-1])
	slock = " Lock:\n"
	for y in range(-1, 6):
		for x in range(-1, 6):
			if x == -1 or y == -1 or x == 5 or y == 5:
				slock += "#" #borders
			else:
				slock += lock[y*5 + x] == "=" and "." or "#"
		slock += "\n"
	
	
	tkey = [" "]*25
	posx = posy = 0
	pick = 0
	press = ""
	while True:
		#Change selected tetronimo
		pick += (press == "q" and -1 or (press == "e" and 1) or 0)
		if pick < 0: pick = len(picks) - 1
		elif pick >= len(picks): pick = 0
		
		#Move the tetromino around
		posx += (press == "d" and 1 or (press == "a" and -1))
		posy += (press == "s" and 1 or (press == "w" and -1))
		while (posx + picks[pick].width) > 5: posx -= 1
		while (posy + picks[pick].height) > 5: posy -= 1
		if posx < 0: posx = 0
		if posy < 0: posy = 0
		
		#Save the current tetronimo + position with `space`
		if press == " ":
			if pins < 1:
				print "You don't have any pins remaining."
				return 0, pins
			for y, row in enumerate(picks[pick].s.split("\n")):
				for x, char in enumerate(row):
					tkey[(posy+y)*5 + (posx+x)] = char == "=" and "=" or " "
			pins -= 1
		#Clear the saved tetrominos with `z`
		elif press == "z":
			tkey = [" "]*25
		#Attempt to solve the lock
		elif press == "\r":
			result = lock == tkey
			if result: print("Your makeshift key manages to open the lock!")
			else: print("Your makeshift key isn't tripping all the tumblers; the door remains locked.")
			return result, pins
		
		#== DRAWING ==
		#=============
		current = [" "]*25
		#Draw the previous tetrominos
		for i, char in enumerate(tkey):
			if char != " ": current[i] = char
		
		#Draw the current tetromino
		for y, row in enumerate(picks[pick].s.split("\n")):
			for x, char in enumerate(row):
				if char != " ":
					current[(posy+y)*5 + (posx+x)] = consolelib.background(current[(posy+y)*5 + (posx+x)], "RED")
		
		#Convert the current board into a string
		skey = " Key:\n" + "#"*7 + "\n"
		for i in range(0,25,5): skey += "#" + "".join(current[i:i+5]) + "#\n"
		skey += "#"*7
		
		consolelib.clear()
		print """\
Using your Booker, you scan the internal layout of the tumblers, creating
a 3D model. You'll need to bend your flexium pins to the correct shape,
and then flashweld them to create a working key.\n"""
		print consolelib.screenSplit((slock, skey, helptext + str(pins)), width=10) + "\n"
		
		try: press = consolelib.getKey()
		except KeyboardInterrupt:
			print "You decide to give up on picking the lock for now."
			return 0, pins


if __name__ == "__main__":
	print main(1, 10)