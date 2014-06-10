__all__ = ["colorama", "colourize", "winchr", "clear", "UP", "DOWN", "RIGHT", "LEFT", "getKey"]
import sys, os, contextlib, time
from io import StringIO

try: 
	import colorama; colorama.init() #Allows console colours on Windows
except ImportError:
	def colourize(text, colour="GREEN"): pass
	def background(text, colour="GREEN"): pass
else:
	def colourize(text, colour="GREEN"):
		return colorama.Fore.__dict__[colour] + text + colorama.Fore.RESET
	def background(text, colour="GREEN"):
		return colorama.Back.__dict__[colour] + text + colorama.Back.RESET
def winchr(num):
	""" Takes a CP850 character int, and returns the unicode string
		Windows's Terminal's extended ASCII is quite nonstandard...
	"""
	if sys.platform != 'win32' and num < 32:
		if num == 1: return unichr(9786)
		elif num == 5: return unichr(9827)
	return unicode(chr(num), "CP850")

UP_ARROW = "\xe0H"
DOWN_ARROW = "\xe0P"
RIGHT_ARROW = "\xe0M"
LEFT_ARROW = "\xe0K"
UP = "w"
DOWN = "s"
RIGHT = "d"
LEFT = "a"

def clear():
	if WEB_MODE:
		print("\\clear")
	else:
		os.system(os.name == "nt" and "cls" or "clear")

try:
	import msvcrt
	#Okay the import succeeded, we're Windows
	def getch():
		ch = msvcrt.getch()
		if ord(ch) == 224:
			ch += msvcrt.getch()
		elif ord(ch) == 3:
			raise KeyboardInterrupt
		return ch
	
	def getKey(timeout=0):
		if timeout:
			endtime = timeout + time.time()
			while time.time() < endtime:
				if msvcrt.kbhit():
					return getch()
				else:
					time.sleep(0.01)
			return None
		else:
			return getch()
except ImportError: #Linux
	import sys, tty, termios, select
	
	def getch():
		ch = sys.stdin.read(1)
		if ch == chr(27):
			ch += sys.stdin.read(2) #For arrow keys
			if   ch[2] == "A": ch = UP
			elif ch[2] == "B": ch = DOWN
			elif ch[2] == "C": ch = RIGHT
			elif ch[2] == "D": ch = LEFT
		elif ch == chr(3):
			raise KeyboardInterrupt
		return ch
	
	def getKey(timeout=0):
		"""Gets a single character from standard input.  Does not echo to the screen."""
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			if timeout: 
				stdinReady,_,_ = select.select([sys.stdin],[],[],timeout)
				if stdinReady:
					ch = getch()
				else:
					ch = None
			else: ch = getch()
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

def ljust_noansi(s, width):
	"""Like str.ljust, but ignores the additional characters of ANSI colours"""
	length = len(s) - s.count("\033")*5
	return s + " "*(width - length)
def screenSplit(strings, width=0):
	"""Takes a tuple of strings (each may contain \n's) and a maximum width (for each column)
	returns a string formatted like a table
	eg. screenSplit(("Hey\nThere\nSir", "My\ntest\nstring", "Third\ncolumn"))
	Hey							My					Third
	There						test				Column
	Sir							string"""
	tabs = [s.split("\n") for s in strings]
	numrows = len(max(tabs, key=len))
	if not width: width = 79 // len(strings)
	ret = [""] * numrows
	for i in range(numrows):
		ret[i] = "".join([ljust_noansi(len(t) > i and t[i] or "", width) for t in tabs])
	return "\n".join(ret)


class mystdout(object):
	def __init__(self, suppress=False):
		self.file = StringIO()
		self.stdout = sys.stdout
		sys.stdout = self
		self.suppress = suppress
	def write(self, data):
		self.file.write(unicode(data))
		if not self.suppress: self.stdout.write(data)
	def close(self):
		s = self.file.getvalue()
		sys.stdout = self.stdout
		self.file.close()
		return s
	def flush(self):
		if not self.suppress: self.stdout.flush()

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

FAST_TEXT = False
def setTextSpeed(fast):
	global FAST_TEXT
	FAST_TEXT = fast

@contextlib.contextmanager
def charByChar(speed=0.0066):
	"""Creates a context that saves all prints to a string, suppressing them.
	When context is left, it prints the string char by char.
	with charByChar(speed=0.1): print("lol")
	"""
	if FAST_TEXT:
		yield
		return

	with listenPrints(suppress=True) as out:
		yield
	for char in out[0]:
		sys.stdout.write(char)
		sys.stdout.flush()
		time.sleep(speed)
@contextlib.contextmanager
def charByLine(speed=0.0066):
	"""Creates a context that saves all prints to a string, suppressing them.
	When context is left, it prints the string char by char, with a longer delay at line endings.
	"""
	if FAST_TEXT:
		yield
		return

	with listenPrints(suppress=True) as out:
		yield
	for i, char in enumerate(out[0]):
		sys.stdout.write(char)
		sys.stdout.flush()
		time.sleep(speed)
		if char == "\n" and out[0][i-1] in ("!",".","?") and i != len(out[0])-1: time.sleep(speed*50)
@contextlib.contextmanager
def lineByLine(speed=0.33):
	"""Creates a context that saves all prints to a string, suppressing them.
	When context is left, it prints the string line by line, with a delay between lines
	"""
	if FAST_TEXT:
		yield
		return

	with listenPrints(suppress=True) as out:
		yield
	for line in out[0].split("\n"):
		sys.stdout.write(line)
		sys.stdout.flush()
		time.sleep(speed)
