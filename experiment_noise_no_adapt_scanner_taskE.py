from psychopy import core, visual, gui, data, event, hardware
from psychopy.hardware import keyboard
from psychopy.tools.filetools import fromFile, toFile
from collections import deque
import numpy as np
import random
import time
import os
import math

def RT_to_reward(RT):
    max_reward = 0.6
    decay = 0.05

    return max_reward * math.exp(-decay * RT)

def set_positive_feedback(feedback, gain=None):
    if not gain:
        correct_fdbk = f'Correct category!'
        feedback.setText(correct_fdbk)
    else:
        correct_fdbk = f'Correct category! +${gain}'
        feedback.setText(correct_fdbk)

def set_negative_feedback(feedback, loss=None):
    if not loss:
        wrong_fdbk = "Wrong category!"
        feedback.setText(wrong_fdbk)
    else:
        wrong_fdbk = f'Wrong category! -${abs(loss)}'
        feedback.setText(wrong_fdbk)

def set_timeout_feedback(feedback, loss=None):
    if not loss:
        timeout_fdbk = f'Too slow!'
        feedback.setText(timeout_fdbk)
    else:
        timeout_fdbk = f'Too slow! -${abs(loss)} \n Please try to respond as quickly as possible.'
        feedback.setText(timeout_fdbk)

def check_threshold(trials, N_thrs, acc_thrs):
    N_trials = len(trials)
    if N_trials >= N_thrs :
        N_corrects = sum([t['correct'] for t in trials])
        acc = N_corrects / N_trials
        if acc >= acc_thrs:
            return True
    
    return False

def run_training(exp, stimuli, win, kb, score, feedback, ITI, check_sign, x_sign, hourglass, T_correct_fbdk, T_incorrect_fdbk):
    random.shuffle(stimuli)
    for trial in stimuli:
        stim = visual.MovieStim(win, trial['stimulus'], pos=[0, 0], size=(0.7, 0.7), units='height')

        keys = None
        correct = 0 
        response = ""
        rt = None
        is_omission = True
        T_feedback = 0

        win.callOnFlip(kb.clock.reset)
        while not stim.isFinished :
            stim.draw()
            score['text'].draw()
            win.flip()
            keys = kb.getKeys(keyList=['left', 'right'])

            if keys :
                is_omission = False
                response = keys[-1].name
                rt = keys[-1].rt
            
                if response in trial['correct_response']:
                    set_positive_feedback(feedback)
                    correct = 1
                    T_feedback = T_correct_fbdk
                else:
                    set_negative_feedback(feedback)
                    T_feedback = T_incorrect_fdbk
                break

        if is_omission : 
            set_timeout_feedback(feedback)
            T_feedback = T_incorrect_fdbk

        exp.addData('stimulus_ID', trial['stimulus_ID'])
        exp.addData('response', response)
        exp.addData('correct', correct)
        exp.addData('correct_response', trial['correct_response'])
        exp.addData('response_time', rt)
        exp.addData('bonus', 0.0)
        exp.addData('difficulty', trial['difficulty'])
        exp.addData('category', trial['category'])
        exp.addData('phase', trial['phase'])
        exp.addData('shape_set', trial['shape_set'])
        exp.nextEntry()

        feedback.draw()
        if is_omission:
            hourglass.draw()
        else:
            if correct:
                check_sign.draw()
            else:
                x_sign.draw()
        score['text'].draw()
        win.flip()
        core.wait(T_feedback)
            
        ITI.draw()
        score['text'].draw()
        win.flip()
        keys = kb.waitKeys(keyList=['left','right','up','down'], waitRelease=True)

