function make_drive_scene(nav)
 local scene = {
  t = 0,
  timer = 0
 }

 function scene:enter(_params)
  self.t = 0
  local segment = nav.state.run.active_segment
  if segment ~= nil then
   self.timer = math.floor(segment.len_units)
  else
   self.timer = 120
  end
 end

 function scene:update(_dt)
  if self.timer > 0 then
   self.timer = self.timer - 1
  end
  self.t = self.t + 1

  if btnp(4) or self.timer <= 0 then
   nav.state:resolve_run()
   nav:go(SceneId.RESULT)
  end
 end

 function scene:draw()
  local x = 96 + math.sin(self.t / 10) * 24
  local y = 64 + math.cos(self.t / 18) * 10
  local route = nav.state.run.active_segment
  local frame = math.floor(self.t / 12) % 2
  cls(13)
  Ui.draw_title("Drive")
  if route ~= nil then
   print("Target node: " .. route.to_node_id, 10, 26, 12)
   print("POI: " .. route.poi_type, 10, 34, 12)
  end
  print("Timer: " .. self.timer, 10, 42, 12)
  print("Press A to finish outbound segment", 10, 50, 12)
  rect(12, 88, 216, 18, 5)
  line(12, 97, 228, 97, 6)
  spr(1 + frame * 2, x, y, 14, 3, 0, 0, 2, 2)
  Ui.draw_hint("A: finish run early")
 end

 return scene
end
