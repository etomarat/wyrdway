RunState = {}
RunState.__index = RunState

function RunState.new(seed, car_hp, car_fuel)
 local self = setmetatable({}, RunState)
 self.seed = math.floor(seed)
 self.node_id = nil
 self.car_hp = car_hp
 self.car_fuel = car_fuel
 self.outbound = {}
 self.return_routes = {}
 self.active_segment = nil
 self.planner = RoutePlanner.new(seed)
 return self
end

function RunState:_find_outbound_by_target(to_node_id)
 local index = 1
 while index <= #self.outbound do
  local plan = self.outbound[index]
  if plan.to_node_id == to_node_id then
   return plan
  end
  index = index + 1
 end
 return nil
end

function RunState:preview_outbound_seed_base(to_node_id)
 local existing = self:_find_outbound_by_target(to_node_id)
 if existing ~= nil then
  return existing.seed_base
 end
 return self.planner:outbound_seed_base(to_node_id)
end

function RunState:preview_outbound_poi_type(to_node_id)
 local existing = self:_find_outbound_by_target(to_node_id)
 if existing ~= nil then
  return existing.poi_type
 end
 local seed_base = self:preview_outbound_seed_base(to_node_id)
 return self.planner:pick_outbound_poi_type(to_node_id, seed_base)
end

function RunState:preview_outbound_rewards(to_node_id)
 local existing = self:_find_outbound_by_target(to_node_id)
 if existing ~= nil then
  return {
   scrap = existing.rewards.scrap,
   fuel = existing.rewards.fuel
  }
 end
 local seed_base = self:preview_outbound_seed_base(to_node_id)
 local poi_type = self:preview_outbound_poi_type(to_node_id)
 local scrap, fuel =
  self.planner:roll_segment_rewards(to_node_id, seed_base, poi_type)
 return {
  scrap = scrap,
  fuel = fuel
 }
end

function RunState:ensure_outbound_segment(to_node_id, len_units)
 local target = math.floor(to_node_id)
 local plan = self:_find_outbound_by_target(target)
 if plan == nil then
  local from_node_id = 0
  if self.node_id ~= nil then
   from_node_id = self.node_id
  end
  local seed_base = self:preview_outbound_seed_base(target)
  local poi_type = self:preview_outbound_poi_type(target)
  local rewards = self:preview_outbound_rewards(target)
  plan = {
   from_node_id = from_node_id,
   to_node_id = target,
   poi_type = poi_type,
   leg_kind = "OUTBOUND",
   seed_base = seed_base,
   len_units = len_units,
   rewards = rewards
  }
  self.outbound[#self.outbound + 1] = plan
 end
 self.active_segment = plan
 self.node_id = target
 return plan
end
