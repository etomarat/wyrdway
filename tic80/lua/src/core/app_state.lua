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
