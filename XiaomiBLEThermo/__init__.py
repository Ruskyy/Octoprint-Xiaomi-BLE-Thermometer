from __future__ import absolute_import, unicode_literals

import bluetooth as bluez
import octoprint.plugin
from datetime import datetime
from octoprint.util import RepeatedTimer

from .bluetooth_utils import (disable_le_scan, enable_le_scan,
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
        self._logger.info("\033[94m[Bluetooth]\033[0m XiaomiBLEThermo plugin started!")

    def get_settings_defaults(self):
        return dict(
            devid="0"
        )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False, template="navbar_blexiaomi.jinja2"),
            dict(type="settings", name="BLE Thermometer",template="blexiaomi_settings.jinja2", custom_bindings=False),
        ]

    def get_template_vars(self):
        return dict(
            mac_address=self._settings.get(["mac_address"]),
        )

    def start_scan(self):
        self._logger.info("Start scan method called")
        toggle_device(self.dev_id, True)
        self._logger.info("\033[94m Scan Start !\033[0m")    
        try:
            sock = bluez.hci_open_dev(self.dev_id)
        except:
            self._logger.error("Cannot open \033[94m bluetooth \033[0m device %i" % self.dev_id)
            raise

        # Set filter to "True" to see only one packet per device
        enable_le_scan(sock, filter_duplicates=False)

        try:
            def le_advertise_packet_handler(mac, adv_type, data, rssi):
                data_str = raw_packet_to_str(data)
                
                # Specify the desired MAC address to filter
                desired_mac = self._settings.get(["mac_address"])

                # Check if the received MAC address matches the desired MAC address
                if mac == desired_mac and data_str[5:10] == "61a18":
                    temp = int(data_str[22:26], 16) / 10
                    hum = int(data_str[26:28], 16)
                    batt = int(data_str[28:30], 16)
                    self.latest_ble_data = {
                        "temperature": temp,
                        "humidity": hum
                    }
                    self._logger.info(
                        "%s - Device: %s Temp: %sc Humidity: %s%%" % (
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            mac,
                            temp,
                            hum,
                        )
                    )
                else:
                    # No valid BLE data, set values to "N/A"
                    self.latest_ble_data = None
                    self._logger.info(
                        "%s - No valid BLE data received for device: %s" % (
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            mac
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
            return flask.jsonify({
                "temperature": "N/A",
                "humidity": "N/A"
            })



__plugin_pythoncompat__ = ">=3.8,<4"
__plugin_name__ = "XiaomiBLEThermo"
__plugin_implementation__ = XiaomiBLEThermo()
