#!/usr/bin/python
"""WebSocket CLI interface."""
import sys
from twisted.application import strports # pip install twisted
from twisted.application import service
from twisted.internet    import protocol
from twisted.python      import log
from twisted.web.server  import Site
from twisted.web.static  import File

from txws import WebSocketFactory # pip install txws


class Protocol(protocol.Protocol):
    def connectionMade(self):
        from twisted.internet import reactor
        log.msg("New connection: launching a new instance of fade.py")
        self.pp = ProcessProtocol()
        self.pp.factory = self
        reactor.spawnProcess(self.pp, sys.executable,
                             [sys.executable, '-u', '../fade.py', '-s', '-f'])
    def dataReceived(self, data):
        log.msg("Recv: %r" % data)
        self.pp.transport.write(data)
    def connectionLost(self, reason):
        self.pp.transport.loseConnection()

    def _send(self, data):
        #if data[-1] != "\n": data += "\n"
        self.transport.write(data) # send back


class ProcessProtocol(protocol.ProcessProtocol):
    def connectionMade(self):
        pass
    def outReceived(self, data):
        #log.msg("send stdout back %r" % data)
        self._sendback(data)
    def errReceived(self, data):
        log.msg("send stderr back %r" % data)
        self._sendback(data)
    def processExited(self, reason):
        log.msg("processExited")
    def processEnded(self, reason):
        log.msg("processEnded")

    def _sendback(self, data):
        self.factory._send(data)

application = service.Application("fade-server")

_echofactory = protocol.Factory()
_echofactory.protocol = Protocol
strports.service("tcp:8076",
                 WebSocketFactory(_echofactory)).setServiceParent(application)

resource = File('.') # serve current directory INCLUDING *.py files
strports.service("tcp:8080",
                 Site(resource)).setServiceParent(application)
