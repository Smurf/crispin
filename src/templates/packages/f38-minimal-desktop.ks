# Base Packages
%packages

# Exclude unwanted groups for minimal install
-@dial-up
-@input-methods
-@standard

# Install workstation-product-environment to resolve RhBug:1891500
@^workstation-product-environment

# Install cracklib-dicts and libpwquality for cryptsetup
cracklib
cracklib-dicts
libpwquality

# Install rpmfusion gpg keys
distribution-gpg-keys

# Exclude unwanted packages
-gfs2-utils
-reiserfs-utils
-cheese
-rhythmbox
-virtualbox-guest-additions
-gnome-software
%end

