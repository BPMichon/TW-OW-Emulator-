import collections
import statistics
import board
import player_p
import locations
import csv
import matplotlib.pyplot as plt
import copy
import os

def save_stats_to_csv(result, sample_size, turn_limit, player_csv_path="player_stats.csv", game_csv_path="game_stats.csv"):
    player_stats = result["PlayerStats"]
    turn_average = result["AverageTurns"]
    turn_variance = result["VarianceTurns"]

    # Create the player CSV if it doesn't exist yet
    if not os.path.exists(player_csv_path):
        with open(player_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "SampleSize", "TurnLimit", "PlayerID",
                "AverageVictoryPoints", "VictoryPointsVariance",
                "AverageMonsterKills", "AverageMonsterAttempts",
                "KillSuccessRate(%)", "WinPercentage(%)",
                "AverageCombat", "AverageAlchemy", "AverageDefence", "AverageSpeciality",
                "AverageSpecialityCount", "AverageTurns", "VarianceTurns"
            ])

    # Write player stats
    with open(player_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        for player in player_stats:
            writer.writerow([
                sample_size, turn_limit, player["Player"],
                f"{player.get('AverageVictoryPoints', 0):.2f}", f"{player.get('VictoryPointsVariance', 0):.2f}",
                f"{player.get('AverageMonsterKills', 0):.2f}", f"{player.get('AverageMonsterAttempts', 0):.2f}",
                f"{player.get('KillSuccessRate', 0):.2f}", f"{player.get('WinPercentage', 0):.2f}",
                f"{player.get('AverageCombat', 0):.2f}", f"{player.get('AverageAlchemy', 0):.2f}",
                f"{player.get('AverageDefence', 0):.2f}", f"{player.get('AverageSpeciality', 0):.2f}",
                f"{player.get('AverageSpecialityCount', 0):.2f}",
                f"{turn_average:.2f}", f"{turn_variance:.2f}"
            ])

def initialize_base_game(player_class=player_p.AI, player_name='AI_BEAR', position=12, school='BEAR'):
    market = board.MARKET()
    game_map = locations.GameMap()
    game_map.start()

    player = player_class(name=player_name, current_position=position, school=school)
    player2 = player_class(name="AI_WOLF", current_position=1, school="WOLF")

    human_wolf = player_p.Player(name='P1', current_position=1, school="WOLF")
    human_bear = player_p.Player(name='P1', current_position=12, school="BEAR")

    board_g = board.Board(graph=game_map.graph, players=[human_bear,player2], market=market)

    return board_g

def run_single_game_from_base(base_board, turn):
    board_g = copy.deepcopy(base_board)
    result = board_g.start_game(turn, debug=True, game_stats=True)
    return {
        "Stats": result
    }

def sample_games(num_samples=1000, turns=20):
    num_players = 2

    # Initialize stats collectors
    player_victory_points = [[] for _ in range(num_players)]
    player_monster_kills = [[] for _ in range(num_players)]
    player_monster_attempts = [[] for _ in range(num_players)]
    player_combat = [[] for _ in range(num_players)]
    player_alchemy = [[] for _ in range(num_players)]
    player_defence = [[] for _ in range(num_players)]
    player_speciality = [[] for _ in range(num_players)]
    player_speciality_count = [[] for _ in range(num_players)]
    player_wins = [0 for _ in range(num_players)]

    turn_lengths = []

    base_board = initialize_base_game()

    for i in range(num_samples):
        result = run_single_game_from_base(base_board, turn=turns)

        for idx, player_stat in enumerate(result.get('Stats', [])):
            player_victory_points[idx].append(player_stat['Victorypoints'])
            player_monster_kills[idx].append(player_stat['MonsterKills'])
            player_monster_attempts[idx].append(player_stat['MonsterAttempts'])
            player_combat[idx].append(player_stat.get('Combat', 0))
            player_alchemy[idx].append(player_stat.get('Alchemy', 0))
            player_defence[idx].append(player_stat.get('Defence', 0))
            player_speciality[idx].append(player_stat.get('Speciality', 0))
            player_speciality_count[idx].append(player_stat.get('SpecialityCount', 0))

            if player_stat['GameWon']:
                player_wins[idx] += 1

            turn_lengths.append(player_stat['Turn'])

        print(f"\rGame {i+1}/{num_samples} complete", end="", flush=True)

    print()

    # Now calculate per player results
    player_stats = []
    for idx in range(num_players):
        total_attempts = sum(player_monster_attempts[idx])
        total_kills = sum(player_monster_kills[idx])

        player_data = {
            "Player": idx,
            "VictoryPointsRaw": player_victory_points[idx],
            "AverageVictoryPoints": statistics.mean(player_victory_points[idx]) if player_victory_points[idx] else 0,
            "VictoryPointsVariance": statistics.variance(player_victory_points[idx]) if len(player_victory_points[idx]) > 1 else 0,
            "AverageMonsterKills": statistics.mean(player_monster_kills[idx]) if player_monster_kills[idx] else 0,
            "AverageMonsterAttempts": statistics.mean(player_monster_attempts[idx]) if player_monster_attempts[idx] else 0,
            "KillSuccessRate": (total_kills / total_attempts) * 100 if total_attempts > 0 else 0,
            "WinPercentage": (player_wins[idx] / num_samples) * 100,
            "AverageCombat": statistics.mean(player_combat[idx]) if player_combat[idx] else 0,
            "AverageAlchemy": statistics.mean(player_alchemy[idx]) if player_alchemy[idx] else 0,
            "AverageDefence": statistics.mean(player_defence[idx]) if player_defence[idx] else 0,
            "AverageSpeciality": statistics.mean(player_speciality[idx]) if player_speciality[idx] else 0,
            "AverageSpecialityCount": statistics.mean(player_speciality_count[idx]) if player_speciality_count[idx] else 0,
        }
        player_stats.append(player_data)

    # Global stats
    average_turns = statistics.mean(turn_lengths)
    variance_turns = statistics.variance(turn_lengths) if len(turn_lengths) > 1 else 0

    return {
        "PlayerStats": player_stats,
        "AverageTurns": average_turns,
        "VarianceTurns": variance_turns,
    }

if __name__ == "__main__":
    ## Make sure to chnage the number of smaples here and turn limit here
    ## !! IMPORTANT !! if you want to be able to play with multiple agents/players,
    ## you have to increase the number of players on line 67 , num_players
    sample_sizes = [3]
    turns = [50]
    results = {}

    for size in sample_sizes:
        results[size] = {}
        for turn_limit in turns:
            print(f"\nRunning {size} simulations with turn limit {turn_limit}...")
            result = sample_games(num_samples=size, turns=turn_limit)
            results[size][turn_limit] = result

            save_stats_to_csv(result, sample_size=size, turn_limit=turn_limit)

    # --- Plotting the Victory Points Distribution ---
    for size in sample_sizes:
        for turn_limit in turns:
            result = results[size][turn_limit]
            player_stats = result["PlayerStats"]

            plt.figure(figsize=(12, 8))

            max_vp = 6

            for player in player_stats:
                vp_list = player.get('VictoryPointsRaw', [])

                total_games = len(vp_list)
                vp_counter = collections.Counter(vp_list)

                percentages = [
                    (vp_counter.get(vp, 0) / total_games) * 100 if total_games > 0 else 0
                    for vp in range(max_vp)
                ]

                plt.bar(
                    [x + 0.15 * player["Player"] for x in range(max_vp)],
                    percentages,
                    width=0.15,
                    label=f'Player {player["Player"]}'
                )

            plt.xlabel('Victory Points')
            plt.ylabel('Percentage of Games (%)')
            plt.title(f'Victory Points Distribution per Player\n({size} games, {turn_limit} turns)')
            plt.xticks(range(max_vp))
            plt.ylim(0, 100)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"victory_points_distribution_{size}_games_{turn_limit}_turns.png")
            plt.show()
