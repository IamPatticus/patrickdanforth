#!/bin/bash
PASS="password123"

# Create mount point and mount drive
echo "$PASS" | sudo -S mkdir -p /mnt/siliconpower
echo "$PASS" | sudo -S mount -t ntfs-3g /dev/sdb1 /mnt/siliconpower

# Add to fstab for auto-mount
echo '/dev/sdb1 /mnt/siliconpower ntfs-3g defaults,uid=patrick,gid=patrick,umask=0022 0 0' | sudo tee -a /etc/fstab

# Configure Samba share
cat << 'EOF' | sudo tee -a /etc/samba/smb.conf

[SiliconPower]
   path = /mnt/siliconpower
   browseable = yes
   read only = no
   guest ok = no
   valid users = patrick
   create mask = 0644
   directory mask = 0755
EOF

# Set up Samba user (will prompt for password)
sudo smbpasswd -a patrick

# Start services
sudo systemctl restart smbd nmbd
sudo systemctl enable smbd nmbd

# Verify
echo "=== Samba Status ==="
sudo systemctl status smbd --no-pager | head -20

echo ""
echo "=== Share Config ==="
sudo testparm --show-all-parameters 2>/dev/null | grep -A5 SiliconPower || echo "Share configured in smb.conf"

echo ""
echo "=== Setup Complete ==="
echo "From Windows, access: \\\\192.168.1.155\\\\SiliconPower"
