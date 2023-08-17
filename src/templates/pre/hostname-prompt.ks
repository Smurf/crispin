# Setup hostname
%pre --interpreter /bin/bash
exec < /dev/tty6 > /dev/tty6 2> /dev/tty6
chvt 6

read -p "Enter hostname:" new_hostname

sleep 1

echo "network --bootproto=dhcp --hostname=$new_hostname --activate" > /tmp/network.ks

chvt 1
exec < /dev/tty1 > /dev/tty1 2> /dev/tty1
%end
