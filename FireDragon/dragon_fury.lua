-- title:   Dragon Fury
-- author:  Frantisek Jahoda
-- desc:    Wings of Fury style raid as a fire dragon, in a Limbo-like world
-- license: MIT License
-- version: 0.1
-- script:  lua
-- saveid:  dragon-fury
-- helpers
local M=math
local sin,cos,abs,flr,sqrt,atan,min,max,pi,exp=M.sin,M.cos,M.abs,M.floor,M.sqrt,M.atan,M.min,M.max,M.pi,M.exp
local rnd=M.random
local function rr(a,b) return a+rnd()*(b-a) end
local function cl(v,a,b) if v<a then return a elseif v>b then return b end return v end
local function wa(a) return (a+pi)%(2*pi)-pi end
local function tt(c,d,s) local f=wa(d-c) if abs(f)<=s then return d end return c+(f>0 and s or -s) end
local function hyp(x,y) return sqrt(x*x+y*y) end
local DT=1/60
if not elli then
 function elli(x,y,a,b,c)
  a,b=flr(a),flr(b)
  for dy=-b,b do local w=b>0 and flr(a*sqrt(1-(dy/b)^2)+.5) or a line(x-w,y+dy,x+w,y+dy,c) end
 end
end
if not ellib then
 function ellib(x,y,a,b,c)
  local px,py
  for i=0,20 do local t=i/20*2*pi local qx,qy=x+cos(t)*a,y+sin(t)*b
   if px then line(px,py,qx,qy,c) end px,py=qx,qy end
 end
end
-- constants
local SW,SH=240,136
local WATER,CEIL=122,10
local LX0,LX1,LY=84,116,100
local LAIR_END,SEA1=170,280
local SANCT=180
local STEP=2
local FIRE,BLAST,CRUSH="fire","blast","crush"
local BREATH_RANGE,BREATH_LIFE=78,.8
local TURN,ROLL=.42,.28
local DIFF={
 {aggr=1,fire=1,wu=.7,lives=3,sc=1},
}
local FEED,COMBO_T,INF_COMBO,INF_T=122,3.5,6,5
-- state
local G={state="title",level=1,score=0,lives=3,time=0,flash=0,hi=0,wind=0,shake=0,mq={},traits={},tlist={},
 mt=0,msg="",sub="",combo=0,ct=0,rt=0,ldt=0,rf=20,cam=0,dif=1,dm=DIFF[1],wu=.7}
