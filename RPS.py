import os
import time

limit = 1000
default_stat_range = 10
verbose_mode = False

def calculate_play_stats(data):
        total_plays = data['w'] + data['l'] + data['t']
        win_freq = sum(data['last_wins'])
        lose_freq = sum(data['last_losses'])
        tie_freq = sum(data['last_ties'])
        win_prob = win_freq / total_plays if total_plays else 0
        lose_prob = lose_freq / total_plays if total_plays else 0
        tie_prob = tie_freq / total_plays if total_plays else 0
        return win_freq, lose_freq, tie_freq, total_plays, win_prob, lose_prob, tie_prob

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def generate_tracker(limit, stat_range, verbose_mode=False):
    new_obj = {
        'limit': limit,
        'verbose': verbose_mode,
        'winning_moves': {'R': 'S', 'P': 'R', 'S': 'P'},
        'counter_move': {'R': 'P', 'S': 'R', 'P': 'S'},
        'player_history': ["R"],
        'opponent_history': [],
        'strategy': [0, 0, 0, 0],
        'opponent_guess': ["", "", "", ""],
        'strategy_guess': ["", "", "", ""],
        'opponent_play_order': {},
        'player_play_order': {},
    }
    new_obj["current_game"] = {
        'count': 0,
        'w': 0,
        'l': 0,
        't': 0,
        'prev_choice': 'random',
        'last_prediction': '',
        'next_prediction': '',
        'predictions': [],
        'prediction_freq_window': stat_range,
    }
    for move in ["strat_1", "strat_2", "strat_3", "strat_4", "random"]:
        new_obj["current_game"][move] = {
            'w': 0,
            'l': 0,
            't': 0,
            'last_wins': [],
            'last_losses': [],
            'last_ties': [],
            'last_plays': [],
            'played_against': [],
            'play_pos': [],
            'stat_freq': stat_range,
        }

    return new_obj

