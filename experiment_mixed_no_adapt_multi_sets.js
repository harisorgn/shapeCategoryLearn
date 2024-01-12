const IS_DEBUG = false
const IS_ONLINE = true
const time_experiment = 10; // minutes
const T_exp = time_experiment * 60 * 1000; // ms  

const difficulty_levels = [1, 2, 3, 4, 5];
const P_difficulty_training = [0.2, 0.2, 0.2, 0.2, 0.2];
const N_exemplars_per_difficulty = 17;
const exemplar_range_per_difficulty = range(1, N_exemplars_per_difficulty)

const correct_bonus = 0.05;
const incorrect_penalty = -0.05;

const N_training_trials = 10;
const N_before_thrs = 30;
const N_thrs = 10;
const thrs_accuracy = 0.75;
const stim_sets = [1, 2, 3, 5];

var trial_bonus = 0;
var is_finished_all_sets = false;
var score = 0;
var current_set_idx = 0;
var current_stimulus = 0;

var timeline = []; 

var stim_path = "./stimuli/" ;
const stimulus_format = "png";

if (IS_ONLINE){
    var jsPsych = initJsPsych({
        on_finish: function() {
            jatos.endStudy(jsPsych.data.get().csv());
        }
    })
    jatos.onLoad(function(){
        var subj_id = jatos.urlQueryParameters.PROLIFIC_PID
        var std_id = jatos.urlQueryParameters.STUDY_ID
        var sess_id = jatos.urlQueryParameters.SESSION_ID

        jsPsych.data.addProperties({
            subject_id: subj_id,
            study_id: std_id,
            session_id: sess_id
        });
    });
}else{
    ID = rand_in_range(1001, 9999)

    var jsPsych = initJsPsych({
        on_finish: function() {
            jsPsych.data.get().localSave('csv',`results_${ID}.csv`);
        }
    })
}

setTimeout(
    function(){
        jsPsych.endExperiment(`<p> The experiment has concluded. <br> Thank you for participating! <br> <font color="green"> You have won a $${score} bonus! </font></p>`);
    }, 
    T_exp
);

var stimuli_training = [];
var stimuli_test = [];
var set_stimuli_training = [];
var set_stimuli_test = [];
var s = stim_sets[current_set_idx];
var set_name = `shapes_${s}`
var c = 0;

for (let d of difficulty_levels){
    const idx_cat_1_training = jsPsych.randomization.sampleWithoutReplacement(exemplar_range_per_difficulty, Math.floor(P_difficulty_training[c]*(N_training_trials/2)));
    const idx_cat_2_training = jsPsych.randomization.sampleWithoutReplacement(exemplar_range_per_difficulty, Math.floor(P_difficulty_training[c]*(N_training_trials/2)));
    const idx_cat_1_test = exemplar_range_per_difficulty.filter(x => !idx_cat_1_training.includes(x));
    const idx_cat_2_test = exemplar_range_per_difficulty.filter(x => !idx_cat_2_training.includes(x));

    const stimuli_cat_1_training = exemplar_stimuli(idx_cat_1_training, stim_path, set_name, 1, d, s, 'train', stimulus_format);
    const stimuli_cat_2_training = exemplar_stimuli(idx_cat_2_training, stim_path, set_name, 2, d, s, 'train', stimulus_format);
    set_stimuli_training.push(stimuli_cat_1_training.concat(stimuli_cat_2_training));

    const stimuli_cat_1_test = exemplar_stimuli(idx_cat_1_test, stim_path, set_name, 1, d, s, 'test', stimulus_format);
    const stimuli_cat_2_test = exemplar_stimuli(idx_cat_2_test, stim_path, set_name, 2, d, s, 'test', stimulus_format);
    set_stimuli_test.push(stimuli_cat_1_test.concat(stimuli_cat_2_test));

    c += 1;
}
stimuli_training.push(set_stimuli_training.flat());
stimuli_test.push(set_stimuli_test.flat());

