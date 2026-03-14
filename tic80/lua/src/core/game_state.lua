GameState = {}
GameState.__index = GameState

function GameState.new()
 local self = setmetatable({}, GameState)
 self.profile = {
  scrap = 12,
  fuel = 9,
  runs = 0,
  garage_hp = 10,
  garage_fuel = 9
 }
 self.run = nil
 self.map_graph = nil
 self.selected_path = nil
 self.last_result_text = "No runs yet"
 self.last_route_summary = ""
 self:start_new_run()
 return self
end

function GameState:start_new_run()
 self.run = RunState.new(7020500, self.profile.garage_hp, self.profile.garage_fuel)
 self.map_graph = nil
 self.selected_path = nil
end

function GameState:reset_profile()
 self.profile.scrap = 12
 self.profile.fuel = 9
 self.profile.runs = 0
 self.profile.garage_hp = 10
 self.profile.garage_fuel = 9
 self.last_result_text = "State reset"
 self.last_route_summary = ""
 self:start_new_run()
end

function GameState:resolve_run()
 local run = self.run
 if run == nil or run.active_segment == nil then
  self.last_result_text = "Run failed: no segment"
  self.last_route_summary = ""
  return
 end

 local segment = run.active_segment
 self.profile.scrap = self.profile.scrap + segment.rewards.scrap
 self.profile.fuel = self.profile.fuel + segment.rewards.fuel
 self.profile.runs = self.profile.runs + 1
 self.last_result_text =
  segment.poi_type .. " +" .. segment.rewards.scrap .. " scrap +" ..
  segment.rewards.fuel .. " fuel"
 self.last_route_summary =
  "node " .. segment.to_node_id .. " seed " .. segment.seed_base
end
