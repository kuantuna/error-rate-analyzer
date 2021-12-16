import chess, chess.engine, chess.pgn, random

pgn_file_name = "test4"
games = []
engine_path = "C:\\Program Files\\ChessBase\\Engines\\lc0-v0.28.0-windows-gpu-nvidia-cudnn\\lc0"
analysis_time = 10

def main():
    pgn_file = open("./pgns/{}.pgn".format(pgn_file_name))

    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None: break
        games.append(game)


    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    number_of_plys = []
    for game in games:
        counter = 0
        for _ in game.mainline_moves():
            counter += 1
        if counter > 2: number_of_plys.append(counter)
    random_plys = [random.randint(1, ply-1) for ply in number_of_plys]

    print(random_plys)
    for game, random_ply in zip(games, random_plys):
        board = game.board()
        node = game
        for move in game.mainline_moves():
            board.push(move)
            node = node.variations[0]
            random_ply -= 1
            if random_ply == 0:
                evaluations = []
                for legal_move in board.legal_moves:
                    board.push(legal_move)
                    best_move_analysis = engine.analyse(board, chess.engine.Limit(time=analysis_time))
                    best_move_expectation = best_move_analysis["score"].wdl().pov(not board.turn).expectation()*100
                    board.pop()
                    evaluations.append({"move": legal_move, "expectation": best_move_expectation})
                    print(evaluations)
                evaluations = sorted(evaluations, key=lambda d: d['expectation'], reverse=True)
                print("*********************************************************************")
                print(evaluations)
                for evaluation in evaluations:
                    node.add_variation(evaluation["move"], comment="%"+"{:.2f}".format(evaluation["expectation"]))
        print(game, file=open("./output/test-generator.pgn", "w"), end="\n\n")

    engine.quit()

if __name__ == "__main__":
    main()