def player(prev_play):
    global tracker
    if prev_play in ["R", "P", "S"]:
        tracker['opponent_history'].append(prev_play)
        track_last_move(prev_play, tracker['player_history'][-1:])
        for i in range(0, 4):
            if tracker['opponent_guess'][i] == prev_play:
                tracker['strategy'][i] += 1
    else:
        reset()

    current_game = tracker["current_game"]
    my_last_ten = tracker['player_history'][-10:]
    if len(my_last_ten) > 0:
        my_most_frequent_move = max(set(my_last_ten), key=my_last_ten.count)
        tracker['opponent_guess'][0] = tracker['counter_move'][my_most_frequent_move]
        tracker['strategy_guess'][0] = tracker['counter_move'][tracker['opponent_guess'][0]]

    if len(tracker['player_history']) > 0:
        my_last_play = tracker['player_history'][-1]
        tracker['opponent_guess'][1] = tracker['counter_move'][my_last_play]
        tracker['strategy_guess'][1] = tracker['counter_move'][tracker['opponent_guess'][1]]

    if len(tracker['opponent_history']) >= 3:
        tracker['opponent_guess'][2] = predict_move(tracker['opponent_history'], 3, tracker['opponent_play_order'])
        tracker['strategy_guess'][2] = tracker['counter_move'][tracker['opponent_guess'][2]]

    if len(tracker['player_history']) >= 2:
        tracker['opponent_guess'][3] = tracker['counter_move'][predict_move(tracker['player_history'], 2, tracker['player_play_order'])]
        tracker['strategy_guess'][3] = tracker['counter_move'][tracker['opponent_guess'][3]]

    best_strategy = tracker['strategy'].index(max(tracker['strategy']))
    guess = tracker['strategy_guess'][best_strategy]

    if tracker['verbose']:
        player_last_play = ''
        opponent_last_play = ''
        if len(tracker['player_history']) > 0:
            player_last_play = tracker['player_history'][-1:][0]
        if len(tracker['opponent_history']) > 0:
            opponent_last_play = tracker['opponent_history'][-1:][0]

        prediction_success = 0
        last_prediction = ''
        if opponent_last_play:
            last_prediction = current_game['last_prediction']
            current_game['predictions'].append(last_prediction == opponent_last_play)
            prediction_success = (sum(current_game['predictions']) / len(current_game['predictions'])) * 100

        current_game['last_prediction'] = tracker['opponent_guess'][best_strategy] if tracker['opponent_guess'][best_strategy] != "" else "S"

        s1_win_freq, s1_lose_freq, s1_tie_freq, s1_total_plays, s1_win_prob, s1_lose_prob, s1_tie_prob = calculate_play_stats(current_game['strat_1'])
        s2_win_freq, s2_lose_freq, s2_tie_freq, s2_total_plays, s2_win_prob, s2_lose_prob, s2_tie_prob = calculate_play_stats(current_game['strat_2'])
        s3_win_freq, s3_lose_freq, s3_tie_freq, s3_total_plays, s3_win_prob, s3_lose_prob, s3_tie_prob = calculate_play_stats(current_game['strat_3'])
        s4_win_freq, s4_lose_freq, s4_tie_freq, s4_total_plays, s4_win_prob, s4_lose_prob, s4_tie_prob = calculate_play_stats(current_game['strat_4'])
        random_win_freq, random_lose_freq, random_tie_freq, random_total_plays, random_win_prob, random_lose_prob, random_tie_prob = calculate_play_stats(current_game['random'])
        
        s1_next_tries = (current_game['strat_1']['w'] / s1_total_plays) * 100 if s1_total_plays else 0
        s2_next_tries = (current_game['strat_2']['w'] / s2_total_plays) * 100 if s2_total_plays else 0
        s3_next_tries = (current_game['strat_3']['w'] / s3_total_plays) * 100 if s3_total_plays else 0
        s4_next_tries = (current_game['strat_4']['w'] / s4_total_plays) * 100 if s4_total_plays else 0
        random_tries = (current_game['random']['w'] / random_total_plays) * 100 if random_total_plays else 0

        last_play_type = current_game["prev_choice"]
        last_play_result = "Tie" if opponent_last_play == player_last_play else "Lose" if opponent_last_play == tracker['counter_move'][player_last_play] else "Win"
        
        current_game['prev_choice'] = f'strat_{str(best_strategy + 1)}'

    if tracker['verbose']:
        clear_screen()
        print_move_header(last_play_type, player_last_play, opponent_last_play, last_play_result, last_prediction, current_game['predictions'], prediction_success)
        print_moves(s1_total_plays, s1_next_tries, s1_win_freq, s1_win_prob, s1_tie_freq, s1_tie_prob, s1_lose_freq, s1_lose_prob,
                        s2_total_plays, s2_next_tries, s2_win_freq, s2_win_prob, s2_tie_freq, s2_tie_prob, s2_lose_freq, s2_lose_prob,
                        s3_total_plays, s3_next_tries, s3_win_freq, s3_win_prob, s3_tie_freq, s3_tie_prob, s3_lose_freq, s3_lose_prob,
                        s4_total_plays, s4_next_tries, s4_win_freq, s4_win_prob, s4_tie_freq, s4_tie_prob, s4_lose_freq, s4_lose_prob,
                        random_total_plays, random_tries, random_win_freq, random_win_prob, random_tie_freq, random_tie_prob, random_lose_freq, random_lose_prob
                        )
        print_move_footer()
        time.sleep(0.075)

    if guess == "":
        guess = "S"
        current_game['prev_choice'] = "random"
    tracker['player_history'].append(guess)
    return guess

def predict_move(history, n, play_order):
    if "".join(history[-n:]) in play_order.keys():
        play_order["".join(history[-n:])] += 1
    else:
        play_order["".join(history[-n:])] = 1
    possible = ["".join(history[-(n - 1) :]) + k for k in ["R", "P", "S"]]
    for pm in possible:
        if not pm in play_order.keys():
            play_order[pm] = 0
    predict = max(possible, key=lambda key: play_order[key])
    return predict[-1]

def print_graph(title, play_type, win_percent, win_freq, win_prob, tie_freq, tie_prob, lose_freq, lose_prob):
    global tracker
    current_game = tracker["current_game"][play_type]
    print(f'| {title}: (Win: {format(win_percent, ".4f")}%)')
    print(f'|     WINS {"".join(" - " if x else "   " for x in current_game["last_wins"][:-1]) + (" o " if current_game["last_wins"] and current_game["last_wins"][-1] else "   ")}    W: {current_game["w"]} [freq: {win_freq}, prob: {format(win_prob, ".4f")}]')
    print(f'|     TIES {"".join(" - " if x else "   " for x in current_game["last_ties"][:-1]) + (" o " if current_game["last_ties"] and current_game["last_ties"][-1] else "   ")}    T: {current_game["t"]} [freq: {tie_freq}, prob: {format(tie_prob, ".4f")}]')
    print(f'|     LOSS {"".join(" - " if x else "   " for x in current_game["last_losses"][:-1]) + (" o " if current_game["last_losses"] and current_game["last_losses"][-1] else "   ")}    L: {current_game["l"]} [freq: {lose_freq}, prob: {format(lose_prob, ".4f")}]')

