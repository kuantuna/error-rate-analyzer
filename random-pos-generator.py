import chess
import chess.engine
import chess.pgn
import random
import numpy as np

pgn_file_name = "test5"
games = []
engine_path = "C:\\Users\\Tuna\\Desktop\\Chess\\Engines\\Fat Frtiz 2 211108\\Windows\\FatFritz2 x64 211108-avx2"
analysis_time = 10


def main():
    pgn_file = open("./pgns/{}.pgn".format(pgn_file_name))
    global games
    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        games.append(game)

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    number_of_plys = []
    short_game_indexes = []
    for idx, game in enumerate(games):
        counter = 0
        for _ in game.mainline_moves():
            counter += 1
        if counter > 10:
            number_of_plys.append(counter)
        else:
            short_game_indexes.append(idx)
    if len(short_game_indexes) != 0:
        games = np.delete(games, short_game_indexes).tolist()
    random_plys = [random.randint(11, ply-1) for ply in number_of_plys]

    print(random_plys)
    for game, random_ply in zip(games, random_plys):
        board = game.board()
        node = game
        game.headers["AnalyzedHalfMove"] = str(random_ply)
        game.headers["SideToPlay"] = "White" if random_ply % 2 == 0 else "Black"
        game.headers["Engine"] = "FatFritz2 x64 211108-avx2"
        game.headers["AnalysisTimePerMove"] = str(analysis_time)
        for move in game.mainline_moves():
            board.push(move)
            node = node.variations[0]
            random_ply -= 1
            if random_ply == 0:
                evaluations = []
                for legal_move in board.legal_moves:
                    board.push(legal_move)
                    best_move_analysis = engine.analyse(
                        board, chess.engine.Limit(time=analysis_time))
                    best_move_expectation = best_move_analysis["score"].wdl().pov(
                        not board.turn).expectation()*100
                    board.pop()
                    evaluations.append(
                        {"move": legal_move, "expectation": best_move_expectation})
                    print(evaluations)
                evaluations = sorted(
                    evaluations, key=lambda d: d['expectation'], reverse=True)
                print(
                    "*********************************************************************")
                print(evaluations)
                best_expectation = evaluations[0]["expectation"]
                for evaluation in evaluations:
                    node.add_variation(
                        evaluation["move"], comment="{:.2f}".format(evaluation["expectation"]) + ",{:.2f}".format(best_expectation - evaluation["expectation"]))
        print(game, file=open("./output/test3.pgn", "w"), end="\n\n")

    engine.quit()


if __name__ == "__main__":
    main()
