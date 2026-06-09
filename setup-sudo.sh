#!/bin/bash
# This script must be run with sudo

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash $0"
    exit 1
fi

cat > /etc/sudoers.d/patrick-talos << 'SUDOERS'
patrick ALL=(ALL) NOPASSWD: *** /usr/bin/apt-get, /usr/bin/apt, /bin/mount, /bin/umount, /bin/mkdir, /usr/bin/systemctl, /usr/bin/tee, /usr/bin/smbpasswd, /usr/bin/chmod, /usr/bin/nano, /usr/bin/vim, /bin/nano
SUDOERS

chmod 0440 /etc/sudoers.d/patrick-talos
visudo -c

if [ $? -eq 0 ]; then
    echo "Sudoers file created and validated successfully."
else
    echo "Error: sudoers file validation failed."
    exit 1
fi
