
%pre --interpreter /bin/bash    
exec < /dev/tty6 > /dev/tty6 2> /dev/tty6    
chvt 6    

# Generated using Blivet version 3.4.3    
echo 'ignoredisk --only-use=nvme0n1' >> /tmp/part.ks    
# Partition clearing information    
echo 'clearpart --all --initlabel' >> /tmp/part.ks    
# Disk partitioning information    
echo 'part /boot/efi --fstype="efi" --size=512 --fsoptions="umask=0077,shortname=winnt"' >> /tmp/part.ks    
echo 'part /boot --fstype="ext4" --size=1024' >> /tmp/part.ks    
echo "part btrfs.249 --fstype=\"btrfs\" --ondisk=nvme0n1 --grow" >> /tmp/part.ks
echo 'btrfs none --label=fedora btrfs.249' >> /tmp/part.ks
echo 'btrfs / --subvol --name=@root LABEL=fedora' >> /tmp/part.ks
echo 'btrfs /var --subvol --name=@var LABEL=fedora' >> /tmp/part.ks
echo 'btrfs /var/log --subvol --name=@var_log LABEL=fedora' >> /tmp/part.ks
echo 'btrfs /home --subvol --name=@home LABEL=fedora' >> /tmp/part.ks
# echo 'btrfs /.snapshots --subvol --name=snapshots LABEL=fedora' >> /tmp/part.ks
chvt 1
exec < /dev/tty1 > /dev/tty1 2> /dev/tty1
%end

%include /tmp/part.ks
