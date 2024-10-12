import pygame
import engine
import ai


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 170
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSIONS = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSIONS
MAX_FPS = 30
IMAGES = {}

def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ'] 
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load('images/'+ piece +".png"), (SQ_SIZE, SQ_SIZE))

def main():
    pygame.init()
    pygame.display.set_caption('Chess-ai')
    screen = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))
    move_log_font = pygame.font.SysFont("Arial", 18, True, False)
    gs = engine.gamestate()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False
    load_images() 
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False
    player_one = False # if humans is playing this will be true if not it will be false
    player_two = False # same above but for black
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = pygame.mouse.get_pos()
                    row = location[1] // SQ_SIZE
                    col = location[0] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8:
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
                # key handler
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
                elif e.key == pygame.K_r:
                    gs = engine.gamestate()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        # AI move finder
        if not game_over and not human_turn:
            AI_Move = ai.find_best_move(gs, valid_moves)
            if AI_Move is None:
                AI_Move = ai.find_random_move(valid_moves)

            gs.make_move(AI_Move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)

            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font)
        
        if gs.checkmate or gs.stalemate:
            game_over = True
            text = "Stalemate" if gs.stalemate else "Black Wins by Checkmate!" if gs.white_to_move else "White Wins by Checkmate!"
            draw_endgame_text(screen, text)

        clock.tick(MAX_FPS)
        pygame.display.flip()

def highlight_square(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected

        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(pygame.Color('green'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font):
    draw_board(screen)
    highlight_square(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, move_log_font)


def draw_board(screen):
    global colors
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_move_log(screen, gs, font):
    move_log_rect = pygame.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color('black'), move_log_rect)
    move_log = gs.move_log
    move_texts = []

    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + str(move_log[i]) + " "

        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + " "

        move_texts.append(move_string)

    moves_per_row = 2
    padding = 5
    text_y = padding
    line_spacing = 2

    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, pygame.Color('Gray'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location.move(2, 2))
        text_y += text_object.get_height() + line_spacing

def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frame_per_square = 10
    frame_count = (abs(dR) + abs(dC)) * frame_per_square

    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)

        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pygame.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, end_square)

        if move.piece_captured != "--":
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = pygame.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.piece_captured], end_square)

        screen.blit(IMAGES[move.piece_moved], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick()

def draw_endgame_text(screen, text):
    font = pygame.font.SysFont("Arial", 32, True, False)
    text_object = font.render(text, 0, pygame.Color('Gray'))
    text_location = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    text_object = font.render(text, 0, pygame.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))

if __name__ == "__main__":
    main()
