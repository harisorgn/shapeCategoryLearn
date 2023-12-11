from psychopy import core, visual, gui, data, event, hardware
from psychopy.hardware import keyboard
from psychopy.tools.filetools import fromFile, toFile
import numpy as np
import random
import time

import os

core.checkPygletDuringWait = False

win = visual.Window(size=(800, 600), fullscr=True, color=(-1,-1,-1), allowGUI=True, monitor='testMonitor', units='height')

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
        You will be shown images of white shapes. Some are category A, some are category B. \n
        You will not know in advance which category a specific shape belongs to. \n
        After you see an image, you will be asked to guess its category (left arrow for category A, right arrow for category B) \n
        After you choose, the screen will show you whether you were correct or not. \n
        You will receive a bonus payment of $0.05 for each correct answer! \n
        You will lose $0.05 from your bonus payment for each incorrect answer! The bonus can not become less than $0. \n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_2 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        The first 10 trials are a practice round that will not count towards your bonus payment.\n
        You will be notified when practice finishes and the test begins.\n
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
    alignment='center'
)

choice_A = visual.TextBox2(win, pos=[-0.3, 0], text="A", alignment='center', letterHeight=0.2)
choice_B = visual.TextBox2(win, pos=[0.3, 0], text="B", alignment='center', letterHeight=0.2)

current_score = 0.0
score = visual.TextBox2(win, pos=[0, 0.4], text=f'Bonus : ${current_score}', alignment='center')

kb = keyboard.Keyboard()

T_stim = 0.6
T_choice = 4
T_delay = 1
T_feedback = 1
correct_bonus = 0.05

correct_fdbk = f'Correct category! + ${correct_bonus}'
wrong_fdbk = "Wrong category! - $0.05"
wrong_fdbk_no_bonus = "Wrong category!"
timeout_fdbk = "Time out! \n - $0.05 \n Please try to respond as quickly as possible."

shape_set = 1
pack_path = f'stimuli/pack_shapes_{shape_set}/'

N_categories = 2
N_difficulty_levels = 5
N_trials_per_difficulty = 5
N_training_trials = 10
P_difficulty_training = [0.6, 0.4, 0.0, 0.0, 0.0]

stim_train = []
stim_test = []

for i in range(N_difficulty_levels) :
    P = P_difficulty_training[i]
    for j in range(N_categories) :
        stim_path = pack_path + f'cat_{j+1}/diff_{i+1}/'
        files = os.listdir(stim_path)
        files = [os.path.join(stim_path, f) for f in files]

        shapes_train = random.choices(files, k = int(np.floor(P * (N_training_trials/2))))
        shapes_test = [f for f in files if f not in shapes_train]


        correct_response = 'right' if j == 1 else 'left'
        
        stim_test += [
            {
                'stimulus' : visual.ImageStim(win, s), 
                'correct_response' : correct_response, 
                'difficulty' : i+1, 
                'category' : j+1,
                'phase' : 'test'
            } 
        for s in shapes_test]

        stim_train += [
            {
                'stimulus' : visual.ImageStim(win, s), 
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

msg_intro_1.draw()
win.flip()
keys = kb.waitKeys()

msg_intro_2.draw()
win.flip()
keys = kb.waitKeys()

for trial in trial_handler:
    img = trial['stimulus']

    ITI.draw()
    score.draw()
    win.flip()
    keys = kb.waitKeys()

    img.draw()
    score.draw()
    win.flip()
    core.wait(T_stim)
    
    score.draw()
    win.flip()
    core.wait(T_delay)

    choice_A.draw()
    choice_B.draw()
    score.draw()
    win.callOnFlip(kb.clock.reset)
    win.flip()

    keys = kb.waitKeys(maxWait=T_choice, keyList=['left', 'right'])

    if not keys :
        feedback.setText(timeout_fdbk)
    else :
        if keys[-1].name == trial['correct_response']:
            current_score += correct_bonus
            feedback.setText(correct_fdbk)
        else:
            if current_score > 0.0 :
                current_score -= correct_bonus
                feedback.setText(wrong_fdbk)
            else : 
                feedback.setText(wrong_fdbk_no_bonus)

    score.setText(f'Bonus : ${current_score}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)

    if 'escape' in event.waitKeys():
        core.quit()

win.close()
core.quit()

