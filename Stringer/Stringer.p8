pico-8 cartridge // http://www.pico-8.com
version 41
__lua__
-- stringer: continue the bead pattern
-- coin stack and sprite: mathieu's rekenspelletje
-- back and error sounds: mathieu's rekenspelletje
-- selection, answer, and coin sounds: original

function center(s,y,c)
 print(s,64-#s*2,y,c)
end

function shuffle(t)
 for i=#t,2,-1 do
  local j=flr(rnd(i))+1
  t[i],t[j]=t[j],t[i]
 end
end

-- Bead identity includes both shape and color.
function bead_key(bead)
 return bead[1]*16+bead[2]
end

function contains_bead(t,bead)
 for item in all(t) do
  if bead_key(item)==bead_key(bead) then return true end
 end
 return false
end

function short_cycle(t)
 for period=1,#t-1 do
  if #t%period==0 then
   local same=true
   for i=period+1,#t do
    if t[i]!=t[(i-1)%period+1] then same=false end
   end
   if same then return true end
  end
 end
 return false
end

function make_puzzle()
 local palette={11,12,13,14,15}
 local pool={}
 for shape=1,4 do
  for color in all(palette) do
   add(pool,{shape,color})
  end
 end
 shuffle(pool)
 beads={}
 local repeat_bead=level>=3 and rnd(1)<0.5
 local distinct=level
 if repeat_bead then
  distinct=level-1
  if level==4 and rnd(1)<0.5 then distinct=2 end
 end
 local pattern={}
 repeat
  pattern={}
  for i=1,distinct do add(pattern,i) end
  while #pattern<level do
   add(pattern,flr(rnd(distinct))+1)
  end
  shuffle(pattern)
 until not short_cycle(pattern)
 for i=1,distinct do
  add(beads,pool[i])
 end
 -- Options contain each pattern bead once, plus enough unique distractors.
 options={}
 for i=1,distinct do add(options,beads[i]) end
 local next_bead=distinct+1
 while #options<level+1 do
  add(options,pool[next_bead])
  next_bead+=1
 end
 shuffle(options)
 -- Avoid the same complete string twice in succession.
 local signature=""
 for i=1,level do
  signature=signature..bead_key(beads[pattern[i]])..","
 end
 if signature==last_signature then
  make_puzzle()
  return
 end
 last_signature=signature
 cycle=pattern
 goal=level==4 and 8 or 6
 selected=1
 correct=0
 wrong=false
 state="play"
end

function _init()
 state="menu"
 level=2
 coins=0
 last_signature=""
end

function _update60()
 if state=="menu" then
  if btnp(0) and level>2 then
   level-=1
   sfx(3)
  end
  if btnp(1) and level<4 then
   level+=1
   sfx(3)
  end
  if btnp(5) then
   srand(time())
   coins=0
   last_signature=""
   make_puzzle()
  end
 elseif state=="play" then
  if btnp(4) then
   sfx(1)
   state="menu"
   return
  end
  if btnp(0) and selected>1 then
   selected-=1
   wrong=false
   sfx(3)
  end
  if btnp(1) and selected<#options then
   selected+=1
   wrong=false
   sfx(3)
  end
  if btnp(5) then
   local expected=beads[cycle[correct%level+1]]
   if bead_key(options[selected])==bead_key(expected) then
    correct+=1
    wrong=false
    if correct%level==0 then
     sfx(6)
     state="award"
     award_frame=0
    else
     sfx(5)
    end
   else
    wrong=true
    sfx(4)
   end
  end
 elseif state=="award" then
  award_frame+=1
  if award_frame==25 then
   coins=min(coins+1,300)
   sfx(7)
  end
  if award_frame==32 and correct>=goal then
   sfx(8)
  end
  if award_frame>=50 then
   if correct>=goal then
    make_puzzle()
   else
    state="play"
   end
  end
 end
end

function draw_bead(bead,x,y,r)
 local shape=bead[1]
 local color=bead[2]
 if shape==1 then
  circfill(x,y,r,0)
  circ(x,y,r,color)
 elseif shape==2 then
  rectfill(x-r,y-r,x+r,y+r,0)
  rect(x-r,y-r,x+r,y+r,color)
 elseif shape==3 then
  local h=flr(r*0.87)
  for yy=0,2*h do
   local width=flr(r*(2*h-yy)/(2*h))
   line(x-width,y-h+yy,x+width,y-h+yy,0)
  end
  line(x-r,y-h,x+r,y-h,color)
  line(x-r,y-h,x,y+h,color)
  line(x+r,y-h,x,y+h,color)
 else
  local h=flr(r*0.87)
  for yy=0,2*h do
   local width=flr(r*yy/(2*h))
   line(x-width,y-h+yy,x+width,y-h+yy,0)
  end
  line(x,y-h,x-r,y+h,color)
  line(x,y-h,x+r,y+h,color)
  line(x-r,y+h,x+r,y+h,color)
 end
end

function draw_empty(x,y)
 for dx=-1,1,2 do
  for dy=-1,1,2 do
   local xx=x+dx*7
   local yy=y+dy*7
   line(xx,yy,xx-dx*3,yy,7)
   line(xx,yy,xx,yy-dy*3,7)
  end
 end
end

function bead_position(n)
 if n>10 then
  -- Six beads fit on the last row because it needs no return bend.
  return 22+(n-11)*17,77
 end
 local row=flr((n-1)/5)
 local col=(n-1)%5
 local x=row%2==0 and 24+col*20 or 104-col*20
 return x,23+row*27
end

function draw_string()
 local total=2*level+goal
 local rows=total>10 and 3 or 2
 for row=0,rows-1 do
  local y=23+row*27
  if row==rows-1 then
   local last_x=bead_position(total)
   local end_x=row%2==0 and last_x+8 or last_x-8
   line(row%2==0 and 16 or 112,y,end_x,y,7)
  else
   line(16,y,112,y,7)
  end
  if row<rows-1 then
   local x=row%2==0 and 112 or 16
   circ(x,y+13,13,7)
   if x==112 then
    rectfill(99,y+1,111,y+25,0)
   else
    rectfill(17,y+1,29,y+25,0)
   end
   line(x,y+26,x,y+27,7)
  end
 end
 for i=1,total do
  local x,y=bead_position(i)
  if i<=2*level+correct then
   local index=cycle[(i-1)%level+1]
   draw_bead(beads[index],x,y,8)
  elseif i==2*level+correct+1 and state=="play" then
   draw_empty(x,y)
  end
 end
end

function draw_coin_parts(x,y,n)
 -- Four 4x2 slices of the visible coin sprite, enlarged for progress.
 for i=1,n do
  local col=(i-1)%2
  local row=flr((i-1)/2)
  sspr(16+4*col,3+2*row,4,2,
   x-6+6*col,y-4+4*row,6,4)
 end
end

-- Coin stack from rekenspelletje by mathieu.
function show_treasure(n)
 local cols=flr(n/25)
 for x=1,cols do
  for y=1,25 do
   spr(2,-5+10*x,120-2*y)
  end
 end
 local rest=n-25*cols
 for y=1,rest do
  spr(2,-5+10*(cols+1),120-2*y)
 end
end

function draw_options()
 local count=#options
 local gap=count==3 and 36 or count==4 and 28 or 23
 local left=flr(64-gap*(count-1)/2)
 for i=1,count do
  draw_bead(options[i],left+(i-1)*gap,106,9)
 end
 local x=left+(selected-1)*gap
 pset(x-2,91,7)
 pset(x+2,91,7)
 pset(x-1,92,7)
 pset(x+1,92,7)
 pset(x,93,7)
end

function _draw()
 cls(0)
 if state=="menu" then
  center("stringer",14,6)
  center("finish the pattern",35,7)
  local preview={{1,12},{4,15},{2,14},{3,11}}
  local left=flr(64-13*(level-1))
  line(left-9,65,left+26*(level-1)+9,65,7)
  for i=1,level do
   draw_bead(preview[i],left+26*(i-1),65,8)
  end
  center("pattern length",84,6)
  center("< "..level.." beads >",96,10)
  center("left/right:choose",107,5)
  center("x:start",116,7)
 else
  center("stringer",2,6)
  print(level.." beads",94,2,6)
  draw_string()
  draw_options()
  show_treasure(coins)
  if state=="award" then
   if award_frame<25 then
    local t=award_frame/25
    local target_x=9+10*flr(coins/25)
    local target_y=124-2*(coins%25+1)
    local x=9+(target_x-9)*t
    local y=40+(target_y-40)*t+12*sin(t/2)
    draw_coin_parts(x,y,4)
   end
  else
   draw_coin_parts(9,40,flr((correct%level)*4/level))
  end
  print(wrong and "try again!" or "x:pick",38,119,wrong and 8 or 6)
  print("o:menu",98,119,6)
 end
end
__gfx__
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000777777000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000009aaaaaa900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000009aaaaaa900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000999999000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__sfx__
00080000245502b5502b5302b5102a50024500285002b50028500287002c3051e5002e1073cb061320014206172001f200222001200108805147000e7000e7000e7000e7000e7000f7000f7000e7000e70000700
0005000024052280522b05218b0506000040000200002000000000000000000000000000000000020000200002000020000200002000020000200004000060000600006000040000400004000040000400004000
000500002b05028050240500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000600001c32000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000800001f1501f150081510814100301003013430138301003010030100301003010030100301003010030100301003010030100301003010030100301003010030100301003010030100301003010030100301
00040000173501c350000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0004000014350183501c3502035024350000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00030000233402b340000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00020000260402d0502a030320502f030370403b02000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
