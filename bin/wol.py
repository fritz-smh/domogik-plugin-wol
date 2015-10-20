#!/usr/bin/python
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

Get informations about one wire network

Implements
==========

Wol feature

@author: Fritz SMH <fritz.smh@gmail.com>
@copyright: (C) 2007-2015 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.xplconnector import Listener
from domogik.xpl.common.plugin import XplPlugin
from domogik_packages.plugin_wol.lib.wol import Wol
import time
import threading
import traceback


class WolManager(XplPlugin):

    def __init__(self):
        """ Init 
        """
        XplPlugin.__init__(self, name='wol')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        #if not self.check_configured():
        #    return

        ### get the devices list
        # for this plugin, if no devices are created we won't be able to use devices.
        # but.... if we stop the plugin right now, we won't be able to detect existing device and send events about them
        # so we don't stop the plugin if no devices are created
        self.devices = self.get_device_list(quit_if_no_device = True)

        ### get all config keys
        # n/a

        ### Listeners
        Listener(self.process_control_basic, self.myxpl,
                 {'schema': 'control.basic',
                  'xpltype': 'xpl-cmnd'})

        ### For each device
        # TODO : delete these lines
        #threads = {}
        #for a_device in self.devices:
        #    try:
        #        mac = self.get_parameter_for_feature(a_device, "xpl_stats", "wol", "device")
        #        port = self.get_parameter_for_feature(a_device, "xpl_stats", "wol", "port")

        # notify ready
        self.ready()

    def process_control_basic(self, message):
        """ Process command messages
        """
        if message.data["type"].lower() != "wakeonlan":
            return
        mac = message.data["device"].lower()
        port = message.data["port"].lower()
        current = message.data["current"].lower()
        if current != "high":
            self.log.warning(u"The value '{0}' is not handle by this plugin. Expected : 'high'".format(current))
            return
        self.log.info(u"Message received to WOL the device with mac '{0}' on port '{1}'".format(mac, port))
        Wol(self.log, mac, port, self.send_xpl)




    def send_xpl(self, type, data):
        """ Send data on xPL network
            @param data : data to send (dict)
        """
        msg = XplMessage()
        msg.set_type(type)
        msg.set_schema("sensor.basic")
        for element in data:
            msg.add_data({element : data[element]})
        self.log.debug(u"Send xpl message...")
        self.log.debug(msg)
        self.myxpl.send(msg)


if __name__ == "__main__":
    w = WolManager()
