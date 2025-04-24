import collections
import statistics
import concurrent.futures
import board
import player_p
import locations
import json

import json
import csv
import matplotlib.pyplot as plt


def run_single_game_human(_=None):  # The argument is required for map()
    market = board.MARKET()
    Human_player = player_p.Player(name='BEAR', current_position=12, school="BEAR")
    board_g = board.Board(graph=locations.GAME_MAP, players=[Human_player], market=market)
    result = board_g.start_game(40, debug=True, game_stats=True)

    return {
        'MonstersKilled': result['MonstersKilled'],
        'TurnTaken': result['TurnTaken'],
        'GameWon': result['GameWon']
    }

def run_single_game(_=None):  # The argument is required for map()
    market = board.MARKET()
    AI_player = player_p.AI(name='AI_BEAR', current_position=12, school="BEAR")
    board_g = board.Board(graph=locations.GAME_MAP, players=[AI_player], market=market)
    result = board_g.start_game(40, debug=True, game_stats=True)

    return {
        'MonstersKilled': result['MonstersKilled'],
        'TurnTaken': result['TurnTaken'],
        'GameWon': result['GameWon']
    }

def sample_games(num_samples=1000):
    monster_kills_counter = collections.Counter()
    turn_lengths = []
    games_won_counter = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(run_single_game, range(num_samples)))

    for result in results:
        monster_kills = result['MonstersKilled']
        turns_taken = result['TurnTaken']
        game_won = result['GameWon']

        monster_kills_counter[monster_kills] += 1
        turn_lengths.append(turns_taken)
        if game_won:
            games_won_counter += 1

    total_games = sum(monster_kills_counter.values())
    kill_percentages = {
        k: (monster_kills_counter.get(k, 0) / total_games) * 100
        for k in range(6)
    }

    average_turns = statistics.mean(turn_lengths)
    variance_turns = statistics.variance(turn_lengths)
    win_percentage = (games_won_counter / num_samples) * 100 if num_samples else 0

    return {
        "KillPercentages": kill_percentages,
        "AverageTurns": average_turns,
        "VarianceTurns": variance_turns,
        "WinPercentage": win_percentage
    }

# Required for Windows multiprocessing!
if __name__ == "__main__":
    sample_sizes = [500, 1000, 2000, 4000, 8000]
    results = {}

    for size in sample_sizes:
        print(f"\n--- Running {size} games ---")
        stats = sample_games(size)
        results[size] = stats
        print(json.dumps(stats, indent=4))

    # Write to CSV
    with open("convergence_data.csv", "w", newline="") as csvfile:
        fieldnames = ["SampleSize", "WinPercentage", "AverageTurns", "VarianceTurns"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for size in sample_sizes:
            data = results[size]
            writer.writerow({
                "SampleSize": size,
                "WinPercentage": data["WinPercentage"],
                "AverageTurns": data["AverageTurns"],
                "VarianceTurns": data["VarianceTurns"]
            })

    # Plotting
    sample_labels = sample_sizes
    win_percentages = [results[size]["WinPercentage"] for size in sample_sizes]
    avg_turns = [results[size]["AverageTurns"] for size in sample_sizes]
    variances = [results[size]["VarianceTurns"] for size in sample_sizes]

    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 3, 1)
    plt.plot(sample_labels, win_percentages, marker='o', color='green')
    plt.title("Win Percentage vs Sample Size")
    plt.xlabel("Sample Size")
    plt.ylabel("Win %")

    plt.subplot(1, 3, 2)
    plt.plot(sample_labels, avg_turns, marker='o', color='blue')
    plt.title("Average Turns vs Sample Size")
    plt.xlabel("Sample Size")
    plt.ylabel("Average Turns")

    plt.subplot(1, 3, 3)
    plt.plot(sample_labels, variances, marker='o', color='red')
    plt.title("Turn Variance vs Sample Size")
    plt.xlabel("Sample Size")
    plt.ylabel("Variance")

    plt.tight_layout()
    plt.savefig("convergence_graphs.png")
    plt.show()