for (let s of stim_sets.slice(1)){
    var set_stimuli_training = [];
    var set_stimuli_test = [];
    var set_name = `shapes_${s}`

    for (let d of difficulty_levels){
        const stimuli_cat_1_test = exemplar_stimuli(exemplar_range_per_difficulty, stim_path, set_name, 1, d, s, 'test', stimulus_format);
        const stimuli_cat_2_test = exemplar_stimuli(exemplar_range_per_difficulty, stim_path, set_name, 2, d, s, 'test', stimulus_format);
        set_stimuli_test.push(stimuli_cat_1_test.concat(stimuli_cat_2_test));

        c += 1;
    }
    stimuli_test.push(set_stimuli_test.flat());
}

var preload = {
    type: jsPsychPreload,
    images: function(){
        const s = stimuli_test.concat(stimuli_training)
        s.flat()
    }
};
timeline.push(preload);

var welcome = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "Welcome to the Category Learning experiment! Press any key to continue.",
  data: {task: 'welcome'}
};
timeline.push(welcome)

var intro_1 = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
            <p>You will be shown images of white shapes. Some are category A, some are category B.
            <br>You will not know in advance which category a specific shape belongs to.</p>
            <p>After you see an image, you will be asked to guess its category <b>(left arrow for category A, right arrow for category B)</b></p>
            <p>After you choose, the screen will show you whether you were correct or not.</p>
            <p><b>You will receive a bonus payment of $0.05 for each correct answer!</b></p>
            <p><b>You will lose $0.05 from your bonus payment for each incorrect answer! The bonus can not become less than $0.</b></p>
            <p>Press any key to continue.</p>
            `,
  data: {task: 'introduction_1'}
};
timeline.push(intro_1)

var intro_2 = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
            <p> <b>The first 10 trials are a practice round that will not count towards your bonus payment.</b></p>
            <p> You will be notified when practice finishes and the test begins. </p>
            <p> Press any key to begin the practice round.</p>
            `,
    data: {task: 'introduction_2'}
  };
timeline.push(intro_2)

var ITI = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        const responses = jsPsych.data.get().filter({task: 'response', phase: 'test', set: stim_sets[current_set_idx]}).last(N_before_thrs + N_thrs).values();
        const N = responses.length;

        if (N == (N_before_thrs + N_thrs)){
            const responses_thrs = responses.slice(-N_thrs);
            const N_corrects = responses_thrs.reduce((acc, x) => acc + x.correct, 0);
            const accuracy = N_corrects / N_thrs;

            if (accuracy >= thrs_accuracy){
                current_set_idx += 1;
                if (current_set_idx > (stim_sets.length-1)){
                    is_finished_all_sets = true;
                }
            }
        }
        return `
            ${wrap_score_in_html(score)}
            <div> Please press any key to continue to the next image.</div>
        `
    },
    data: {task: 'ITI'},
    on_finish: function(data){
        if(is_finished_all_sets){
            jsPsych.endExperiment(`<p> The experiment has concluded. <br> Thank you for participating! <br> <font color="green"> You have won a $${score} bonus! </font></p>`);
        }
      }
};

var stim_train = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return wrap_stim_in_html(jsPsych.timelineVariable('stimulus'), score)
    },
    choices: "NO_KEYS",
    trial_duration: 600,
    data: {task : 'stimulus'}
};

var stim_test = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        current_stimulus = sample_stimulus(stimuli_test, current_set_idx);
        return wrap_stim_in_html(current_stimulus.stimulus, score)
    },
    choices: "NO_KEYS",
    trial_duration: 600,
    data: {task : 'stimulus'}
};

var blank = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return `${wrap_score_in_html(score)}`
    },
    choices: "NO_KEYS",
    trial_duration: 1000,
};

var choices_train = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return IS_DEBUG ? 
        wrap_choices_debug_in_html(jsPsych.timelineVariable('category'), jsPsych.timelineVariable('exemplar_ID'), jsPsych.timelineVariable('set'), score) :
        wrap_choices_in_html(score)
    },
    choices: ['ArrowLeft', 'ArrowRight'],
    data: function(){
        return {
            task: 'response',
            stimulus: jsPsych.timelineVariable('stimulus'),
            correct_response: jsPsych.timelineVariable('correct_response'),
            exemplar_ID: jsPsych.timelineVariable('exemplar_ID'),
            category: jsPsych.timelineVariable('category'),
            difficulty: jsPsych.timelineVariable('difficulty'),
            set: jsPsych.timelineVariable('set'),
            phase: jsPsych.timelineVariable('phase')
        }
    },
    trial_duration: 4000,
    on_finish: function(data){
        data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    }
};

