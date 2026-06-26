#!/bin/bash
# Reginald screen OFF — blank the framebuffer

# The SPI display is on fb1 (480x320, fb_ili9486)
# fb0 is vc4drmfb (800x480 virtual, not the physical SPI screen)
FB_DEV="/dev/fb1"
WIDTH=480
HEIGHT=320

# Write black pixels in chunks (RGB565 = 0x0000)
python3 -c "
import struct

fb = open('$FB_DEV', 'wb')
pixel = struct.pack('<H', 0x0000)  # black in RGB565
chunk = pixel * 512  # 1KB chunks

remaining = $WIDTH * $HEIGHT * 2
while remaining > 0:
    to_write = min(len(chunk), remaining)
    fb.write(chunk[:to_write])
    remaining -= to_write

fb.close()
print('Reginald screen OFF at $FB_DEV (' + str($WIDTH) + 'x' + str($HEIGHT) + ')')
"
