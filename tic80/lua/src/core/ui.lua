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
