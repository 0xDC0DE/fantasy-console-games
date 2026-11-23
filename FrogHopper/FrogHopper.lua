-- title:   Frog Hopper
-- author:  Little Pixel Games
-- desc:    Count, add and subtract across a pond
-- script:  lua

local min,max,floor,sin,pi=math.min,math.max,math.floor,math.sin,math.pi
local LEVELS={
 {name="EASY",count=6,jump=3},
 {name="MEDIUM",count=7,jump=4},
 {name="HARD",count=9,jump=5},
}
local MODES={"COUNT HOPS","SUMS","PLUS & MINUS"}
local MODE_SHORT={"COUNT HOPS","SUMS","+ AND -"}
-- These IDs are generated from the 24x24 source frames by build.py.
local F={idle=0,idle2=3,croak1=6,croak2=9,croak3=12,
 jump1=48,jump2=51,jump3=54,jump4=57,
 hurt1=60,hurt2=96,shock1=99,shock2=102,shock3=105,
 purple=108,purple_speak=144,green_speak=147,mini=150,heart=153,crown=156,
 smile=192,fish_green_low=195,fish_green_high=198,
 fish_gold_low=201,fish_gold_high=204}
local G={mode="menu",menu_focus=1,game_mode=1,level=1,t=0,base=0,at=1,choice=2,add=1,
 direction=1,back_count=0,jump_t=0,turn_t=0,from=1,to=1,
 wrong_t=0,party_t=0,slide_t=0,next_base=0,
 croak_t=0,guide_t=0,party_icons=1,labels={},path={},target=2,path_step=1,
 wrong_kind=1,mistakes=0,hint_t=0,hint_kind=1}

local function rand(a,b) return math.random(a,b) end
local function start_number(level)
 if level==1 then return 0 end
 if level==2 then return rand(1,3) end
 local band=rand(1,3)
 return ({5,10,15})[band]+rand(0,2)
end
local function step_size() return 204/(LEVELS[G.level].count-1) end
local function stone_x(i) return 18+(i-1)*step_size() end
local function shuffle(list)
 for i=#list,2,-1 do
  local j=rand(1,i)
  list[i],list[j]=list[j],list[i]
 end
