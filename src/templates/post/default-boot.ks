# Set default boot target and remove gnome setup
%post --interpreter /bin/bash
exec < /dev/tty6 > /dev/tty6 2> /dev/tty6
chvt 6

dnf remove gnome-initial-setup -y
ln -sf /lib/systemd/system/runlevel5.target /etc/systemd/system/default.target

chvt 1
exec < /dev/tty1 > /dev/tty1 2> /dev/tty1
%end
