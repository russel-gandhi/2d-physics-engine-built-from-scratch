# Future Vision — Not Part of the Current Build

This captures the fuller RoboForge Arena vision — the parts that are genuinely a different scale of engineering than the physics/robot/combat/RL work in `04_IMPLEMENTATION_PLAN.md`, and so are documented here as direction, not turned into stages. Building any of this "for real," in the same spirit as the rest of the project (no shortcuts, no faked results), means real server infrastructure and real client-server networking — that's a substantial, separate project in its own right, not something to bolt on as an afterthought stage.

## Why this is separated out

`02_AGENT_RULES.md` bans faked results. A stubbed or partial multiplayer layer — one that looks like it works in a demo but isn't real networked play — would violate that rule as surely as a hardcoded physics result would. So rather than pretend this fits alongside everything else, it's parked here until there's real time budgeted for it.

## Multiplayer Battles

- Real client-server architecture: a simulation server authoritative over match state, clients sending robot actions/inputs
- Matchmaking (pairing players by rank or robot stats)
- Ranked ladder with a rating system (e.g. Elo/Glicko)
- Tournaments — bracket-based, potentially running many matches server-side
- Spectator mode for *live* remote matches (Phase 5's replay/spectator work covers local playback; watching someone else's live match over a network is a networking problem, not a rendering one)

## Platform & Community

- Persistent accounts, saved robot designs and trained models tied to an account
- Robot marketplace — sharing/trading designs or trained policies
- Global rankings, leaderboards
- Community tournaments, "evolution leagues" (persistent evolving populations across many players' robots)
- Custom arenas shared/rated by the community

## A reasonable path to this later, if it's ever picked up

1. Get the local version (this repo, Phases 1-7) fully working and polished first — it's a complete, honest project on its own.
2. Networking is its own learning arc: start with something much simpler than a full match server — e.g. two local processes exchanging robot actions over a socket for a single 1v1 match — before attempting matchmaking or ranked infrastructure.
3. Treat the multiplayer/platform layer as a second project that *uses* this one's simulation core, rather than trying to retrofit networking into code that was written for a single local process.
