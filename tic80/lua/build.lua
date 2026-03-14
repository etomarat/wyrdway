-- title:   Wyrdway Lua Experiment
-- author:  Marat Azizov, t.me/etomarat, @etomarat
-- desc:    Lua migration experiment for code budget and scene architecture.
-- site:    https://github.com/etomarat
-- license: MIT License (change this to your license of choice)
-- version: 0.0.1
-- script:  lua

-- BEGIN core\scene_ids.lua
SceneId = {
 MAIN_MENU = "main_menu",
 STATUS = "status"
}
-- END core\scene_ids.lua

-- BEGIN core\app_state.lua
AppState = {}
AppState.__index = AppState

function AppState.new()
 local self = setmetatable({}, AppState)
 self.runs_started = 0
 self.reset_count = 0
 self.message = "Booted"
 return self
end

function AppState:start_new_run()
 self.runs_started = self.runs_started + 1
 self.message = "Run " .. self.runs_started .. " prepared"
end

function AppState:reset_profile()
 self.runs_started = 0
 self.reset_count = self.reset_count + 1
 self.message = "Counter reset"
end
-- END core\app_state.lua

-- BEGIN core\scene_manager.lua
SceneManager = {}
SceneManager.__index = SceneManager

function SceneManager.new(state)
 local self = setmetatable({}, SceneManager)
 self.state = state
 self.factories = {}
 self.current_id = nil
 self.current_scene = nil
 return self
end

function SceneManager:register(scene_id, factory)
 self.factories[scene_id] = factory
end

function SceneManager:go(scene_id, params)
 local factory = self.factories[scene_id]
 if factory == nil then
  return
 end

 local next_scene = factory(self)
 if self.current_scene ~= nil and self.current_scene.exit ~= nil then
  self.current_scene:exit()
 end

 self.current_id = scene_id
 self.current_scene = next_scene
 if next_scene.enter ~= nil then
  next_scene:enter(params)
 end
end

function SceneManager:update(dt)
 if self.current_scene == nil or self.current_scene.update == nil then
  return
 end
 self.current_scene:update(dt)
end

function SceneManager:draw()
 if self.current_scene == nil or self.current_scene.draw == nil then
  return
 end
 self.current_scene:draw()
end
-- END core\scene_manager.lua

-- BEGIN core\ui.lua
Ui = {}

function Ui.draw_title(text)
 print(text, 10, 10, 12, false, 2)
end

function Ui.draw_hint(text)
 print(text, 10, 126, 13, false, 1)
end

function Ui.draw_panel(x, y, w, h, color)
 rect(x, y, w, h, color)
 rectb(x, y, w, h, 12)
end

function Ui.draw_stat_line(label, value, x, y, color)
 print(label .. ": " .. tostring(value), x, y, color or 12)
end

function Ui.draw_menu(items, selected_index, x, y)
 local index = 1
 while index <= #items do
  local color = 12
  local prefix = "  "
  if index == selected_index then
   color = 4
   prefix = "> "
  end
  print(prefix .. items[index], x, y + (index - 1) * 10, color)
  index = index + 1
 end
end
-- END core\ui.lua

-- BEGIN scenes\main_menu_scene.lua
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
-- END scenes\main_menu_scene.lua

-- BEGIN scenes\status_scene.lua
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
-- END scenes\status_scene.lua


APP = nil
APP_ERROR = nil

local function boot()
 local scene_manager = SceneManager.new(AppState.new())
 scene_manager:register(SceneId.MAIN_MENU, make_main_menu_scene)
 scene_manager:register(SceneId.STATUS, make_status_scene)
 scene_manager:go(SceneId.MAIN_MENU)
 APP = {
  scene_manager = scene_manager
 }
end

function TIC()
 cls(0)

 if APP_ERROR ~= nil then
  print("LUA EXPERIMENT ERROR", 8, 8, 2)
  print(APP_ERROR, 8, 20, 12)
  return
 end

 if APP == nil then
  local ok, err = pcall(boot)
  if not ok then
   APP_ERROR = tostring(err)
   print("LUA EXPERIMENT ERROR", 8, 8, 2)
   print(APP_ERROR, 8, 20, 12)
   return
  end
 end

 local ok, err = pcall(function()
  APP.scene_manager:update(1 / 60)
  APP.scene_manager:draw()
 end)
 if not ok then
  APP_ERROR = tostring(err)
  print("LUA EXPERIMENT ERROR", 8, 8, 2)
  print(APP_ERROR, 8, 20, 12)
 end
end
