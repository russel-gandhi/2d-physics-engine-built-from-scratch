import asyncio
import json
import websockets
import urllib.request

async def test_ws():
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/spawn_robot",
        data=json.dumps({"preset_path": "robots/presets/boxer.json", "x": 0.0, "y": 4.0}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Spawn Robot API Status: {resp.status}")

    async with websockets.connect("ws://127.0.0.1:8000/ws/state") as ws:
        for tick in range(5):
            msg = await ws.recv()
            data = json.loads(msg)
            bodies = data.get("bodies", [])
            print(f"=== WS TICK {tick} (Total Bodies: {len(bodies)}) ===")
            for b_idx, b in enumerate(bodies):
                if not b['is_static']:
                    print(f"  Body {b_idx} (Dynamic): Pos=({b['pos'][0]:.6f}, {b['pos'][1]:.6f}), Angle={b['angle']:.6f}")

if __name__ == "__main__":
    asyncio.run(test_ws())
