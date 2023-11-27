from psychopy import core, visual, gui, data, event, hardware
from psychopy.hardware import keyboard
from psychopy.tools.filetools import fromFile, toFile
import numpy
import random
import time

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
        You will be shown images of black shapes. Some are category A, some are category B.\n
        You will not know in advance which category a specific shape belongs to.\n
        After you see an image, you will be asked to guess its category <b>(left arrow for category A, right arrow for category B)</b>\n
        After you choose, the screen will show you whether you were correct or not.\n
        <b>You will receive a bonus payment of $0.05 for each correct answer!</b>\n
        So you can increase your bonus by guessing correctly, and by guessing as quickly as possible so you move on to the next image sooner.\n
        Press any key to continue.
        """,
    alignment='center'
)

msg_intro_2 = visual.TextBox2(
    win, 
    pos=[0, 0], 
    text="""
        <b>The first 10 trials are a practice round that will not count towards your bonus payment.</b>\n
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

current_score = 0
score = visual.TextBox2(win, pos=[0, 0.4], text=f'Bonus : ${current_score}', alignment='center')

kb = keyboard.Keyboard()

T_stim = 0.6
T_choice = 4
T_delay = 1
T_feedback = 1
correct_bonus = 0.05

correct_fdbk = f'Correct category! + ${correct_bonus}'
wrong_fdbk = "Wrong category!"

stim_path = 'stimuli/pack_shapes_diff/'
img = visual.ImageStim(win, stim_path + 'cat_1/diff_1/ex_1_1_1.png')

trial_handler = data.TrialHandler(
    trialList=[
          {'image': img, 'correct_response': 'left'}
    ],
    nReps = 2  
)

for trial in trial_handler:
    img = trial['image']

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
    print(keys[-1].name)
    print(keys[-1].rt)

    if keys[-1].name == trial['correct_response']:
        current_score += correct_bonus
        feedback.setText(correct_fdbk)
    else:
        feedback.setText(wrong_fdbk)
    score.setText(f'Bonus : ${current_score}')
    feedback.draw()
    score.draw()
    win.flip()
    core.wait(T_feedback)
    
win.close()
core.quit()

