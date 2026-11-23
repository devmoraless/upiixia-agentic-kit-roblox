local Score = require("../src/shared/score")

local function eq(actual, expected)
	if actual ~= expected then
		error(string.format("expected %s, got %s", tostring(expected), tostring(actual)), 2)
	end
end

return {
	adds_points = function()
		eq(Score.add(10, 5), 15)
	end,
	rejects_negative_points = function()
		eq((pcall(Score.add, 10, -1)), false)
	end,
}
