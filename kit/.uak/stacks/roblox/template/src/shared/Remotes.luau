--!strict
-- Owner: the contracts task. Declare every remote here; the server creates them, the client waits for them.
-- A new or changed remote is a contract change: uak msg impact:ID --kind contract "what changed · what to do".
local Remotes = {
	events = {
		-- RequestAttack = "RequestAttack",
	},
	functions = {},
}

return Remotes
