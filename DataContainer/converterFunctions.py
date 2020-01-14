def get_converter_function(sensor_name: str):
    for key in converter_functions.keys():
        if key == sensor_name:
            return converter_functions[sensor_name]

    return None


def distance_GP2Y0A710K0F(volt_value: float) -> float:
    if volt_value > 2.5 or volt_value < 1.4:
        return 0
    else:
        return 1 / (((volt_value * 1000) - 1125) / 137500)


converter_functions = {"DistanceSensor_GP2Y0A710K0F": distance_GP2Y0A710K0F}
