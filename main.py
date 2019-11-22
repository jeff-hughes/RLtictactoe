from abc import abstractmethod
import random
from datetime import datetime
import numpy as np
import pickle
import csv
import os

debug = False


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
            'O': 0,
            'T': 0,
            'total': 0
        }
        self.detailed_tally = {
            'game': [],
            'X': [],
            'O': [],
            'T': [],
            'cum_X': [],
            'cum_O': [],
            'cum_T': []
        }

    def init_game_set(self, player1, player2, num_games=1):
        self.player1 = player1
        self.player2 = player2
        self.player_turn = player1

        if isinstance(self.player1, HumanPlayer) or isinstance(self.player2, HumanPlayer):
            self.human_player = True
        else:
            self.human_player = False

        for i in range(num_games):
            self.play_game(i)

        if num_games > 1:
            print('Final score:')
            print('{}: {} wins, {}: {} wins, {} tie games'.format(
                  self.player1.name, self.tally['X'], self.player2.name, self.tally['O'], self.tally['T']))

        if not self.human_player:
            save = input('Save detailed tally? (Y/n) ')
            if save == 'Y' or save == 'y':
                time = datetime.now().strftime("%Y%m%d_%H%M%S")
                keys = ['game', 'X', 'O', 'T', 'cum_X', 'cum_O', 'cum_T']
                with open('tally_{}.csv'.format(time), 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(keys)
                    writer.writerows(
                        zip(*[self.detailed_tally[key] for key in keys]))

    def play_game(self, game_num):
        # reset the board
        self.state = ['_', '_', '_', '_', '_', '_', '_', '_', '_']
        self.move_num = 0
        self.turn = 'X'
        self.player_turn = self.player1

        while self.move_num < 9:
            move = self.player_turn.make_move(self.state)
            if debug:
                print('{} chooses {}'.format(self.turn, move))
            self.state[move] = self.turn

            if debug and not self.human_player:
                self.print_board()

            if self.human_player:
                self.print_board()
                print()

            winner = self.check_win()
            if winner != -1:
                # game has ended
                self.record_win(game_num, winner)

                if self.human_player:
                    # if a human is playing, we'll print a nice message
                    if winner == 'X':
                        print('{} wins the game!'.format(self.player1.name))
                    elif winner == 'O':
                        print('{} wins the game!'.format(self.player2.name))
                    else:
                        print('Tie game.')
                else:
                    # both players update the final board state
                    self.player1.learn_state(self.state.copy(), winner)
                    self.player2.learn_state(self.state.copy(), winner)

                    # otherwise, we only want to print to screen occasionally
                    if self.tally['total'] % 50 == 0:
                        print('After {} games... {}: {} wins, {}: {} wins, {} tie games'.format(
                            self.tally['total'], self.player1.name, self.tally['X'], self.player2.name, self.tally['O'], self.tally['T']))
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

    def record_win(self, game_num, winner):
        self.tally[winner] += 1
        self.tally['total'] += 1

        self.detailed_tally['game'].append(game_num+1)

        for tag in ['X', 'O', 'T']:
            add = 1 if winner == tag else 0
            self.detailed_tally[tag].append(add)

            if game_num > 0:
                prev_score = self.detailed_tally['cum_{}'.format(
                    tag)][game_num-1]
                self.detailed_tally['cum_{}'.format(
                    tag)].append(prev_score + add)
            else:
                self.detailed_tally['cum_{}'.format(tag)].append(add)


class Player():
    def __init__(self, name, tag):
        self.name = name  # string to identify player
        self.tag = tag    # which player they are ('X' or 'O')

    @abstractmethod
    def make_move(self, state):
        pass

    @abstractmethod
    def learn_state(self, new_state, winner):
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
    def __init__(self, name, tag, learn=True, model=None, alpha=.2, exploration_factor=1):
        super().__init__(name, tag)
        self.learn = learn
        self.alpha = alpha
        self.exploration_factor = exploration_factor
        self.prev_state = '_________'

        if model is not None:
            self.values = model
        else:
            self.values = dict()

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
        elif winner == -1:
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
    game = TicTacToe()
    trained_model = {}

    if os.path.exists('model_values.pkl'):
        load_trained_agent = input('Load trained model from "model_values.pkl"? (Y/n) ')
        if load_trained_agent == 'Y' or load_trained_agent == 'y':
            with open('model_values.pkl', 'rb') as f:
                trained_model = pickle.load(f)

    if not trained_model:
        num_iter = int(input('How many iterations do you want to train for? '))
        game.init_game_set(QPlayer('QPlayer 1', 'X', learn=True),
                           QPlayer('QPlayer 2', 'O', learn=True), num_iter)
        trained_model['X'] = game.player1.values
        trained_model['O'] = game.player2.values
        
        save_model = input('Do you want to save the trained model to \
            "model_values.pkl"? (Y/n) ')
        if save_model == 'Y' or save_model == 'y':
            with open('model_values.pkl', 'wb') as f:
                pickle.dump(trained_model, f, protocol=pickle.HIGHEST_PROTOCOL)

    human = input('Do you want to play against the computer? (Y/n) ')
    if human == 'Y' or human == 'y':
        playing = True
        while playing:
            game = TicTacToe()  # reset
            which_player = random.randint(1, 2)
            if which_player == 1:
                print('You will be Player 1, playing X.')
                game.init_game_set(HumanPlayer('Puny human', 'X'),
                    QPlayer('QPlayer', 'O', learn=False, model=trained_model['O']))
            else:
                print('You will be Player 2, playing O.')
                game.init_game_set(QPlayer('QPlayer', 'X', learn=False,
                    model=trained_model['X']), HumanPlayer('Puny human', 'O'))
            play_again = input('Do you want to play again? (Y/n) ')
            if play_again != 'Y' and play_again != 'y':
                break

    print('k bye!')

if __name__ == "__main__":
    main()
