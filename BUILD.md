### 1. Update and upgrade (as root)

```sh
$ pacman -Syu --noconfirm
```

### 2. Install packages (as root)

```sh
$ pacman -S --noconfirm \
base-devel \
git \
realtime-privileges \
libffado \
rtaudio \
qt5-base \
jack2
```

### 3. Build jacktrip from source (as root)

```sh
$ git clone https://github.com/jacktrip/jacktrip.git && \
cd jacktrip/src && \
./build && \
make install
```

### 4. Prepare user (as root)

```sh
$ usermod -a -G realtime <username> && \
usermod -a -G audio <username>
```

### 6. Create service for Jack2

```sh
$ 
```
### 7. Cleanup (as root)

```sh
$ rm -Rf jacktrip
```

```sh
$ pacman -Rsu git base-devel
```
