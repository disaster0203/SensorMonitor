def get_converter_function(sensor_name: str):
    for key in converter_functions.keys():
        if key == sensor_name:
            return converter_functions[sensor_name]

    return None


def distance_GP2Y0A710K0F(volt_value: float) -> float:
    if volt_value > 2.5 or volt_value < 1.4:
        return 0
    else:
        return 222799 * pow((1 / volt_value), 3) - 319655 * pow((1 / volt_value), 2) + 158254 * (1 / volt_value) - 25501


def distance_GP2Y0A21YK0F(volt_value: float) -> float:
    if volt_value > 2.2 or volt_value < 0.29:
        return 0
    else:
        return 252.77 * (1 / volt_value) - 20.237


converter_functions = {"DistanceSensor_GP2Y0A710K0F": distance_GP2Y0A710K0F, "DistanceSensor_GP2Y0A21YK0F": distance_GP2Y0A21YK0F}
