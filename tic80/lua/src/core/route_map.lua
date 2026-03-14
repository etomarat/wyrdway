RouteMap = {}

local function node_label(poi_type)
 if poi_type == "gas_station" then
  return "GAS"
 end
 if poi_type == "scrapyard" then
  return "SCRAP"
 end
 return "DEPOT"
end

local function poi_color(poi_type)
 if poi_type == "gas_station" then
  return 12
 end
 if poi_type == "scrapyard" then
  return 9
 end
 return 4
end

function RouteMap.build(run)
 local graph = {
  rows = {},
  nodes_by_id = {}
 }
 local row_sizes = { 3, 4, 5 }
 local node_id = 1
 local row_index = 1

 while row_index <= #row_sizes do
  local count = row_sizes[row_index]
  local row = {
   index = row_index,
   nodes = {}
  }
  local col = 1
  while col <= count do
   local poi_type = run:preview_outbound_poi_type(node_id)
   local rewards = run:preview_outbound_rewards(node_id)
   local node = {
    id = node_id,
    row = row_index,
    col = col,
    poi_type = poi_type,
    label = node_label(poi_type),
    color = poi_color(poi_type),
    rewards = rewards,
    outgoing = {}
   }
   row.nodes[#row.nodes + 1] = node
   graph.nodes_by_id[node_id] = node
   node_id = node_id + 1
   col = col + 1
  end
  graph.rows[#graph.rows + 1] = row
  row_index = row_index + 1
 end

 row_index = 1
 while row_index < #graph.rows do
  local current_row = graph.rows[row_index]
  local next_row = graph.rows[row_index + 1]
  local index = 1
  while index <= #current_row.nodes do
   local node = current_row.nodes[index]
   node.outgoing[#node.outgoing + 1] = next_row.nodes[index].id
   if index + 1 <= #next_row.nodes then
    node.outgoing[#node.outgoing + 1] = next_row.nodes[index + 1].id
   else
    node.outgoing[#node.outgoing + 1] = next_row.nodes[#next_row.nodes].id
   end
   index = index + 1
  end
  row_index = row_index + 1
 end

 return graph
end
