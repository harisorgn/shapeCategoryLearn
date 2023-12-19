from psychopy import core, visual, gui, data, event, hardware
from psychopy.hardware import keyboard
from psychopy.tools.filetools import fromFile, toFile
from collections import deque
import numpy as np
import random
import time
import os
import math
#import ffmpeg

def update_difficulty(current_diff, max_diff, thrs_acc, past_data):
    N = len(past_data)
    if (N == past_data.maxlen) and (all(map(lambda d: d['difficulty'] == current_diff, past_data))) :
        N_corrects = sum([d['correct'] for d in past_data])
        acc = N_corrects / N

        if (acc >= thrs_acc) and (current_diff < max_diff) : 
            current_diff += 1
        elif (acc < thrs_acc) and (current_diff > 1) :
            current_diff -= 1

    return current_diff

def RT_to_reward(RT):
    max_reward = 0.1
    decay = 0.2

    return max_reward * math.exp(-decay * RT)


core.checkPygletDuringWait = False
win = visual.Window(size=(800,600), fullscr=False, color=(-1,-1,-1), allowGUI=True, monitor='testMonitor', units='height')

msg_welcome = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="Welcome to the Category Learning experiment! Press any key to continue.",
    alignment='center'
)

msg_intro_1 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        You will be shown movies. Each movie contains a sequence of shapes changing form. \n
        Some shapes are category A, some are category B. Within a single movie, all shapes belong to the same category. \n
        You will not know in advance which category the shapes of each movie belong to. \n
        While you watch a movie, you have to guess the category that its shapes belong to (left arrow for category A, right arrow for category B) \n
        After you choose, the screen will show you whether you were correct or not. \n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_2 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        You will receive a bonus payment for each correct answer! The faster you answer the higher the bonus will be! \n
        So you can increase your bonus by guessing as quickly and accurately as possible. \n
        You will lose $0.05 from your bonus payment for each incorrect answer! The bonus can not become less that $0. \n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_3 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        The first 10 trials are a practice round that will not count towards your bonus payment. \n
        You will be notified when practice finishes and the test begins. \n
        Press any key to begin the practice round.
        """,
    alignment='center'
)

ITI = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="Please press any button to continue to the next trial.",
    alignment='center'
)

feedback = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="",
    letterHeight = 0.05,
    alignment='center'
)

debug_msg = visual.TextBox2(win, pos=[0.0, -0.1], text="", alignment='center')

current_score = 0.0
score = visual.TextBox2(
    win, 
    pos=[0, 0.4], 
    text=f'Bonus : ${np.round(current_score,3)}', 
    letterHeight = 0.05,
    alignment='center'
)

kb = keyboard.Keyboard()

#T_experiment = 10 # minutes
T_experiment = 1 # minutes
T_feedback = 1 # seconds
T_correct_fbdk = 1.5 # seconds
T_incorrect_fdbk = 5 # seconds
T_bonus_1 = 3 # minutes
T_bonus_2 = 6 # minutes

incorrect_penalty = -0.05
thrs_acc = 0.75
IS_DEBUG_MODE = False

correct_fdbk_no_bonus = f'Correct category!'
wrong_fdbk_no_bonus = "Wrong category!"
timeout_fdbk_no_bonus = f'Time out! \nPlease try to respond as quickly as possible.'

shape_set = 3
pack_path = f'stimuli/pack_noise_shapes_{shape_set}/'

N_categories = 2
N_difficulty_levels = 5
N_trials_per_difficulty = 5
N_training_trials = 10
P_difficulty_training = [0.6, 0.4, 0.0, 0.0, 0.0]

stim_train = []
stim_test = [[] for i in range(N_difficulty_levels)]

for i in range(N_difficulty_levels) :
    P = P_difficulty_training[i]
    for j in range(N_categories) :
        stim_path = pack_path + f'cat_{j+1}/diff_{i+1}/'
        files = os.listdir(stim_path)
        files = [os.path.join(stim_path, f) for f in files]

        shapes_train = random.choices(files, k = int(np.floor(P * (N_training_trials/2))))
        shapes_test = [f for f in files if f not in shapes_train]


        #correct_response = 'right' if j == 1 else 'left'
        correct_response = ['1','2','3','4','5'] if j == 1 else ['6','7','8','9','0']
        
        stim_test[i] += [
            {
                'stimulus' : visual.MovieStim(win, s, pos=[0, 0], size=(0.7,0.7), units='height'), 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'correct_response' : correct_response, 
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'test'
            } 
        for s in shapes_test]

        stim_train += [
            {
                'stimulus' : visual.MovieStim(win, s, pos=[0, 0], size=(0.7, 0.7), units='height'), 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'correct_response' : correct_response, 
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'train'
            } 
        for s in shapes_train]

trial_handler = data.TrialHandler(
    trialList = stim_train,
    nReps = 1
)

info = {'participant':'', 'session':''}

info['date'] = data.getDateStr()

exp = data.ExperimentHandler(
    name='SCL_noise',
    extraInfo = info, 
    dataFileName = 'output', 
)

msg_intro_1.draw()
win.flip()
keys = kb.waitKeys()

msg_intro_2.draw()
win.flip()
keys = kb.waitKeys()

msg_intro_3.draw()
win.flip()
keys = kb.waitKeys()

#-------------------
#--Training trials--
#-------------------
for trial in trial_handler:
    stim = trial['stimulus']

    ITI.draw()
    score.draw()
    win.flip()
    keys = kb.waitKeys(waitRelease=True)

    keys = None
    correct = 0 
    response = ""
    rt = None
    is_omission = True
    T_feedback = 0

    win.callOnFlip(kb.clock.reset)
    while not stim.isFinished :
        stim.draw()
        score.draw()
        win.flip()
        keys = kb.getKeys(keyList=['1','2','3','4','5','6','7','8','9','0'])
        #keys = kb.getKeys(keyList=['left', 'right'])

        if keys :
            is_omission = False
            response = keys[-1].name
            rt = keys[-1].rt
            #if response == trial['correct_response']:
            if response in trial['correct_response']:
                feedback.setText(correct_fdbk_no_bonus)
                correct = 1
                T_feedback = T_correct_fbdk
            else:
                feedback.setText(wrong_fdbk_no_bonus)
                T_feedback = T_incorrect_fdbk
            break

    if is_omission : 
        feedback.setText(timeout_fdbk_no_bonus)
        T_feedback = T_incorrect_fdbk

    exp.addData('response', response)
    exp.addData('correct', correct)
    exp.addData('correct_response', trial['correct_response'])
    exp.addData('response_time', rt)
    exp.addData('difficulty', trial['difficulty'])
    exp.addData('category', trial['category'])
    exp.addData('phase', trial['phase'])
    exp.nextEntry()

    score.setText(f'Bonus : ${np.round(current_score,3)}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)

    if 'escape' in event.waitKeys():
        exp.saveAsWideText('output.csv')
        win.close()
        core.quit()

intermission = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        The practice round has finished. \n
        For the rest of the experiment you will receive a $0.05 bonus for each correct answer and lose $0.05 from your bonus for each incorrect answer! \n
        The bonus can not become less than $0. \n
        Press any key to begin the test.
    """,
    alignment='center'
)
intermission.draw()
win.flip()
keys = kb.waitKeys()

