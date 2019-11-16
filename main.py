from abc import abstractmethod
import random
import numpy as np


def print_board(state):
    print(' {} | {} | {} '.format(*state[0:3]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*state[3:6]))
    print('---+---+---')
    print(' {} | {} | {} '.format(*state[6:9]))


class TicTacToe():
    def __init__(self):
        self.state = ['_', '_', '_', '_', '_', '_', '_', '_', '_']
        self.move_num = 0

        self.player1 = None
        self.player2 = None

        self.turn = 'X'
        self.player_turn = None

        self.tally = {
            'X': 0,
            'Y': 0,
            'T': 0,
            'total': 0
        }

    def init_game(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.player_turn = player1

        if isinstance(self.player1, HumanPlayer) or isinstance(self.player2, HumanPlayer):
            self.human_player = True
        else:
            self.human_player = False

        self.play_game()

    def play_game(self):
        while self.move_num < 9:
            print(self.state)
            move = self.player_turn.make_move(self.state)
            print('{} chooses {}'.format(self.turn, move))
            self.state[move] = self.turn

            winner = self.check_win()
            if winner != -1:
                # game has ended
                self.tally[winner] += 1
                self.tally['total'] += 1
                if self.human_player:
                    # if a human is playing, we'll print a nice message
                    if winner != 'T':
                        print('{} wins the game!'.format(winner))
                    else:
                        print('Tie game.')
                else:
                    # both players update the final board state
                    self.player1.learn_state(self.state.copy(), winner)
                    self.player2.learn_state(self.state.copy(), winner)

                    # otherwise, we only want to print to screen occasionally
                    if self.tally['total'] % 50:
                        print('{}: {} wins, {}: {} wins, {} tie games'.format(
                            self.player1.name, self.tally['X'], self.player2.name, self.tally['Y'], self.tally['T']))
                break
            else:
                # switch to the other player and continue
                if self.turn == 'X':
                    self.player_turn = self.player2
                    self.turn = 'O'
                    # player 2 gets a chance to learn right before their turn
                    self.player2.learn_state(self.state.copy(), winner)
                else:
                    self.player_turn = self.player1
                    self.turn = 'X'
                    # player 1 gets a chance to learn right before their turn
                    self.player1.learn_state(self.state.copy(), winner)

    def print_board(self):
        st_fmt = [' ' if s == '_' else s for s in self.state]
        print_board(st_fmt)

    def check_win(self):
        wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
                [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
        for line in wins:
            s = self.state[line[0]] + self.state[line[1]] + self.state[line[2]]
            if s == 'XXX':
                return 'X'
            elif s == 'OOO':
                return 'O'
        if '_' in self.state:
            return -1
        else:
            return 'T'


class Player():
    def __init__(self, name, tag):
        self.name = name  # string to identify player
        self.tag = tag    # which player they are ('X' or 'O')

    @abstractmethod
    def make_move(self, state):
        pass

    @abstractmethod
    def learn_state(self, prev_state, new_state, winner):
        pass


class HumanPlayer(Player):
    def __init__(self, name, tag):
        super().__init__(name, tag)

    def make_move(self, state):
        avail_opts = [k for k, v in enumerate(state) if v == '_']
        st_fmt = [k if v == '_' else ' ' for k, v in enumerate(state)]
        print_board(st_fmt)

        choice = None
        while choice not in avail_opts:
            choice = int(input('Choose your move: '))
        return choice


class QPlayer(Player):
    def __init__(self, name, tag, learn=True, alpha=.2, exploration_factor=1):
        super().__init__(name, tag)
        self.learn = learn
        self.alpha = alpha
        self.exploration_factor = exploration_factor
        self.values = dict()
        self.prev_state = ''

        if self.tag == 'X':
            self.op_tag = 'O'
        else:
            self.op_tag = 'X'

    def learn_state(self, new_state, winner):
        new_state = ''.join(new_state)
        if self.tag in new_state:
            if self.prev_state in self.values.keys():
                v_s = self.values[self.prev_state]
            else:
                v_s = 0

            R = self.reward(winner)

            if new_state in self.values.keys() and winner is None:
                v_s_tag = self.values[new_state]
            else:
                v_s_tag = 0

            self.values[self.prev_state] = v_s + self.alpha*(R + v_s_tag - v_s)
        self.prev_state = new_state

    def calc_value(self, state):
        if state in self.values.keys():
            return self.values[state]
        else:
            return None

    def reward(self, winner):
        if winner is self.tag:
            R = 1
        elif winner is None:
            R = 0
        elif winner == 'T':
            R = 0.5
        else:
            R = -1
        return R

    def make_move(self, state):
        if self.learn:
            p = random.uniform(0, 1)
            if p < self.exploration_factor:
                return self.make_optimal_move(state)
            else:
                avail_opts = [k for k, v in enumerate(state) if v == '_']
                return random.choice(avail_opts)
        else:
            return self.make_optimal_move(state)

    def make_optimal_move(self, state):
        avail_opts = [k for k, v in enumerate(state) if v == '_']

        if len(avail_opts) == 1:
            return avail_opts[0]

        options_list = []
        v_best = -float('Inf')

        state = ''.join(state.copy())

        # check value of every option
        for idx in avail_opts:
            v_temp = []
            temp_state = state[:idx] + self.tag + state[idx + 1:]

            # check the available options that would give our opponent, and calculate value
            moves_op = [k for k, v in enumerate(temp_state) if v == '_']
            for idy in moves_op:
                temp_state_op = temp_state[:idy] + \
                    self.op_tag + temp_state[idy + 1:]
                v_temp.append(self.calc_value(temp_state_op))

            # deletes Nones
            v_temp = list(filter(None.__ne__, v_temp))

            if len(v_temp) > 0:
                v_temp = np.min(v_temp)
            else:
                # encourage exploration
                v_temp = 1

            if v_temp > v_best:
                options_list = [idx]
                v_best = v_temp
            elif v_temp == v_best:
                options_list.append(idx)

        if len(options_list) == 1:
            return options_list[0]
        else:
            return random.choice(options_list)


def main():
    # state = ['X', 'X', 'X', '_', '_', 'O', '_', '_', '_']
    # print_board(state)
    # print(check_win(state))

    new_game = input('Do you want to start a new game? (Y/n) ')
    if new_game == 'Y' or new_game == 'y':
        game = TicTacToe()
        human = input(
            'Is there a human player? (Otherwise, we are doing training.) (Y/n) ')
        if human == 'Y' or human == 'y':
            which_player = random.randint(1, 2)
            if which_player == 1:
                print('You will be Player 1, playing X.')
                game.init_game(HumanPlayer('Puny human', 'X'),
                               QPlayer('QPlayer', 'O', learn=False))
            else:
                print('You will be Player 2, playing O.')
                game.init_game(QPlayer('QPlayer', 'X', learn=False),
                               HumanPlayer('Puny human', 'O'))
        else:
            game.init_game(QPlayer('QPlayer X', 'X', learn=True),
                           QPlayer('QPlayer O', 'O', learn=True))


if __name__ == "__main__":
    main()
