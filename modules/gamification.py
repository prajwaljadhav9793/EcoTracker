# modules/gamification.py

def get_badge(eco_points):
    """
    Returns badge based on eco points
    """
    if eco_points >= 90:
        return "🌍 Eco Hero"
    elif eco_points >= 70:
        return "🌱 Green Champion"
    elif eco_points >= 50:
        return "♻️ Eco Starter"
    else:
        return "⚠️ Needs Improvement"


# In-memory leaderboard (for now)
leaderboard = []


def update_leaderboard(username, eco_points):
    """
    Adds/updates user score in leaderboard
    """

    # Check if user already exists
    found = False
    for user in leaderboard:
        if user["name"] == username:
            user["points"] = eco_points
            found = True
            break

    if not found:
        leaderboard.append({
            "name": username,
            "points": eco_points
        })

    # Sort leaderboard
    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    return leaderboard