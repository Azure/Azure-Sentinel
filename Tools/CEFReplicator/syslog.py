"""
Remote syslog client.

Works by sending UDP messages to a remote syslog server. The remote server
must be configured to accept logs from the network.

License: PUBLIC DOMAIN
Author: Christian Stigen Larsen

For more information, see RFC 3164.
"""

import socket

class Facility:
  "Syslog facilities"
  KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, \
  LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)

  LOCAL0, LOCAL1, LOCAL2, LOCAL3, \
  LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)

class Level:
  "Syslog levels"
  EMERG, ALERT, CRIT, ERR, \
  WARNING, NOTICE, INFO, DEBUG = range(8)

class Syslog:
  """A syslog client that logs to a remote server.

  Example:
  >>> log = Syslog(host="foobar.example")
  >>> log.send("hello", Level.WARNING)
  """
  def __init__(self,
               host="localhost",
               port=514,
               facility=Facility.DAEMON,
               protocol='UDP'):
    self.host = host
    self.port = port
    self.facility = facility
    self.protocol = protocol
    if self.protocol == 'UDP':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif self.protocol == 'TCP':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
    else:
        raise Exception('Invalid protocol {}, valid options are UDP and TCP'.format(self.protocol))

  def send(self, message, level=Level.NOTICE):
    "Send a syslog message to remote host using UDP or TCP"
    data = "<%d>%s" % (level + self.facility*8, message)
    if self.protocol == 'UDP':
        self.socket.sendto(data.encode('utf-8'), (self.host, self.port))
    else:
        self.socket.send(data.encode('utf-8'))

  def warn(self, message):
    "Send a syslog warning message."
    self.send(message, Level.WARNING)

  def notice(self, message):
    "Send a syslog notice message."
    self.send(message, Level.NOTICE)

  def error(self, message):
    "Send a syslog error message."
    self.send(message, Level.ERR)
