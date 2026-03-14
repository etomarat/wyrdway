function make_main_menu_scene(nav)
 local scene = {
  cursor = 1,
  items = {
   "Open status",
   "Prepare run",
   "Reset counter"
  }
 }

 function scene:enter(_params)
  self.cursor = 1
 end

 function scene:update(_dt)
  if btnp(0) then
   self.cursor = self.cursor - 1
   if self.cursor < 1 then
    self.cursor = #self.items
   end
  end
  if btnp(1) then
   self.cursor = self.cursor + 1
   if self.cursor > #self.items then
    self.cursor = 1
   end
  end

  if btnp(4) then
   if self.cursor == 1 then
    nav:go(SceneId.STATUS)
   elseif self.cursor == 2 then
    nav.state:start_new_run()
   else
    nav.state:reset_profile()
   end
  end
 end

 function scene:draw()
  cls(1)
  Ui.draw_title("Wyrdway Lua experiment")
  print("Scene manager + UI layer restored", 10, 28, 12)
  print("Message: " .. nav.state.message, 10, 38, 13)
  Ui.draw_menu(self.items, self.cursor, 16, 50)
  Ui.draw_hint("D-pad: move  A: confirm")
 end

 return scene
end
