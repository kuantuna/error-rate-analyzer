import chess.pgn
import chess.engine
import chess

pgn_file_name="test2"
games = []
engine_path = "C:\\Program Files\\ChessBase\\Engines\\Lc0\\lc0"
color_list = [chess.WHITE, chess.BLACK] # Notes that I was white on the first game, black on the second and etc.
start_moves = [2, 3]  # Notes that I want to start analyzing the game with the fifth move
analysis_time = 10  # seconds
evaluation_list = []

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
    for game, color, start_move in zip(games, color_list, start_moves):
        board = game.board()
        start_ply = start_move*2-color-1
        node = game
        for move in game.mainline_moves():
            node = node.variations[0]
            board.push(move)
            if board.is_game_over():
                print("Game is over, please check provided start move number")
                break
            if board.ply() < start_ply: continue
            if board.turn == color:
                best_move_analysis = engine.analyse(board, chess.engine.Limit(time=analysis_time))
                node.add_variation(best_move_analysis["pv"][0], comment=str(best_move_analysis["score"].wdl().pov(color).expectation()*100))
                board.push(node[0].move)
                current_move_analysis = engine.analyse(board, chess.engine.Limit(time=analysis_time))
                board.pop()
                node[0].comment = str(current_move_analysis["score"].wdl().pov(color).expectation()*100)
                print(game)
        
    '''
    CLOSE THE ENGINE
    '''
    engine.quit()

if __name__ == "__main__":
    main()



