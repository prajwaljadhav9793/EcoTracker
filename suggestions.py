import random

TRANSPORT_TIPS = [
    "Use public transport instead of private vehicles",
    "Try carpooling to reduce emissions",
    "Try walking or cycling for short distances",
    "Avoid unnecessary travel",
    "Consider switching to electric or hybrid vehicles",
    "Plan trips to combine errands and reduce total travel",
    "Use fuel-efficient driving techniques, such as smooth acceleration and braking",
    "Maintain your vehicle regularly to ensure optimal fuel efficiency",
    "Consider telecommuting or working from home when possible",
]

ELECTRICITY_TIPS = [
    "Switch off unused appliances",
    "Use energy-efficient devices",
    "Reduce AC usage and use fans instead",
    "Use LED bulbs instead of traditional ones",
    "Unplug chargers when not in use",
    "Consider switching to renewable energy sources if available",
    "Use natural light during the day to reduce electricity consumption",
    "Use power strips to easily turn off multiple devices at once",
]

WASTE_TIPS = [
    "Segregate waste properly",
    "Recycle materials whenever possible",
    "Reduce plastic usage",
    "Compost organic waste",
    "Avoid single-use products",
    "Buy products with minimal packaging to reduce waste",
]

GAS_TIPS = [
    "Use cooking gas efficiently",
    "Avoid leaving gas on unnecessarily",
    "Consider switching to electric cooking appliances",
    "Ensure proper ventilation when using gas appliances to improve efficiency",
    "Regularly maintain gas appliances to ensure they are working efficiently",
    "Consider using a pressure cooker to reduce cooking time and gas usage",
    "Use a microwave for reheating food instead of the stove to save gas",
    "Plan meals to minimize cooking time and reduce gas consumption",
    "Consider using a slow cooker for meals that require long cooking times, as it can be more energy-efficient than using the stove",
]

APPLIANCE_TIPS = [
    "Reduce appliance usage time",
    "Turn off devices when not needed",
    "Use energy-efficient appliances",
    "Unplug devices when not in use to prevent phantom energy consumption",
    "Use appliances during off-peak hours to reduce strain on the grid",
]


def generate_suggestions(user_data):
    tips = []

    # Priority: highest emission
    if user_data["highest_source"] == "Transport":
        tips += random.sample(TRANSPORT_TIPS, 2)

    elif user_data["highest_source"] == "Electricity":
        tips += random.sample(ELECTRICITY_TIPS, 2)

    elif user_data["highest_source"] == "Waste":
        tips += random.sample(WASTE_TIPS, 2)

    elif user_data["highest_source"] == "Gas":
        tips += random.sample(GAS_TIPS, 1)

    elif user_data["highest_source"] == "Appliances":
        tips += random.sample(APPLIANCE_TIPS, 1)

    # Add more based on thresholds
    if user_data["transport_co2"] > 5:
        tips += random.sample(TRANSPORT_TIPS, 1)

    if user_data["electricity_co2"] > 5:
        tips += random.sample(ELECTRICITY_TIPS, 1)

    if user_data["waste_co2"] > 2:
        tips += random.sample(WASTE_TIPS, 1)

    # Remove duplicates
    tips = list(set(tips))

    # Shuffle for randomness
    random.shuffle(tips)

    return tips[:4]
