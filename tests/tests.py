#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.xpl.common.plugin import XplPlugin
from domogik.tests.common.plugintestcase import PluginTestCase
from domogik.tests.common.testplugin import TestPlugin
from domogik.tests.common.testdevice import TestDevice
from domogik.tests.common.testsensor import TestSensor
from domogik.tests.common.testcommand import TestCommand
from domogik.common.utils import get_sanitized_hostname
from datetime import datetime
import unittest
import sys
import os
import traceback

class WolTestCase(PluginTestCase):

    def test_0100_wol(self):
        """ check if after a command is requested over rest, we receive the xpl-trig message and status is sotred in database

        """
        global devices
        global wol_port
 
        mac = "112233445566"
        port = 9


        # test 
        print(u"Device mac address = {0}".format(mac))
        print(u"Device port = {0}".format(port))
        print(u"Device id = {0}".format(devices[mac]))

        print(u"Call REST to send an '{0}'  command".format(1))
        tc = TestCommand(device_id, "wol")
        # send command
        #tc.send_command(1)   # 1 is high
        tc.send_command({'current' : 1})   # 1 is high
        print(u"Check that a message with command = 'high' is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"device" : mac,
                                                  "port" : port,
                                                  "type" : "wakeonlan",
                                                  "current" : "high"},
                                          timeout = 60))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "wol")
        print(sensor.get_last_value())
        from domogik_packages.plugin_wol.conversion.from_high_to_DT_Trigger import from_high_to_DT_Trigger
        # the data is converted to be inserted in database
        self.assertTrue(int(sensor.get_last_value()[1]) == from_high_to_DT_Trigger(self.xpl_data.data['current']))




if __name__ == "__main__":

    test_folder = os.path.dirname(os.path.realpath(__file__))

    ### global variables
    # the key will be the device address
    devices = { "112233445566" : 0
              }
    wol_port = 9

    ### configuration

    # set up the xpl features
    xpl_plugin = XplPlugin(name = 'test', 
                           daemonize = False, 
                           parser = None, 
                           nohub = True,
                           test  = True)

    # set up the plugin name
    name = "wol"

    # set up the configuration of the plugin
    # configuration is done in test_0010_configure_the_plugin with the cfg content
    # notice that the old configuration is deleted before
    cfg = { 'configured' : True}
   

    ### start tests

    # load the test devices class
    td = TestDevice()

    # delete existing devices for this plugin on this host
    client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
    try:
        td.del_devices_by_client(client_id)
    except: 
        print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
        sys.exit(1)

    # create a test device
    try:
        params = td.get_params(client_id, "wol.wol")
   
        for dev in devices:
            # fill in the params
            params["device_type"] = "wol.wol"
            params["name"] = "test_device_wol_{0}_é".format(dev)
            params["reference"] = "reference"
            params["description"] = "description"
            # global params
            pass # there are no global params for this plugin
            # xpl params
            # usually we configure the xpl parameters. In this device case, we can have multiple addresses
            # so the parameters are configured on xpl_stats level
            for the_param in params['xpl']:
                if the_param['key'] == "device":
                    the_param['value'] = dev
                if the_param['key'] == "port":
                    the_param['value'] = wol_port
            print params['xpl']
            # create
            device_id = td.create_device(params)['id']
            devices[dev] = device_id

    except:
        print(u"Error while creating the test devices : {0}".format(traceback.format_exc()))
        sys.exit(1)

    
    ### prepare and run the test suite
    suite = unittest.TestSuite()
    # check domogik is running, configure the plugin
    suite.addTest(WolTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
    suite.addTest(WolTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))
    
    # start the plugin
    suite.addTest(WolTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

    # do the specific plugin tests
    suite.addTest(WolTestCase("test_0100_wol", xpl_plugin, name, cfg))

    # do some tests comon to all the plugins
    #suite.addTest(WolTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(WolTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))
    
    # quit
    res = unittest.TextTestRunner().run(suite)
    if res.wasSuccessful() == True:
        rc = 0   # tests are ok so the shell return code is 0
    else:
        rc = 1   # tests are ok so the shell return code is != 0
    xpl_plugin.force_leave(return_code = rc)


