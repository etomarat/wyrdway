# title:   game title
# author:  game developers, email, etc.
# desc:    short description
# site:    website link
# license: MIT License (change this to your license of choice)
# version: 0.1
# script:  python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from tic80 import *
  from .test import *

include("test")

t=0
x=96
y=24

def TIC():
 global t
 global x
 global y

 if btn(0): y-=1
 if btn(1): y+=1
 if btn(2): x-=1
 if btn(3): x+=1

 cls(13)
 spr(
  1+t%60//30*2,
  x,y,
  colorkey=14,
  scale=3,
  w=2,h=2
 )
 print("HELLO WORLD!!" + msg,84,84)
 t+=1
