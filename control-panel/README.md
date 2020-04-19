# patchOS Control Panel

A web control panel for patchOS

## Developer notes

### Watch files and sync
You can watch your local files when editing and sync to the raspberry pi running patchOS.  
This is done using [watchman](https://facebook.github.io/watchman) and `rsync`.

Install rsync on patchOS:
```sh
$ pacman -S rsync
```

Install watchman on your machine:
```sh
$ brew install rsync watchman
```

Copy your public key to patchOS
```sh
$ ssh-copy-id -i ~/.ssh/id_rsa.pub patch@patchos.local
```

Set up watcher:
```sh
$ cd control-panel
$ watchman watch .
```

Start syncing:
```sh
$ watchman -- trigger . 'patchos' -- sh ./sync
```

### Stop watch files and sync

```sh
$ cd control-panel
$ watchman watch-del .
```
