-- title:  vand particles pack
-- author: vand
-- desc:   a set of beautiful particles ready to be used on any project!!!
-- script: lua

-- !!! COPY THIS PARTT !!! --
pi=3.14159
sqrt=math.sqrt
sin=math.sin
cos=math.cos
rnd=math.random
min=math.min
max=math.max
del=table.remove
part={}
-- !!! COPY THAT PARTT !!! --

--each particle has a draw() and move()
--function, you need to call both for
--it to work

w,h=240,136
hw,hh=w/2,h/2

t=0
mode=0

function TIC()
		controls()
		update()
end

function update()

	 cls(0)
		
		--use this to draw all the particles
		--on the list
		for i,p in pairs(part) do
				p.draw(p)
		end
		
		--use this to update the particles
		--on the list
		for i,p in pairs(part) do
				if p.move(p) then del(part,i) end
		end
		
		print("use Z,X to change particles")
		print(mode.."/6",0,10)
		
end

function controls()
		mx,my,mclick,mmclick,mrclick = mouse()
		if btnp(2) or btnp(4) then mode=max(0,mode-1) end
		if btnp(3) or btnp(5) then mode=min(6,mode+1) end
		
		
		if mclick then 
				--calling the particles
				--new_pparticle(x,y,size)
				if mode==0 then
						new_ptri(mx,my,rnd()*8)
				
				elseif mode==1 then
						new_ptri2(mx,my,rnd()*4)
				
				elseif mode==2 then
						new_pplus(mx,my,rnd()*8)
				
				elseif mode==3 then
						new_pmarker(mx,my)
				
				elseif mode==4 then
						--this one uses new_pfire() too
						new_pexplosion(mx,my,rnd()*8)
						
				elseif mode==5 then
						for i=0,3 do
								new_pdust(mx,my,rnd()*8)
						end 
						
				elseif mode==6 then
						new_pstar(mx,my,rnd()*8)
						
				end
		end
		
		t=t+1
end

---------------------------------------
--all the particles themselves
---------------------------------------

function new_ptri(x_,y_,r_)
		local ang_=rnd()*pi*2
		table.insert(part,{
				x=x_,
				y=y_,
				ang=rnd()*pi,
				angv=rnd()*2-1,
				c=4,
				vx= cos(ang_),
		 	vy= sin(ang_),
			 r=rnd()*r_,
				t=20,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.95,o.vy*.95
						o.angv=o.angv*.9
						o.ang=o.ang+o.angv
						if o.t<5 then
							 o.r=o.r/1.1  
								if t%5==0 then o.c=min(o.c-(o.c>1 and 1 or 0),15) end end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)local a,b,c=o.ang,o.ang+(2/3*pi),o.ang+(4/3*pi)
						local xa,xb,xc,ya,yb,yc=cos(a),cos(b),cos(c),sin(a),sin(b),sin(c)
			
						tri(o.x+xa*o.r,o.y+ya*o.r,
										o.x+xb*o.r,o.y+yb*o.r,
										o.x+xc*o.r,o.y+yc*o.r,o.c)
				end
				})
end

function new_ptri2(x_,y_,r_)
		local ang_=rnd()*pi*2
		local force_=1+rnd()/2
		table.insert(part,{
				x=x_,
				y=y_,
				ang=ang_,
				c=12,
				vx= cos(ang_)*force_,
		 	vy= sin(ang_)*force_,
			 r=rnd()*r_,
				t=20,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.95,o.vy*.95
						
						if o.t<10 then
							 o.r=o.r/1.1  
								if t%5==0 then o.c=o.c+(o.c<15 and 1 or 0) end end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)local a,b,c=o.ang,o.ang+(2/3*pi),o.ang+(4/3*pi)
						local xa,xb,xc,ya,yb,yc=cos(a),cos(b),cos(c),sin(a),sin(b),sin(c)
			
						tri(o.x+xa*o.r*2,o.y+ya*o.r*2,
										o.x+xb*o.r,o.y+yb*o.r,
										o.x+xc*o.r,o.y+yc*o.r,o.c)
				end
				})
end