def run_test(
        exp, 
        stimuli, 
        win, 
        kb, 
        score, 
        feedback, 
        ITI, 
        dollar_sign, 
        x_sign, 
        hourglass, 
        T_correct_fbdk, 
        T_incorrect_fdbk,
        timer
):
    idx_trial = 0
    N_before_thrs = 30
    N_thrs = 10
    acc_thrs = 0.75

    epi_clock = core.Clock() 
    past_data = deque([], N_thrs)
    is_finished = False

    while (timer.getTime() > 0) and not is_finished :

        trial = random.choice(stimuli)
        stim = visual.MovieStim(win, trial['stimulus'], pos=[0, 0], size=(0.7, 0.7), units='height') 

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
            score['text'].draw()
            win.flip()
            stim_time = epi_clock.getTime()
            exp.addData('stimulus_ID', trial['stimulus_ID'])
            exp.addData('stim_presentation_time', stim_time)
            keys = kb.getKeys(keyList=['left', 'right'])
        
            if keys :
                is_omission = False
                response = keys[-1].name
                rt = keys[-1].rt
                
                if response in trial['correct_response']:
                    trial_bonus = np.round(RT_to_reward(rt), 3)
                    set_positive_feedback(feedback, gain=trial_bonus)

                    correct = 1
                    T_feedback = T_correct_fbdk
                else:
                    T_feedback = T_incorrect_fdbk
                    if score['current_score'] >= abs(score['incorrect_penalty']) :
                        trial_bonus = score['incorrect_penalty']
                        set_negative_feedback(feedback, loss=trial_bonus)
                    else:
                        set_negative_feedback(feedback)
                break

        if is_omission:
            T_feedback = T_incorrect_fdbk
            if score['current_score'] >= abs(score['incorrect_penalty']) :
                trial_bonus = score['incorrect_penalty']
                set_timeout_feedback(feedback, loss=trial_bonus)
            else :
                set_timeout_feedback(feedback)

        score['current_score'] += trial_bonus

        exp.addData('response', response)
        exp.addData('correct', correct)
        exp.addData('correct_response', trial['correct_response'])
        exp.addData('response_time', rt)
        exp.addData('bonus', trial_bonus)
        exp.addData('difficulty', trial['difficulty'])
        exp.addData('category', trial['category'])
        exp.addData('phase', trial['phase'])
        exp.addData('shape_set', trial['shape_set'])

        score['text'].setText(f"Bonus : ${np.round(score['current_score'], 3)}")
        feedback.draw()
        if is_omission:
            hourglass.draw()
        else:
            if correct:
                dollar_sign.draw()
            else:
                x_sign.draw()
        score['text'].draw()
        win.flip()
        feedback_time = epi_clock.getTime()
        exp.addData('feedback_presentation_time', feedback_time)
        core.wait(T_feedback)

        ITI.draw()
        score['text'].draw()
        win.flip()
        ITI_time = epi_clock.getTime()
        exp.addData('ITI_presentation_time', ITI_time)
        keys = kb.waitKeys(keyList=['left','right','up','down'],waitRelease=True)
        exp.addData('ITI_response_time', keys[-1].rt)
        exp.nextEntry()

        idx_trial += 1
        if idx_trial > N_before_thrs :
            past_data.appendleft({'correct' : correct})
            is_finished = check_threshold(past_data, N_thrs, acc_thrs)

fontsize = 0.03
keylist = ['left','right','up','down']
T_experiment = 11 # minutes
T_feedback = 1 # seconds
T_correct_fbdk = 1.5 # seconds
T_incorrect_fdbk = 5 # seconds

IS_DEBUG_MODE = False

N_categories = 2
N_difficulty_levels = 5
N_trials_per_difficulty = 5
N_training_trials = 2
N_shape_sets = 3
P_difficulty_training = [0.2, 0.2, 0.2, 0.2, 0.2]

core.checkPygletDuringWait = False
win = visual.Window(size=(800,600), fullscr=False, color=(-1,-1,-1), allowGUI=True, monitor='testMonitor', units='height')

msg_wait = visual.TextBox2(
    win, 
    letterHeight = fontsize,
    pos=[0, 0], 
    text="Waiting for scanner...",
    alignment='center'
)

msg_welcome = visual.TextBox2(
    win, 
    letterHeight = fontsize,
    pos=[0, 0], 
    text="Welcome to the Category Learning experiment! Press any key to continue.",
    alignment='center'
)