timer = core.CountdownTimer(T_experiment * 60)

timer_bonus_1 = core.CountdownTimer(T_bonus_1 * 60)
timer_bonus_2 = core.CountdownTimer(T_bonus_2 * 60)
done_bonus_1 = False
done_bonus_2 = False
additional_bonus = 0.0
#-------------------
#----Test trials----
#-------------------
current_difficulty = 1
past_data = deque([], N_trials_per_difficulty)
while timer.getTime() > 0 :

    current_difficulty = update_difficulty(current_difficulty, N_difficulty_levels, thrs_acc, past_data)

    trial = random.choice(stim_test[current_difficulty - 1])
    stim = trial['stimulus']

    ITI.draw()
    score.draw()
    win.flip()
    keys = kb.waitKeys(waitRelease=True)

    keys = None
    correct = 0 
    response = ""
    rt = None
    is_omission = True
    T_feedback = 0

    trial_bonus = 0
    win.callOnFlip(kb.clock.reset)

    while not stim.isFinished :
        stim.draw()
        score.draw()
        win.flip()
        keys = kb.getKeys(keyList=['1','2','3','4','5','6','7','8','9','0'])
        #keys = kb.getKeys(keyList=['left', 'right'])
    
        if keys :
            is_omission = False
            response = keys[-1].name
            rt = keys[-1].rt
            #if response == trial['correct_response']:
            if response in trial['correct_response']:
                trial_bonus = np.round(RT_to_reward(rt) + additional_bonus, 3)
                correct_fdbk = f'Correct category! + ${trial_bonus}'
                feedback.setText(correct_fdbk)
                correct = 1
                T_feedback = T_correct_fbdk
            else:
                T_feedback = T_incorrect_fdbk
                if current_score >= abs(incorrect_penalty) :
                    trial_bonus = incorrect_penalty
                    wrong_fdbk = f'Wrong category! - ${abs(trial_bonus)}'
                    feedback.setText(wrong_fdbk)
                else:
                    feedback.setText(wrong_fdbk_no_bonus)
            break

    if is_omission:
        T_feedback = T_incorrect_fdbk
        if current_score >= incorrect_penalty :
            trial_bonus = incorrect_penalty
            timeout_fdbk = f'Time out! - ${abs(trial_bonus)} \n Please try to respond as quickly as possible.'
            feedback.setText(timeout_fdbk)
        else :
            feedback.setText(timeout_fdbk_no_bonus)

    current_score += trial_bonus

    exp.addData('response', response)
    exp.addData('correct', correct)
    exp.addData('correct_response', trial['correct_response'])
    exp.addData('response_time', rt)
    exp.addData('bonus', trial_bonus)
    exp.addData('difficulty', trial['difficulty'])
    exp.addData('category', trial['category'])
    exp.addData('phase', trial['phase'])
    exp.nextEntry()

    past_data.appendleft({'correct' : correct, 'difficulty' : trial['difficulty']})

    score.setText(f'Bonus : ${np.round(current_score, 3)}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)

    if 'escape' in event.waitKeys():
        exp.saveAsWideText('output.csv')
        win.close()
        core.quit()
    
    if (not done_bonus_1) and (timer_bonus_1.getTime() <= 0) :
        done_bonus_1 = True
        additional_bonus += 0.05
    elif (not done_bonus_2) and (timer_bonus_2.getTime() <= 0) :
        done_bonus_2 = True
        additional_bonus += 0.05

win.close()
core.quit()

