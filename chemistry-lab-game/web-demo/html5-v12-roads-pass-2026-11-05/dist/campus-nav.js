// Local edge sliding only. Every movement sample remains inside the existing map mask.
// Look beyond small roundabouts before selecting a route, so a forward-facing dead-end spur is not preferred.
// Short lookahead is a fallback near genuine corridor endpoints.
// Small print gaps and angled curb pixels must not require deliberate player zigzags.
class RoadNavigator {
 constructor(canWalk){this.canWalk=canWalk;this.reset()}
 reset(){this.path=[];this.direction=[0,0];this.retry=0}
 clearLine(a,b){const n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.35));for(let i=1;i<=n;i++)if(!this.canWalk(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n))return false;return true}
 plan(p,dx,dy,reach=28){const sx=Math.round(p[0]),sy=Math.round(p[1]),nodes=[[sx,sy,-1,0]],seen=new Set([sx+','+sy]);let best=-1,score=Infinity;
  for(let i=0;i<nodes.length&&i<12000;i++){const [x,y,parent,depth]=nodes[i],ox=x-sx,oy=y-sy,forward=ox*dx+oy*dy,side=Math.abs(ox*dy-oy*dx);
   if(forward>=reach&&forward<=reach+4){const cost=depth+side*.8-forward*.15;if(cost<score){score=cost;best=i}continue}
   if(depth>=110)continue;
   for(const [nx,ny]of [[x+1,y],[x-1,y],[x,y+1],[x,y-1]]){const ox=nx-sx,oy=ny-sy,f=ox*dx+oy*dy,s=Math.abs(ox*dy-oy*dx),key=nx+','+ny;if(f< -5||f>reach+5||s>25||seen.has(key)||!this.canWalk(nx,ny))continue;seen.add(key);nodes.push([nx,ny,i,depth+1])}
  }
  if(best<0)return reach>8?this.plan(p,dx,dy,8):[];let path=[];for(let i=best;i>=0;i=nodes[i][2])path.push(nodes[i].slice(0,2));path.reverse();if(!this.clearLine(p,path[0]))return [];
  // Keep the safe orthogonal corridor; shortcuts can clip the corners of tiny raster holes.
  return path;

 }
 advance(p,dx,dy,distance){if(this.direction[0]*dx+this.direction[1]*dy<.94){this.path=[];this.retry=0}this.direction=[dx,dy];this.retry=Math.max(0,this.retry-distance);let remaining=distance,travel=0,limit=0,planned=false;
  while(remaining>.0001&&limit++<256){while(this.path.length&&Math.hypot(this.path[0][0]-p[0],this.path[0][1]-p[1])<.00001)this.path.shift();let ux=dx,uy=dy,step=Math.min(.35,remaining);if(this.path.length){const q=this.path[0],len=Math.hypot(q[0]-p[0],q[1]-p[1]);ux=(q[0]-p[0])/len;uy=(q[1]-p[1])/len;step=Math.min(step,len)}
   const next=[p[0]+ux*step,p[1]+uy*step];if(this.canWalk(...next)&&this.clearLine(p,next)){p[0]=next[0];p[1]=next[1];remaining-=step;travel+=step;continue}
   this.path=[];if(this.retry>0||planned)break;planned=true;this.path=this.plan(p,dx,dy);if(!this.path.length){this.retry=5;break}
  }return travel;
 }
}
if(typeof module!=='undefined')module.exports=RoadNavigator;
