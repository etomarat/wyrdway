RoutePlanner = {}
RoutePlanner.__index = RoutePlanner

local MOD32 = 4294967296
local MOD31 = 2147483647

local function clamp_non_negative(value)
 local n = math.floor(value)
 if n < 0 then
  return 0
 end
 return n
end

function RoutePlanner.new(run_seed)
 local self = setmetatable({}, RoutePlanner)
 self.run_seed = math.floor(run_seed) % MOD31
 return self
end

function RoutePlanner:_mix_seed(node_id, salt)
 local s = self.run_seed % MOD31
 local n = (math.floor(node_id) + 1) % MOD31
 local x = (s * 1103515245 + n * 12345 + salt * 97 + 1013904223) % MOD31
 if x == 0 then
  x = 1234567
 end
 return x
end

function RoutePlanner:outbound_seed_base(to_node_id)
 return self:_mix_seed(to_node_id, 8013)
end

function RoutePlanner:_next_u32(x)
 return (1664525 * x + 1013904223) % MOD32
end

function RoutePlanner:_roll_range(x, min_inclusive, max_inclusive)
 local a = clamp_non_negative(min_inclusive)
 local b = clamp_non_negative(max_inclusive)
 if b < a then
  b = a
 end
 local span = b - a + 1
 if span <= 1 then
  return a, self:_next_u32(x)
 end
 local n = self:_next_u32(x)
 return a + (n % span), n
end

function RoutePlanner:_pick_weighted_index(x, weights)
 local n = self:_next_u32(x)
 local total = 0
 local index = 1
 local last_positive = 1
 while index <= #weights do
  local w = weights[index]
  if w > 0 then
   total = total + w
   last_positive = index
  end
  index = index + 1
 end
 if total <= 0 then
  return 1, n
 end

  local r = (n / 4294967296) * total
  local acc = 0
  index = 1
  while index <= #weights do
   local w = weights[index]
   if w > 0 then
    acc = acc + w
    if r < acc then
     return index, n
    end
   end
   index = index + 1
  end
 return last_positive, n
end

function RoutePlanner:pick_outbound_poi_type(to_node_id, seed_base)
 local x = (seed_base * 1597 + (to_node_id + 31) * 31337 + 17) % MOD32
 local idx = self:_pick_weighted_index(x, { 35, 35, 30 })
 if idx == 1 then
  return "gas_station"
 end
 if idx == 2 then
  return "scrapyard"
 end
 return "depot"
end

function RoutePlanner:roll_segment_rewards(to_node_id, seed_base, poi_type)
 local x = (seed_base * 811 + (to_node_id + 17) * 9973 + 23) % MOD32
 if poi_type == "gas_station" then
  local scrap
  scrap, x = self:_roll_range(x, 1, 2)
  local fuel
  fuel, x = self:_roll_range(x, 2, 4)
  return scrap, fuel
 end
 if poi_type == "scrapyard" then
  local scrap
  scrap, x = self:_roll_range(x, 3, 5)
  local fuel
  fuel, x = self:_roll_range(x, 0, 1)
  return scrap, fuel
 end
 local scrap
 scrap, x = self:_roll_range(x, 2, 3)
 local fuel
 fuel, x = self:_roll_range(x, 1, 2)
 return scrap, fuel
end
