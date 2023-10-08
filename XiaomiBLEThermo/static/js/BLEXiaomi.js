$(function() {
    function BlexiaomiViewModel(parameters) {
        var self = this;

        // Assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // Function to update the navbar data
        function updateNavbarData() {
            $.ajax({
                url: BASEURL + "plugin/bledata",
                type: "GET",
                dataType: "json",
                success: function(data) {
                    // Update temperature and humidity values
                    $(".temperature-value").text(data.temperature === "N/A" ? "-- °C" : data.temperature + "°C");
                    $(".humidity-value").text(data.humidity === "N/A" ? "-- %" : data.humidity + "%");
                    
                }
            });
        }

        // Call updateNavbarData every 5 seconds (5000 milliseconds)
        setInterval(updateNavbarData, 5000);

        // TODO: Implement your plugin's view model here.
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: BlexiaomiViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ /* "loginStateViewModel", "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_BLEXiaomi, #tab_plugin_BLEXiaomi, ...
        elements: [ /* ... */ ]
    });
});
