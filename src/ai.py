import random

piece_score = {"K": 0, "Q": 8, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_best_move_min_max(gs, valid_moves):
    turn_multi = 1 if gs.white_to_move else -1
    max_score = -CHECKMATE 
    best_move = None
    for player_move in valid_moves:
        gs.make_move(player_move)
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        score = turn_multi * score_material(gs.board)
        if score > max_score:
            max_score = score
            best_move = player_move
        gs.undo_move()
    return best_move

"""
Helper method to make first recursive call
"""
def find_best_move(gs, valid_moves):
    global next_move, counter
    counter = 0
    next_move = None
    random.shuffle(valid_moves)
    # find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    print("moves evaulated: ", counter)
    return next_move

def find_move_min_max(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_material(gs.board)
    
    if gs.white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs,next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

def find_move_nega_max(gs, valid_moves, depth, turn_multi):
    global next_move
    if depth == 0:
        return turn_multi * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max(gs, next_moves, depth -1, -turn_multi)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

    return max_score

def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multi):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multi * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth -1, -beta, -alpha, -turn_multi)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score

# if a positive score good for white meaning white if meaning for not black is winning
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score

"""
Score the board based on material
"""
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score