local D={}
local ENT,DEC,PS,HT,ES,PT,TX={},{},{},{},{},{},{}
local ROW={}
local PADDR={}
for _,c in ipairs({10,11,8,6}) do for j=0,2 do PADDR[#PADDR+1]=0x3FC0+c*3+j end end
local d_hurt,on_kill,msg,snd,sbreath,explode,flak,shoot,add_text,damage,kill,auto_target
-- sprites
local KEY=11
--- where each sprite is: {cell x, cell y, width, height} in 8x8 cells
local SP={
 dragon={0,0,6,4},
 dragon_front={12,0,4,4},
 dragon_top={0,26,6,6},
 house1={0,16,2,2},house2={2,16,2,2},house3={4,16,2,2},
 mill={6,16,2,3},church={8,16,2,4},tower={10,16,1,3},mage={11,16,1,3},keep={12,16,4,4},
 archer1={0,18,1,1},archer2={1,18,1,1},spear1={2,18,1,1},spear2={3,18,1,1},
 bucket1={4,18,1,1},bucket2={5,18,1,1},douse={0,19,1,1},cannon={1,19,1,1},gyro={2,19,1,1},
 eagle1={3,19,1,1},eagle2={4,19,1,1},eagle3={5,19,1,1},
 ballista={0,20,2,1},catapult={2,20,2,1},hunter={4,20,2,1},
 balloon={6,20,2,3},orni1={8,20,2,2},orni2={10,20,2,2},griffin1={12,20,2,2},griffin2={14,20,2,2},
 griffin3={0,21,2,2},airship={2,23,8,3},
 cursor={15,23,1,1},
 tree1={6,26,1,2},tree2={7,26,1,2},tree3={8,26,1,2},tree4={9,26,1,2},
 ftree1={10,26,1,1},ftree2={11,26,1,1},ftree3={12,26,1,1},
 castle1={6,28,2,2},castle2={8,28,2,2},castle3={10,28,2,2},
}
local SB={}
local function spx(s,x,y)
 local cx,cy=s[1]+x//8,s[2]+y//8
 return peek4(0x8000+(cy*16+cx)*64+(y%8)*8+x%8)
end
function sprite_boxes()
 for n,s in pairs(SP) do
  local x0,y0,x1,y1=99,99,-1,-1
  for y=0,s[4]*8-1 do for x=0,s[3]*8-1 do
   if spx(s,x,y)~=KEY then x0,y0,x1,y1=min(x0,x),min(y0,y),max(x1,x),max(y1,y) end
  end end
  if x1<0 then x0,y0,x1,y1=0,0,s[3]*8-1,s[4]*8-1 end
  SB[n]={x0,y0,x1,y1}
 end
end
function sput(n,x,by,flip)
 local s=SP[n] spr(s[2]*16+s[1],flr(x-s[3]*4),flr(by-s[4]*8),KEY,1,flip or 0,0,s[3],s[4])
end
function sputc(n,x,y,flip)
 local s=SP[n] spr(s[2]*16+s[1],flr(x-s[3]*4),flr(y-s[4]*4),KEY,1,flip or 0,0,s[3],s[4])
end
function sfill(n,x,y,flip,c,centre)
 local s=SP[n] local w,h=s[3]*8,s[4]*8
 local x0,y0=flr(x-w/2),centre and flr(y-h/2) or flr(y-h)
 for py=0,h-1 do for px=0,w-1 do
  if spx(s,px,py)~=KEY then pix(x0+(flip==1 and w-1-px or px),y0+py,c) end
 end end
end
function sdraw(e,n,x,y,flip,centre)
 if e.flash>0 then sfill(n,x,y,flip,15,centre)
 elseif centre then sputc(n,x,y,flip) else sput(n,x,y,flip) end
end
-- sound
local SFXB=0x100E4
function sfx_speed(id) local s=(peek(SFXB+id*66+60)>>4)&7 return s>3 and s-8 or s end
function snd(id,ch,vol,spd)
 if G.mute then return end
 local s=spd or sfx_speed(id)
 local dur=s<0 and 30*(1-s) or 30//(1+s)
 if spd then sfx(id,nil,dur,ch,vol or 15,spd) else sfx(id,nil,dur,ch,vol or 15) end
end
function bgm() if G.mute then music() else music(0) end end
local breath_on=false
function sbreath(on)
 if on and not G.mute then if not breath_on then sfx(0,nil,-1,0,6) breath_on=true end
 elseif breath_on then sfx(-1,nil,0,0) breath_on=false end
end
-- particles
local function pe(x,y,vx,vy,l,s,k,g,dr,gr,c)
 if #PT>=360 then return end
 PT[#PT+1]={x=x,y=y,vx=vx,vy=vy,t=0,l=l,s=s,g=g or 0,k=k,dr=dr or 0,gr=gr or 0,c=c or 3}
end
local function flame(x,y,vx,vy,s,l,sp)
 sp=sp or 5 s=s or 1
 pe(x,y,vx+rr(-sp,sp),vy+rr(-sp,sp),(l or .6)*rr(.7,1.2),s*rr(.7,1.2),1,s*.8,1,-8)
end
function smoke(x,y,s,l,c) s=s or 1.5 pe(x,y,rr(-3,3),rr(-8,-5),(l or 2)*rr(.8,1.2),s,2,s*1.2,.5,-1,c or 3) end
function burst(x,y,n,sp,k,l,s,gr,c,dr,g)
 for _=1,n do local a=rr(0,6.283) local v=rr(.2,1)*sp
  pe(x,y,cos(a)*v,sin(a)*v,(l or .6)*rr(.6,1.2),(s or 1)*rr(.6,1.3),k,g or 0,dr or 1,gr or 0,c) end
end
function boom(x,y,r)
 local k=r/11
 burst(x,y,flr(6+12*k),48*k,1,.7,1.7*k,0,nil,2.5,1.9*k)
 burst(x,y,flr(3+5*k),22*k,2,2.2,2.2*k,0,3,1.5,2.6*k)
 burst(x,y,flr(4+7*k),80*k,3,.8,.5,56,nil,.5)
 pe(x,y,0,0,.35,r*.3,7,r*2.6)
end
function shake(a) G.shake=max(G.shake,a) end
-- terrain
local T,TK,TN={}, {}, 0
local MTN,WSP={}, {}
function volc(x)
 if x>=LX0 and x<=LX1 then return LY end
 local t=x<LX0 and min(1,(LX0-x)/56) or min(1,(x-LX1)/56)
 return LY+(115-LY)*t^1.3-2.6*exp(-((t-.04)*18)^2)
end
local function gy(x)
 local f=x/STEP local i=flr(f)
 if i<0 then return T[0] end
 if i>=TN then return T[TN] end
 local t=f-i return T[i]*(1-t)+T[i+1]*t
end
local function wet(x) return gy(x)>WATER end
function calc_water()
 WSP={} local s=nil
 for i=0,TN do local w=T[i]>WATER
  if w and not s then s=i elseif not w and s then WSP[#WSP+1]={s*STEP,i*STEP} s=nil end end
 if s then WSP[#WSP+1]={s*STEP,TN*STEP} end
end
--- generate the terrain of a level w px wide
function gen_terrain(w,l0,l1,s0,s1,mch)
 G.W=w TN=flr(w/STEP)+2
 local segs={{0,LAIR_END,1},{LAIR_END,SEA1,2}}
 local x=SEA1
 while x<w do
  local x1=min(x+rr(l0,l1),w) if w-x1<170 then x1=w end
  segs[#segs+1]={x,x1,3} x=x1
  if x<w then local s=rr(s0,s1) segs[#segs+1]={x,x+s,2} x=x+s end
 end
 for i=0,TN do TK[i]=3 end
 for _,s in ipairs(segs) do for i=flr(s[1]/STEP),min(TN,flr(s[2]/STEP)) do TK[i]=s[3] end end
 local p1,p2,p3=rr(0,6),rr(0,6),rr(0,6)
 for i=0,TN do local x=i*STEP local k=TK[i]
  if k==1 then T[i]=volc(x) elseif k==2 then T[i]=140
  else T[i]=112+3.4*sin(x/34+p1)+1.9*sin(x/11.4+p2)+.8*sin(x/4.3+p3) end end
 MTN={}
 for _,s in ipairs(segs) do
  if s[3]==3 and s[2]-s[1]>356 and rnd()<mch then
   local mx=rnd()<.5 and s[1]+79 or s[2]-79
   local mh=rr(32,54)+(mch>1 and 11 or 0) local mw=rr(28,43)
   for i=max(0,flr((mx-3*mw)/STEP)),min(TN,flr((mx+3*mw)/STEP)) do
    local d=(i*STEP-mx)/mw
    T[i]=T[i]-mh*exp(-d*d*1.4)*(1+.12*sin(i*1.7)+.08*sin(i*.53))
   end
   MTN[#MTN+1]={mx-2*mw,mx+2*mw}
  end
 end
 for _=1,8 do
  local g={} for i=0,TN do g[i]=T[i] end
  for i=2,TN-2 do if TK[i]~=1 then g[i]=(T[i-2]+T[i-1]+T[i]+T[i+1]+T[i+2])/5 end end
  for i=0,TN do T[i]=g[i] end
 end
 calc_water()
end
function flatten(x0,x1)
 local i0,i1=max(0,flr(x0/STEP)),min(TN-1,flr(x1/STEP))
 local s=0 for i=i0,i1 do s=s+T[i] end
 local a=s/(i1-i0+1)
 for i=i0,i1 do T[i]=a end
 for j=1,6 do local t=j/7
  if i0-j>=0 then T[i0-j]=a+(T[i0-j]-a)*t end
  if i1+j<=TN then T[i1+j]=a+(T[i1+j]-a)*t end end
 calc_water()
end
function land_spans()
 local sp={} local s=nil
 for i=0,TN do local x=i*STEP
  local ok=TK[i]==3 and T[i]<WATER-4
  if ok then for _,m in ipairs(MTN) do if x>=m[1] and x<=m[2] then ok=false break end end end
  if ok and not s then s=x elseif not ok and s then sp[#sp+1]={s+30,x-30} s=nil end
 end
 if s then sp[#sp+1]={s+30,G.W-30} end
 local r={} for _,v in ipairs(sp) do if v[2]-v[1]>66 then r[#r+1]=v end end
 return r
end
-- light & background
local PRE={
 {top=118,mid=214,bot=165,tr=1,tg=1,tb=.97,lit=false},
 {top=66,mid=172,bot=118,tr=1.07,tg=.99,tb=.9,lit=true},
 {top=20,mid=88,bot=52,tr=.9,tg=.97,tb=1.12,lit=true},
 {top=92,mid=198,bot=150,tr=1.05,tg=1,tb=.95,lit=false},
}
function rgb(v,p) return cl(flr(v*p.tr),0,255),cl(flr(v*p.tg),0,255),cl(flr(v*p.tb),0,255) end
--- set the palette for lighting preset p
function build_light(p)
 local fb,mb=p.mid*.66,p.mid*.42
 for r=0,135 do
  local t=r/135
  local b=p.top+(p.bot-p.top)*t+(p.mid-(p.top+p.bot)/2)*exp(-((r-58)/34)^2)
  local fog=cl((r-62)/60,0,1)*.6
  local v={}
  local function put(x) local a,bb,c=rgb(x,p) v[#v+1]=a v[#v+1]=bb v[#v+1]=c end
  put(min(250,b*1.13+8)) put(b) put(fb+(b-fb)*fog) put(mb+(b-mb)*fog*.6)
  ROW[r]=v
 end
 for i=0,9 do
  if i~=6 and i~=7 and i~=8 then
   local g=({[0]=10,22,34,46,60,78,0,0,0,175})[i]
   local a,b,c=rgb(g,p) poke(0x3FC0+i*3,a) poke(0x3FC0+i*3+1,b) poke(0x3FC0+i*3+2,c)
  end
 end
 local wr,wg,wb=36,34,32 if p.lit then wr,wg,wb=200,110,40 end
 poke(0x3FC0+21,wr) poke(0x3FC0+22,wg) poke(0x3FC0+23,wb)
 for i,v in ipairs({0x6e,0x1a,0x0e,0xd2,0x50,0x1a,0xff,0xb4,0x3c,0xff,0xf2,0xd8}) do poke(0x3FC0+12*3+i-1,v) end
end
local function scanline(r)
 if r<0 or r>135 then return end
 local t=ROW[r] if not t then return end
 local f=flr(G.flash)
 if f>0 then for j=1,12 do poke(PADDR[j],min(255,t[j]+f)) end
 else for j=1,12 do poke(PADDR[j],t[j]) end end
end
function SCN(row) scanline(row) end
function BDR(row) scanline(row-4) end
local FAR,MID,FTR,MTR,FCS={}, {}, {}, {}, {}
--- generate the two parallax hill layers, their trees and a few distant castles
function gen_bg()
 local a={rr(0,6),rr(0,6),rr(0,6),rr(0,6),rr(0,6),rr(0,6)}
 for i=0,511 do local x=i/512*2*pi
  FAR[i]=flr(84-30*(.55+.45*(.5*sin(2*x+a[1])+.3*sin(3*x+a[2])+.2*sin(7*x+a[3]))))
  MID[i]=flr(104-18*(.55+.45*(.5*sin(3*x+a[4])+.3*sin(5*x+a[5])+.2*sin(11*x+a[6]))))
 end
 FTR,MTR,FCS={},{},{}
 for _=1,rnd(2,3) do
  local bx=nil
  for _=1,6 do local x=rnd(512)-1
   local free=true for _,c in ipairs(FCS) do if abs(c[1]-x)<60 then free=false end end
   if free and (not bx or FAR[x]<FAR[bx]) then bx=x end
  end
  if bx then FCS[#FCS+1]={bx,"castle"..rnd(3)} end
 end
 for i=1,30 do FTR[i]={rnd(512)-1,"ftree"..rnd(3)} end
 for i=1,22 do MTR[i]={rnd(512)-1,"tree"..rnd(4)} end
end
function recolour(c)
 for i=0,15 do if i~=KEY then poke4(0x3FF0*2+i,c or i) end end
end
function draw_layer(list,hills,o,c,sink)
 recolour(c)
 for _,t in ipairs(list) do
  local sx=(t[1]-o)%512
  if sx>500 then sx=sx-512 end
  if sx<250 then sput(t[2],sx,hills[t[1]]+sink) end
 end
 recolour()
end
function draw_bg(cx)
 cls(11)
 for i=0,3 do local x=((i*97-cx*.04)%340)-60 tri(x,0,x+16,0,x+64,SH,10) end
 local o=cx*.15
 for sx=0,239 do line(sx,FAR[flr(sx+o)%512],sx,SH,8) end
 draw_layer(FCS,FAR,o,8,3) draw_layer(FTR,FAR,o,8,2)
 o=cx*.35
 for sx=0,239 do line(sx,MID[flr(sx+o)%512],sx,SH,6) end
 draw_layer(MTR,MID,o,6,2)
end
function draw_terrain(cx,cy)
 for sx=0,239 do
  local wx=sx+cx local g=gy(wx)-cy
  line(sx,g,sx,SH,0)
  local hsh=flr(wx*37)%11
  if hsh<3 and g<SH then line(sx,g,sx+(hsh-1),g-1-hsh%2,0) end
 end
end
function draw_water(cx,cy)
 for _,w in ipairs(WSP) do
  local a,b=max(w[1],flr(cx)),min(w[2],flr(cx)+SW)
  for x=a,b do
   local y=WATER+.8*sin(x*.19+G.time*2.2)+.5*sin(x*.06-G.time*1.3)-cy
   line(x-cx,y,x-cx,SH,1) pix(x-cx,y,(x*7+flr(G.time*4))%11==0 and 9 or 3)
   if (x*13+flr(G.time*3))%17==0 then pix(x-cx,y+3+(x%5),2) end
  end
 end
end
function draw_lair(cx,cy)
 if cx>LAIR_END+10 then return end
 for _,s in ipairs({{34,74},{126,154}}) do
  local px,py=nil,nil
  for x=s[1],s[2],2 do
   local y=gy(x)-cy+.6 local X=x-cx+.8*sin(x*.5+G.time*2)
   if px then line(px,py,X,y,(flr(G.time*3+x*.1)%3==0) and 14 or 13) end px,py=X,y
  end
 end
 local px,py=100-cx,LY-cy
 for k=0,13 do pix(px-8+(k*7)%17,py-1-(k%3),(flr(G.time*3)+k)%5==0 and 15 or 14) end
 pix(px-2,py-3,12)
 line(px+2,py-1,px+3,py-5,5)
end
-- dragon
function d_reset()
 D.x,D.y,D.a,D.v,D.f=100,63,0,54,1
 D.vx,D.vy=54,0
 D.landed,D.alive,D.hp,D.fire,D.exh=false,true,100,100,false
 D.fb,D.bm,D.ph,D.tt,D.tm,D.tf=8,5,0,0,nil,false
 D.inv,D.hf,D.br,D.boost,D.stall,D.np=0,0,false,false,false,0
 D.rs,D.frd,D.scd,D.bcd,D.fht,D.at,D.atk,D.inf,D.net=0,0,0,0,0,0,0,0,0
 D.fall=false
end
function dtrav() return cos(D.a)>=0 and 1 or -1 end
function dupside() return cos(D.a)*D.f<-.15 end
function dl2w(lx,ly) local c,s=cos(D.a),sin(D.a) ly=ly*D.f return D.x+lx*c-ly*s,D.y+lx*s+ly*c end
function d_fireball()
 if D.scd>0 then return end
 D.scd=.25
 local mx,my=dl2w(17,-4)
 local tx,ty=auto_target(mx,my,190,true)
 local vx,vy=125,20
 if tx then
  local t=(tx-mx)/vx
  vy=cl((ty-my-8.5*t*t)/t,-75,95)
 end
 PS[#PS+1]={k="fb",x=mx,y=my,vx=vx,vy=vy,t=0}
 snd(2,1,11)
end
--- fire breath and its meter
function d_breath(want)
 D.br=want
 if D.br then
  local mx,my=dl2w(17,-4)
  local tx,ty=auto_target(mx,my,BREATH_RANGE,false)
  local a=tx and atan(ty-my,tx-mx) or .2
  local ca,sa=cos(a),sin(a)
  local bvx,bvy=D.vx*.3,D.vy*.3
  for _=1,2 do
   local sp=rr(135,160) local s=rr(-.08,.08)
   pe(mx,my,bvx+cos(a+s)*sp,bvy+sin(a+s)*sp,rr(.75,.9),rr(.6,.9),1,rr(3.4,5.2),1.6,-11)
  end
  D.fht=D.fht-DT
  if D.fht<=0 then D.fht=1/30
   HT[#HT+1]={x=mx,y=my,vx=bvx+ca*150,vy=bvy+sa*150,t=0,hit={},dm=1.5} end
 end
 sbreath(D.br)
end
--- automatic flight follows the landscape and continues to the right
function d_update()
 D.scd=max(0,D.scd-DT)
 D.hf=max(0,D.hf-DT)
 d_breath(btn(5) or key(48))
 local horizontal=(btn(3) and 1 or 0)-(btn(2) and 1 or 0)
 local speed=horizontal<0 and 32 or horizontal>0 and 80 or 54
 D.vx=D.vx+(speed-D.vx)*min(1,5*DT)
 D.v=D.vx
 local look=D.vx*1.2
 local ground=min(gy(D.x),gy(D.x+look*.5),gy(D.x+look))
 local vertical=(btn(1) and 1 or 0)-(btn(0) and 1 or 0)
 local shift=vertical<0 and -23 or vertical>0 and 15 or 0
 local track=cl(ground-35,23,70)
 local target=cl(track+shift,CEIL+12,max(CEIL+12,min(ground-20,90)))
 local climb=vertical~=0 and 48 or 37
 D.vy=cl((target-D.y)*(vertical~=0 and 3 or 2),-climb,climb)
 D.x=D.x+D.vx*DT
 D.y=cl(D.y+D.vy*DT,CEIL+12,90)
 D.a=atan(D.vy,D.vx)
 D.ph=D.ph+DT*2.8
end
function d_hurt(dm)
 shake(.7)
end
function d_entangle(s) burst(D.x,D.y,5,13,6,.4,.5) end
local ox,oy,ca,sa,uu,kx,ky=0,0,1,0,1,1,1
local function TP(lx,ly) lx=lx*kx ly=ly*ky*uu return ox+lx*ca-ly*sa,oy+lx*sa+ly*ca end
--- draw the dragon
function d_draw(cx,cy)
 if not D.alive and not D.fall then return end
 if D.inv>.3 and flr(D.inv*12)%2==0 then return end
 ox,oy=flr(D.x-cx+.5),flr(D.y-cy+.5) ca,sa=cos(D.a),sin(D.a) uu=D.f kx,ky=1,1
 local view=nil
 if D.tt>0 then
  local k=abs(cos(pi*D.tt/(D.tm=="turn" and TURN or ROLL)))
  if k<.5 then
   if D.tm=="turn" then view=SP.dragon_front k=.6+.8*(.5-k)
   else view=SP.dragon_top k=.33+1.34*(.5-k) end
  end
  if D.tm=="turn" then kx=k else ky=k end
 end
 if D.v>75 and not D.landed then
  local k=min(1,(D.v-75)/60)
  for i=0,3 do
   local off=(i-1.5)*3 local st=10+(i%2)*4 local ln=(8+13*k)*(.7+.3*sin(G.time*20+i*2))
   local x0,y0=ox-ca*st-sa*off,oy-sa*st+ca*off
   line(x0,y0,x0-ca*ln,y0-sa*ln,9)
  end
 end
 local u0,v0,L,R,T,B=0,0,-26,22,-16,16
 if view then
  u0,v0=view[1]*8,view[2]*8
  if view==SP.dragon_front then L,R=-16,16 else T,B=-24,24 end
 else
  local fr
  if D.landed then fr=7 elseif D.ph==0 and not D.br then fr=6 else fr=flr(D.ph*6)%6 end
  local s=SP.dragon
  u0,v0=s[1]*8+(fr%2)*48,s[2]*8+(fr//2)*32
 end
 local u1,v1=u0+R-L-.1,v0+B-T-.1
 local x1,y1=TP(L,T) local x2,y2=TP(R,T) local x3,y3=TP(R,B) local x4,y4=TP(L,B)
 textri(x1,y1,x2,y2,x3,y3,u0,v0,u1,v0,u1,v1,false,KEY)
 textri(x1,y1,x3,y3,x4,y4,u0,v0,u1,v1,u0,v1,false,KEY)
 if D.br and not view then local mx,my=TP(17.5,-3.6) circ(mx,my,1,14) end
 if D.inf>0 and rnd()<.6 then local fx,fy=dl2w(rr(-10,8),rr(-3,3)) flame(fx,fy,D.vx*.3,-8,.8,.4) end
end
-- enemies: definitions
local STONE={fire=.2,blast=.7,crush=1.6}
local IRON={fire=.3,blast=1.7,crush=1.4}
local ARMOUR={fire=.4,blast=1.8}
local WOOD={fire=1.5}
--- properties of every enemy kind
local KD={
 house={hp=30,sc=50,heal=6,bl=1,weak=WOOD},
 mill={hp=40,sc=80,heal=6,bl=1,weak=WOOD},
 church={hp=90,sc=150,heal=10,bl=1,weak=STONE,ctr="use fireballs (A)"},
 tower={hp=80,sc=120,heal=6,bl=1,weak=STONE,ctr="use fireballs (A)"},
 keep={hp=220,sc=350,heal=20,bl=1,weak={fire=.15,crush=1.6,blast=.8},ctr="use fireballs (A)",bdps=5,heavy=1},
 mage={hp=70,sc=160,heal=8,bl=1,weak={fire=.15,blast=2,crush=.6},ctr="fireball the crystal (A)",heavy=1},
 soldier={hp=6,sc=15,r=2,bt=4,bdps=3},
 bucket={hp=6,sc=25,r=2,bt=4,bdps=3},
 ballista={hp=40,sc=70,r=3,weak=WOOD,heavy=1},
 hunter={hp=50,sc=130,r=3,weak=IRON,ctr="fireball it (A)",heavy=1},
 catapult={hp=50,sc=90,r=3.4,weak=WOOD,heavy=1},
 cannon={hp=45,sc=110,r=3,weak=IRON,ctr="fireball it (A)",heavy=1},
 eagle={hp=10,sc=30,r=2.4,air=1,heal=5},
 balloon={hp=35,sc=100,r=6,air=1,heal=5,weak={fire=2}},
 orni={hp=30,sc=130,r=4,air=1,heal=5,weak=WOOD,ws=16},
 gyro={hp=25,sc=160,r=3,air=1,heal=5,weak=ARMOUR,ctr="fireball it (A)",ws=12},
 griffin={hp=45,sc=220,r=3.4,air=1,heal=8,weak=ARMOUR,ctr="fireball it (A)",ws=16},
 airship={hp=420,sc=1000,r=12,air=1,heal=40,weak={fire=.35,blast=1.5,crush=1.8},ctr="use fireballs (A)",bdps=4,ws=50},
}
for k,d in pairs(KD) do
 d.r=d.r or 2 d.heal=d.heal or 2 d.weak=d.weak or {}
 d.bt=d.bt or (d.bl and 7 or 3) d.bdps=d.bdps or (d.bl and 7 or 8) d.ws=d.ws or 20
end
local UNLOCK={tower=2,spearman=2,ballista=2,orni=2,church=3,keep=3,catapult=3,bucket=3,cannon=4,gyro=4,mage=4,airship=5,griffin=6,hunter=7}
local function unl(L,k) return L>=(UNLOCK[k] or 1) end
local INTRO={
 [2]={{"Stone towers","Fireballs crack their stone walls"}},
 [3]={{"Castles & catapults","Fireballs break stone"}},
 [4]={{"Frost mages","Fireballs pierce their wards"}},
 [5]={{"The royal airship","Rain fireballs on its hull"}},
}
local TRAITS={archipelago="Archipelago",highlands="Highlands",fortress="Fortress realm",eyrie="Eagle eyrie",armada="Sky armada",storm="Storm"}
local TRAIT_DESC={archipelago="scattered islands - mind the water",highlands="towering mountains",fortress="castles and towers everywhere",
 eyrie="the skies teem with eagles",armada="a fleet of flying machines",storm="rain dampens fires, wind pushes you"}
local TRAIT_KEYS={"archipelago","highlands","fortress","eyrie","armada","storm"}
function place(e,x)
 local s,b=SP[e.sn],SB[e.sn]
 e.x=x e.base=gy(x) e.l=x-s[3]*4+b[1] e.w=b[3]-b[1]+1
 e.h=s[4]*8-b[2] e.top=e.base-e.h e.y=e.base-e.h/2
end
function new(k,x,y)
 local d=KD[k]
 local e={k=k,d=d,x=x,y=y or 0,hp=d.hp,alive=true,burn=0,flash=0,t=rr(0,10),cd=rr(1,3),ch=0,aim=-pi/2}
 if d.bl then
  e.bl=true e.sn=k=="house" and "house"..rnd(3) or k
  place(e,x)
 elseif not d.air then e.y=gy(x)-2 end
 if k=="mage" then e.cd=rr(1.5,3.5) end
 ENT[#ENT+1]=e
 return e
end
local function vul(e,k) return e.d.weak[k] or 1 end
local function hit(e,x,y,r)
 if e.bl then local nx=cl(x,e.l,e.l+e.w) local ny=cl(y,e.top,e.base) return (x-nx)^2+(y-ny)^2<=r*r end
 local k=e.k
 if k=="balloon" then return (x-e.x)^2+(y-e.y+4)^2<=(r+6)^2 or (abs(x-e.x)<2+r and abs(y-e.y-4)<2+r) end
 if k=="airship" then local a,b=(x-e.x)/(24+r),(y-e.y)/(7+r) return a*a+b*b<=1 or (abs(x-e.x)<8+r and y>e.y and y-e.y<11+r) end
 local q=r+e.d.r return (x-e.x)^2+(y-e.y)^2<=q*q
end
auto_target=function(x,y,range,ball)
 local bx,by,score=nil,nil,1e9
 for _,e in ipairs(ENT) do
  if e.alive then
   local tx=e.bl and e.l+e.w/2 or e.x
   local ty=e.bl and e.top+min(e.h*.55,12) or e.y
   local dx,dy=tx-x,ty-y
   if dx>8 and dx<range and abs(dy)<70 then
    local n=dx+abs(dy)*.45
    if ball then
     local weak=e.d.weak
     if (weak.blast or 1)>(weak.fire or 1) then n=n-35 end
    end
    if n<score then bx,by,score=tx,ty,n end
   end
  end
 end
 return bx,by
end
function damage(e,a,k,ign,burn,show)
 if not e.alive then return end
 local m=vul(e,k)
 e.hp=e.hp-a*m e.flash=.07
 if ign then
  local t=burn or e.d.bt local fm=vul(e,FIRE)
  if fm<.5 then t=t*fm end
  e.burn=max(e.burn,t)
 end
 if e.hp<=0 then kill(e) end
end
local function tgt() if D.alive and D.x>SANCT then return D end end
local function take_tok(heavy)
 if heavy then if G.tokH>=1 then G.tokH=G.tokH-1 return true end
 elseif G.tokL>=1 then G.tokL=G.tokL-1 return true end
 return false
end
local function ready(e,inr)
 e.cd=e.cd-DT*G.aggr
 if e.cd>0 or not inr then return false end
 if not take_tok(e.d.heavy) then e.cd=rr(.3,.8) return false end
 return true
end
function lead(sx,sy,spd)
 local t=hyp(D.x-sx,D.y-sy)/spd return D.x+D.vx*t,D.y+D.vy*t,t
end
function wu_aim(sx,sy,spd,g)
 local tf=hyp(D.x-sx,D.y-sy)/spd local tx,ty
 for _=1,4 do local t=G.wu+tf tx,ty=D.x+D.vx*t,D.y+D.vy*t tf=hyp(tx-sx,ty-sy)/spd end
 return atan(ty-sy-.5*g*tf*tf,tx-sx),ty,tf
end
function ontg(a,w) return abs(wa(w-a))<.05 end
function ballistic(sx,sy,tx,ty,v,g)
 local dx,dy=tx-sx,sy-ty local v2=v*v
 local disc=v2*v2-g*(g*dx*dx+2*dy*v2)
 if disc<0 or abs(dx)<1 then return nil end
 local th=atan((v2-sqrt(disc))/(g*abs(dx)))
 return (dx<0 and -1 or 1)*v*cos(th),-v*sin(th)
end
function fire_arrow(sx,sy)
 local d=hyp(D.x-sx,D.y-sy) if d>143 then return end
 local t=max(.25,d/90) local ld=rr(.4,.9)
 local vx=(D.x+D.vx*t*ld-sx)/t local vy=(D.y+D.vy*t*ld-sy)/t-.5*49*t
 local s=rr(-.06,.06) local c,n=cos(s),sin(s)
 shoot("arrow",sx,sy,vx*c-vy*n,vx*n+vy*c) snd(3,3,4)
end
function sloppy(sx,sy,spd,sp)
 local _,_,t=lead(sx,sy,spd) t=t*.6
 return atan(D.y+D.vy*t-sy,D.x+D.vx*t-sx)+rr(-(sp or .08),sp or .08)
end
-- enemies: behaviour
function emit_fire(e)
 if e.bl then
  for _=1,1+flr(e.w/5) do if rnd()<22*DT then
   flame(rr(e.l+1,e.l+e.w-1),rr(e.top,e.top+e.h*.5),0,-17,1.1,.7) end end
  if rnd()<5*DT then smoke(e.x+rr(-2,2),e.top,2,2.8) end
 elseif e.k=="airship" then
  for _=1,3 do if rnd()<25*DT then flame(e.x+rr(-19,19),e.y+rr(-4,4),0,-13,1.3,.7) end end
 else
  if rnd()<30*DT then flame(e.x+rr(-e.d.r,e.d.r),e.y+rr(-e.d.r,e.d.r)*.6,0,-13,.8,.5) end
  if rnd()<6*DT then smoke(e.x,e.y-e.d.r,1.2) end
 end
end
local function eupd(e)
 e.t=e.t+DT if e.flash>0 then e.flash=e.flash-DT end
 if e.burn>0 and e.alive then
  e.burn=e.burn-DT*(G.rain and 1.7 or 1)
  e.hp=e.hp-e.d.bdps*DT*vul(e,FIRE)
  emit_fire(e)
  if e.hp<=0 then kill(e) end
 end
end
local function bupd(e)
 eupd(e)
 if e.burn>0 and e.alive then
  e.sp=(e.sp or 1)-DT
  if e.sp<=0 then e.sp=1
   for _,b in ipairs(ENT) do
    if b~=e and b.bl and b.alive and abs(b.x-e.x)<(b.w+e.w)/2+8 and rnd()<.3 then damage(b,3,FIRE,true,nil,false) end
   end
  end
 end
end
local function fmove(e)
 e.x=e.x+cos(e.hd)*e.v*DT e.y=e.y+sin(e.hd)*e.v*DT
 local g=gy(e.x)
 if e.y>g-13 then e.hd=tt(e.hd,-pi/2,3*DT) e.y=min(e.y,g-6) end
 if e.y<12 then e.hd=tt(e.hd,pi/2,2*DT) end
 if e.x<SANCT then e.hd=tt(e.hd,0,3*DT) elseif e.x>G.W-11 then e.hd=tt(e.hd,pi,3*DT) end
 e.vx,e.vy=cos(e.hd)*e.v,sin(e.hd)*e.v
end
local UPD={}
UPD.house=bupd UPD.mill=bupd UPD.church=bupd
UPD.tower=function(e)
 bupd(e) if not e.alive then return end
 local d=tgt() if not d then return end
 local sx,sy=e.x,e.top-2
 if ready(e,hyp(d.x-sx,d.y-sy)<131) then e.cd=rr(1.8,2.8) fire_arrow(sx,sy) end
end
UPD.keep=function(e)
 bupd(e) if not e.alive then return end
 local sx,sy=e.x,e.top+11
 if e.ch>0 then e.ch=e.ch-DT
  if e.ch<=0 then shoot("bolt",sx,sy,cos(e.aim)*146,sin(e.aim)*146) snd(3,3,7) end return end
 local d=tgt() if not d then return end
 local w,ty=wu_aim(sx,sy,146,9) e.aim=tt(e.aim,w,2.5*DT)
 if ready(e,hyp(d.x-sx,d.y-sy)<169 and ty<sy and ontg(e.aim,w)) then e.cd=rr(2.6,3.6) e.ch=G.wu end
end
UPD.mage=function(e)
 bupd(e) if not e.alive then return end
 local cx,cy=e.x,e.top-2.5
 if e.ch>0 then e.ch=e.ch-DT
  if e.ch<=0 then local a=atan(D.y-cy,D.x-cx) shoot("frost",cx,cy,cos(a)*45,sin(a)*45) snd(2,3,6) end return end
 local d=tgt() if not d then return end
 if ready(e,hyp(d.x-cx,d.y-cy)<141) then e.cd=rr(3.5,5) e.ch=.9 end
end
function siege(e,shot,spd,g)
 local sx,sy=e.x,e.y-1
 if e.ch>0 then e.ch=e.ch-DT
  if e.ch<=0 then shoot(shot,sx,sy,cos(e.aim)*spd,sin(e.aim)*spd) snd(3,3,8) end return end
 local d=tgt() if not d then return end
 local w,ty=wu_aim(sx,sy,spd,g) e.aim=tt(e.aim,w,2*DT)
 if ready(e,hyp(d.x-sx,d.y-sy)<160 and ty<sy-4 and ontg(e.aim,w)) then e.cd=rr(3,4) e.ch=G.wu end
end
UPD.ballista=function(e) eupd(e) if e.alive then siege(e,"bolt",150,9) end end
UPD.hunter=function(e) eupd(e) if e.alive then siege(e,"net",120,26) end end
--- cannon: telegraphed flak shell that bursts near where the dragon will be
UPD.cannon=function(e)
 eupd(e) if not e.alive then return end
 e.rc=max(0,(e.rc or 0)-DT*3)
 local sx,sy=e.x,e.y-1
 if e.ch>0 then e.ch=e.ch-DT
  if e.ch<=0 then e.rc=1
   local mx,my=sx+cos(e.aim)*4,sy+sin(e.aim)*4
   shoot("flak",mx,my,cos(e.aim)*122,sin(e.aim)*122,e.fuse)
   burst(mx,my,5,15,2,.8,1,0,5,1,1.5) snd(8,3,7)
  end return end
 local d=tgt() if not d then return end
 local w,ty=wu_aim(sx,sy,122,11) e.aim=tt(e.aim,w,1.8*DT)
 if ready(e,hyp(d.x-sx,d.y-sy)<178 and ty<sy-7.5 and ontg(e.aim,w)) then
  e.cd=rr(3,4) e.ch=G.wu local _,_,t=lead(sx,sy,122) e.fuse=t*rr(.9,1.1)
 end
end
UPD.catapult=function(e)
 eupd(e) if not e.alive then return end
 e.arm=max(0,(e.arm or 0)-DT*.6)
 local d=tgt() if not d then return end
 if ready(e,abs(d.x-e.x)<169) then
  local sx,sy=e.x,e.y-5
  local tx,ty=lead(sx,sy,105)
  local vx,vy=ballistic(sx,sy,tx,ty,120,94)
  if vx then e.cd=rr(3.8,5) e.arm=1 shoot("rock",sx,sy,vx,vy) snd(3,3,8) else e.cd=.5 end
 end
end
function walker(e,speed,x0,x1)
 local nx=e.x+speed*e.dir*DT
 if nx<x0 or nx>x1 or wet(nx) then e.dir=-e.dir else e.x=nx end
 e.y=gy(e.x)-2
end
UPD.soldier=function(e)
 eupd(e) if not e.alive then return end
 local d=tgt() e.walk=true
 if e.burn>0 then
  if rnd()<2*DT then e.dir=-e.dir end walker(e,20,e.x0,e.x1)
 elseif d and abs(d.x-e.x)<113 then
  e.dir=d.x>e.x and 1 or -1 e.walk=false
  local inr=e.spear==nil or (abs(d.x-e.x)<56 and d.y>e.y-60)
  if ready(e,inr) then
   if not e.spear then e.cd=rr(2,3.4) fire_arrow(e.x,e.y-2)
   else e.cd=rr(2.2,3.5) local vx,vy=ballistic(e.x,e.y-2,d.x,d.y,81,71) if vx then shoot("spear",e.x,e.y-2,vx,vy) end end
  end
  e.y=gy(e.x)-2
 else walker(e,e.spd,e.x0,e.x1) end
end
UPD.bucket=function(e)
 eupd(e) if not e.alive then return end
 e.walk=true e.douse=false
 if e.burn>0 then if rnd()<2*DT then e.dir=-e.dir end walker(e,20,e.x0-22,e.x1+22) return end
 local f=nil
 for _,b in ipairs(ENT) do
  if b.bl and b.alive and b.burn>0 and b.x>e.x0-22 and b.x<e.x1+22 and (not f or abs(b.x-e.x)<abs(f.x-e.x)) then f=b end
 end
 if not f then walker(e,4.7,e.x0-22,e.x1+22) return end
 if abs(f.x-e.x)<f.w/2+2 then
  e.walk=false e.douse=true e.dir=f.x>e.x and 1 or -1
  f.burn=max(0,f.burn-3*DT)
  e.st=(e.st or 0)-DT
  if e.st<=0 then e.st=.15 pe(f.x+rr(-f.w/3,f.w/3),f.top+1,rr(-4,4),-9,.8,1,5,2,1) end
 else e.dir=f.x>e.x and 1 or -1 walker(e,14,e.x0-22,e.x1+22) end
end
--- eagle: circles its home; dives at a dragon in range, hits, retreats upwards, repeats
UPD.eagle=function(e)
 eupd(e) if not e.alive then return end
 local d=tgt() e.st=e.st+DT
 if e.state=="patrol" then
  e.circ=e.circ+DT*.8
  local hx,hy=e.hx+cos(e.circ)*30,e.hy+sin(e.circ)*11
  e.hd=tt(e.hd,atan(hy-e.y,hx-e.x),2*DT) e.v=30
  if d and hyp(d.x-e.x,d.y-e.y)<98 then e.state="attack" e.st=0
   if not e.scr then e.scr=true snd(5,3,9) end end
 elseif e.state=="attack" then
  if not d then e.state="patrol" else
   local tx,ty=lead(e.x,e.y,60)
   e.hd=tt(e.hd,atan(ty-e.y,tx-e.x),3.2*DT) e.v=56
   local dist=hyp(d.x-e.x,d.y-e.y)
   if dist<4+e.d.r then
    d_hurt(5) burst(e.x,e.y,4,22,6,1.5,1,11) e.state="retreat" e.st=0 e.hd=e.hd+pi*.8
   elseif dist>206 then e.state="patrol" e.hx,e.hy=e.x,cl(e.y,22,75) end
  end
 else
  e.v=49 e.hd=tt(e.hd,-pi/2,DT) if e.st>2.5 then e.state="attack" end
 end
 fmove(e)
end
--- griffin rider: patrols, rears up (the warning), charges, retreats
UPD.griffin=function(e)
 eupd(e) if not e.alive then return end
 local d=tgt() e.st=e.st+DT
 local dist=d and hyp(d.x-e.x,d.y-e.y) or 1e9
 if e.state=="patrol" then
  e.circ=e.circ+DT*.6
  local hx,hy=e.hx+cos(e.circ)*41,e.hy+sin(e.circ)*13
  e.hd=tt(e.hd,atan(hy-e.y,hx-e.x),1.8*DT) e.v=32
  if d and dist<103 and e.st>1 then e.state="rear" e.st=0 snd(5,3,11) end
 elseif e.state=="rear" then
  e.v=6 if d then e.hd=tt(e.hd,atan(d.y-e.y,d.x-e.x),4*DT) end
  if e.st>=.65 then
   if d then local t=min(.6,dist/105) e.hd=atan(d.y+d.vy*t*.5-e.y,d.x+d.vx*t*.5-e.x) end
   e.state="charge" e.st=0
  end
 elseif e.state=="charge" then
  e.v=105
  if d and dist<4+e.d.r then d_hurt(12) e.state="retreat" e.st=0 e.hd=e.hd+pi*.7
  elseif e.st>1.1 then e.state="retreat" e.st=0 end
  if rnd()<.5 then pe(e.x,e.y,-e.vx*.2,-e.vy*.2,.4,1,6,0,0,0,0) end
 else
  e.v=41 e.hd=tt(e.hd,-pi/2,.8*DT)
  if e.st>2.2 then e.hx,e.hy=e.x,cl(e.y,22,71) e.state="patrol" e.st=0 end
 end
 fmove(e)
end
UPD.balloon=function(e)
 eupd(e) if not e.alive then return end
 e.x=e.x+e.dr*DT e.y=e.by+sin(e.t*.7)*4.7
 if e.x<188 or e.x>G.W-19 then e.dr=-e.dr end
 e.vx,e.vy=e.dr,0
 local d=tgt() if not d then return end
 if ready(e,hyp(d.x-e.x,d.y-e.y)<113) then e.cd=rr(2,3) fire_arrow(e.x,e.y+2.6) end
end
--- ornithopter: patrols its stretch, follows the dragon's altitude, shoots forward
UPD.orni=function(e)
 eupd(e) if not e.alive then return end
 local d=tgt()
 local f=cos(e.hd)>=0 and 1 or -1
 local alt
 if d and abs(d.x-e.x)<131 then alt=cl(d.y-7.5,15,90) if (d.x-e.x)*f<-38 then f=-f end
 else alt=e.alt if e.x>e.x1 then f=-1 elseif e.x<e.x0 then f=1 end end
 local base=f==1 and 0 or pi
 e.hd=tt(e.hd,base+cl((alt-e.y)/38,-.5,.5)*f,1.5*DT)
 fmove(e)
 if d then
  local dx,dy=d.x-e.x,d.y-e.y
  if ready(e,dx*f>0 and hyp(dx,dy)<113) then
   e.cd=rr(2,3) local a=sloppy(e.x,e.y,105)
   shoot("bolt",e.x,e.y,cos(a)*105+e.vx,sin(a)*105+e.vy) snd(3,3,5)
  end
 end
end
UPD.gyro=function(e)
 eupd(e) if not e.alive then return end
 local d=tgt()
 if d then
  local gx,gy_=d.x+e.side*49,cl(d.y-11,11,88)
  if hyp(gx-e.x,gy_-e.y)<15 then e.side=-e.side end
  e.hd=tt(e.hd,atan(gy_-e.y,gx-e.x),2.2*DT) e.v=45
  if ready(e,hyp(d.x-e.x,d.y-e.y)<103) then e.cd=rr(3,4.2) e.bu=3 end
  if (e.bu or 0)>0 then e.bt=(e.bt or 0)-DT
   if e.bt<=0 then e.bt=.15 e.bu=e.bu-1 local a=sloppy(e.x,e.y,113,.1)
    shoot("bolt",e.x,e.y,cos(a)*113,sin(a)*113) snd(3,3,4) end end
 else e.v=22 e.hd=tt(e.hd,e.x<560 and 0 or pi,DT) end
 fmove(e)
end
--- airship: slowly follows the dragon, shoots and bombs
UPD.airship=function(e)
 eupd(e) if not e.alive then return end
 e.pr=(e.pr or 0)+DT*20
 local d=tgt()
 if d then
  if abs(d.x-e.x)>56 then e.hd=tt(e.hd,d.x>e.x and 0 or pi,.3*DT) end
  for i,ox_ in ipairs({-13,0,13}) do
   e.cds[i]=e.cds[i]-DT*G.aggr
   local tx,ty=e.x+ox_,e.y+(i==2 and 7.5 or 2)
   if e.cds[i]<=0 and hyp(d.x-tx,d.y-ty)<141 then
    if take_tok(false) then e.cds[i]=rr(2.4,3.4) local a=sloppy(tx,ty,113)
     shoot("bolt",tx,ty,cos(a)*113,sin(a)*113) snd(3,3,5)
    else e.cds[i]=rr(.3,.8) end
   end
  end
  e.bc=(e.bc or 2)-DT
  if e.bc<=0 and abs(d.x-e.x)<28 and d.y>e.y then e.bc=1.2 shoot("bomb",e.x,e.y+9,e.vx or 0,6) end
 else e.hd=tt(e.hd,e.x>560 and pi or 0,.3*DT) end
 e.hd=tt(e.hd,cos(e.hd)>0 and 0 or pi,.5*DT)
 fmove(e)
 if e.hp<e.d.hp*.5 and rnd()<8*DT then smoke(e.x+rr(-15,15),e.y,2,2,2) end
end
-- decor: ruins & wrecks
function add_ruin(e)
 local pts={} local n=max(3,flr(e.w/2))
 for i=0,n do pts[#pts+1]={e.l-1+(e.w+2)*i/n,e.base-rr(1,min(5,e.h*.35))} end
 DEC[#DEC+1]={k="ruin",x=e.x,base=e.base,w=e.w+2,l=e.l-1,pts=pts,age=0,alive=true,
  bm={{rr(e.l,e.l+e.w),rr(-.8,.8)},{rr(e.l,e.l+e.w),rr(-.8,.8)}}}
end
function add_wreck(e)
 local n=6 local sh={} local s=e.d.ws/5.33
 for i=0,n-1 do local a=i/n*2*pi sh[#sh+1]={cos(a)*s*rr(.6,1.1),sin(a)*s*rr(.4,.8)} end
 DEC[#DEC+1]={k="wreck",x=e.x,y=e.y,vx=(e.vx or 0)*.5,vy=(e.vy or 0)*.5-9,ws=e.d.ws,rot=0,spin=rr(-4,4),sh=sh,alive=true}
end
--- update ruins and wrecks
function dec_update()
 for i=#DEC,1,-1 do local o=DEC[i]
  if o.k=="ruin" then
   o.age=o.age+DT local s=max(0,1-o.age/30)
   if rnd()<5*DT*s then smoke(o.x+rr(-o.w/3,o.w/3),o.base-2,1.5,3,2) end
   if rnd()<3*DT*s then pe(o.x+rr(-o.w/3,o.w/3),o.base-2,rr(-4,4),rr(-11,-4),1.2,.5,3,0,0,-2) end
   if o.age<8 and rnd()<10*DT*(1-o.age/8) then flame(o.x+rr(-o.w/3,o.w/3),o.base-1.5,0,-11,.8,.5) end
  else
   o.vy=o.vy+79*DT o.x=o.x+o.vx*DT o.y=o.y+o.vy*DT o.rot=o.rot+o.spin*DT
   for _=1,1+flr(o.ws/15) do flame(o.x+rr(-1,1)*o.ws/10,o.y+rr(-1,1)*o.ws/16,0,-8,.8+o.ws*.02,.5) end
   if rnd()<.5 then smoke(o.x,o.y,1+o.ws*.04,2,2) end
   local g=gy(o.x)
   if o.y>g-1 then
    table.remove(DEC,i)
    if wet(o.x) then burst(o.x,WATER,8+flr(o.ws/5),28,5,1.5,1.5,0,nil,1.5,2.6) snd(9,3,9)
    else explode(o.x,g-1,7.5+o.ws*.26,25+o.ws,o.ws>30,nil,CRUSH,false) end
   end
  end
 end
end
--- draw ruins (wrecks=false, behind units) or falling wrecks (wrecks=true)
function dec_draw(cx,cy,wrecks)
 for _,o in ipairs(DEC) do
  if o.k=="ruin" and not wrecks then
   if o.x>cx-30 and o.x<cx+270 then
    for _,b in ipairs(o.bm) do line(b[1]-cx,o.base-cy,b[1]-cx+b[2]*4,o.base-5-cy,0) end
    local p=o.pts
    for i=1,#p-1 do tri(p[i][1]-cx,p[i][2]-cy,p[i+1][1]-cx,p[i+1][2]-cy,p[i][1]-cx,o.base-cy,0)
     tri(p[i+1][1]-cx,p[i+1][2]-cy,p[i+1][1]-cx,o.base-cy,p[i][1]-cx,o.base-cy,0) end
    if o.age<30 and flr(G.time*4+o.x)%3==0 then pix(o.x-cx+rr(-2,2),o.base-1-cy,12) end
   end
  elseif o.k=="wreck" and wrecks then
   local c,s=cos(o.rot),sin(o.rot) local sh=o.sh
   local x0,y0=o.x-cx+sh[1][1]*c-sh[1][2]*s,o.y-cy+sh[1][1]*s+sh[1][2]*c
   for i=2,#sh-1 do
    tri(x0,y0,o.x-cx+sh[i][1]*c-sh[i][2]*s,o.y-cy+sh[i][1]*s+sh[i][2]*c,
     o.x-cx+sh[i+1][1]*c-sh[i+1][2]*s,o.y-cy+sh[i+1][1]*s+sh[i+1][2]*c,0)
   end
  end
 end
end
-- deaths
function death(e)
 local k=e.k
 if e.bl then
  boom(e.x,e.y,5+e.w*.3)
  for _=1,flr(e.w*.8) do pe(rr(e.l,e.l+e.w),rr(e.top,e.base),rr(-28,28),rr(-49,-11),2,1,4,0,0,113,0) end
  add_ruin(e) snd(10,1,10) shake(1.2)
 elseif k=="eagle" then
  burst(e.x,e.y,10,26,6,2.5,1,9,0,1.5) burst(e.x,e.y,5,15,1,.5,1,0,nil,1,1)
 elseif e.d.air then
  boom(e.x,e.y,6) add_wreck(e)
  if k=="airship" then
   for _=1,4 do boom(e.x+rr(-19,19),e.y+rr(-6,6),10) end
   shake(4) snd(1,1,15,-3) msg("AIRSHIP DOWN!",2,"")
  end
 else
  burst(e.x,e.y,5,15,4,1,1,113,0,1) smoke(e.x,e.y,1)
  if k~="soldier" and k~="bucket" then boom(e.x,e.y,6) end
 end
end
function kill(e)
 if not e.alive then return end
 e.alive=false on_kill(e) death(e)
end
-- enemies: drawing
local function ecol(e) return e.flash>0 and 15 or 0 end
function windup(x,y,a,p)
 local c,s=cos(a),sin(a)
 circ(x+c*4.5,y+s*4.5,.6+.8*p,flr(p*10)%2==0 and 13 or 14)
 for k=2,14,2 do local A,B=4.5+k*4,6.8+k*4 line(x+c*A,y+s*A,x+c*B,y+s*B,k<8 and 13 or 12) end
end
local function face(e) return cos(e.hd)>=0 and 1 or -1 end
local function bld(e,cx,cy) sdraw(e,e.sn,e.x-cx,e.base-cy+1) end
--- per-kind draw functions (camera at cx,cy)
local DRW={}
DRW.house=bld DRW.church=bld
DRW.mill=function(e,cx,cy)
 bld(e,cx,cy)
 local c=ecol(e) local hx,hy=e.x-cx,e.top-cy+4.5 local sp=e.burn>0 and 0 or e.t*1.4
 for k=0,3 do local a=sp+k*pi/2 local ex,ey=hx+cos(a)*9,hy+sin(a)*9
  line(hx,hy,ex,ey,c) local px,py=-sin(a)*1.5,cos(a)*1.5
  line(hx+cos(a)*3+px,hy+sin(a)*3+py,ex+px,ey+py,c) end
end
DRW.tower=bld
DRW.keep=function(e,cx,cy)
 bld(e,cx,cy)
 local bx,by=e.x-cx,e.top-cy+11
 line(bx,by,bx+cos(e.aim)*4,by+sin(e.aim)*4,ecol(e))
 if e.ch>0 then windup(bx,by,e.aim,1-e.ch/G.wu) end
end
DRW.mage=function(e,cx,cy)
 bld(e,cx,cy)
 local x,y=e.x-cx,e.top-cy-2.5
 local k=1
 if e.ch>0 then k=1.5+.5*sin(e.t*30) circb(x,y,(1-e.ch/.9)*4+1.5,15) end
 circb(x,y,2.5*k,9)
 tri(x,y-2.5,x+1.3,y,x,y+2.5,15) tri(x,y-2.5,x-1.3,y,x,y+2.5,9)
end
DRW.soldier=function(e,cx,cy)
 local n=(e.spear and "spear" or "archer")..((e.walk and flr(e.t*5)%2==1) and 2 or 1)
 local fl=e.dir<0 and 1 or 0
 if e.burn>0 then sfill(n,e.x-cx,e.y-cy+3,fl,12) else sdraw(e,n,e.x-cx,e.y-cy+3,fl) end
end
DRW.bucket=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy
 local n=e.douse and "douse" or ("bucket"..((e.walk and flr(e.t*5)%2==1) and 2 or 1))
 local fl=e.dir<0 and 1 or 0
 if e.burn>0 then sfill(n,x,y+3,fl,12) else sdraw(e,n,x,y+3,fl) end
 if e.douse then for i=0,4 do pix(x+e.dir*(3+i),y-5-sin(i/4*pi)*3,9) end end
end
--- carriage sprite n plus the aiming bow arm and the wind-up warning
local function siege_draw(e,cx,cy,n)
 local x,y=e.x-cx,e.y-cy
 sdraw(e,n,x,y+3)
 local c=ecol(e) local ca_,sa_=cos(e.aim),sin(e.aim)
 line(x-ca_*1.5,y-1-sa_*1.5,x+ca_*4.5,y-1+sa_*4.5,c)
 local mx,my=x+ca_*2.5,y-1+sa_*2.5
 line(mx-sa_*2.6,my+ca_*2.6,mx+sa_*2.6,my-ca_*2.6,c)
 if e.ch>0 then windup(x,y-1,e.aim,1-e.ch/G.wu) end
end
DRW.ballista=function(e,cx,cy) siege_draw(e,cx,cy,"ballista") end
DRW.hunter=function(e,cx,cy) siege_draw(e,cx,cy,"hunter") end
DRW.catapult=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy
 sdraw(e,"catapult",x,y+3)
 local a=(200-120*(e.arm or 0))*pi/180
 local ex,ey=x+cos(a)*6,y-3-sin(a)*6
 line(x,y-3,ex,ey,ecol(e)) circb(ex,ey,1,ecol(e))
end
DRW.cannon=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy local c=ecol(e)
 local ln=4.5-(e.rc or 0)*1.2
 local ex,ey=x+cos(e.aim)*ln,y-1+sin(e.aim)*ln
 line(x,y-1,ex,ey,c) line(x,y,ex,ey+1,c)
 sdraw(e,"cannon",x,y+3)
 if e.ch>0 then windup(x,y-1,e.aim,1-e.ch/G.wu) end
end
DRW.eagle=function(e,cx,cy)
 local fl=sin(e.t*(e.state=="attack" and 14 or 9))
 sdraw(e,fl>.33 and "eagle1" or (fl<-.33 and "eagle3" or "eagle2"),e.x-cx,e.y-cy,face(e)<0 and 1 or 0,true)
end
DRW.balloon=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy
 sdraw(e,"balloon",x,y,0,true)
 pix(x,y+2,flr(e.t*20)%2==0 and 14 or 13)
end
DRW.orni=function(e,cx,cy)
 sdraw(e,sin(e.t*7)>0 and "orni1" or "orni2",e.x-cx,e.y-cy-1,face(e)<0 and 1 or 0,true)
end
DRW.gyro=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy
 sdraw(e,"gyro",x,y,face(e)<0 and 1 or 0,true)
 local rw=6*abs(sin(e.t*25))+1 line(x-rw,y-3,x+rw,y-3,ecol(e))
end
DRW.griffin=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy local f=face(e)
 local rear=e.state=="rear"
 local n=rear and "griffin3" or (sin(e.t*(e.state=="charge" and 16 or 8))>0 and "griffin1" or "griffin2")
 sdraw(e,n,x,y-2,f<0 and 1 or 0,true)
 local la=rear and -.9 or 0
 local lx,ly=x+cos(la)*6*f,y-2+sin(la)*6
 line(x-f,y-2,lx,ly,ecol(e))
 if rear and flr(e.st*12)%2==0 then circ(lx,ly,1,14) end
end
DRW.airship=function(e,cx,cy)
 local x,y=e.x-cx,e.y-cy
 if x<-40 or x>280 then return end
 local f=face(e)
 sdraw(e,"airship",x,y-2,f<0 and 1 or 0,true)
 local px,gy,ph=x-10*f,y+3,3*abs(sin(e.pr or 0))
 line(x-8*f,gy,px,gy,ecol(e)) line(px,gy-ph,px,gy+ph,ecol(e))
end
-- projectiles
local SPEC={arrow={49,5,1,4},bolt={9,10,1.2,3},rock={94,16,1.7,6},flak={11,13,1,3},
 bomb={113,18,1.5,5},spear={71,7,1,3},frost={0,8,1.7,4.5},net={26,4,2.2,3}}
function shoot(k,x,y,vx,vy,fu)
 local s=SPEC[k]
 ES[#ES+1]={k=k,x=x,y=y,vx=vx,vy=vy,t=0,fu=fu,g=s[1],dm=s[2],r=s[3],l=s[4]}
end
function flak(x,y)
 boom(x,y,6)
 if D.alive and hyp(D.x-x,D.y-y)<13 then d_hurt(13) end
 snd(8,3,8)
end
function explode(x,y,r,dm,big,burn,k,show)
 boom(x,y,r)
 for _,e in ipairs(ENT) do
  if e.alive and abs(e.x-x)<r+40 and hit(e,x,y,r) then
   damage(e,dm*(hit(e,x,y,r*.45) and 1 or .6),k or CRUSH,true,burn,show)
  end
 end
 shake(big and 2.5 or 1.4) snd(1,1,big and 15 or 10,big and -2 or -1)
end
--- update the dragon's fireballs
function ps_update()
 for i=#PS,1,-1 do local s=PS[i] s.t=s.t+DT
  local hitit=false
  if s.k=="fb" then
   s.vy=s.vy+17*DT
   pe(s.x,s.y,rr(-4,4),rr(-4,4),.35,1.2,1,1.9,2)
   if rnd()<.4 then pe(s.x,s.y,0,-2,1,.8,2,1.5,1,0,4) end
   hitit=s.t>2
  else
   s.vy=s.vy+113*DT s.vx=s.vx*(1-.15*DT)
   if rnd()<.7 then pe(s.x,s.y,rr(-2,2),-4,.9,.8,2,1.7,1,0,3) end
  end
  s.x=s.x+s.vx*DT s.y=s.y+s.vy*DT
  local r=s.k=="fb" and 1.3 or 1.7
  for _,e in ipairs(ENT) do if e.alive and abs(e.x-s.x)<50 and hit(e,s.x,s.y,r) then hitit=true break end end
  local g=gy(s.x)
  if s.y>g then
   if s.k=="bm" and wet(s.x) then table.remove(PS,i) snd(9,3,9)
    burst(s.x,WATER,12,30,5,1.4,1.5,0,nil,1.5,3) goto cont end
   hitit=true
  end
  if hitit then table.remove(PS,i)
   if s.k=="fb" then explode(s.x,s.y,11,32,false,1.5,BLAST) else explode(s.x,s.y,18,75,true,nil,CRUSH) end
  end
  ::cont::
 end
end
--- update the breath's flame hitboxes
function ht_update()
 for i=#HT,1,-1 do local h=HT[i]
  h.t=h.t+DT local f=max(0,1-1.6*DT)
  h.vx,h.vy=h.vx*f,h.vy*f h.x,h.y=h.x+h.vx*DT,h.y+h.vy*DT
  local dead=h.t>BREATH_LIFE
  if not dead then
   local r=1.5+6.4*h.t/BREATH_LIFE
   for _,e in ipairs(ENT) do
    if e.alive and not h.hit[e] and abs(e.x-h.x)<50 and hit(e,h.x,h.y,r) then h.hit[e]=true damage(e,h.dm,FIRE,true) end
   end
   if h.y>gy(h.x)-1 then
    if wet(h.x) then dead=true if rnd()<.5 then pe(h.x,WATER,rr(-6,6),-15,1,1.2,5,2.6,1) end
    else h.vy=-abs(h.vy)*.2 end
   end
  end
  if dead then table.remove(HT,i) end
 end
end
--- update enemy shots
function es_update()
 for i=#ES,1,-1 do local s=ES[i]
  s.t=s.t+DT s.vy=s.vy+s.g*DT
  if s.k=="arrow" or s.k=="spear" or s.k=="net" then s.vx=s.vx+G.wind*.5*DT end
  s.x,s.y=s.x+s.vx*DT,s.y+s.vy*DT
  local dead=false
  if s.k=="frost" then
   if D.alive and s.t<3 then
    local cur=atan(s.vy,s.vx) local sp=hyp(s.vx,s.vy)
    cur=tt(cur,atan(D.y-s.y,D.x-s.x),1.1*DT) s.vx,s.vy=cos(cur)*sp,sin(cur)*sp
   end
   if rnd()<.5 then pe(s.x,s.y,rr(-3,3),rr(-3,3),.6,.6,5,.8,1) end
   for _,h in ipairs(HT) do local r=1.5+6.4*h.t/BREATH_LIFE
    if (h.x-s.x)^2+(h.y-s.y)^2<(r+s.r)^2 then dead=true burst(s.x,s.y,8,17,5,1,1,0,nil,1,1.5)
     break end end
  elseif s.k=="flak" then
   if rnd()<.5 then pe(s.x,s.y,0,0,.4,.4,2,.8,0,0,4) end
   if (s.fu and s.t>=s.fu) or (D.alive and hyp(D.x-s.x,D.y-s.y)<8.5) then dead=true flak(s.x,s.y) end
  elseif s.k=="rock" and rnd()<.3 then pe(s.x,s.y,0,0,.5,.6,8,.8,0,0,5) end
  if not dead and D.alive and (D.x-s.x)^2+(D.y-s.y)^2<(4+s.r)^2 then
   dead=true d_hurt(s.dm)
   if s.k=="frost" then burst(s.x,s.y,10,22,5,.9,1,0,nil,1,1.5) snd(9,3,8)
   elseif s.k=="net" then d_entangle(2.2)
   else burst(s.x,s.y,5,28,3,.4) if s.k=="bomb" then flak(s.x,s.y) end end
  end
  if not dead then
   local g=gy(s.x)
   if s.y>g or s.t>s.l or s.y<-40 then dead=true
    if s.y>g-1 then
     if wet(s.x) then burst(s.x,WATER,4,15,5,.8,.8,0,nil,1,1)
     elseif s.k=="rock" or s.k=="bomb" then burst(s.x,g,6,17,8,1,1.2,0,5,1,2) if s.k=="bomb" then flak(s.x,g-1) end end
    end
   end
  end
  if dead then table.remove(ES,i) end
 end
end
function es_draw(cx,cy)
 for _,s in ipairs(ES) do
  local x,y=s.x-cx,s.y-cy local k=s.k
  if k=="arrow" or k=="bolt" or k=="spear" then
   local a=atan(s.vy,s.vx) local ln=k=="arrow" and 1.5 or 2.2
   line(x-cos(a)*ln,y-sin(a)*ln,x+cos(a)*ln,y+sin(a)*ln,0)
   if k=="bolt" then pix(x+cos(a)*ln,y+sin(a)*ln,3) end
  elseif k=="rock" then circ(x,y,1.5,0)
  elseif k=="flak" then rect(x-1,y-1,2,2,0) pix(x,y,13)
  elseif k=="bomb" then circ(x,y,1.5,0) pix(x+1,y-2,14)
  elseif k=="frost" then local p=1+.2*sin(s.t*14) circb(x,y,3*p,9) circ(x,y,1.7*p,15)
  elseif k=="net" then local r=1+min(2,s.t*6) circb(x,y,r,3) line(x-r,y,x+r,y,3) line(x,y-r,x,y+r,3) end
 end
end
function ps_draw(cx,cy)
 for _,s in ipairs(PS) do local x,y=s.x-cx,s.y-cy
  if s.k=="fb" then circ(x,y,2.5,12) circ(x,y,1.5,13) pix(x,y,15)
  else circ(x,y,1.7,0) local a=s.t*9 pix(x+cos(a),y+sin(a),13) end
 end
end
-- particles update/draw
function pt_update()
 for i=#PT,1,-1 do local p=PT[i]
  p.t=p.t+DT
  if p.t>=p.l then table.remove(PT,i) else
   if p.dr~=0 then local f=max(0,1-p.dr*DT) p.vx,p.vy=p.vx*f,p.vy*f end
   p.vy=p.vy+p.gr*DT p.x,p.y=p.x+p.vx*DT,p.y+p.vy*DT
   if (p.k==4 or p.k==3) and p.y>gy(p.x) then
    if p.k==4 and p.vy>11 then p.vy=-p.vy*.3 p.vx=p.vx*.5 p.y=gy(p.x)-.5 else table.remove(PT,i) end
   end
  end
 end
end
local FLC={15,15,14,14,14,13,13,13,12,12,3}
local BACK={[2]=true,[5]=true,[8]=true}
function pt_draw(cx,cy,back)
 for _,p in ipairs(PT) do
  local x,y=p.x-cx,p.y-cy
  if (BACK[p.k] or false)==back and x>-10 and x<250 and y>-10 and y<146 then
   local f=p.t/p.l local r=p.s+p.g*p.t local k=p.k
   if k==1 then circ(x,y,r*(1-.4*f),FLC[flr(f*10)+1])
   elseif k==2 then circ(x,y,r,min(5,p.c+flr(f*3)))
   elseif k==3 then pix(x,y,f<.5 and 14 or 13)
   elseif k==4 then pix(x,y,p.c)
   elseif k==5 then circ(x,y,r,f<.5 and 9 or 10)
   elseif k==6 then pix(x,y,p.c) pix(x+1,y,p.c)
   elseif k==7 then if r>1 then circb(x,y,r,f<.4 and 14 or 12) end
   elseif k==8 then circ(x,y,r,f<.5 and 5 or 6) end
  end
 end
end
-- messages & texts
function msg(m,dur,sub) G.msg,G.sub,G.mt=m,sub or "",dur or 2 end
function add_text(s,x,y,c,l) TX[#TX+1]={s=s,x=x,y=y,c=c or 14,t=0,l=l or 1.2} end
function ot(s,x,y,c,small,sc)
 sc=sc or 1
 for i=-1,1 do for j=-1,1 do if i~=0 or j~=0 then print(s,x+i,y+j,0,false,sc,small) end end end
 return print(s,x,y,c,false,sc,small)
end
function cprint(s,y,c,small,sc)
 local w=print(s,0,-30,c,false,sc or 1,small)
 ot(s,(SW-w)//2,y,c,small,sc)
end
-- scoring, death, progress
function on_kill(e)
 G.score=G.score+flr(e.d.sc*G.dm.sc)
end
-- level generation
local MIX={
 village={house=70,mill=22,tower=8},
 town={house=55,church=12,tower=15,mill=8,mage=10},
 castle={house=40,tower=30,mage=15,church=8,mill=7},
}
function wpick(t,L)
 local tot=0 for k,w in pairs(t) do if unl(L,k) then tot=tot+w end end
 local r=rnd()*tot
 for k,w in pairs(t) do if unl(L,k) then r=r-w if r<=0 then return k end end end
 return "house"
end
function settlement(kind,x0,x1,hw)
 local L=G.level local blk=nil
 if kind=="castle" and hw>47 then
  local k=new("keep",(x0+x1)/2) blk={k.l-6,k.l+k.w+6}
 end
 local x=x0+4
 while true do
  local k=wpick(MIX[kind],L)
  local e=new(k,x)
  table.remove(ENT)
  if blk and x+e.w>blk[1] and x<blk[2] then x=blk[2]
  elseif x+e.w>x1-2 then break
  else place(e,x+e.w/2) ENT[#ENT+1]=e x=x+e.w+rr(3,9) end
 end
end
function ramp(k,cap) return min(cap,G.level-(UNLOCK[k] or 1)+1) end
--- fill the level with enemies
function populate()
 local L=G.level local tr=G.traits
 local has=function(k) return unl(L,k) end
 local sites={}
 for _,s in ipairs(land_spans()) do
  local a,b=s[1],s[2] local n=max(1,flr((b-a)/188)) local sg=(b-a)/n
  for k=0,n-1 do local c=a+sg*(k+.5) local hw=min(sg/2-7,rr(43,75)) if hw>28 then sites[#sites+1]={c,hw} end end
 end
 local want=min(#sites,2+min(L,6))
 while #sites>want do table.remove(sites,rnd(#sites)) end
 local kinds={"village"} if L>=2 then kinds[2]="town" end if has("keep") then kinds[#kinds+1]="castle" end
 local hunters=0
 for _,s in ipairs(sites) do
  local c,hw=s[1],s[2] local x0,x1=c-hw,c+hw
  flatten(x0,x1)
  local kind=tr.fortress and kinds[#kinds] or kinds[rnd(#kinds)]
  settlement(kind,x0,x1,hw)
  for _=1,3+min(L,6)+rnd(0,2) do
   local e=new("soldier",rr(x0,x1)) e.x0,e.x1,e.dir,e.spd=x0,x1,rnd()<.5 and 1 or -1,rr(3.7,7.5)
   if has("spearman") and rnd()<.4 then e.spear=true end
  end
  if has("bucket") then for _=1,rnd(1,2+L//4) do local e=new("bucket",rr(x0,x1)) e.x0,e.x1,e.dir=x0,x1,1 end end
  if has("ballista") then for _=1,rnd(0,ramp("ballista",1+L//3))+(kind=="castle" and 1 or 0) do new("ballista",rr(x0+4,x1-4)) end end
  if has("catapult") and (kind=="castle" or rnd()<.5) then new("catapult",rr(x0+4,x1-4)) end
  if has("cannon") then for _=1,rnd(0,ramp("cannon",1+L//4)) do new("cannon",rr(x0+4,x1-4)) end end
  if has("hunter") then for _=1,rnd(0,1+(L-7)//2) do new("hunter",rr(x0+4,x1-4)) hunters=hunters+1 end end
 end
 if has("hunter") and hunters==0 and #sites>0 then local s=sites[rnd(#sites)] new("hunter",s[1]+rr(-s[2],s[2])*.8) end
 local W=G.W
 local function sky(xm) return rr(xm or 412,W-56),rr(26,68) end
 local flocks=2+min(L,6) if tr.eyrie then flocks=flocks*2 end
 for _=1,flocks do local fx,fy=sky()
  for _=1,rnd(3,4) do local e=new("eagle",fx+rr(-11,11),fy+rr(-7,7))
   e.hd=rnd()<.5 and 0 or pi e.v=30 e.state="patrol" e.st=0 e.circ=rr(0,6) e.hx,e.hy=e.x,e.y end end
 local list={}
 for _=1,1+min(L,5) do list[#list+1]="balloon" end
 if has("orni") then for _=1,min(L,6)-1 do list[#list+1]="orni" end end
 if has("gyro") then for _=1,min(L-3,4) do list[#list+1]="gyro" end end
 if tr.armada then local pool={"balloon"} if has("orni") then pool[2]="orni" end if has("gyro") then pool[#pool+1]="gyro" end
  for _=1,3+L//2 do list[#list+1]=pool[rnd(#pool)] end end
 for _,k in ipairs(list) do local x,y=sky(375) local e=new(k,x,y)
  e.hd=rnd()<.5 and 0 or pi e.v=k=="orni" and 24 or 37
  if k=="balloon" then e.dr=rr(-4.7,4.7) e.by=y e.v=0 end
  if k=="orni" then e.x0,e.x1,e.alt=max(188,x-131),min(W-19,x+131),y end
  if k=="gyro" then e.side=rnd()<.5 and 1 or -1 end
 end
 if has("griffin") then for _=1,min(L-5,4)+(tr.eyrie and 2 or 0) do local x,y=sky(488) local e=new("griffin",x,y)
  e.hd=0 e.v=32 e.state="patrol" e.st=0 e.circ=rr(0,6) e.hx,e.hy=x,y end end
 local ships=(has("airship") and 1 or 0)+(L>=8 and 1 or 0)+((tr.armada and L>=3) and 1 or 0)
 for k=0,ships-1 do local e=new("airship",W-112-k*469,rr(28,41)) e.hd=pi e.v=8.4 e.cds={rr(1,3),rr(1,3),rr(1,3)} end
end
local MINI={}
--- generate the current level
function build_level()
 local L=G.level
 G.pre=PRE[(L-1)%4+1] G.lit=G.pre.lit
 local prev=G.traits G.traits={} G.tlist={}
 local n=L<3 and 0 or (L<6 and 1 or 2)
 local pool={} for _,k in ipairs(TRAIT_KEYS) do if not prev[k] then pool[#pool+1]=k end end
 for _=1,n do local i=rnd(#pool) G.traits[pool[i]]=true G.tlist[#G.tlist+1]=pool[i] table.remove(pool,i) end
 local tr=G.traits
 local dm=G.dm
 G.aggr=min(1.3,1+.06*(L-1))*dm.aggr G.wu=dm.wu
 G.rateL,G.rateH=min(1.6,1+.1*(L-1))*dm.fire,min(.8,.35+.07*(L-1))*dm.fire
 G.tokL,G.tokH=1,1 G.combo,G.ct=0,0
 local w=1690+300*min(L,6)
 local l0,l1,s0,s1=281,488,56,122
 if tr.archipelago then l0,l1,s0,s1=169,281,84,150 end
 gen_terrain(w,l0,l1,s0,s1,tr.highlands and 1.5 or .65)
 gen_bg() build_light(G.pre)
 G.rain=tr.storm G.wind=0 G.flash=0 G.lt=rr(4,10)
 G.drops={} if G.rain then for i=1,70 do G.drops[i]={rr(0,SW),rr(0,SH),rr(130,170)} end end
 ENT,DEC,PS,HT,ES,PT,TX={},{},{},{},{},{},{}
 populate()
 for i=0,79 do MINI[i]=gy((i+.5)/80*G.W) end
 d_reset()
 G.cam=0 G.shake=0 G.rt=0 G.ldt=0 G.rf=20 G.mq={}
 local sub="Hold B for breath, tap A for fireballs"
 if #G.tlist>0 then local t={} for _,k in ipairs(G.tlist) do t[#t+1]=TRAITS[k] end sub=table.concat(t," + ") end
 msg("Level "..L..": let the fire fly!",4,sub)
 for _,c in ipairs(INTRO[L] or {}) do G.mq[#G.mq+1]={"New: "..c[1],3.5,c[2]} end
 for _,k in ipairs(G.tlist) do G.mq[#G.mq+1]={TRAITS[k],3,TRAIT_DESC[k]} end
end
function new_game()
 G.score,G.lives,G.level,G.traits,G.rank,G.nb=0,G.dm.lives,1,{},nil,false
 build_level() G.state="play"
end
-- world update
function storm()
 G.wind=13*sin(G.time*.23)+6.6*sin(G.time*.9+1)
 for _,d in ipairs(G.drops) do d[1]=(d[1]+G.wind*.8*DT)%SW d[2]=(d[2]+d[3]*DT)%SH end
 G.lt=G.lt-DT
 if G.lt<=0 then G.lt=rr(6,14) G.flash=90 snd(1,1,6,-3) end
end
function reinforce()
 G.rf=G.rf-DT
 if G.rf>0 or G.state~="play" then return end
 G.rf=max(10,24-G.level*2)*(G.traits.eyrie and .5 or 1)
 if not tgt() then return end
 local n=0 for _,e in ipairs(ENT) do if e.k=="eagle" then n=n+1 end end
 if n>=10+G.level*2 then return end
 local side=rnd()<.5 and -1 or 1
 local fx=cl(D.x+side*180,SANCT+19,G.W-19) local fy=rr(22,56)
 for _=1,rnd(2,3+min(G.level,8)//2) do local e=new("eagle",fx+rr(-9,9),fy+rr(-7,7))
  e.hd=0 e.v=30 e.state="patrol" e.st=0 e.circ=rr(0,6) e.hx,e.hy=e.x,e.y end
 if unl(G.level,"griffin") and rnd()<.35 then local e=new("griffin",fx,fy-11)
  e.hd=0 e.v=32 e.state="patrol" e.st=0 e.circ=0 e.hx,e.hy=fx,fy end
end
--- one frame of the world simulation
function world_update()
 G.time=G.time+DT
 G.mt=max(0,G.mt-DT)
 if G.mt==0 and #G.mq>0 and G.state=="play" then local m=table.remove(G.mq,1) msg(m[1],m[2],m[3]) end
 G.tokL=min(2,G.tokL+G.rateL*DT) G.tokH=min(2,G.tokH+G.rateH*DT)
 G.ct=max(0,G.ct-DT) if G.ct==0 then G.combo=0 end
 G.flash=max(0,G.flash-DT*270)
 if G.rain then storm() end
 if G.state=="play" then
  d_update()
  if btnp(4) then d_fireball() end
 else sbreath(false) end
 for _,e in ipairs(ENT) do if e.alive then UPD[e.k](e) end end
 local keep={} for _,e in ipairs(ENT) do if e.alive then keep[#keep+1]=e end end ENT=keep
 dec_update() ps_update() ht_update() es_update()
 if G.cam<LAIR_END+20 and rnd()<6*DT then local x=rnd()<.5 and rr(38,72) or rr(128,150) smoke(x,gy(x)-1,1.2,3,4) end
 if G.cam<LAIR_END+20 and rnd()<4*DT then local x=rr(38,150) pe(x,gy(x),rr(-4,4),rr(-17,-8),1.5,.5,3,0,0,4) end
 reinforce()
 pt_update()
 for i=#TX,1,-1 do local t=TX[i] t.t=t.t+DT t.y=t.y-7.5*DT if t.t>t.l then table.remove(TX,i) end end
 if G.state=="title" then
  G.cam=G.cam+((sin(G.time*.05)*.5+.5)*(G.W-SW)-G.cam)*min(1,.5*DT)
 else
  local tg=D.x-SW/2+cl(D.vx,-75,75)/75*43
  G.cam=G.cam+(tg-G.cam)*min(1,4*DT)
 end
 G.cam=cl(G.cam,0,G.W-SW)
 G.shake=max(0,G.shake-6*DT)
end
--- advance after one pass across the landscape
function progress()
 if D.x>=G.W-30 then
  G.level=G.level+1
  build_level()
  snd(7,1,13)
 end
end
-- drawing
function hud()
 rect(0,0,49,9,0)
 print("LEVEL "..G.level,3,2,15,false,1,true)
end
--- draw the whole world, back to front
function draw_world()
 local cam=G.cam+rr(-G.shake,G.shake) local cx,cy=flr(cam),flr(rr(-G.shake,G.shake))
 draw_bg(cx)
 pt_draw(cx,cy,true)
 draw_terrain(cx,cy) draw_lair(cx,cy)
 dec_draw(cx,cy,false)
 for _,e in ipairs(ENT) do if not e.d.air and e.x>cx-30 and e.x<cx+270 then DRW[e.k](e,cx,cy) end end
 draw_water(cx,cy)
 for _,e in ipairs(ENT) do if e.d.air and e.x>cx-45 and e.x<cx+285 then DRW[e.k](e,cx,cy) end end
 dec_draw(cx,cy,true)
 d_draw(cam,cy)
 ps_draw(cx,cy) es_draw(cx,cy)
 pt_draw(cx,cy,false)
 if G.rain then local dx=-G.wind*.03 for _,d in ipairs(G.drops) do line(d[1],d[2],d[1]+dx,d[2]-3,9) end end
 for _,t in ipairs(TX) do ot(t.s,t.x-cx-#t.s*2,t.y-cy,t.c,true) end
end
--- two-button title screen
function title()
 local w=print("DRAGON FURY",0,-30,0,false,2)
 ot("DRAGON FURY",(SW-w)//2,22,13,false,2)
 print("DRAGON FURY",(SW-w)//2,21,14,false,2)
 cprint("THE DRAGON FLIES AND AIMS",48,15,true)
 cprint("B  HOLD FOR FIRE BREATH",65,14,true)
 cprint("A  TAP FOR FIREBALLS",77,14,true)
 cprint("ARROWS ARE OPTIONAL",93,15,true)
 cprint("UP/DOWN: HEIGHT   LEFT/RIGHT: SPEED",103,14,true)
 if flr(G.time*2)%2==0 then cprint("PRESS B OR A TO START",120,15,true) end
end
-- main
function init()
 if G.ready then return end
 G.ready=true
 M.randomseed(tstamp and tstamp() or 1)
 sprite_boxes()
 G.level=1 G.traits={} build_level() G.state="title"
 bgm()
end
function BOOT() init() end
--- main loop, 60 times a second
function TIC()
 init()
 poke(0x3FFB,127)
 if G.state=="title" and (btnp(4) or btnp(5) or keyp(48) or keyp(50)) and G.time>.5 then
  new_game() snd(7,1,13)
 end
 world_update()
 if G.state=="play" then progress() end
 draw_world()
 if G.state=="title" then title() else hud() end
end
