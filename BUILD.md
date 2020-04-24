## Building patchOS

### 1. Install Vagrant

Head to [vagrantup.com](https://www.vagrantup.com/downloads.html) and download Vagrant.

### 2. Set up the patchOS build environment

In your `patchOS` source directory:
```sh
$ vagrant up && vagrant halt && vagrant up
```

First time setup will take about 1 hour on a decent laptop.  
The reason for halting and upping is to load any new kernel updates that was installed when upgrading Arch Linux.

### 3. Build patchOS

```sh
$ vagrant ssh -c "sudo /vagrant/vagrant-build"
```

This will take about 2 hours on a decent laptop.

The final `patchOS` image will be in the `release` directory if everything went smoothly.
