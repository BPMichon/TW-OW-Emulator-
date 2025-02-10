import random

# Define the 3x3 Grid
class Board:
    def __init__(self):
        self.grid = [[None, None, None], [None, None, None], [None, None, None]]  # 3x3 grid
        self.positions = {'P1': (0, 0), 'AI': (2, 2)}  # Initial positions
    
    def display(self):
        for r in range(3):
            row = []
            for c in range(3):
                if (r, c) == self.positions['P1']:
                    row.append('P1')
                elif (r, c) == self.positions['AI']:
                    row.append('AI')
                else:
                    row.append('--')
            print(" ".join(row))
        print()
    
    def get_valid_moves(self, player):
        r, c = self.positions[player]
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3 and (nr, nc) != self.positions['P1' if player == 'AI' else 'AI']:
                moves.append((nr, nc))
        return moves
    
    def move(self, player, new_pos):
        if new_pos in self.get_valid_moves(player):
            self.positions[player] = new_pos
            return True
        return False

# Heuristic function (chasing the player)
def heuristic(position):
    player_pos = board.positions['P1']
    return - (abs(player_pos[0] - position[0]) + abs(player_pos[1] - position[1]))  # Minimize distance to player

# AI using state search
class AI:
    def __init__(self):
        pass
    
    def choose_move(self, board):
        possible_moves = board.get_valid_moves('AI')
        if not possible_moves:
            return None
        
        # Evaluate moves based on heuristic
        best_move = max(possible_moves, key=heuristic)
        return best_move

# Game loop
board = Board()
ai = AI()
player_turn = True

while True:
    board.display()
    if player_turn:
        print("Your turn! Choose a move:")
        moves = board.get_valid_moves('P1')
        for i, move in enumerate(moves):
            print(f"{i}: Move to {move}")
        choice = int(input("Enter move index: "))
        board.move('P1', moves[choice])
    else:
        print("AI's turn...")
        ai_move = ai.choose_move(board)
        if ai_move:
            board.move('AI', ai_move)
    
    player_turn = not player_turn
