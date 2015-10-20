# -*- coding: utf-8 -*- 

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Ping ip devices

Implements
==========

class Wol

@author: Fritz SMH <fritz.smh@gmail.com>
@copyright: (C) 2007-2015 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import traceback
import socket
import struct

class Wol:
    """
    """

    def __init__(self, log, mac, port, callback):
        """
        Ping a device each n seconds
        @param log : log instance
        @param mac : mac address
        @param port : port for wol
        @param callback : callback to return values
        """
        self.log = log
        #self.mac = mac
        #self.port = port
        self.callback = callback
        self.wake_up(mac, port)
    

    def wake_up(self, mac, port):
        """
        Send a magic packet to wake a computer on lan
        """
        self.log.debug(u"Start processing wol on %s port %s" % (mac, str(port)))
        try:
            port = int(port)
        except:
            self.log.error(u"Port is not an integer!")
        # Verify and convert mac format
        self.log.debug(u"Check mac format")
        if len(mac) == 12:
            pass
        elif len(mac) == 12 + 5:
            separator = mac[2]
            mac = mac.replace(separator, '')
        else:
            self.log.error(u"Wrong mac address : " + mac)
            return False

        # Create magic packet
        self.log.debug(u"Create magic packet")
        magic_packet = ''.join(['FFFFFFFFFFFF', mac * 20])
        magic_hexa = ''

        # Convert magic packet in hexa
        for i in range(0, len(magic_packet), 2):
            magic_hexa = ''.join([magic_hexa, 
                         struct.pack('B', int(magic_packet[i: i + 2], 16))])

        # Send magic packet
        self.log.debug(u"Send magic packet to broadcast")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_hexa, ('<broadcast>', port))
            self.log.info(u"Magic packet send")
            sock.close()
            self.callback("xpl-trig", {'type' : 'wakeonlan',
                                       'current' : 'high',
                                       'device' : mac,
                                       'port' : port})
            return True
        except:
            self.log.error(u"Fail to send magic packet : %s" % traceback.format_exc())
            return False
