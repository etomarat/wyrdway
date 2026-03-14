-- title:   Wyrdway Lua Experiment
-- author:  Marat Azizov, t.me/etomarat, @etomarat
-- desc:    Lua migration experiment for code budget and scene architecture.
-- site:    https://github.com/etomarat
-- license: MIT License (change this to your license of choice)
-- version: 0.0.1
-- script:  lua

require "core/scene_ids"
require "core/app_state"
require "core/scene_manager"
require "core/ui"
require "scenes/main_menu_scene"
require "scenes/status_scene"

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
