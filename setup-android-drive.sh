#!/bin/bash
# Setup Android 1TB drive for Samba sharing
# Run with: sudo bash setup-android-drive.sh

set -e

echo "=== Setting up Android 1TB Drive ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Install exfat support if not present
if ! command -v exfatfsck &> /dev/null; then
    echo "Installing exFAT support..."
    apt-get update
    apt-get install -y exfat-fuse exfat-utils
fi

# Create mount point
mkdir -p /mnt/android

# Mount the drive
echo "Mounting /dev/sdc1 to /mnt/android..."
mount -t exfat /dev/sdc1 /mnt/android

# Add to fstab for auto-mount
if ! grep -q "/dev/sdc1" /etc/fstab; then
    echo "Adding to /etc/fstab..."
    echo "/dev/sdc1 /mnt/android exfat defaults,nofail,uid=1000,gid=1000,umask=000 0 0" >> /etc/fstab
fi

# Backup Samba config
cp /etc/samba/smb.conf /etc/samba/smb.conf.backup.$(date +%Y%m%d%H%M%S)

# Add Samba share
echo "Adding Samba share..."
cat >> /etc/samba/smb.conf << 'EOF'

[Android]
    comment = Android 1TB External Drive
    path = /mnt/android
    browsable = yes
    read only = no
    valid users = patrick
    create mask = 0777
    directory mask = 0777
    force user = patrick
    force group = patrick
EOF

# Test Samba config
echo "Testing Samba configuration..."
testparm -s /etc/samba/smb.conf > /dev/null && echo "Samba config OK"

# Restart Samba
echo "Restarting Samba..."
systemctl restart smbd
systemctl restart nmbd

# Verify
echo ""
echo "=== Setup Complete ==="
echo "Mount point: /mnt/android"
echo "Samba share: \\$(hostname -I | awk '{print $1}')\Android"
echo ""
echo "Current contents:"
ls -la /mnt/android | head -10
echo ""
echo "Samba shares:"
smbclient -L localhost -U patrick
