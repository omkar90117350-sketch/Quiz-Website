const TIMER_SEC = 20;
const CIRC = 2 * Math.PI * 27;

let questions=[], currentIdx=0, answers={}, score=0, streak=0;
let timerInterval=null, answered=false;

async function loadQuestions(){
  const root = document.getElementById('quiz-root');
  const {topic,difficulty,mode} = root.dataset;
  try{
    const r = await fetch(`/api/questions?topic=${topic}&difficulty=${difficulty}&mode=${mode}`);
    // Use session questions via hidden form approach instead
    // Questions already loaded server-side into session
    // Fetch from dedicated endpoint
    const res = await fetch(`/quiz/questions`);
    questions = await res.json();
    if(!questions.length){showError('No questions found.');return}
    renderQuestion();startTimer();
  }catch(e){showError('Failed to load. Please refresh.')}
}

// Questions passed directly via data attribute
function initQuiz(qs){
  questions = qs;
  renderQuestion();startTimer();
}

function renderQuestion(){
  answered=false;
  const q=questions[currentIdx],total=questions.length;
  const opts=[{l:'A',t:q.option_a},{l:'B',t:q.option_b},{l:'C',t:q.option_c},{l:'D',t:q.option_d}];

  document.getElementById('prog-fill').style.width=(currentIdx/total*100)+'%';
  document.getElementById('prog-txt').textContent=`${currentIdx+1} / ${total}`;
  document.getElementById('score-txt').textContent=`Score: ${score}`;
  document.getElementById('streak-txt').textContent=streak>1?`🔥 ×${streak}`:'';

  const card=document.getElementById('q-card');
  card.dataset.num=`QUESTION ${currentIdx+1} / ${total}`;
  document.getElementById('q-text').textContent=q.question;

  document.getElementById('opts').innerHTML=opts.map((o,i)=>`
    <button class="opt" data-ans="${o.t.replace(/"/g,'&quot;')}" onclick="selectAnswer(this,'${q.correct_answer.replace(/'/g,"\\'")}')">
      <span class="opt-lbl">${o.l}</span><span>${o.t}</span>
    </button>`).join('');

  card.classList.remove('exit');card.classList.add('enter');
  setTimeout(()=>card.classList.remove('enter'),300);
}

function selectAnswer(btn, correct){
  if(answered)return;
  answered=true;stopTimer();
  const userAns=btn.dataset.ans;
  const isCorrect=userAns.trim().toLowerCase()===correct.trim().toLowerCase();
  answers[currentIdx]=userAns;

  document.querySelectorAll('.opt').forEach(b=>{
    b.disabled=true;
    if(b.dataset.ans.trim().toLowerCase()===correct.trim().toLowerCase())b.classList.add('correct');
    else if(b===btn&&!isCorrect)b.classList.add('wrong');
  });

  if(isCorrect){streak++;score++;showToast('✓ CORRECT!','ok');playSound('correct')}
  else{streak=0;showToast('✗ WRONG','err');playSound('wrong')}
  document.getElementById('streak-txt').textContent=streak>1?`🔥 ×${streak}`:'';

  const form=document.getElementById('ans-form');
  const inp=document.createElement('input');inp.type='hidden';inp.name=currentIdx;inp.value=userAns;
  form.appendChild(inp);

  setTimeout(nextQuestion,1300);
}

function nextQuestion(){
  currentIdx++;
  if(currentIdx>=questions.length){playSound('complete');document.getElementById('ans-form').submit();return}
  resetTimer();renderQuestion();
}

// Timer
function startTimer(){
  let rem=TIMER_SEC;
  const arc=document.getElementById('t-arc'),txt=document.getElementById('timer-txt'),ring=document.getElementById('timer-ring');
  arc.style.strokeDasharray=CIRC;arc.style.strokeDashoffset=0;txt.textContent=TIMER_SEC;ring.className='timer-ring';
  timerInterval=setInterval(()=>{
    rem--;
    arc.style.strokeDashoffset=CIRC*(1-rem/TIMER_SEC);txt.textContent=rem;
    if(rem<=5)ring.className='timer-ring danger';
    else if(rem<=10)ring.className='timer-ring warn';
    if(rem<=0){clearInterval(timerInterval);timeOut()}
  },1000);
}
function stopTimer(){clearInterval(timerInterval)}
function resetTimer(){stopTimer();startTimer()}
function timeOut(){
  if(answered)return;answered=true;streak=0;
  showToast('⏰ TIME OUT','err');
  document.querySelectorAll('.opt').forEach(b=>{
    b.disabled=true;
    if(b.dataset.ans.trim().toLowerCase()===questions[currentIdx].correct_answer.trim().toLowerCase())b.classList.add('correct');
  });
  const form=document.getElementById('ans-form');
  const inp=document.createElement('input');inp.type='hidden';inp.name=currentIdx;inp.value='';
  form.appendChild(inp);
  setTimeout(nextQuestion,1300);
}

function showError(msg){
  document.getElementById('quiz-root').innerHTML=`<div class="glass" style="padding:40px;text-align:center;margin-top:80px"><p class="neon-pink">${msg}</p><a href="/play" class="btn" style="margin-top:20px">← Go Back</a></div>`;
}
