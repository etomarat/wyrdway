function make_region_map_scene(nav)
 local scene = {
  selected_row = 1,
  selected_col = 1
 }

 function scene:ensure_graph()
  if nav.state.map_graph == nil then
   nav.state.map_graph = RouteMap.build(nav.state.run)
  end
 end

 function scene:enter(_params)
  self:ensure_graph()
  self.selected_row = 1
  self.selected_col = 1
  nav.state.selected_path = nil
 end

 function scene:current_row()
  return nav.state.map_graph.rows[self.selected_row]
 end

 function scene:selected_node()
  local row = self:current_row()
  if row == nil then
   return nil
  end
  return row.nodes[self.selected_col]
 end

 function scene:reachable_from_previous(node)
  if self.selected_row <= 1 then
   return true
  end
  local path = nav.state.selected_path
  if path == nil then
   return false
  end
  local previous = path[self.selected_row - 1]
  if previous == nil then
   return false
  end
  local index = 1
  while index <= #previous.outgoing do
   if previous.outgoing[index] == node.id then
    return true
   end
   index = index + 1
  end
  return false
 end

 function scene:clamp_selection()
  local row = self:current_row()
  if row == nil then
   return
  end
  if self.selected_col < 1 then
   self.selected_col = 1
  end
  if self.selected_col > #row.nodes then
   self.selected_col = #row.nodes
  end
  if self:reachable_from_previous(row.nodes[self.selected_col]) then
   return
  end

  local index = 1
  while index <= #row.nodes do
   if self:reachable_from_previous(row.nodes[index]) then
    self.selected_col = index
    return
   end
   index = index + 1
  end
 end

 function scene:move_horizontal(delta)
  local row = self:current_row()
  if row == nil then
   return
  end
  local start = self.selected_col
  local probe = start + delta
  while probe >= 1 and probe <= #row.nodes do
   if self:reachable_from_previous(row.nodes[probe]) then
    self.selected_col = probe
    return
   end
   probe = probe + delta
  end
 end

 function scene:advance_selection()
  local node = self:selected_node()
  if node == nil then
   return
  end
  if nav.state.selected_path == nil then
   nav.state.selected_path = {}
  end
  nav.state.selected_path[self.selected_row] = node

  if self.selected_row >= #nav.state.map_graph.rows then
   local run = nav.state.run
   run:ensure_outbound_segment(node.id, 120)
   nav:go(SceneId.DRIVE)
   return
  end

  self.selected_row = self.selected_row + 1
  self.selected_col = 1
  self:clamp_selection()
 end

 function scene:update(_dt)
  if btnp(2) then
   self:move_horizontal(-1)
  end
  if btnp(3) then
   self:move_horizontal(1)
  end
  if btnp(0) and self.selected_row > 1 then
   nav.state.selected_path[self.selected_row] = nil
   self.selected_row = self.selected_row - 1
   self.selected_col = nav.state.selected_path[self.selected_row].col
  end
  if btnp(4) then
   self:advance_selection()
  end
  if btnp(5) then
   nav:go(SceneId.GARAGE)
  end
 end

 function scene:draw_connections(row, next_row, x0, x1)
  local a = 1
  while a <= #row.nodes do
   local from_node = row.nodes[a]
   local ax = x0 + (from_node.col - 1) * 48
   local ay = 46 + (from_node.row - 1) * 28
   local b = 1
   while b <= #from_node.outgoing do
    local target = nav.state.map_graph.nodes_by_id[from_node.outgoing[b]]
    local bx = x1 + (target.col - 1) * 48
    local by = 46 + (target.row - 1) * 28
    line(ax, ay, bx, by, 13)
    b = b + 1
   end
   a = a + 1
  end
 end

 function scene:draw_node(node)
  local x = 30 + (node.col - 1) * 48 + (node.row - 1) * 8
  local y = 46 + (node.row - 1) * 28
  local selected = false
  local committed = false
  if self.selected_row == node.row and self.selected_col == node.col then
   selected = true
  end
  if nav.state.selected_path ~= nil and nav.state.selected_path[node.row] ~= nil then
   committed = nav.state.selected_path[node.row].id == node.id
  end

  circ(x, y, 8, node.color)
  circb(x, y, 9, committed and 4 or 12)
  if selected then
   rectb(x - 11, y - 11, 22, 22, 4)
  end
  print(node.label, x - 10, y + 12, 12)
  print("S+" .. node.rewards.scrap, x - 10, y + 20, 11)
  print("F+" .. node.rewards.fuel, x + 10, y + 20, 4)
 end

 function scene:draw_header()
  local profile = nav.state.profile
  local run = nav.state.run
  Ui.draw_title("Region map")
  print(
   "HP " .. run.car_hp .. "  FUEL " .. run.car_fuel ..
   "  SCRAP " .. profile.scrap,
   10,
   24,
   12
  )
  print("Seed " .. run.seed .. "  segment rows 3 -> 4 -> 5", 10, 32, 13)
 end

 function scene:draw_selected_summary()
  local node = self:selected_node()
  if node == nil then
   return
  end
  Ui.draw_panel(146, 50, 86, 54, 15)
  print("NODE " .. node.id, 154, 58, 0)
  print(node.poi_type, 154, 68, 0)
  print("SCRAP +" .. node.rewards.scrap, 154, 80, 0)
  print("FUEL +" .. node.rewards.fuel, 154, 90, 0)
 end

 function scene:draw()
  cls(8)
  self:draw_header()

  local row_index = 1
  while row_index < #nav.state.map_graph.rows do
   self:draw_connections(
    nav.state.map_graph.rows[row_index],
    nav.state.map_graph.rows[row_index + 1],
    30 + (row_index - 1) * 8,
    30 + row_index * 8
   )
   row_index = row_index + 1
  end

  row_index = 1
  while row_index <= #nav.state.map_graph.rows do
   local row = nav.state.map_graph.rows[row_index]
   print("ROW " .. row.index, 10, 42 + (row_index - 1) * 28, 12)
   local index = 1
   while index <= #row.nodes do
    self:draw_node(row.nodes[index])
    index = index + 1
   end
   row_index = row_index + 1
  end

  self:draw_selected_summary()
  Ui.draw_hint("Left/Right: node  Up: back  A: confirm  B: garage")
 end

 return scene
end
