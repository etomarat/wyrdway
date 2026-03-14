function make_status_scene(nav)
 local scene = {}

 function scene:enter(_params)
 end

 function scene:update(_dt)
  if btnp(4) or btnp(5) then
   nav:go(SceneId.MAIN_MENU)
  end
 end

 function scene:draw()
  cls(3)
  Ui.draw_title("Status")
  Ui.draw_panel(10, 28, 180, 58, 14)
  Ui.draw_stat_line("Runs prepared", nav.state.runs_started, 18, 40, 12)
  Ui.draw_stat_line("Reset count", nav.state.reset_count, 18, 52, 12)
  print("Message: " .. nav.state.message, 18, 68, 12)
  Ui.draw_hint("A/B: back to menu")
 end

 return scene
end
