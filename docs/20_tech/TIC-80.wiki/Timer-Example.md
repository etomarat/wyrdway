TIC() function in executed in 60fps.  
So just record the frames in total, then use frames/60 to get time.  
中文：因为tic函数每秒运行60次，所以只需要记录总帧数，然后用总帧数除以60就能获得时间。
```
local frame=0
local second=0
function TIC()
	 cls(2)
  frame = frame+1
  second= math.floor(frame/60)
  print("frame:"..tostring(frame),100,100,4)
  print("second:"..tostring(second),100,80,4)
end
```