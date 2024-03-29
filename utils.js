function wrap_choices_debug_in_html(category, exemplar, set, score){
    txt = `
        ${wrap_score_in_html(score)}
        <div class="left_choice">A</div>
        <div class="right_choice">B</div>
        <p>
            cat: ${category} <br> ex: ${exemplar} <br> set: ${set}
        </p>
    `;
    return txt
}

function wrap_choices_in_html(score){
    txt = `
        ${wrap_score_in_html(score)}
        <div class="left_choice">A</div>
        <div class="right_choice">B</div>
    `;
    return txt
}

function wrap_stim_in_html(stimulus, score){
    txt = `
        ${wrap_score_in_html(score)}
        <img class="stim" src=${stimulus}></img>
    `;
    return txt
}

function wrap_video_stim_in_html(stimulus, score){
    txt = `
        ${wrap_score_in_html(score)}
        <video autoplay class="stim" src=${stimulus}></video>    
    `;
    return txt
}

function wrap_score_in_html(score){
    txt = `
        <div style="text-align: center; position: fixed; top: 5vh; left: 40vw;">
            <div style="margin:0 auto; width: 20vw; top: 8vh; font-size: 2vw"> 
            <font color="green"> Bonus : $${score} </font>
            </div>
        </div>
    `;
    return txt
}

function wrap_wrong_feedback_in_html(stimulus, category){
    txt = (category == 1) ?
        `<img class="left_stim" src=${stimulus}></img>`: 
        `<img class="right_stim" src=${stimulus}></img>
    `;
    return txt
}

function positive_feedback(gain){
    return `<p> <font color="green" size="5vw"> Correct category! </font> <br> <br> <font color="green" size="8vw"> + $${gain} </font> </p>`;
}

function positive_feedback_no_bonus(){
    return `<p><font color="green" size="5vw"> Correct category! </font></p>`;
}

function negative_feedback(loss){
    return `<p> <font color="red" size="5vw"> Wrong category! </font> <br> <br> <font color="red" size="8vw"> - $${Math.abs(loss)} </font> </p>`;
}

function negative_feedback_no_bonus(){
    return `<p> <font color="red" size="5vw"> Wrong category! </font> </p>`
}

function timeout_feedback(loss){
    return `<p> <font color="red" size="5vw"> Time out! </font> <br> <br> <font color="red" size="8vw"> - $${Math.abs(loss)} </font> <br> <br> Please try to respond as quickly as possible. </p>`
}

function timeout_feedback_no_bonus(){
    return `<p> <font color="red" size="5vw"> Time out! </font> <br> <br> Please try to respond as quickly as possible. </p>`
}

function* range_iter(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

function range(start, end) {
    return Array.from(range_iter(start, end))
}

function exemplar_stimulus(idx, stim_path, pack_name, category, difficulty, set, phase, format){
    return {
        stimulus: `${stim_path}/${pack_name}/cat_${category}/diff_${difficulty}/ex_${category}_${difficulty}_${idx}.${format}`, 
        correct_response: (category == 1) ? `ArrowLeft` : `ArrowRight`,
        exemplar_ID: idx,
        category: category,
        difficulty: difficulty,
        set: set,
        phase: phase
    };
}

function exemplar_stimuli(indices, stim_path, pack_name, category, difficulty, set, phase, format){
    return Array.from(
        indices, 
        (idx) => (exemplar_stimulus(idx, stim_path, pack_name, category, difficulty, set, phase, format))
    );
}

function rand_in_range(minVal,maxVal)
{
  var randVal = minVal+(Math.random()*(maxVal-minVal));
  return Math.round(randVal);
}

function sample_stimulus(stimuli, idx){
    const stims = stimuli[idx];
    return jsPsych.randomization.sampleWithoutReplacement(stims, 1)[0];
}

function RT_to_reward(RT){
    max_reward = 0.1
    decay = 0.2
    return max_reward * Math.exp(-decay * (RT/1000))
}
