# Loomo Jailbreak Guide

**Source:** https://github.com/nullicman/loomo-jailbreak

## Background

On **January 10th, 2025**, Segway shut down the Loomo activation/verification servers at `https://api-g1-sg.segwayrobotics.com/`. This means:
- New Loomos cannot be activated
- OTA updates no longer work
- Existing unactivated Loomos are "paperweights"

The jailbreak provides a **rooted Android firmware** to bypass this.

## You Need This If:

✅ Your Loomo is stuck on the "Provision" app and won't activate  
✅ You want root access for custom robotics projects  
⚠️ Your Loomo is already working - jailbreak is riskier and optional

## Requirements

- Windows PC (Intel Platform Flash Tool Lite is Windows-only)
- USB-C cable
- Loomo in DNX Fastboot mode
- `userdebug.zip` rooted firmware (from GitHub releases)

## Steps

### 1. Download Rooted Firmware

Get the `userdebug.zip` from the GitHub releases:
https://github.com/nullicman/loomo-jailbreak/releases

### 2. Install Intel Platform Flash Tool Lite

Download from Intel (search "Intel Platform Flash Tool Lite")

### 3. Put Loomo in DNX Fastboot Mode

1. Power off Loomo
2. Hold **Volume Down** button
3. Press **Power** button
4. Keep holding Volume Down until you see DNX Fastboot mode

### 4. Flash the Root Firmware

1. Connect Loomo to PC via USB-C
2. Open Intel Platform Flash Tool Lite
3. Load the `userdebug.zip` file
4. Flash to Loomo

### 5. First Boot

After flashing:
- Loomo will boot into Android
- Root access available via ADB
- No more activation required!

## What You Get

- **Rooted Android** - full system access
- **ADB enabled** - development access over USB/WiFi
- **No activation** - works offline
- **Custom apps** - can install own APKs
- **ROS compatible** - can run robotics stacks

## Post-Jailbreak Setup

Once rooted, we can:

1. **Enable ADB over WiFi:**
   ```bash
   adb tcpip 5555
   adb connect <LOOMO_IP>:5555
   ```

2. **Install Python/ROS:**
   - Via Termux or custom root scripts
   - Or use external computer as bridge

3. **Deploy our Loomo Bridge:**
   ```bash
   python3 loomo-bridge/tools/discover_loomo.py
   ```

## Risks

⚠️ **WARNING:**
- Could brick Loomo (unlikely but possible)
- Boot loops possible if flash fails
- Warranty definitely void (Segway abandoned it anyway)
- No official support path back

## Resources

- **Video Tutorial:** https://youtu.be/uUaLv8AlMkE
- **GitHub:** https://github.com/nullicman/loomo-jailbreak
- **Firmware:** Check GitHub Releases tab
- **Our Bridge:** `~/openclaw/workspace/loomo-bridge/`

## Talos Integration

Post-jailbreak Loomo + Talos/OpenClaw:
- Voice control via Talos
- Autonomous patrol modes
- Camera streaming to OpenClaw
- Integration with other robots (Clawcar, etc.)
- Custom behaviors written in Python

---

*Remember: This is a rescue for abandoned hardware. Segway orphaned these robots - we're giving them new purpose.* 🤖
