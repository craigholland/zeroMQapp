"""Lightweight client that announces existence/availability/specs to HQ."""

import zmq
import time

OUTPOST_CONFIG = {
  'outpost_name': 'Johnny 5',
  'socket_type': 'tcp',
  'server_listening_socket': 5555,
  'my_url': 'localhost'
}
# Sleeper (True) turns on ZMQ server while awaiting to be signaled by HQ.  Upon receiving HQ
# signal, Outpost 'wakes up' (Sleeper=False) and turns off server and reconnects to HQ as a client.
sleeper_status = True
context = zmq.Context()


class Sleepmode(object):
  """In sleepmode, Outpost is a zmq server and listens for a message from HQ."""
  def __init__(self):
    self.socket = context.socket(zmq.REP)
    print "Outpost is Waiting to hear from HQ"
    bind_str = 'tcp://*:{0}'.format(OUTPOST_CONFIG['server_listening_socket'])
    self.socket.bind(bind_str)
    self.message = None
    self.Listen()

  def MsgInterpret(self):
    print self.message

  def Listen(self):
    while True:
      message = self.socket.recv()
      print message

  def close(self):
    pass

a = Sleepmode()

#
# #  Socket to talk to server
#
# socket = context.socket(zmq.REP)
# bind_str =
# socket.bind(bind_str)
#
# print "Outpost is Waiting to hear from HQ"
# print "Connection str: {0}".format(bind_str)
# while True:
#     #  Wait for next request from HQ
#     message = socket.recv()
#
#     print("Received request from HQ to connect to socket with validation: %s" % message)
#
#     #  Do some 'work'
#     time.sleep(5)
#
#     #  Send reply back to client
#     socket.send(b'{0} is alive!'.format(OUTPOST_CONFIG['outpost_name']))