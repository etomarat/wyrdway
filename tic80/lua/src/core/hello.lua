function hello_draw(frame)
 local band = math.floor(frame / 30) % 4
 cls(1 + band)
 print("WYRDWAY LUA TEST", 58, 48, 12, false, 2)
 print("If you see this, the Lua cart is running.", 30, 70, 12)
 print("Bundler pipeline is alive.", 54, 82, 13)
 print("Next step: re-enable modules one by one.", 24, 102, 12)
 rect(70, 118, 100, 8, 0)
 rect(72, 120, 24 + band * 18, 4, 4)
end
