import pygame
import sys
import math
from copy import deepcopy

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 680, 680
ROWS, COLS = 10, 10  # 10x10 board
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
CROWN = (255, 215, 0)  # Gold color for kings
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (211, 84, 0)

# Setup the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checker Game')

class Piece:
    PADDING = 12  # Slightly smaller padding for 10x10
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            # Draw crown symbol for kings
            pygame.draw.circle(win, CROWN, (self.x, self.y), radius // 1.8)
            # Add star points to make crown more visible
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi / 2
                outer_x = self.x + (radius // 2) * 0.8 * math.cos(angle)
                outer_y = self.y + (radius // 2) * 0.8 * math.sin(angle)
                inner_x = self.x + (radius // 3) * math.cos(angle + math.pi / 5)
                inner_y = self.y + (radius // 3) * math.sin(angle + math.pi / 5)
                pygame.draw.polygon(win, CROWN, [
                    (self.x, self.y),
                    (outer_x, outer_y),
                    (inner_x, inner_y)
                ])

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 20  # 20 pieces each for 10x10
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return enhanced_evaluate(self)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            if not piece.king:  # Only promote if not already a king
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 5:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            if piece != 0:
                self.board[piece.row][piece.col] = 0
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        
        # Check for no valid moves (stalemate)
        red_has_moves = any(self.all_valid_moves(RED).values())
        white_has_moves = any(self.all_valid_moves(WHITE).values())
        
        if not red_has_moves:
            return WHITE
        if not white_has_moves:
            return RED
        
        return None
        
    def all_valid_moves(self, color):
        moves = {}
        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)
            if valid_moves:
                moves[piece] = valid_moves
        return moves

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
        self.font = pygame.font.SysFont('comic sans', 70)
        self.small_font = pygame.font.SysFont('comic sans', 40)
        self.medium_font = pygame.font.SysFont('comic sans', 50)
        self.ai_thinking = False
        self.last_move_time = 0
        self.move_delay = 500  # milliseconds

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        self.draw_turn_indicator()
        if self.ai_thinking:
            self.draw_thinking_text()
        if self.game_over:
            self.draw_game_over()
        pygame.display.update()


    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.game_over = False
        self.winner = None
        self.ai_thinking = False

    def get_winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            
            # Check for additional jumps
            if skipped and self.board.get_valid_moves(self.selected).get((row, col), None):
                return False  # Don't change turn, allow for multiple jumps
            
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 12)

    def draw_turn_indicator(self):
        turn_text = "Turn: Red" if self.turn == RED else "AI Thinking..."
        color = RED if self.turn == RED else GREY
        text = self.small_font.render(turn_text, 1, color)
        self.win.blit(text, (WIDTH - text.get_width() - 10, 10))

    def draw_thinking_text(self):
        text = self.small_font.render("AI is thinking...", 1, GREY)
        self.win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

        # Check for winner after each turn
        winner = self.get_winner()
        if winner:
            self.game_over = True
            self.winner = winner

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()

    def draw_game_over(self):
        winner = self.board.winner()
        if winner == RED:
            text = "Red Player Wins!"
            color = RED
        elif winner == WHITE:
            text = "White Player Wins!"
            color = WHITE
        else:
            text = "Game Over: It's a Draw!"
            color = GREY
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180 alpha (semi-transparent)
        self.win.blit(overlay, (0, 0))
        
        # Render the game over text
        font = pygame.font.SysFont('comicsans', 70)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.win.blit(text_surface, text_rect)
        
        # Add a "Click to exit" message
        small_font = pygame.font.SysFont('comicsans', 30)
        exit_text = small_font.render("Click anywhere to exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        self.win.blit(exit_text, exit_rect)
        
        pygame.display.update()
        
        # Wait for user click to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    pygame.quit()
                    sys.exit()
            pygame.time.delay(100)

def minimax(position, depth, max_player, game, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or position.winner() is not None:
        return enhanced_evaluate(position), position

    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, WHITE, game):
            evaluation = minimax(move, depth-1, False, game, alpha, beta)[0]
            maxEval = max(maxEval, evaluation)
            alpha = max(alpha, evaluation)
            if maxEval == evaluation:
                best_move = move
            if beta <= alpha:
                break
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, RED, game):
            evaluation = minimax(move, depth-1, True, game, alpha, beta)[0]
            minEval = min(minEval, evaluation)
            beta = min(beta, evaluation)
            if minEval == evaluation:
                best_move = move
            if beta <= alpha:
                break
        return minEval, best_move

def enhanced_evaluate(board):
    # Piece count evaluation
    piece_score = (board.white_left - board.red_left) * 1.0
    
    # King evaluation (kings are more valuable)
    king_score = (board.white_kings * 2.0 - board.red_kings * 2.0)  # Increased king value for 10x10
    
    # Positional evaluation
    positional_score = 0
    center_rows = range(3, 7)  # Center rows for 10x10 board
    center_cols = range(3, 7)  # Center columns for 10x10 board
    
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.board[row][col]
            if piece != 0:
                # Central control bonus (more important in 10x10)
                distance_to_center = abs(col - COLS//2) + abs(row - ROWS//2)
                center_bonus = (COLS//2 - distance_to_center) * 0.15  # Increased center bonus
                
                if piece.color == WHITE:
                    positional_score += center_bonus
                    # King mobility bonus
                    if piece.king:
                        positional_score += 0.8  # Kings are very valuable in 10x10
                        # Bonus for being on opponent's side
                        if row < ROWS//2:
                            positional_score += 0.4
                        # Extra bonus for central control
                        if row in center_rows and col in center_cols:
                            positional_score += 0.3
                else:
                    positional_score -= center_bonus
                    if piece.king:
                        positional_score -= 0.8
                        if row > ROWS//2:
                            positional_score -= 0.4
                        if row in center_rows and col in center_cols:
                            positional_score -= 0.3
    
    # Aggression bonus (pieces closer to promotion)
    aggression_score = 0
    white_pieces = board.get_all_pieces(WHITE)
    red_pieces = board.get_all_pieces(RED)
    
    for piece in white_pieces:
        if not piece.king:
            aggression_score += (ROWS - 1 - piece.row) * 0.25  # More aggressive in 10x10
    
    for piece in red_pieces:
        if not piece.king:
            aggression_score -= piece.row * 0.25  # More aggressive in 10x10
    
    # Back row defense bonus (more important in 10x10)
    back_row_score = 0
    # Check white back row (row 0)
    for col in range(COLS):
        piece = board.board[0][col]
        if piece != 0 and piece.color == WHITE and not piece.king:
            back_row_score += 0.4  # Stronger defense bonus
    
    # Check red back row (row ROWS-1)
    for col in range(COLS):
        piece = board.board[ROWS-1][col]
        if piece != 0 and piece.color == RED and not piece.king:
            back_row_score -= 0.4
    
    # Mobility bonus (number of available moves - more important in 10x10)
    mobility_score = 0
    white_moves = len(board.all_valid_moves(WHITE))
    red_moves = len(board.all_valid_moves(RED))
    mobility_score = (white_moves - red_moves) * 0.15  # Increased mobility importance
    
    # King mobility bonus (separate from piece mobility)
    king_mobility_score = 0
    white_kings = board.get_all_pieces(WHITE)
    red_kings = board.get_all_pieces(RED)
    
    for king in white_kings:
        if king.king:
            king_moves = len(board.get_valid_moves(king))
            king_mobility_score += king_moves * 0.1
    
    for king in red_kings:
        if king.king:
            king_moves = len(board.get_valid_moves(king))
            king_mobility_score -= king_moves * 0.1
    
    return (piece_score + king_score + positional_score + 
            aggression_score + back_row_score + 
            mobility_score + king_mobility_score)

def simulate_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)
    return board

def get_all_moves(board, color, game):
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, game, skip)
            moves.append(new_board)
    
    return moves

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(60)
        
        if game.game_over:
            game.draw_game_over()  # This will handle the display and exit
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if not game.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if game.turn == RED:
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                    
                    if game.selected:
                        result = game._move(row, col)
                        if not result:
                            game.select(row, col)
                    else:
                        game.select(row, col)

        if not game.game_over and game.turn == WHITE:
            current_time = pygame.time.get_ticks()
            if current_time - game.last_move_time > game.move_delay:
                game.ai_thinking = True
                game.update()
                
                # AI move logic
                best_move = None
                max_depth = 3
                total_pieces = game.board.red_left + game.board.white_left
                if total_pieces < 15: max_depth = 4
                elif total_pieces < 10: max_depth = 5
                elif total_pieces < 6: max_depth = 6
                
                for depth in range(3, max_depth + 1):
                    value, new_board = minimax(game.get_board(), depth, True, game)
                    if new_board:
                        best_move = new_board
                
                if best_move:
                    game.ai_move(best_move)
                    game.last_move_time = current_time
                game.ai_thinking = False

        game.update()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()