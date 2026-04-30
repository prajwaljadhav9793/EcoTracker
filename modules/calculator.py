# modules/calculator.py

def calculate_score(vehicle, electricity, waste):

    vehicle_score_map = {
        "Car": 5,
        "Bike": 7,
        "Bus": 8,
        "electric car": 9,
        "electric bike": 10,
        "Bicycle": 10,
        "Walk": 10
    }

    vehicle_score = vehicle_score_map.get(vehicle, 5)

    electricity_score = 10 if electricity <= 50 else 7 if electricity <= 100 else 4
    waste_score = 10 if waste <= 2 else 6 if waste <= 5 else 3

    total_score = vehicle_score + electricity_score + waste_score

    if total_score >= 25:
        message = "Excellent 🌱 Eco Friendly!"
    elif total_score >= 15:
        message = "Good 👍 Keep Improving!"
    else:
        message = "Needs Improvement ⚠️"

    return total_score, message, [vehicle_score, electricity_score, waste_score]