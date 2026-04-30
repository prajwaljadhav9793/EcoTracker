'''emission calculations
    eco points '''
# emissions.py

VEHICLE_FACTORS = {
    "Car": 0.21,
    "Bike": 0.12,
    "Bus": 0.10,
    "Train": 0.05,
    "Walk": 0.0,
}


def calculate_emissions(electricity, vehicle, distance, waste, gas, appliance_hours):
    transport_co2 = distance * VEHICLE_FACTORS.get(vehicle, 0.0)
    electricity_co2 = electricity * 0.82
    waste_co2 = waste * 0.30
    gas_co2 = gas * 2.30
    appliance_co2 = appliance_hours * 0.10

    breakdown = {
        "Transport": round(transport_co2, 2),
        "Electricity": round(electricity_co2, 2),
        "Waste": round(waste_co2, 2),
        "Gas": round(gas_co2, 2),
        "Appliances": round(appliance_co2, 2),
    }

    carbon = round(sum(breakdown.values()), 2)

    if carbon == 0:
        highest_source = "None"
    else:
        highest_source = max(breakdown, key=breakdown.get)

    return breakdown, carbon, highest_source


def calculate_eco_points(breakdown, carbon):
    points = 100

    if breakdown["Transport"] > 5:
        points -= 20
    if breakdown["Electricity"] > 5:
        points -= 20
    if breakdown["Waste"] > 2:
        points -= 10
    if breakdown["Gas"] > 3:
        points -= 15
    if breakdown["Appliances"] > 1:
        points -= 10

    if carbon < 5:
        points += 5

    return max(0, min(100, points))
