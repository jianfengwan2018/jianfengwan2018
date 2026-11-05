// Raster road mask derived from the unmodified 2025 reference, with manual exclusions.
// All playable pixels belong to one connected road/paved-walkway component.
const WALK_WIDTH=2048,WALK_HEIGHT=1228;let roadError=false,roadReady=false;const roadPixels=new Uint8Array(WALK_WIDTH*WALK_HEIGHT);const roadOverlay=document.createElement('canvas');roadOverlay.width=WALK_WIDTH;roadOverlay.height=WALK_HEIGHT;const roadCtx=roadOverlay.getContext('2d');
fetch('walkable.json').then(r=>r.json()).then(data=>{roadCtx.fillStyle='#ffc857';for(const [y,a,b]of data.runs){roadPixels.fill(1,y*WALK_WIDTH+a,y*WALK_WIDTH+b);roadCtx.fillRect(a,y,b-a,1)}roadReady=true}).catch(()=>{document.querySelector('#hint').textContent='道路数据加载失败，请刷新重试。'});
function onCampusRoad(x,y){x=Math.round(x);y=Math.round(y);return x>=0&&y>=0&&x<WALK_WIDTH&&y<WALK_HEIGHT&&roadPixels[y*WALK_WIDTH+x]===1}
