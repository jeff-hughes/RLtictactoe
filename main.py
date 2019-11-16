from abc import abstractmethod
import random


def print_board(state):
    print(' {} | {} | {} '.format(*state[0:3]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*state[3:6]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*state[6:9]))


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

    def init_game(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def play_game(self):
        pass

    def print_board(self, state):
        st_fmt = [' ' if s == '_' else s for s in state]
        print_board(st_fmt)

    def check_win(self, state):
        wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
                [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
        for line in wins:
            s = state[line[0]] + state[line[1]] + state[line[2]]
            if s == 'XXX':
                return 'X'
            elif s == 'OOO':
                return 'O'
        return -1


class Player():
    def __init__(self, name, exploration_factor=1):
        self.name = name
        self.exploration_factor = exploration_factor

    @abstractmethod
    def make_move(self, state):
        pass


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def make_move(self, state):
        avail_opts = set([k for k, v in enumerate(state) if v == '_'])
        st_fmt = [k if v == '_' else ' ' for k, v in enumerate(state)]
        print_board(st_fmt)

        choice = None
        while choice not in avail_opts:
            choice = int(input('Choose your move: '))
        return choice


def main():
    # state = ['X', 'X', 'X', '_', '_', 'O', '_', '_', '_']
    # print_board(state)
    # print(check_win(state))

    new_game = input('Do you want to start a new game? (Y/n)')
    if new_game == 'Y' or new_game == 'y':
        game = TicTacToe()
        human = input(
            'Is there a human player? (Otherwise, we are doing training.) (Y/n)')
        if human == 'Y' or human == 'y':
            which_player = random.randint(1, 2)
            if which_player == 1:
                print('You will be Player 1, playing X.')
                game.init_game('human', 'robot')
            else:
                print('You will be Player 2, playing O.')
                game.init_game('robot', 'human')
        else:
            game.init_game('robot', 'robot')


if __name__ == "__main__":
    main()