def print_moves(s1_total_plays, s1_next_tries, s1_win_freq, s1_win_prob, s1_tie_freq, s1_tie_prob, s1_lose_freq, s1_lose_prob,
                      s2_total_plays, s2_next_tries, s2_win_freq, s2_win_prob, s2_tie_freq, s2_tie_prob, s2_lose_freq, s2_lose_prob,
                      s3_total_plays, s3_next_tries, s3_win_freq, s3_win_prob, s3_tie_freq, s3_tie_prob, s3_lose_freq, s3_lose_prob,
                      s4_total_plays, s4_next_tries, s4_win_freq, s4_win_prob, s4_tie_freq, s4_tie_prob, s4_lose_freq, s4_lose_prob,
                      random_total_plays, random_tries, random_win_freq, random_win_prob, random_tie_freq, random_tie_prob, random_lose_freq, random_lose_prob
                      ):
    if s1_total_plays:
        print_graph("STRAT_1", "strat_1", s1_next_tries, s1_win_freq, s1_win_prob, s1_tie_freq, s1_tie_prob, s1_lose_freq, s1_lose_prob)
        print_play_list("strat_1")
    if s2_total_plays:
        print_graph("STRAT_2", "strat_2", s2_next_tries, s2_win_freq, s2_win_prob, s2_tie_freq, s2_tie_prob, s2_lose_freq, s2_lose_prob)
        print_play_list("strat_2")
    if s3_total_plays:
        print_graph("STRAT_3", "strat_3", s3_next_tries, s3_win_freq, s3_win_prob, s3_tie_freq, s3_tie_prob, s3_lose_freq, s3_lose_prob)
        print_play_list("strat_3")
    if s4_total_plays:
        print_graph("STRAT_4", "strat_4", s4_next_tries, s4_win_freq, s4_win_prob, s4_tie_freq, s4_tie_prob, s4_lose_freq, s4_lose_prob)
        print_play_list("strat_4")
    if random_total_plays:
        print_graph("RANDOM", "random", random_tries, random_win_freq, random_win_prob, random_tie_freq, random_tie_prob, random_lose_freq, random_lose_prob)
        print_play_list("random")

def print_move_footer():
    print('\'-------------')

def print_move_header(last_play_type, player_last_play, opponent_last_play, last_play_result, last_prediction, prediction_array, prediction_success):
    global tracker
    print(f'    __________')
    print(f'   / Move: [{len(tracker['opponent_history'])}] Strategy: [{last_play_type}] Last Guess: [{player_last_play}] Opponent Guess: [{opponent_last_play}] Result: [{last_play_result}]')
    print(f'  /  Last Prediction: [{last_prediction}] Result: [{" " if len(prediction_array) == 0 else "CORRECT" if prediction_array[-1:][0] == True else "INCORRECT"}] Correct Predictions: [{format(prediction_success, ".4f")}%]')        
    print(f',-------------')

def print_play_list(play_type, show_plays=True, show_play_num=True):
    global tracker
    print_string = ""
    temp_string = ""
    if show_plays:
        for i in range(len(tracker["current_game"][play_type]["last_plays"])):
            p = tracker["current_game"][play_type]["last_plays"][i]
            o = tracker["current_game"][play_type]["played_against"][i]
            play = p.upper() if tracker['winning_moves'][p] == o else p.lower()
            temp_string += " " + play + " "
        print_string += f'|     You: {temp_string}\n'
        temp_string = ""
        for i in range(len(tracker["current_game"][play_type]["played_against"])):
            p = tracker["current_game"][play_type]["last_plays"][i]
            o = tracker["current_game"][play_type]["played_against"][i]
            play = o.upper() if tracker['winning_moves'][o] == p else o.lower()
            temp_string += " " + play + " "
        print_string += f'|     OPP: {temp_string}\n'
    
    if show_play_num:
        play_list = [str(num) for num in tracker["current_game"][play_type]["play_pos"][-tracker["current_game"][play_type]["stat_freq"]:]]
        max_digits = max(len(num) for num in play_list)
        on_streak = False

        for digit_pos in range(max_digits):
            temp_string = ""
            on_streak = False
            prev_streak = False
            for i in range(len(play_list)):
                num = play_list[i]
                if (len(num)) <= digit_pos:
                    temp_string += "| |"
                else:
                    on_streak = True if i < (len(play_list) - 1) and int(play_list[i+1]) == int(play_list[i]) + 1 else False
                    if not prev_streak and on_streak:
                        temp_string += '['
                    elif prev_streak and on_streak:
                        temp_string += " "
                    elif not on_streak and prev_streak:
                        temp_string += " "
                    else:
                        temp_string += "|" 
                    temp_string += num[digit_pos]
                    if prev_streak and not on_streak:
                        temp_string += ']'
                    elif on_streak:
                        temp_string += " "
                    else:
                        temp_string += "|"
                    prev_streak = on_streak

            print_string += f'|          {temp_string}\n'
    
    print_string += "|"
    
    print(print_string)