msg_intro_1 = visual.TextBox2(
    win, 
    letterHeight = fontsize,
    pos=[0, 0], 
    text="""
        You will be shown movies. Each movie contains a sequence of shapes changing form. \n
        Some shapes are category A, some are category B. Within a single movie, all shapes belong to the same category. \n
        You will not know in advance which category the shapes of each movie belong to. \n
        While you watch a movie, you have to guess the category that its shapes belong to (left arrow for category A, right arrow for category B). \n
        After you choose, the screen will show you whether you were correct or not. \n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_2 = visual.TextBox2(
    win, 
    letterHeight = fontsize,
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
    letterHeight = fontsize,
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
    letterHeight = fontsize,
    pos=[0, 0], 
    text="Please press any button to continue to the next trial.",
    alignment='center'
)

feedback = visual.TextBox2(
    win, 
    pos=[0, 0.25], 
    text="",
    letterHeight = 0.05,
    alignment='center'
)

dollar_sign = visual.ImageStim(win, 'stimuli/dollar_sign.png',size=[0.5,0.5],pos=[0,-0.1])
check_sign = visual.ImageStim(win, 'stimuli/green_check.png',size=[0.5,0.5],pos=[0,-0.1])
x_sign = visual.ImageStim(win, 'stimuli/red_x.png',size=[0.5,0.5],pos=[0,-0.1])
hourglass = visual.ImageStim(win, 'stimuli/hourglass.png',size=[0.5,0.5],pos=[0,-0.1])

debug_msg = visual.TextBox2(win, pos=[0.0, -0.1], text="", alignment='center')

score = {
    'current_score' : 0.0,
    'incorrect_penalty' : -1, # USD
    'text' : visual.TextBox2(
                            win, 
                            pos=[0, 0.4], 
                            text=f'Bonus : ${np.round(0.0, 3)}', 
                            letterHeight = 0.05,
                            alignment='center'
    )
}

intermission = visual.TextBox2(
    win, 
    letterHeight=fontsize,
    pos=[0, 0], 
    text="""
        The practice round has finished. \n
        For the rest of the experiment you will receive a bonus payment for each correct answer, which will be higher the faster you answer! \n
        Also you will lose $0.05 from your bonus payment for each incorrect answer! \n
        The bonus can not become less than $0. \n
        Press any key to begin the test.
    """,
    alignment='center'
)

kb = keyboard.Keyboard()

stim_train = []
stim_test = [[] for i in range(N_shape_sets)]

set = 0
pack_path = f'stimuli/pack_noise_gif_shapes_{set+1}/'

for i in range(N_difficulty_levels) :
    P = P_difficulty_training[i]
    for j in range(N_categories) :
        stim_path = pack_path + f'cat_{j+1}/diff_{i+1}/'
        files = os.listdir(stim_path)
        files = [os.path.join(stim_path, f) for f in files]

        shapes_train = random.choices(files, k = int(np.floor(P * (N_training_trials/2))))
        shapes_test = [f for f in files if f not in shapes_train]

        correct_response = 'right' if j == 1 else 'left'
        
        stim_test[set] += [
            {
                'stimulus' : s, 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'correct_response' : correct_response,
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'test',
                'shape_set' : set+1
            } 
        for s in shapes_test]

        stim_train += [
            {
                'stimulus' : s, 
                'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                'correct_response' : correct_response,
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'train',
                'shape_set' : set+1
            } 
        for s in shapes_train]

for set in range(1, N_shape_sets) :
    pack_path = f'stimuli/pack_noise_gif_shapes_{set+1}/'

    for i in range(N_difficulty_levels) :
        P = P_difficulty_training[i]
        for j in range(N_categories) :
            stim_path = pack_path + f'cat_{j+1}/diff_{i+1}/'
            files = os.listdir(stim_path)
            shapes_test = [os.path.join(stim_path, f) for f in files]

            correct_response = 'right' if j == 1 else 'left'
            
            stim_test[set] += [
                {
                    'stimulus' : s, 
                    'stimulus_ID' : int(s.split('_')[-1].split('.')[0]),
                    'correct_response' : correct_response,
                    'difficulty' : i+1, 
                    'category' : j+1,
                    'phase' : 'test',
                    'shape_set' : set+1
                } 
            for s in shapes_test]

info = {'participant':'', 'session':''}

info['date'] = data.getDateStr()

exp = data.ExperimentHandler(
    name='SCL_noise',
    extraInfo = info, 
    dataFileName = 'output', 
)

msg_intro_1.draw()
win.flip()
keys = kb.waitKeys(keyList=keylist)

msg_intro_2.draw()
win.flip()
keys = kb.waitKeys(keyList=keylist)

msg_intro_3.draw()
win.flip()
keys = kb.waitKeys(keyList=keylist)

#-------------------
#--Training trials--
#-------------------
run_training(
            exp, 
            stim_train, 
            win, 
            kb, 
            score, 
            feedback, 
            ITI, 
            check_sign, 
            x_sign, 
            hourglass, 
            T_correct_fbdk, 
            T_incorrect_fdbk
)

intermission.draw()
win.flip()
keys = kb.waitKeys(keyList=keylist)

msg_wait.draw()
win.flip()
epi_kb = keyboard.Keyboard()
epi_keys = epi_kb.getKeys()
keys = epi_kb.waitKeys(keyList=['equal'])

timer = core.CountdownTimer(T_experiment * 60)

#-------------------
#----Test trials----
#-------------------
run_test(
        exp, 
        stim_test[0], 
        win, 
        kb, 
        score, 
        feedback, 
        ITI, 
        dollar_sign, 
        x_sign, 
        hourglass, 
        T_correct_fbdk, 
        T_incorrect_fdbk,
        timer
)

idx_set = 1
while (timer.getTime() > 0) and (idx_set+1 <= N_shape_sets) :

    run_test(
        exp, 
        stim_test[idx_set], 
        win, 
        kb, 
        score, 
        feedback, 
        ITI, 
        dollar_sign, 
        x_sign, 
        hourglass, 
        T_correct_fbdk, 
        T_incorrect_fdbk,
        timer
    )

    idx_set += 1

win.close()
core.quit()