from __future__ import absolute_import, unicode_literals

from datetime import datetime

import bluetooth as bluez
import octoprint.plugin
from octoprint.util import RepeatedTimer

from bluetooth_utils import (disable_le_scan, enable_le_scan,
                             parse_le_advertising_events, raw_packet_to_str,
                             toggle_device)


class XiaomiBLEThermo(octoprint.plugin.StartupPlugin,
                octoprint.plugin.TemplatePlugin,
                octoprint.plugin.SettingsPlugin):

    def __init__(self):
        super(XiaomiBLEThermo, self).__init__()
        self.latest_ble_data = None
        self.dev_id = 0

    def on_after_startup(self):
        self._logger.info("XiaomiBLEThermo plugin started!")

    def get_settings_defaults(self):
        return dict(
            url="https://en.wikipedia.org/wiki/Hello_world",
            devid="0"
        )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False, template="navbar_ble_thermometer.jinja2"),
            dict(type="settings", name="BLE Thermometer", custom_bindings=False),
        ]

    def get_template_vars(self):
        return dict(
            mac_address=self._settings.get(["mac_address"]),
        )

    def start_scan(self):
        toggle_device(self.dev_id, True)

        try:
            sock = bluez.hci_open_dev(self.dev_id)
        except:
            self._logger.error("Cannot open bluetooth device %i" % self.dev_id)
            raise

        # Set filter to "True" to see only one packet per device
        enable_le_scan(sock, filter_duplicates=False)

        try:
            def le_advertise_packet_handler(mac, adv_type, data, rssi):
                data_str = raw_packet_to_str(data)
                # Check for ATC preamble
                if data_str[5:10] == "61a18":
                    temp = int(data_str[22:26], 16) / 10
                    hum = int(data_str[26:28], 16)
                    batt = int(data_str[28:30], 16)
                    self.latest_ble_data = {
                        "temperature": temp,
                        "humidity": hum,
                        "battery": batt
                    }
                    self._logger.info(
                        "%s - Device: %s Temp: %sc Humidity: %s%% Batt: %s%%" % (
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            mac,
                            temp,
                            hum,
                            batt,
                        )
                    )

            # Called on new LE packet
            parse_le_advertising_events(
                sock, handler=le_advertise_packet_handler, debug=False
            )
        # Scan until Ctrl-C
        except KeyboardInterrupt:
            disable_le_scan(sock)

    @octoprint.plugin.BlueprintPlugin.route("/bledata", methods=["GET"])
    def get_ble_data(self):
        if self.latest_ble_data:
            return flask.jsonify(self.latest_ble_data)
        else:
            return flask.jsonify(error="No BLE data available")

__plugin_pythoncompat__ = ">=3.8,<4"
__plugin_name__ = "XiaomiBLEThermo"
__plugin_implementation__ = XiaomiBLEThermo()
