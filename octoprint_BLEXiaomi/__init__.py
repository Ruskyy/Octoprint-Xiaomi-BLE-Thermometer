#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import bluetooth._bluetooth as bluez
from datetime import datetime
from bluetooth_utils import (toggle_device, enable_le_scan,
                             parse_le_advertising_events,
                             disable_le_scan, raw_packet_to_str)
import octoprint.plugin

class XiaomiBLE(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin):
    def on_after_startup(self):
        self._logger.info("RUSKLYYYYYYYYYYYYYYYYYYYY OWO! (more: %s)" % self._settings.get(["url"]))

    def get_settings_defaults(self):
        return dict(url="https://en.wikipedia.org/wiki/Hello_world")

    def get_template_vars(self):
        return dict(url=self._settings.get(["url"]))

    def test(self):
        # Use 0 for hci0
        dev_id = 0
        toggle_device(dev_id, True)

        try:
            sock = bluez.hci_open_dev(dev_id)
        except:
            print("Cannot open bluetooth device %i" % dev_id)
            raise

        # Set filter to "True" to see only one packet per device
        enable_le_scan(sock, filter_duplicates=False)

        try:
            def le_advertise_packet_handler(mac, adv_type, data, rssi):
                data_str = raw_packet_to_str(data)
                # Check for ATC preamble
                if data_str[5:10] == '61a18':
                    temp = int(data_str[22:26], 16) / 10
                    hum = int(data_str[26:28], 16)
                    batt = int(data_str[28:30], 16)
                    print("%s - Device: %s Temp: %sc Humidity: %s%% Batt: %s%%" % \
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mac, temp, hum, batt))

            # Called on new LE packet
            parse_le_advertising_events(sock,
                                        handler=le_advertise_packet_handler,
                                        debug=False)
        # Scan until Ctrl-C
        except KeyboardInterrupt:
            disable_le_scan(sock)

__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = XiaomiBLE()