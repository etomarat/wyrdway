function make_result_scene(nav)
 local scene = {}

 function scene:enter(_params)
 end

 function scene:update(_dt)
  if btnp(4) then
    nav:go(SceneId.GARAGE)
  end
  if btnp(5) then
    nav:go(SceneId.MAIN_MENU)
  end
 end

 function scene:draw()
  local profile = nav.state.profile
  cls(2)
  Ui.draw_title("Result")
  Ui.draw_panel(8, 28, 200, 48, 15)
  print(nav.state.last_result_text, 16, 40, 0)
  print(nav.state.last_route_summary, 16, 50, 0)
  Ui.draw_stat_line("Scrap", profile.scrap, 16, 90, 12)
  Ui.draw_stat_line("Fuel", profile.fuel, 16, 100, 12)
  Ui.draw_stat_line("Runs", profile.runs, 16, 110, 12)
  Ui.draw_hint("A: garage  B: main menu")
 end

 return scene
end
