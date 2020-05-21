# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "archlinux/archlinux"

  config.vm.provider "virtualbox" do |v|
    v.name = "patchOS_build_env"
    v.memory = 2048
    v.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    sudo echo "Server = http://mirror.archlinux.no/\\$repo/os/\\$arch" > /etc/pacman.d/mirrorlist
    sudo pacman -Syu --noconfirm
    sudo pacman -S base-devel xmlto kmod inetutils libelf bc bison flex ncurses parted dosfstools gcc-libs wget rsync git python2 --noconfirm
    sudo echo 'MAKEFLAGS="-j$(($(nproc) + 1))"' >> /etc/makepkg.conf
    su vagrant -c "git clone https://aur.archlinux.org/yay-git.git"
    cd yay-git
    su vagrant -c "makepkg -si --skipchecksums --noconfirm"
    su vagrant -c "yay -Syu --noconfirm"
    su vagrant -c "gpg --keyserver keys.gnupg.net --recv-key 45F68D54BBE23FB3039B46E59766E084FB0F43D8"
    su vagrant -c "gpg --keyserver keys.gnupg.net --recv-key CEACC9E15534EBABB82D3FA03353C9CEF108B584"
    su vagrant -c "yay -S binfmt-qemu-static-all-arch qemu-user-static --noconfirm"
    su vagrant -c "yay -S binfmt-qemu-static-all-arch qemu-user-static --noconfirm"
    sudo systemctl restart systemd-binfmt.service
    wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
    chmod +x pishrink.sh
    sudo mv pishrink.sh /usr/local/bin
    su vagrant -c "git clone --depth=1 https://github.com/raspberrypi/tools ~/tools"
  SHELL
end
