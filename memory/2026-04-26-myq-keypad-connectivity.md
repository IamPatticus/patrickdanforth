# Session: 2026-04-26 01:14:04 UTC

- **Session Key**: agent:main:main
- **Session ID**: 569ed943-cfd3-4d8b-a26c-3fdfd7d6001d
- **Source**: webchat

## Conversation Summary

assistant: 

Nice — come back when the parts arrive and we'll get it all wired up.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 19:52 CDT] Will do.....now another MyQ question....I have the key pad with video.....is that no longer going to connect to the MyQ opener?
assistant: 

Depends on what the keypad needs the hub for. Most MyQ video keypads work as part of the MyQ ecosystem — they need the hub to feed video to the cloud and to trigger the opener. Without a working hub, the video part goes dark.

**What likely stops working without the hub:**
- Live video feed in the MyQ app
- Motion alerts
- Two-way audio (if it has that)
- Any remote unlock/trigger from the app

**What might still work:**
- Physical keypad buttons to open/close the door (if it wired directly to the opener, not through the hub)
- If it has its own WiFi, it might still connect to the network, but the MyQ app integration is done without the hub

If it's a pure MyQ accessory that relies entirely on the hub for everything, it's dead in the water without a working hub — same problem as the opener itself.

What brand/model is the keypad? That'll tell us if it's standalone or hub-dependent.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 19:55 CDT] It has a keypad but since the garage opener won't connect to wifi I am guessing this won't work?
assistant: 

Yeah — it's cascading now. The keypad with video probably needs the MyQ hub to relay everything (video stream, door commands) through MyQ's cloud. Without a working hub, it's just a fancy keypad that can't phone home.

If the keypad has its own WiFi connection and streams directly to the MyQ app without the hub, it might still show up in the app — but the door trigger part still needs the hub to talk to the opener. So even if video works, you still can't open the door from the app.

Short version: **yes, the keypad is also affected.** The hub was the bridge everything used to communicate.

When you replace the hub (Shelly path), the keypad becomes the weak link. MyQ accessories don't really work with non-MyQ systems. If the keypad is important to you, the Shelly replacement won't restore its functionality — you'd need a different video doorbell or keypad that works with Home Assistant (like a Ring or UniFi product) if you want that feature back.

What's your priority — getting the garage door itself working, or preserving the video keypad? If it's mostly about the door, the Shelly fix handles that and the keypad is just lost. If the keypad matters a lot, there might be a workaround depending on what it is.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 19:57 CDT] Video works, how do I setup a pin to open garage?
assistant: 

If the keypad has a wired connection to the opener (which it likely does — the physical keypad buttons usually wire directly to the opener's terminals), the PIN is set on the opener itself, not through MyQ.

**How to set/change the PIN:**

1. **Find the "Learn" button** on your garage door opener — it's usually on the back or side, colored (red, yellow, purple, etc.) depending on the year

2. **Press the Learn button** — the opener's LED will light up and you'll have 30 seconds to pair the keypad

3. **On the keypad**, enter the PIN you want to use, then press the Enter or OK button

4. **Press the Learn button again** on the opener to confirm

5. Test it — enter your PIN and press the opener button (usually the up arrow or #)

The keypad's video stream goes through the MyQ cloud (which is why video still works), but the actual door trigger is wired direct — so the PIN still works even without the hub.

Check your opener's manual or look up the model number if the Learn button process doesn't match your setup. What model is the garage door opener?
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:01 CDT] The Keypad is MyQ smart wireless door video keypad....I will go find the garage door model
assistant: 

Ah — if it's a **MyQ wireless keypad with video**, it pairs with the MyQ hub, not directly to the opener. That means without the hub, it can't trigger the door at all — the video feed might still work if it has its own WiFi connection, but the door button is dead in the water without the hub pairing.

So the situation is:
- **Video** → might still work (separate WiFi connection to MyQ cloud)
- **Door trigger** → dead without hub
- **PIN setup** → not accessible without the hub to sync the keypad

That's frustrating — the keypad became a expensive paperweight because the hub died. When you find the opener model, we'll confirm what's possible. If the keypad was the only way to get video on this garage, it's a genuine loss.

Let me know what opener model you find.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:05 CDT] damn them LOL Can the Garage door connect to the keypad vs wireless network?
assistant: 

Check the keypad itself — does it have a wiring terminal block on the back or bottom? Some "smart" keypads with video still have two terminals for direct wired connection to an opener as a fallback.

If it has those two terminals, you can wire it directly to the opener just like a standard keypad — bypassing the MyQ network entirely for the PIN. The video part might still need WiFi, but the door trigger would work through the direct wire.

Look for two small screw terminals labeled something like "OPENER" or "RELAY" or just two empty ports. If it's there, you can wire it directly and the PIN becomes independent of the hub.

What model is the keypad? (Usually on a label on the back or inside the battery compartment)
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:10 CDT] It does not, so sad. Oh well sometimes tech is just garbage....I am surprised MyQ is still around as the reviews are HORRIBLE.
assistant: 

MyQ has basically built a monopoly on garage access and charges for it — reviews are brutal because they're the only game in town for Chamberlain/LiftMaster owners. The hardware works when it works, but the moment something breaks or they change their cloud policy, you're stuck.

Better long-term play: go fully local. The Shelly setup you're ordering gives you garage control in HA without any cloud account, no subscription, no risk of MyQ cutting you off when they change their business model.

The video keypad can become a standard Ring doorbell at the garage (or just accept the loss) — and the door itself runs on your own MQTT forever, no matter what happens to MyQ's cloud or business decisions.

Sometimes the best move is to stop feeding a bad ecosystem and build your own that you actually own.

Anyway — good plans in motion. Parts ordered, Alpha testing live, self-hosted app built. Solid Saturday work.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:11 CDT] I prefer local anyway, cloud connect just opens to many doors and you never OWN anything connected to the cloud.
assistant: 


Exactly right. When it's local, it's yours. Cloud is rental — you own nothing and they can take it away whenever they want.

Shelly + HA = yours forever.