var choices_test = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function (){
        return IS_DEBUG ? 
        wrap_choices_debug_in_html(current_stimulus.category, current_stimulus.exemplar_ID, current_stimulus.set, score) :
        wrap_choices_in_html(score)
    },
    choices: ['ArrowLeft', 'ArrowRight'],
    data: function(){
        return {
            task: 'response',
            stimulus: current_stimulus.stimulus,
            correct_response: current_stimulus.correct_response,
            exemplar_ID: current_stimulus.exemplar_ID,
            category: current_stimulus.category,
            difficulty: current_stimulus.difficulty,
            set: current_stimulus.set,
            phase: current_stimulus.phase
        }
    },
    trial_duration: 4000,
    on_finish: function(data){
        data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    }
};

var feedback_test = {
    type: jsPsychHtmlKeyboardResponse,
    trial_duration: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if(last_trial.correct){
            return 1500
        }else{
            return 5000
        }
    },
    stimulus: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        const is_score_zero = !(score >= Math.abs(incorrect_penalty));
        if (last_trial.response) {
            if(last_trial.correct){
                trial_bonus = correct_bonus;
                trial_bonus = Math.round(trial_bonus * 100) / 100;

                score += trial_bonus;
                score = Math.round(score * 100) / 100;
                return positive_feedback(trial_bonus)
            } else {
                if (!is_score_zero){
                    trial_bonus = incorrect_penalty;
                    score += trial_bonus;
                    score = Math.round(score * 100) / 100;
                    return negative_feedback(trial_bonus)
                }else{
                    return negative_feedback_no_bonus()
                }
            }
        } else {
            if (!is_score_zero){
                trial_bonus = incorrect_penalty;
                score += trial_bonus;
                score = Math.round(score * 100) / 100;
                return timeout_feedback(trial_bonus)
            } else {
                return timeout_feedback_no_bonus()
            }
        }
    },
    data: function(){
        return {task: 'feedback', bonus: score, trial_bonus: trial_bonus}
    },
    choices: "NO_KEYS"
};

var feedback_train = {
    type: jsPsychHtmlKeyboardResponse,
    trial_duration: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if(last_trial.correct){
            return 1500
        }else{
            return 5000
        }
    },
    stimulus: function(){
        const last_trial = jsPsych.data.get().filter({task: 'response'}).last(1).values()[0];
        if (last_trial.response) {
            if(last_trial.correct){
                return positive_feedback_no_bonus()
            } else {
                return negative_feedback_no_bonus()
            }
        } else {
            return timeout_feedback_no_bonus()
        }
    },
    data: function(){
        return {task: 'feedback', bonus: score}
    },
    choices: "NO_KEYS"
};

var trials_training = {
    timeline : [stim_train, blank, choices_train, feedback_train, ITI],
    timeline_variables : stimuli_training.flat(),
    randomize_order : true
};
timeline.push(trials_training)

var intermission = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
            <b> <p> The practice round has finished.</p>
            <p> For the rest of the experiment you will receive a $0.05 bonus for each correct answer and lose $0.05 from your bonus for each incorrect answer!</p>
            <p> The bonus can not become less than $0. </b>
            <p> Press any key to begin the test. </p>
            `,
    data: {task: 'intermission'}
  };
timeline.push(intermission)

var trials = {
    timeline : [stim_test, blank, choices_test, feedback_test, ITI],
    loop_function: function(data){
        return is_finished_all_sets ? false : true
    }
};
timeline.push(trials)

if (IS_ONLINE){
    jatos.onLoad(() => {jsPsych.run(timeline);});
}else{
    jsPsych.run(timeline);
}
