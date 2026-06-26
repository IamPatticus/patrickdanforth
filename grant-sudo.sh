#!/bin/bash
# Grant Talos passwordless sudo for specific commands

echo 'patrick ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get, /bin/mount, /bin/umount, /bin/mkdir, /usr/bin/systemctl, /usr/bin/tee, /usr/bin/smbpasswd' | sudo tee /etc/sudoers.d/patrick-talos
sudo chmod 0440 /etc/sudoers.d/patrick-talos
sudo visudo -c  # Validate syntax
echo "Sudo access granted."
