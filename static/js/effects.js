// Particle system
(function(){
  const canvas=document.getElementById('particle-canvas');
  if(!canvas)return;
  const ctx=canvas.getContext('2d');
  let W,H,particles=[],mouse={x:-999,y:-999};
  const COLORS=['#00f5ff','#bf00ff','#ffd700','#39ff14','#ff006e'];

  function resize(){W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight}

  class P{
    constructor(){this.reset(true)}
    reset(init){
      this.x=Math.random()*W; this.y=init?Math.random()*H:H+10;
      this.vx=(Math.random()-.5)*.4; this.vy=-(Math.random()*.8+.2);
      this.size=Math.random()*1.8+.4; this.life=0; this.maxLife=Math.random()*280+160;
      this.color=COLORS[Math.floor(Math.random()*COLORS.length)];
    }
    update(){
      this.life++; this.x+=this.vx; this.y+=this.vy;
      const dx=this.x-mouse.x,dy=this.y-mouse.y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<90){this.vx+=dx/d*.25;this.vy+=dy/d*.25}
      if(this.life>this.maxLife||this.y<-10)this.reset(false);
    }
    draw(){
      const a=Math.sin(this.life/this.maxLife*Math.PI)*.55;
      ctx.save();ctx.globalAlpha=a;ctx.fillStyle=this.color;
      ctx.shadowColor=this.color;ctx.shadowBlur=5;
      ctx.beginPath();ctx.arc(this.x,this.y,this.size,0,Math.PI*2);ctx.fill();ctx.restore();
    }
  }

  function drawLines(){
    for(let i=0;i<particles.length;i++)
      for(let j=i+1;j<particles.length;j++){
        const dx=particles[i].x-particles[j].x,dy=particles[i].y-particles[j].y;
        const d=Math.sqrt(dx*dx+dy*dy);
        if(d<75){ctx.save();ctx.globalAlpha=(1-d/75)*.07;ctx.strokeStyle='#00f5ff';
          ctx.lineWidth=.5;ctx.beginPath();ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);ctx.stroke();ctx.restore()}
      }
  }

  resize();
  for(let i=0;i<100;i++)particles.push(new P());
  window.addEventListener('resize',resize);
  window.addEventListener('mousemove',e=>{mouse.x=e.clientX;mouse.y=e.clientY});

  (function loop(){
    ctx.clearRect(0,0,W,H);drawLines();
    particles.forEach(p=>{p.update();p.draw()});
    requestAnimationFrame(loop);
  })();
})();

// Toast utility
function showToast(msg,type='info',dur=1400){
  let t=document.getElementById('toast');
  if(!t){t=document.createElement('div');t.id='toast';t.className='toast';document.body.appendChild(t)}
  t.textContent=msg;t.className=`toast toast-${type} show`;
  clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('show'),dur);
}

// Confetti
function launchConfetti(){
  const colors=['#00f5ff','#ffd700','#bf00ff','#39ff14','#ff006e'];
  const style=document.createElement('style');
  style.textContent='@keyframes cffall{to{transform:translateY(110vh) rotate(720deg);opacity:0}}';
  document.head.appendChild(style);
  for(let i=0;i<90;i++){
    const el=document.createElement('div');
    el.style.cssText=`position:fixed;width:8px;height:8px;border-radius:2px;pointer-events:none;z-index:9999;
      left:${Math.random()*100}vw;top:-10px;
      background:${colors[i%colors.length]};
      transform:rotate(${Math.random()*360}deg);
      animation:cffall ${1.5+Math.random()*2}s linear ${Math.random()*.6}s forwards`;
    document.body.appendChild(el);
    setTimeout(()=>el.remove(),3200);
  }
}

// Sound
const AC=window.AudioContext||window.webkitAudioContext;
let ac=null;
function playSound(type){
  try{
    if(!ac)ac=new AC();
    const o=ac.createOscillator(),g=ac.createGain();
    o.connect(g);g.connect(ac.destination);
    if(type==='correct'){o.frequency.setValueAtTime(523,ac.currentTime);o.frequency.setValueAtTime(659,ac.currentTime+.1);o.frequency.setValueAtTime(784,ac.currentTime+.2)}
    else if(type==='wrong'){o.frequency.setValueAtTime(200,ac.currentTime);o.frequency.setValueAtTime(140,ac.currentTime+.15)}
    else if(type==='complete'){o.frequency.setValueAtTime(523,ac.currentTime);o.frequency.setValueAtTime(784,ac.currentTime+.1);o.frequency.setValueAtTime(1047,ac.currentTime+.2);o.frequency.setValueAtTime(1319,ac.currentTime+.3)}
    g.gain.setValueAtTime(.28,ac.currentTime);g.gain.exponentialRampToValueAtTime(.001,ac.currentTime+.45);
    o.start();o.stop(ac.currentTime+.45);
  }catch(e){}
}

// Background music (ambient drone)
let bgMusic=null,bgGain=null;
function startBgMusic(){
  try{
    if(!ac)ac=new AC();
    if(bgMusic)return;
    bgGain=ac.createGain();bgGain.gain.value=0.04;bgGain.connect(ac.destination);
    const freqs=[55,82.4,110,146.8];
    freqs.forEach(f=>{
      const o=ac.createOscillator();
      o.type='sine';o.frequency.value=f;o.connect(bgGain);o.start();
    });
    bgMusic=true;
  }catch(e){}
}
document.addEventListener('click',()=>startBgMusic(),{once:true});
