import collections
import statistics
import board
import player_p
import locations
import json

def run_single_game():
    market = board.MARKET()
    AI_player = player_p.AI(name='AI_BEAR', current_position=12, school="BEAR")
    game_map = locations.GameMap()
    game_map.start()
    board_g = board.Board(graph=game_map.graph, players=[AI_player], market=market)
    result = board_g.start_game(2, debug=False, game_stats=True)

    return {
        'MonstersKilled': result['MonstersKilled'],
        'TurnTaken': result['TurnTaken'],
        'GameWon': result['GameWon']
    }

def sample_games_linear(num_samples=1000):
    monster_kills_counter = collections.Counter()
    turn_lengths = []
    games_won_counter = 0

    for i in range(1, num_samples + 1):
        result = run_single_game()
        monster_kills = result['MonstersKilled']
        turns_taken = result['TurnTaken']
        game_won = result['GameWon']

        monster_kills_counter[monster_kills] += 1
        turn_lengths.append(turns_taken)
        if game_won:
            games_won_counter += 1

        print(f"\rGame {i}/{num_samples} complete", end="", flush=True)

    print()  # new line after progress

    total_games = sum(monster_kills_counter.values())
    kill_percentages = {
        k: (monster_kills_counter.get(k, 0) / total_games) * 100
        for k in range(6)
    }

    average_turns = statistics.mean(turn_lengths)
    variance_turns = statistics.variance(turn_lengths) if len(turn_lengths) > 1 else 0
    win_percentage = (games_won_counter / num_samples) * 100 if num_samples else 0

    return {
        "KillPercentages": kill_percentages,
        "AverageTurns": average_turns,
        "VarianceTurns": variance_turns,
        "WinPercentage": win_percentage,
        "TurnLengthsRaw": turn_lengths,
        "MonsterKillsRaw": list(monster_kills_counter.elements())
    }

if __name__ == "__main__":
    stats = sample_games_linear(200)
    print(json.dumps(stats, indent=4))