-- Minimal Lune test runner: runs every tests/*.spec.luau, or only the one named by the first argument.
-- A spec returns a table { case_name = function() ... end }; an error in a case is a failure.
local fs = require("@lune/fs")
local process = require("@lune/process")

local only = process.args[1]
local failed, passed = 0, 0
for _, file in fs.readDir("tests") do
	local name = string.match(file, "^(.+)%.spec%.luau$")
	if name and (only == nil or only == name) then
		local cases = require("./" .. name .. ".spec")
		for caseName, fn in cases do
			local ok, err = pcall(fn)
			if ok then
				passed += 1
			else
				failed += 1
				print(string.format("FAIL %s · %s\n  %s", name, caseName, tostring(err)))
			end
		end
	end
end
print(string.format("%d passed, %d failed", passed, failed))
process.exit(if failed > 0 then 1 else 0)
