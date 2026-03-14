function make_garage_scene(nav)
 local scene = {}

 function scene:enter(_params)
 end

 function scene:update(_dt)
  if btnp(4) then
   nav.state:start_new_run()
   nav:go(SceneId.REGION_MAP)
  end
  if btnp(5) then
   nav:go(SceneId.MAIN_MENU)
  end
 end

 function scene:draw()
  local profile = nav.state.profile
  cls(3)
  Ui.draw_title("Garage")
  Ui.draw_panel(8, 24, 120, 54, 14)
  Ui.draw_stat_line("Scrap", profile.scrap, 16, 34, 12)
  Ui.draw_stat_line("Fuel", profile.fuel, 16, 46, 12)
  Ui.draw_stat_line("Runs", profile.runs, 16, 58, 12)
  print("This scene is intentionally compact.", 10, 92, 12)
  Ui.draw_hint("A: choose route  B: main menu")
 end

 return scene
end
