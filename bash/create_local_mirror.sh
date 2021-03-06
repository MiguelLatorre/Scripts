#!/bin/bash

TMP_DB="/tmp/pacdb"
ROOT_PATH="/srv/http/local_mirror"
BIN_PATH="os/x86_64"
# expac simply resolves dependencies, splits them into new lines and tr just wraps them on the same line
PACKAGES="base base-devel linux linux-firmware btrfs-progs efibootmgr nano wpa_supplicant dialog nano lollypop gstreamer gst-plugins-good gnome-keyring nemo gpicview-gtk3 chromium awesome xorg-server xorg-xrandr xorg-twm xorg-xinit xterm feh slock xscreensaver terminus-font-otb gnu-free-fonts ttf-liberation xsel qemu ovmf openssh sshfs git htop pkgfile scrot dhclient wget smbclient cifs-utils libu2f-host pulseaudio pulseaudio-alsa pavucontrol python git python-psutil python-systemd python-pygeoip geoip-database syslinux haveged intel-ucode amd-ucode memtest86+ mkinitcpio-nfs-utils nbd zsh efitools arch-install-scripts b43-fwcutter broadcom-wl btrfs-progs clonezilla crda darkhttpd ddrescue dhclient dhcpcd dialog diffutils dmraid dnsmasq dnsutils dosfstools elinks ethtool exfat-utils f2fs-tools fsarchiver gnu-netcat gpm gptfdisk grml-zsh-config grub hdparm ipw2100-fw ipw2200-fw irssi iwd jfsutils lftp linux-atm linux-firmware lsscsi lvm2 man-db man-pages mc mdadm mtools nano ndisc6 netctl nfs-utils nilfs-utils nmap ntfs-3g ntp openconnect openssh openvpn partclone parted partimage ppp pptpclient refind-efi reiserfsprogs rp-pppoe rsync sdparm sg3_utils smartmontools sudo tcpdump testdisk usb_modeswitch usbutils vi vim-minimal vpnc wget wireless-regdb wireless_tools wpa_supplicant wvdial xfsprogs xl2tpd git python python-psutil python-systemd python-pygeoip geoip-database"
#PACKAGES=$(expac -S '%E' -l '\n' ${PACKAGES} | tr '\n' ' ')

mkdir -p "${TMP_DB}"
mkdir -p "${BIN_PATH}"
sudo pacman --dbpath "${TMP_DB}" -Syu -w --root "${ROOT_PATH}" --cachedir "${BIN_PATH}" ${PACKAGES}
sudo repo-add "${ROOT_PATH}/${BIN_PATH}/local_repo.db.tar.gz" "${ROOT_PATH}/${BIN_PATH}/{*.pkg.tar.xz,*.pkg.tar.zst}"

cat <<EOF
[local_repo]
Server = http://local-repo/$repo/os/$arch
SigLevel = Optional TrustAll
EOF