function new_pplus(x_,y_,r_)
		table.insert(part,{
				x=x_,
				y=y_,
				ang=rnd()*pi,
				angv=rnd()*2-1,
				c=6,
		 	vx= cos(rnd()*pi*2) ,
		 	vy= sin(rnd()*pi*2),
			 r=rnd()*r_,
				t=20,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.95,o.vy*.95
						o.angv=o.angv*.9
						o.ang=o.ang+o.angv
						if o.t<5 then
							 o.r=o.r/1.1  
								if t%5==0 then o.c=min(o.c-(o.c>1 and 1 or 0),15) end end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)local a,b,c,d=o.ang,o.ang+(pi),o.ang+(pi/2),o.ang+((3*pi)/2)
						local xa,xb,xc,xd,ya,yb,yc,yd=cos(a),cos(b),cos(c),cos(d),sin(a),sin(b),sin(c),sin(d)
			
						line(o.x+xa*o.r,o.y+ya*o.r,
											o.x+xb*o.r,o.y+yb*o.r,o.c)
						line(o.x+xc*o.r,o.y+yc*o.r,
											o.x+xd*o.r,o.y+yd*o.r,o.c)
											
				end
				})
end

function new_pmarker(x_,y_,r_)
		table.insert(part,{
				x=x_,
				y=y_,
				p1=0.1,
				p2=1.1,
				ang=rnd()*pi*2,
				c=8,
				t=20,
				move=function(o)
						if o.t<10 then
							 o.p1=o.p1/1.1
							 o.p2=o.p2/1.08  
								if t%20==0 then o.c=o.c+(o.c<11 and 1 or 0) end
						else
								o.p1=o.p1+1
								o.p2=o.p2+1.2
						end
						
						o.t=o.t-1+rnd()
						if o.p2<2 then	return true end
				end,
				draw=function(o)local a=o.ang
						local xa,ya=cos(a),sin(a)
			
						line(o.x+xa*o.p1,o.y+ya*o.p1,
											o.x+xa*o.p2,o.y+ya*o.p2,o.c)
				end
				})
end

function new_pdust(x_,y_,r_)
		local ang_=rnd()*pi+(pi)
		table.insert(part,{
				x=x_,
				y=y_,
				c=12,
				ty=rnd(-1,1),
				vx=cos(ang_),
		 	vy=sin(ang_),
				r=rnd()*r_,
				t=20,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.95,o.vy*.95
						if o.t<5 then
							 o.r=o.r/1.1  
								if t%10==0 then o.c=min(o.c+(o.c<15 and 1 or 0),15) end end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)
						if o.ty>=0 then	circ(o.x,o.y,o.r,o.c)
						else circb(o.x,o.y,o.r,0) end
				end
				})
end

--this one uses new_pfire() too
function new_pexplosion(x_,y_,r_)
		local ang_=rnd()*pi+pi
		table.insert(part,{
				x=x_,
				y=y_,
				c=4,
				vx=cos(ang_)*rnd()*2,
		 	vy=sin(ang_)*rnd()*2,
				r=rnd()*r_,
				t=20,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.99,o.vy*.99
						if o.t<5 then
							 o.r=o.r/1.1  
								if t%5==0 then o.c=o.c-(o.c>1 and 1 or 0) end
						else
								new_pfire(o.x,o.y,o.r,o.c)
						end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)
						circ(o.x,o.y,o.r,o.c)
				end
				})
end

function new_pfire(x_,y_,r_,c_)
		local ang_=rnd()*pi*2
		table.insert(part,{
				x=x_,
				y=y_,
				c=c_,
				vx=cos(ang_)/2,
		 	vy=sin(ang_)/2,
				r=rnd()*r_,
				t=10,
				move=function(o)
						o.x,o.y=o.x+o.vx,o.y+o.vy
						o.vx,o.vy=o.vx*.95,o.vy*.95
						if o.t<5 then
							 o.r=o.r/1.1  
								if t%5==0 then o.c=o.c-(o.c>1 and 1 or 0) end end
						
						o.t=o.t-1+rnd()
						if o.r<1 then	return true end
				end,
				draw=function(o)
						circ(o.x,o.y,o.r,o.c)
				end
				})
end

function new_pstar(x_,y_)
		local ang_=rnd()*pi*2
		table.insert(part,{
					x=x_,
					y=y_,
					vx=cos(ang_),
			 	vy=sin(ang_),
					r=rnd(0,1),
					t=10,
					move=function(o)
							o.x,o.y=o.x+o.vx,o.y+o.vy
							o.vx,o.vy=o.vx/1.1,o.vy/1.1
							o.t=o.t-1+rnd() 
							if o.t<0 then return true end
							end,
					draw=function(o)
						 circb(o.x,o.y,o.r,14) end
							})
end
