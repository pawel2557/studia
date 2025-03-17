import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# API Configuration
API_URL = "https://api.football-data.org/v4/matches"
HEADERS = {"X-Auth-Token": "50f44c1922bb46b7bd07f96e02e0af5e"}

# Fetch data from the last 10 days
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')
params = {"dateFrom": start_date, "dateTo": end_date}

response = requests.get(API_URL, headers=HEADERS, params=params)
data = response.json()

# Check if matches are available
if "matches" in data and len(data["matches"]) > 0:
    matches = data["matches"]
else:
    print("No available matches in the given date range.")
    exit()

# Get available leagues
leagues = {}
for match in matches:
    league_code = match["competition"]["code"]
    league_name = match["competition"]["name"]
    leagues[league_code] = league_name

# User selects a league
while True:
    print("\nAvailable leagues:")
    for i, (code, name) in enumerate(leagues.items()):
        print(f"{i + 1}. {name} ({code})")
    try:
        choice = int(input("Select a league by entering the corresponding number: "))
        if 1 <= choice <= len(leagues):
            selected_league_code = list(leagues.keys())[choice - 1]
            selected_league_name = leagues[selected_league_code]
            break
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Process data for selected league
data_list = []
teams_set = set()
for match in matches:
    if match["competition"]["code"] == selected_league_code:
        if match["score"]["fullTime"]["home"] is not None and match["score"]["fullTime"]["away"] is not None:
            data_list.append({
                "date": match["utcDate"],
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
                "home_score": match["score"]["fullTime"]["home"],
                "away_score": match["score"]["fullTime"]["away"],
                "winner": match["score"]["winner"]
            })
            teams_set.add(match["homeTeam"]["name"])
            teams_set.add(match["awayTeam"]["name"])

teams_list = sorted(list(teams_set))
df_scores = pd.DataFrame(data_list)

# Convert date to readable format
df_scores["date"] = pd.to_datetime(df_scores["date"])

# Calculate average goals per match for the selected league
df_scores["total_goals"] = df_scores["home_score"] + df_scores["away_score"]
df_scores["rolling_avg_goals"] = df_scores["total_goals"].rolling(window=5, min_periods=1).mean()

# Print league goal statistics
print(f"\nAverage goals per match in {selected_league_name} in the last 10 days: {df_scores['total_goals'].mean():.2f}")

# Plot average goals per match for the selected league
plt.figure(figsize=(10, 5))
plt.plot(df_scores["date"], df_scores["rolling_avg_goals"], marker='o', linestyle='-', label=f"{selected_league_name} Average Goals")
plt.xlabel("Date")
plt.ylabel("Average goals per match")
plt.title(f"Goal trend for {selected_league_name}")
plt.grid()
plt.xticks(rotation=45)
plt.legend()
plt.show()

# Allow user to choose a team
while True:
    print("\nAvailable teams in selected league:")
    for i, team in enumerate(teams_list):
        print(f"{i + 1}. {team}")
    try:
        choice = int(input("Select a team by entering the corresponding number: "))
        if 1 <= choice <= len(teams_list):
            team_name = teams_list[choice - 1]
            break
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Filter matches for the selected team
team_matches = df_scores[(df_scores['home_team'] == team_name) | (df_scores['away_team'] == team_name)].copy()

if not team_matches.empty:
    wins = 0
    losses = 0
    draws = 0
    for _, match in team_matches.iterrows():
        if match['winner'] == "HOME_TEAM" and match['home_team'] == team_name:
            wins += 1
        elif match['winner'] == "AWAY_TEAM" and match['away_team'] == team_name:
            wins += 1
        elif match['winner'] == "HOME_TEAM" and match['away_team'] == team_name:
            losses += 1
        elif match['winner'] == "AWAY_TEAM" and match['home_team'] == team_name:
            losses += 1
        else:
            draws += 1

    print(f"\nStatistics for {team_name} in the last 10 days:")
    print(f"Wins: {wins}")
    print(f"Draws: {draws}")
    print(f"Losses: {losses}")

    print(f"\nRecent matches of {team_name}:")
    for _, match in team_matches.iterrows():
        print(f"{match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']} ({match['date']})")

    # Calculate total goals per match for selected team
    team_matches["rolling_avg_goals"] = team_matches["total_goals"].rolling(window=5, min_periods=1).mean()

    # Display trend of goals per match for selected team
    plt.figure(figsize=(10, 5))
    plt.plot(team_matches["date"], team_matches["rolling_avg_goals"], marker='o', linestyle='-', label=f"{team_name} Goals")
    plt.xlabel("Date")
    plt.ylabel("Average goals per match")
    plt.title(f"Goal trend for {team_name}")
    plt.grid()
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()
else:
    print("\nNo matches found for this team in the given date range.")
