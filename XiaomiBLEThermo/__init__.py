import octoprint.plugin
import threading
import time
import asyncio
import bleak

class XiaomiBLEThermo(octoprint.plugin.StartupPlugin,
                octoprint.plugin.TemplatePlugin,
                octoprint.plugin.SettingsPlugin,
                octoprint.plugin.BlueprintPlugin):

    def __init__(self):
        super(XiaomiBLEThermo, self).__init__()
        self.latest_ble_data = None
        self.mac_address = "A4:C1:38:5C:E8:78"
        self.scan_thread = None
        
    def stop_scan(self):
        if self.scan_thread is not None:
            self._logger.info("Stopping BLE scan thread...")
            self.scan_thread.stop()  # You need to implement stop method in your custom thread
            self.scan_thread.join()  # Wait for the thread to complete
            self._logger.info("BLE scan thread stopped.")

    def on_shutdown(self):
        self._logger.info("Shutting down XiaomiBLEThermo plugin...")
        self.stop_scan()
        self._logger.info("XiaomiBLEThermo plugin stopped.")
        
    def on_after_startup(self):
        self._logger.info("\033[94m[Bluetooth]\033[0m XiaomiBLEThermo plugin started!")
        if self.mac_address:
            self.start_scan()

    def get_settings_defaults(self):
        return dict(
            mac_address="A4:C1:38:5C:E8:78"
        )
        
    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False, template="navbar_blexiaomi.jinja2"),
            dict(type="settings", name="BLE Thermometer", template="blexiaomi_settings.jinja2", custom_bindings=False),
        ]

    def on_settings_save(self, data):
        old_mac_address = self._settings.get(["mac_address"])
        new_mac_address = data["mac_address"]
        self._settings.set(["mac_address"], new_mac_address)
        self._settings.save()

        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        if old_mac_address != new_mac_address:
            self._logger.info("MAC Address changed. Initiating a new scan.")
            if self.scan_thread is not None:
                self.scan_thread.stop()
            self.scan_thread = threading.Thread(target=self.start_scan)
            self.scan_thread.daemon = True
            self.scan_thread.start()
        else:
            self._logger.info("MAC Address unchanged. No need to restart the scan.")

    def start_scan(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def scan():
                while True:
                    # Scan for nearby BLE devices
                    devices = await bleak.discover()

                    # Look for the Xiaomi BLE thermometer in the list of discovered devices
                    for device in devices:
                        if device.address == self.mac_address:
                            # Read the advertising data from the Xiaomi BLE thermometer
                            advertising_data = device.metadata.get("manufacturer_data", b'')

                            self._logger.warning(advertising_data) 

                            # Extract temperature, humidity, and battery data from the advertising data
                            if len(advertising_data) >= 17:
                                mac_address = advertising_data[4:10]
                                temperature = int.from_bytes(advertising_data[10:12], byteorder='little', signed=True) / 100
                                humidity = advertising_data[12]
                                battery_percentage = advertising_data[13]
                                battery_voltage = int.from_bytes(advertising_data[14:16], byteorder='little', signed=False) / 1000
                                frame_counter = advertising_data[16]

                                # Update latest_ble_data
                                self.latest_ble_data = {
                                    "mac_address": mac_address,
                                    "temperature": temperature,
                                    "humidity": humidity,
                                    "battery_percentage": battery_percentage,
                                    "battery_voltage": battery_voltage,
                                    "frame_counter": frame_counter
                                }

                                self._logger.info(f"MAC Address: {mac_address.hex()}, Temperature: {temperature}°C, Humidity: {humidity}%, Battery Percentage: {battery_percentage}%, Battery Voltage: {battery_voltage}V, Frame Counter: {frame_counter}")
                            else:
                                self._logger.warning("Received advertising data does not match the expected format")

                    await asyncio.sleep(60)  # Sleep for 60 seconds before the next scan

            loop.run_until_complete(scan())
        except Exception as e:
            self._logger.error(f"Error during BLE scan: {e}")

    @octoprint.plugin.BlueprintPlugin.route("/bledata", methods=["GET"])
    def get_ble_data(self):
        if self.latest_ble_data:
            return flask.jsonify(self.latest_ble_data)
        else:
            return flask.jsonify({
                "temperature": "N/A",
                "humidity": "N/A",
                "battery_percentage": "N/A"
            })

__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_name__ = "XiaomiBLEThermo"
__plugin_implementation__ = XiaomiBLEThermo()
