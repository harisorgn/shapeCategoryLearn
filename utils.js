function wrap_choices_debug_in_html(category, exemplar, difficulty, score){
    txt = `
        ${wrap_score_in_html(score)}
        <div class="left_choice">A</div>
        <div class="right_choice">B</div>
        <p>
            cat: ${category} <br> ex: ${exemplar} <br> diff: ${difficulty}
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

function* range_iter(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

function range(start, end) {
    return Array.from(range_iter(start, end))
}

function exemplar_stimulus(idx, stim_path, pack_ID, category, difficulty, phase){
    return {
        stimulus: `${stim_path}/pack_${pack_ID}/cat_${category}/diff_${difficulty}/ex_${category}_${difficulty}_${idx}.png`, 
        correct_response: (category == 1) ? `ArrowLeft` : `ArrowRight`,
        exemplar_ID: idx,
        category: category,
        difficulty: difficulty,
        phase: phase
    };
}

function exemplar_stimuli(indices, stim_path, pack_ID, category, difficulty, phase){
    return Array.from(
        indices, 
        (idx) => (exemplar_stimulus(idx, stim_path, pack_ID, category, difficulty, phase))
    );
}

function rand_in_range(minVal,maxVal)
{
  var randVal = minVal+(Math.random()*(maxVal-minVal));
  return Math.round(randVal);
}

function sample_stimulus(stimuli, difficulty){
    const stims = stimuli[difficulty-1];
    return jsPsych.randomization.sampleWithoutReplacement(stims, 1)[0];
}
