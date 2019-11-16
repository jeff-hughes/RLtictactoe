class TicTacToe():
    def __init__(self):
        self.player1 = None
        self.player2 = None

        self.turn = 'X'
        self.player_turn = None

        self.tally = {
            'X': 0,
            'Y': 0,
            'T': 0
        }

        self.init_game()

    def init_game(self):
        pass

    def play_game(self):
        pass


def print_board(state):
    st_fmt = [' ' if s == '_' else s for s in state]
    print(' {} | {} | {} '.format(*st_fmt[0:3]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*st_fmt[3:6]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*st_fmt[6:9]))


def check_win(state):
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
            [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for line in wins:
        s = state[line[0]] + state[line[1]] + state[line[2]]
        if s == 'XXX':
            return 'X'
        elif s == 'OOO':
            return 'O'
    return -1


def main():
    state = ['X', 'X', 'X', '_', '_', 'O', '_', '_', '_']
    print_board(state)
    print(check_win(state))

    new_game = input('Do you want to start a new game? (Y/n)')
    if new_game == 'Y' or new_game == 'y':
        game = TicTacToe()
        human = input(
            'Is there a human player? (Otherwise, we are doing training.) (Y/n)')
        if human == 'Y' or human == 'y':
            game.init_game()
        else:
            game.init_game()


if __name__ == "__main__":
    main()
