import chess.pgn
import chess.engine
import chess

pgn_file_name="test"
games = []
engine_path = "C:\\Program Files\\ChessBase\\Engines\\lc0-v0.28.0-windows-gpu-nvidia-cudnn\\lc0"
color_list = [chess.WHITE, chess.BLACK] # Notes that I was white on the first game, black on the second and etc.
start_move_number_numbers = [2, 3]  # Notes that I want to start analyzing the game with the fifth move
analysis_time = 10  # seconds
evaluation_list = []
error_log_threshold = 5

def round_up(value):
    return int(value) + (value % 1 > 0)

def calculate_error_for_move(current_move, best_move, current_move_expectation, best_move_expectation):
    return 0 if (current_move_expectation > best_move_expectation) or (current_move == best_move) else best_move_expectation - current_move_expectation

def log_to_pgn(node, current_move, best_move, current_move_expectation, best_move_expectation, error):
    if current_move != best_move:
        node.add_variation(best_move, comment="{:.2f}".format(best_move_expectation))
    node[0].comment = str(current_move_expectation) + " (" + "{:.2f}".format(error) + "%)"
    if(error >= 5 and error < 10): node[0].nags = [chess.pgn.NAG_DUBIOUS_MOVE]
    elif(error >= 10 and error < 20): node[0].nags = [chess.pgn.NAG_MISTAKE]
    elif(error >= 20): node[0].nags = [chess.pgn.NAG_BLUNDER]

def calculate_error_for_game(evaluation_list):
    sum = 0
    for evaluation in evaluation_list:
        sum += evaluation["error"]
    error = sum/len(evaluation_list)
    return "{:.2f}".format(error)


def main():
    '''
    LOAD ALL THE GAMES FROM THE PGN
    '''
    pgn_file = open("./pgns/{}.pgn".format(pgn_file_name))

    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None: break
        games.append(game)

    '''
    OPEN THE ENGINE
    '''
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)


    '''
    ANALYZE WITH THE ENGINE
    '''
    for game, color, start_move_number in zip(games, color_list, start_move_number_numbers):
        board = game.board()
        start_ply = start_move_number*2-color-1  # Keeps the start move number
        node = game  # Keeps the node for every move
        for move in game.mainline_moves():
            node = node.variations[0]
            board.push(move)
            if board.is_game_over():
                print("Game is over, please check provided start move number")
                break
            if board.ply() < start_ply: continue
            if board.turn == color:
                best_move_analysis = engine.analyse(board, chess.engine.Limit(time=analysis_time))
                best_move = best_move_analysis["pv"][0]
                best_move_expectation = best_move_analysis["score"].wdl().pov(color).expectation()*100

                current_move = node[0].move
                board.push(current_move)
                current_move_analysis = engine.analyse(board, chess.engine.Limit(time=analysis_time))
                current_move_expectation = current_move_analysis["score"].wdl().pov(color).expectation()*100
                board.pop()

                error = calculate_error_for_move(current_move, best_move, current_move_expectation, best_move_expectation)
                if error >= error_log_threshold:
                    log_to_pgn(node, current_move, best_move, current_move_expectation, best_move_expectation, error)

                evaluation_list.append({
                    "move_number": round_up(node.ply()/2), 
                    "best_move": best_move, 
                    "current_move": current_move,
                    "best_move_exp": best_move_expectation,
                    "current_move_exp": current_move_expectation,
                    "error": error
                })
                print(game)

        game.variations[0].starting_comment = "Error: {}%".format(calculate_error_for_game(evaluation_list))
        print(game, file=open("./output/test-analysis.pgn", "w"), end="\n\n")
        
    '''
    CLOSE THE ENGINE
    '''
    engine.quit()

if __name__ == "__main__":
    main()



