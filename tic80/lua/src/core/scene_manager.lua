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