end
local function path_positions(count,length)
 local middle={}
 for i=2,count-1 do middle[#middle+1]=i end
 shuffle(middle)
 local chosen={}
 for i=1,length-2 do chosen[i]=middle[i] end
 shuffle(chosen)
 local backward=false
 for i=2,#chosen do
  if chosen[i]<chosen[i-1] then backward=true break end
 end
 if not backward then chosen[1],chosen[2]=chosen[2],chosen[1] end
 local stops={1}
 for _,position in ipairs(chosen) do stops[#stops+1]=position end
 stops[#stops+1]=count
 return stops
end
local function new_board()
 local base=start_number(G.level)
 local count=LEVELS[G.level].count
 local labels,path={},{}
 if G.game_mode==1 then return base,labels,path end
 local values,top={},base+count-1
 if G.game_mode==2 then
  -- Positive sums follow rising values, but can hop in either direction.
  repeat
   values={base}
   while values[#values]<top do
    local step=rand(1,min(LEVELS[G.level].jump,top-values[#values]))
    values[#values+1]=values[#values]+step
   end
  until #values>=4 and #values<count
 else
  -- One distractor remains after swapping neighboring values. The swap
  -- creates a subtraction prompt without exceeding Easy's largest step.
  local omitted=rand(1,count-2)
  for offset=0,count-1 do
   if offset~=omitted then values[#values+1]=base+offset end
  end
  local index=rand(2,#values-2)
  values[index],values[index+1]=values[index+1],values[index]
 end
 path=path_positions(count,#values)
 for i,position in ipairs(path) do labels[position]=values[i] end
 local unused={}
 for value=base+1,top-1 do
  local on_path=false
  for _,v in ipairs(values) do if v==value then on_path=true break end end
  if not on_path then unused[#unused+1]=value end
 end
 shuffle(unused)
 local next_unused=1
 for i=2,count-1 do
  if labels[i]==nil then
   labels[i]=unused[next_unused]
   next_unused=next_unused+1
  end
 end
 return base,labels,path
end
local function new_prompt()
 local count=LEVELS[G.level].count
 if G.at==count then return end
 if G.game_mode==1 then
  local left,right=G.at-1,count-G.at
  if left==0 then G.direction=1
  elseif G.back_count==0 and right<=LEVELS[G.level].jump then G.direction=-1
  elseif G.back_count<2 and rand(1,100)<=35 then G.direction=-1
  else G.direction=1 end
  local available=(G.direction==1) and right or left
  G.add=rand(1,min(LEVELS[G.level].jump,available))
  G.target=G.at+G.direction*G.add
  G.choice=G.at+G.direction
 else
  G.target=G.path[G.path_step+1]
  G.add=G.labels[G.target]-G.labels[G.at]
  G.choice=min(count,G.at+1)
 end
 G.guide_t=18
 G.mistakes=0
end
local function start_game()
 math.randomseed(time())
 G.mode="play" G.t=0
 G.base,G.labels,G.path=new_board()
 G.at=1 G.choice=2 G.croak_t=0 G.back_count=0
 G.path_step=1
 new_prompt()
end

-- A larger golden V, kept symmetric at native size.
local function selector(x,y,c)
 x=floor(x+.5)
 pix(x-3,y,c) pix(x+3,y,c)
 pix(x-2,y+1,c) pix(x+2,y+1,c)
 pix(x-1,y+2,c) pix(x+1,y+2,c)
 pix(x,y+3,c)
end
local function center_text(s,x,y,c,scale)
 scale=scale or 1
 local w=#s*6*scale
 print(s,floor(x-w/2),floor(y),c,false,scale)
end
local function prompt_arrow(x,y,direction)
 for i=0,10 do pix(x+i,y+3,1) end
 for i=1,3 do
  local ax=(direction==1) and x+10-i or x+i
  pix(ax,y+3-i,1) pix(ax,y+3+i,1)
 end
end
local function frog(frame,x,bottom,flip)
 spr(frame,floor(x-12+.5),floor(bottom-24+.5),0,1,flip or 0,0,3,3)
end
local function sound_pick() sfx(0,65,6,0,7) end
local function sound_confirm() sfx(5,72,7,0,6) end
local function sound_boing_start() sfx(1,62,12,0,9) end
local function sound_boing_down() sfx(1,50,12,0,8) end
local function sound_boing_land() sfx(1,57,7,1,6) end
local function sound_oww_start() sfx(3,58,12,0,8) end
local function sound_oww_tail() sfx(3,49,14,0,8) end
local function sound_cricket(note) sfx(4,note,5,0,6) end
local function sound_fanfare(note) sfx(2,note,13,0,8) end
local function sound_here(note) sfx(6,note,7,0,7) end
local function water(t)
 rect(0,0,240,45,7)
 rect(0,0,240,11,6)
 rect(0,45,240,91,2)
 rect(0,45,240,14,3)
 line(0,45,239,45,4)
 for y=61,135,13 do
  for x=0,239,31 do
   local drift=floor(sin(t/65+x*.09+y*.17)*3)
   line(x+drift,y,x+8+drift,y,3)
   pix(x+13+drift,y+2,4)
  end
 end
 for k=0,3 do
  local x=19+k*64+floor(sin(t/43+k)*3)
  local y=119+(k%2)*9
  line(x-7,y,x-3,y,4) line(x+3,y,x+7,y,4)
 end
 -- A small floating leaf keeps the bottom of the pond alive.
 local lx,ly=126+floor(sin(t/85)*5),118+floor(sin(t/46)*2)
 elli(lx,ly,9,3,5) elli(lx,ly-1,7,2,7)
 line(lx-5,ly,lx+5,ly-1,11)
 line(lx+7,ly-3,lx+10,ly-5,5)
end
local function rock(x,i,t)
 local r=(LEVELS[G.level].count==9) and 11 or 14
 local v=(i-1)%4
 x=floor(x+.5)
 local y=88
 elli(x,y+6,r+2,3,1)
 elli(x,y+2,r,5,8)
 elli(x+(v==1 and 1 or 0),y-1,r-1,4,9)
 if v==0 then line(x-r+4,y-3,x+1,y-4,10)
 elseif v==1 then line(x-2,y-4,x+r-5,y-3,10)
 elseif v==2 then line(x-r+3,y-2,x-2,y-4,10)
 else line(x+1,y-4,x+r-4,y-2,10) end
 line(x-r+3,y+3,x+r-4,y+3,8)
end
local function draw_stone(x,i,n,t)
 if x < -20 or x > 260 then return end
 rock(x,i,t)
 if n~=nil then center_text(tostring(n),x,101,4,1) end
end
local function scene(t)
 water(t)
 -- Irregular grass clumps and small flowers along the bank.
 for i=0,23 do
  local x=i*11+((i*7)%5)
  local h=3+(i*3)%5
  if x<76 or x>115 then
   line(x,43,x-2,43-h,5)
   line(x+1,43,x+2,42-h,5)
   line(x+3,43,x+3,40-h,6)
  end
 end
 for _,x in ipairs({4,27,207,230}) do
  line(x+2,43,x+2,31,5)
  line(x+2,38,x-1,35,6)
  line(x+2,40,x+5,36,6)
  pix(x+1,30,15) pix(x+3,30,15) pix(x+2,29,4)
 end
 -- Cattails grow at the waterline; their heads share the warm gold accent.
 for _,x in ipairs({7,228}) do
  for j=0,1 do
   local sx=x+j*5
   line(sx,67,sx+1,48-j*2,5)
   line(sx,59,sx-4,55,11)
   line(sx,62,sx+4,57,11)
   rect(sx,43-j*2,3,8,10)
   pix(sx+1,42-j*2,10)
  end
 end
end
local function bubble(x,y,w,h)
 -- Fill over the left border where the tail joins the bubble.
 rect(x+2,y,w-4,h,1) rect(x,y+2,w,h-4,1)
 rect(x+3,y+1,w-6,h-2,4) rect(x+1,y+3,w-2,h-6,4)
 tri(x+1,y+12,x+1,y+22,x-9,y+20,1)
 rect(x,y+15,3,6,4)
 tri(x+2,y+14,x+2,y+20,x-6,y+20,4)
end
local function party_bubble()
 if G.party_icons==1 then
  spr(F.smile,115,12,0,1,0,0,3,3)
  spr(F.mini,130,12,0,1,0,0,3,3)
  spr(F.heart,147,14,0,1,0,0,3,3)
  spr(F.heart,159,14,0,1,0,0,3,3)
 elseif G.party_icons==2 then
  spr(F.mini,116,12,0,1,0,0,3,3)
  for i=0,2 do spr(F.heart,132+i*12,14,0,1,0,0,3,3) end
 else
  spr(F.crown,116,12,0,1,0,0,3,3)
  spr(F.mini,137,12,0,1,0,0,3,3)
  spr(F.heart,155,14,0,1,0,0,3,3)
 end
 pix(171,12,10) pix(173,16,15) pix(170,25,10)
end
local function confetti(x,t)
 for i=1,12 do
  local dx=((i*13)%39)-19
  local dy=((i*17+floor(t/3))%26)
  local c=({10,15,4,7})[i%4+1]
  local px=floor(x+dx+.5)
  pix(px,49+dy,c)
  if i%3==0 then pix(px+1,49+dy,c) end
 end
end
local function party_frog(x,t)
 local frame=({F.croak1,F.croak2,F.croak3,F.croak2})[1+floor(t/9)%4]
 frog(frame,x,88-(floor(t/10)%2)*3)
 confetti(x,t)
end
local function header(t,menu)
 local celebrating=G.mode=="celebrate" or G.mode=="slide"
 local host=(celebrating and floor(t/9)%2==0) or G.guide_t>0 or floor(t/23)%16==0
 host=host and F.purple_speak or F.purple
 if menu then
  bubble(114,6,43,24)
  center_text("HOP!",136,13,1)
  center_text("FROG HOPPER",197,2,1)
  center_text("LEARN & HOP",197,22,5)
 else
  bubble(110,5,68,26)
  if celebrating then
   party_bubble()
  elseif G.game_mode==1 then
   print("HOP",122,16,1)
   prompt_arrow(144,15,G.direction)
   print(tostring(G.add),161,16,1)
  else
   center_text(((G.add<0) and "" or "+")..G.add,144,13,1,2)
  end
  print("MODE: "..MODE_SHORT[G.game_mode],4,2,1)
  local difficulty=LEVELS[G.level].name
  print(difficulty,236-#difficulty*6,2,1)
 end
 frog(host,95,42)
end
local function draw_menu()
 G.level=max(1,min(3,G.level))
 scene(G.t)
 local preview={0,3,1,5,2,4,6,8,7}
 local start=({0,1,5})[G.level]
 for i=1,LEVELS[G.level].count do
  local value=start+preview[i]
  if G.game_mode==1 then value=nil end
  draw_stone(stone_x(i),i,value,G.t)
 end
 frog(F.idle,stone_x(1),88)
 header(G.t,true)
 rect(19,108,202,28,1)
 center_text("MODE  < "..MODES[G.game_mode].." >",120,111,G.menu_focus==1 and 10 or 4)
 center_text("DIFFICULTY < "..LEVELS[G.level].name.." >",120,122,G.menu_focus==2 and 10 or 4)
end
local function hint_fish()
 local rise=min(16,G.hint_t*2,(80-G.hint_t)*2)
 local low=(G.hint_kind==1) and F.fish_green_low or F.fish_gold_low
 local high=(G.hint_kind==1) and F.fish_green_high or F.fish_gold_high
 local frame=(rise<10) and low or high
 local x=stone_x(G.target)
 spr(frame,floor(x-12+.5),floor(78-rise+.5),0,1,0,0,3,3)
 center_text("HERE!",x,54,4)
end
local function party_fish(x,t,low,high,bob_offset)
 if t<3 then return end
 local popped,y
 if t<14 then
  popped=t>=9
  y=116-min(12,t)
 else
  popped=floor((t-14+bob_offset)/16)%2==0
  y=popped and 104 or 106
 end
 local frame=popped and high or low
 x=floor(x+.5)
 spr(frame,x-12,y,0,1,0,0,3,3)
end
local function draw_play()
 scene(G.t)
 header(G.t,false)
 local count=LEVELS[G.level].count
 local shift=(G.mode=="slide") and step_size()*(count-1)*G.slide_t/40 or 0
 if G.mode=="hint" then hint_fish() end
 if G.mode=="slide" then
  for i=1,count-1 do
   draw_stone(stone_x(i)-shift,i,G.labels[i],G.t)
  end
  for j=0,count-1 do
   draw_stone(stone_x(count+j)-shift,count+j,G.next_labels[j+1],G.t)
  end
  local x=stone_x(count)-shift
  if G.slide_t<30 then party_frog(x,G.party_t+G.slide_t)
  else frog(F.idle,x,88) end
 else
  for i=1,count do draw_stone(stone_x(i),i,G.labels[i],G.t) end
  if G.mode=="jump" then
   local p=min(1,G.jump_t/32)
   local x=stone_x(G.from)+(stone_x(G.to)-stone_x(G.from))*p
   local arc=34*sin(pi*p)
   local frame=F.jump1
   if p>.22 then frame=F.jump2 end
   if p>.5 then frame=F.jump3 end
   if p>.78 then frame=F.jump4 end
   frog(frame,x,88-arc,(G.to<G.from) and 1 or 0)
  elseif G.mode=="turn" then
   local turning_left=G.turn_t<8
   frog(turning_left and F.idle2 or F.idle,stone_x(G.at),88,turning_left and 1 or 0)
  elseif G.mode=="wrong" then
   local frame
   if G.wrong_kind==1 then
    frame=(G.wrong_t>=10 and G.wrong_t<20) and F.hurt2 or F.hurt1
   else
    frame=({F.shock1,F.shock2,F.shock3,F.shock2})[min(4,1+floor(G.wrong_t/8))]
   end
   frog(frame,stone_x(G.at),88)
  elseif G.mode=="celebrate" then
   party_frog(stone_x(G.at),G.party_t)
  else
   local frame=F.idle
   if G.croak_t>0 then
    local p=floor((24-G.croak_t)/6)
    frame=({F.croak1,F.croak2,F.croak3,F.croak1})[min(4,p+1)]
   elseif floor(G.t/36)%2==1 then frame=F.idle2 end
   frog(frame,stone_x(G.at),88)
  end
  if G.mode=="play" or G.mode=="wrong" then
   selector(stone_x(G.choice),(G.choice==G.at) and 58 or 66,
    (G.mode=="wrong") and 15 or 10)
  end
 end
 if G.mode=="celebrate" or G.mode=="slide" then
  local fish_t=G.party_t+((G.mode=="slide") and G.slide_t or 0)
  local pebble_x=stone_x(count)-shift
  party_fish(pebble_x-18,fish_t,F.fish_green_low,F.fish_green_high,0)
  party_fish(pebble_x+8,fish_t,F.fish_gold_low,F.fish_gold_high,16)
 end
 rect(0,123,240,13,1)
 if G.mode=="wrong" then
  center_text((G.wrong_kind==1) and "OWW! TRY AGAIN" or "DID ANYONE SEE THAT?",120,126,4)
 elseif G.mode=="celebrate" then center_text("GREAT HOP!",120,126,4)
 elseif G.mode=="slide" then center_text("NEW PEBBLES!",120,126,4)
 elseif G.mode=="turn" then center_text("TURNING AROUND!",120,126,4)
 elseif G.mode=="hint" then center_text("A LITTLE HELP!",120,126,4)
 else center_text("LEFT/RIGHT:CHOOSE  X:HOP  O:MENU",120,126,4) end
end

local function finish_wrong()
 if G.mistakes>=3 then
  G.mode="hint" G.hint_t=0 G.hint_kind=rand(1,2)
  sound_here(74)
 else G.mode="play" end
end

function TIC()
 G.t=G.t+1
 if G.mode=="menu" then
  if btnp(0) and G.menu_focus~=1 then G.menu_focus=1 sound_pick() end
  if btnp(1) and G.menu_focus~=2 then G.menu_focus=2 sound_pick() end
  if G.menu_focus==1 then
   local before=G.game_mode
   if btnp(2,18,7) then G.game_mode=max(1,G.game_mode-1) end
   if btnp(3,18,7) then G.game_mode=min(#MODES,G.game_mode+1) end
   if G.game_mode~=before then sound_pick() end
  else
   local before=G.level
   if btnp(2,18,7) then G.level=max(1,G.level-1) end
   if btnp(3,18,7) then G.level=min(#LEVELS,G.level+1) end
   if G.level~=before then sound_pick() end
  end
  if btnp(5) then sound_confirm() start_game() draw_play() return end
  draw_menu()
  return
 end
 if btnp(4) then G.mode="menu" G.menu_focus=1 draw_menu() return end
 if G.mode=="play" then
  if G.guide_t>0 then G.guide_t=G.guide_t-1 end
  local before=G.choice
  if btnp(2,14,5) then G.choice=max(1,G.choice-1) end
  if btnp(3,14,5) then G.choice=min(LEVELS[G.level].count,G.choice+1) end
  if G.choice~=before then sound_pick() end
  if btnp(5) then
   if G.choice==G.target then
    G.from=G.at G.to=G.choice G.jump_t=0 G.mode="jump" sound_boing_start()
   else
    G.wrong_t=0 G.wrong_kind=rand(1,2) G.mode="wrong"
    G.mistakes=G.mistakes+1
    if G.wrong_kind==1 then sound_oww_start() else sound_cricket(82) end
   end
  end
  if G.croak_t>0 then G.croak_t=G.croak_t-1
  elseif G.t%235==0 then G.croak_t=24 end
 elseif G.mode=="jump" then
  G.jump_t=G.jump_t+1
  if G.jump_t==10 then sound_boing_down() end
  if G.jump_t>=32 then
   sound_boing_land()
   G.at=G.to
   if G.game_mode==1 and G.to<G.from then G.back_count=G.back_count+1 end
   if G.game_mode>=2 then G.path_step=G.path_step+1 end
   if G.at==LEVELS[G.level].count then
    G.mode="celebrate" G.party_t=0 G.party_icons=rand(1,3) sound_fanfare(60)
   elseif G.to<G.from then G.mode="turn" G.turn_t=0
   else G.mode="play" new_prompt() end
  end
 elseif G.mode=="turn" then
  G.turn_t=G.turn_t+1
  if G.turn_t>=16 then G.mode="play" new_prompt() end
 elseif G.mode=="wrong" then
  G.wrong_t=G.wrong_t+1
  if G.wrong_kind==1 then
   if G.wrong_t==10 then sound_oww_tail() end
   if G.wrong_t>=30 then finish_wrong() end
  else
   if G.wrong_t==8 then sound_cricket(86) end
   if G.wrong_t==16 then sound_cricket(82) end
   if G.wrong_t==24 then sound_cricket(86) end
   if G.wrong_t>=32 then finish_wrong() end
  end
 elseif G.mode=="hint" then
  G.hint_t=G.hint_t+1
  if G.hint_t==9 then sound_here(81) end
  if G.hint_t>=80 then G.mode="play" end
 elseif G.mode=="celebrate" then
  G.party_t=G.party_t+1
  if G.party_t==15 then sound_fanfare(64) end
  if G.party_t==30 then sound_fanfare(67) end
  if G.party_t==45 then sound_fanfare(72) end
  if G.party_t==60 then sound_fanfare(67) end
  if G.party_t==75 then sound_fanfare(72) end
  if G.party_t==90 then sound_fanfare(67) end
  if G.party_t==105 then sound_fanfare(72) end
  if G.party_t>=110 then
   G.next_base,G.next_labels,G.next_path=new_board()
   G.slide_t=0 G.mode="slide"
  end
 elseif G.mode=="slide" then
  G.slide_t=G.slide_t+1
  if G.slide_t==10 then sound_fanfare(67) end
  if G.slide_t==25 then sound_fanfare(72) end
  if G.slide_t==39 then sound_fanfare(76) end
  if G.slide_t>=40 then
   G.base,G.labels,G.path=G.next_base,G.next_labels,G.next_path
   G.at=1 G.choice=2 G.path_step=1 G.back_count=0
   G.mode="play" new_prompt()
  end
 end
 draw_play()
end
