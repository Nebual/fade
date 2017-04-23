import time, sys, random

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol # pip install twisted autobahn pypiwin32
from twisted.internet import protocol
from twisted.python import log


class FadeProcessProtocol(protocol.ProcessProtocol):
	def __init__(self, ws):
		self.ws = ws
		reactor.spawnProcess(self, sys.executable,
							 [sys.executable, '-u', '../fade.py', '-s', '-f', '--web'])

	def outReceived(self, data):
		self.ws.nebSendToClient(data)
	def errReceived(self, data):
		self.ws.nebSendToClient(data)


class FadeWSManager(WebSocketServerProtocol):
	def onOpen(self):
		log.msg("New connection: launching a new instance of fade.py")
		self.logfile = open("logs/" + time.strftime("%Y-%m-%d_%H-%M-%S") + "_" + ''.join(random.choice('0123456789ABCDEF') for i in range(8)) + ".log", "w", 2048)
		self.process = FadeProcessProtocol(self)

	def onMessage(self, payload, isBinary):
		self.logfile.write(payload.decode('UTF-8'))
		self.process.transport.write(payload)

	def nebSendToClient(self, payload):
		self.logfile.write(payload.decode('UTF-8'))
		self.sendMessage(payload)
		self.logfile.flush()


if __name__ == '__main__':

	import argparse
	from twisted.internet.endpoints import serverFromString

	parser = argparse.ArgumentParser()
	parser.add_argument("--websocket", default="tcp:8076",
						help='WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".')
	parser.add_argument("--wsurl", default=u"ws://127.0.0.1:8076",
						help='WebSocket URL (must suit the endpoint), e.g. ws://127.0.0.1:9000.')
	parser.add_argument("--web", default="tcp:8080",
						help='Web server endpoint descriptor, e.g. "tcp:8080".')
	args = parser.parse_args()

	from autobahn.twisted.choosereactor import install_reactor

	reactor = install_reactor()
	log.startLogging(sys.stdout)

	wsfactory = WebSocketServerFactory(args.wsurl)
	wsfactory.protocol = FadeWSManager
	wsserver = serverFromString(reactor, args.websocket)
	wsserver.listen(wsfactory)

	if args.web != "":
		from twisted.web.server import Site
		from twisted.web.static import File

		webfactory = Site(File("."))
		webserver = serverFromString(reactor, args.web)
		webserver.listen(webfactory)

	reactor.run()  # enter the Twisted reactor loop