def reset():
    global tracker, default_stat_range
    tracker['player_history'] = ["R"]
    tracker['opponent_history'].clear()
    tracker['strategy'] = [0, 0, 0, 0]
    tracker['opponent_guess'] = ["", "", "", ""]
    tracker['strategy_guess'] = ["", "", "", ""]
    tracker['opponent_play_order'] = {}
    tracker['player_play_order'] = {}
    for key in ["current_game"]:
        tracker[key]['count'] = 0
        tracker[key]['l'] = 0
        tracker[key]['t'] = 0
        tracker[key]['w'] = 0
        tracker[key]['last_prediction'] = ''
        tracker[key]['next_prediction'] = ''
        tracker[key]['predictions'] = []
        for subkey in ['strat_1', 'strat_2', 'strat_3', 'strat_4', 'random']:
            tracker[key][subkey]['w'] = 0
            tracker[key][subkey]['l'] = 0
            tracker[key][subkey]['t'] = 0
            tracker[key][subkey]['last_wins'] = []
            tracker[key][subkey]['last_losses'] = []
            tracker[key][subkey]['last_ties'] = []
            tracker[key][subkey]['last_plays'] = []
            tracker[key][subkey]['played_against'] = []
            tracker[key][subkey]['play_pos'] = []
            tracker[key][subkey]['stat_freq'] = default_stat_range

def track_last_move(prev_play, last_move):
    global tracker
    if last_move != '' and len(tracker['opponent_history']) < tracker['limit']:
        losing_choice = tracker['winning_moves'][last_move[0]]
        winning_choice = tracker['counter_move'][last_move[0]]
        move_data = tracker["current_game"][tracker["current_game"]['prev_choice']]
        stat_freq = move_data['stat_freq']
        move_data['play_pos'].append(len(tracker['player_history']))

        move_data['last_wins'] = move_data['last_wins'][-stat_freq:]
        move_data['last_ties'] = move_data['last_ties'][-stat_freq:]
        move_data['last_losses'] = move_data['last_losses'][-stat_freq:]
        move_data['last_plays'] = move_data['last_plays'][-stat_freq:]
        move_data['played_against'] = move_data['played_against'][-stat_freq:]

        if len(move_data['last_plays']) == stat_freq:
            move_data['last_plays'].pop(0)
        move_data['last_plays'].append(last_move[0])

        if len(move_data['played_against']) == stat_freq:
            move_data['played_against'].pop(0)
        move_data['played_against'].append(prev_play)

        if prev_play == losing_choice:
            if len(move_data['last_wins']) == stat_freq:
                move_data['last_wins'].pop(0)
            move_data['w'] += 1
            move_data['last_wins'].append(True)
        else:
            if len(move_data['last_wins']) == stat_freq:
                move_data['last_wins'].pop(0)
            move_data['last_wins'].append(False)

        if prev_play == last_move[0]:
            if len(move_data['last_ties']) == stat_freq:
                move_data['last_ties'].pop(0)
            move_data['t'] += 1
            move_data['last_ties'].append(True)
        else:
            if len(move_data['last_ties']) == stat_freq:
                move_data['last_ties'].pop(0)
            move_data['last_ties'].append(False)

        if prev_play == winning_choice:
            if len(move_data['last_losses']) == stat_freq:
                move_data['last_losses'].pop(0)
            move_data['l'] += 1
            move_data['last_losses'].append(True)
        else:
            if len(move_data['last_losses']) == stat_freq:
                move_data['last_losses'].pop(0)
            move_data['last_losses'].append(False)

tracker = generate_tracker(limit=limit, stat_range=default_stat_range, verbose_mode=verbose_mode)