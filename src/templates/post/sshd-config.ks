
# Install SSH keys
%post --interpreter /bin/bash

echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
echo "ChallengeResponseAuthentication no" >> /etc/ssh/sshd_config
echo "Subsystem       sftp    /usr/libexec/openssh/sftp-server" >> /etc/ssh/sshd_config

systemctl enable sshd --now
%end
