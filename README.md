<img src="./assets/logo.svg" width="300"/>
<img src="./assets/diagram.svg" width="100%"/>

## What is patchOS?

patchOS is an operating system for the Raspberry PI 4 that makes two modular synths patchable over the internet.

## Requirements

- Raspberry PI 4
- 8GB+ SD card
- [Expert Sleepers ES-8 module](https://www.expert-sleepers.co.uk/es8.html)

## How to install

1. Grab the [latest release](/elektrofon/patchOS/releases/latest/download/asset-name.zip) of patchOS
2. Use [etcher](https://www.balena.io/etcher/) to burn patchOS to the SD card
3. Boot your Raspberry PI with the new patchOS SD card

## How to use

patchOS is controlled via a simple web interface.  
It's best to use your phone for this.  
Open your web bowser and navigate to `http://patchos.local`

### Special note for Android user

Android doesen't support mDNS in the browser.
You will therefore not be able to connect to `http://patchos.local`.

Thankfully there is an easy fix by installing a network discovery app.  
A good suggestion is [BonjourBrowser](https://play.google.com/store/apps/details?id=de.wellenvogel.bonjourbrowser)

Install the app and it will find `patchOS control panel` for you.

## Notes

patchOS is an experiment; not a product.  
Feedback is most welcome, and pull requests – even more so!
