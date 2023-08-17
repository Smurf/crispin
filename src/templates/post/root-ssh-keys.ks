
# Install SSH keys
%post --interpreter /bin/bash

#---- Install SSH key ----
mkdir -m0700 /root/.ssh/

cat <<EOF >/root/.ssh/authorized_keys
{% for ssh_key in root_ssh_keys -%}
{{ ssh_key }}
{% endfor %}
EOF

### set permissions
chmod 0600 /root/.ssh/authorized_keys

### fix up selinux context
restorecon -R /root/.ssh/

%end
