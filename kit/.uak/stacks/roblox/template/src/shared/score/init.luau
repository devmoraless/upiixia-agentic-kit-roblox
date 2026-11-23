--!strict
-- Example pure module: no services at require time, so Lune can test it outside Studio.
local Score = {}

function Score.add(current: number, points: number): number
	assert(points >= 0, "points must be non-negative")
	return current + points
end

return Score
