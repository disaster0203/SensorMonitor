import jsonpickle
import os


class Sensor:
    def __init__(self, name, gpio_pin, offset, active, color, unit):
        self.name = name
        self.gpioPin = gpio_pin
        self.offset = offset
        self.active = active
        self.color = color
        self.unit = unit


class WindowSettings:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class OutputSettings:
    def __init__(self, default_path, default_filename, default_file_extension):
        self.defaultPath = default_path
        self.defaultFilename = default_filename
        self.defaultFileExtension = default_file_extension


class ConfigData:
    def __init__(self, sensors, window_settings, output_settings):
        self.sensors = sensors
        self.window_settings = window_settings
        self.output_settings = output_settings


class ConfigManager:
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.config_data = self.load_config(self.path_to_config)

    def load_config(self, path):
        if not os.path.exists(path) or not os.path.isfile(path):
            return self.__create_config_from_defaults__()
        else:
            config_file = open(self.path_to_config, "r")
            content = config_file.read()
            return jsonpickle.decode(content)

    def write_config_data(self):
        if os.path.exists(self.path_to_config) and os.path.isfile(self.path_to_config):
            config_file = open(self.path_to_config, "w")
            config_file.write(jsonpickle.encode(self.config_data))
            config_file.close()

    def get_sensor(self, index):
        if self.config_data is not None and 0 <= index < len(self.path_to_config.sensors):
            return self.config_data.sensors[index]
        else:
            return None

    def get_sensors(self):
        if self.config_data is not None:
            return self.config_data.sensors
        else:
            return None

    def change_sensor_state(self, new_state, index):
        if self.config_data is not None and 0 <= index < len(self.config_data.sensors):
            self.config_data.sensors[index].active = new_state
            self.write_config_data()
            return True
        else:
            return False

    def get_window_settings(self):
        if self.config_data is not None:
            return self.config_data.window_settings
        else:
            return None

    def get_output_settings(self):
        if self.config_data is not None:
            return self.config_data.output_settings
        else:
            return None

    def __create_config_from_defaults__(self):
        window = WindowSettings(800, 600)
        output = OutputSettings("./", "Measurement_", ".csv")
        sensors = [Sensor("TestSensor", 1, 0, True, "#FF0000", "°C")]
        new_config = ConfigData(sensors, window, output)

        config_file = open(self.path_to_config, "x")
        config_file.write(jsonpickle.encode(new_config))
        config_file.close()

        return new_config
