// Start only from an explicit button gesture. One element survives scene changes.
const bgm=document.querySelector('#bgm'),musicButton=document.querySelector('#musicToggle'),musicStatus=document.querySelector('#musicStatus');
// Audio assets are pre-attenuated to 25% amplitude because iOS ignores programmatic volume.
bgm.volume=1;bgm.loop=true;let musicStarting=false;
function musicUI(text){musicButton.textContent=bgm.paused?'♪ 开启':'♪ 暂停';musicButton.setAttribute('aria-pressed',String(!bgm.paused));musicButton.setAttribute('aria-label',bgm.paused?'开启背景音乐':'暂停背景音乐');musicStatus.textContent=text||(!bgm.paused?'正在循环播放《春日回声·2050》 · 轻音量':'音乐已暂停，点击画面顶部 ♪ 开启即可继续。')}
musicButton.addEventListener('click',async()=>{if(musicStarting)return;if(!bgm.paused){bgm.pause();musicUI();return}musicStarting=true;musicButton.textContent='♪ 加载';try{await bgm.play();musicUI()}catch(e){musicUI('音乐未能播放，请再次点击顶部 ♪ 开启。浏览器需由你点击后才允许播放。')}finally{musicStarting=false}});
bgm.addEventListener('playing',()=>musicUI());bgm.addEventListener('pause',()=>musicUI());bgm.addEventListener('error',()=>musicUI('音乐加载失败，请刷新后再点击 ♪ 开启。'));
function suspendMusic(){if(!bgm.paused){bgm.pause();musicUI('已在离开页面时暂停。回来后点击顶部 ♪ 开启，从原位置继续。')}}
document.addEventListener('visibilitychange',()=>{if(document.hidden)suspendMusic()});window.addEventListener('pagehide',suspendMusic);
