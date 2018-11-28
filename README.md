## Saavn music downloader
Download Saavn playlists by just passing the link of it.
*ALL THE EXECUTABLES GIVEN HERE ARE FOR LINUX x64 system, tested on a debian based OS (elementary OS), Kernel: 4.15.0-39-generic, Download the binaries from the link below, if it's not compatible on your system*
## Usage:
```sh
    pip3 install -r requirements.txt
```
- download [browsermob-proxy](https://github.com/lightbody/browsermob-proxy/releases) and paste the executable in the directory
- download [Chrome Web Driver](http://chromedriver.chromium.org/downloads) and paste it here in the folder
- copy the link of playlist you want to download and paste it in a text file, and pass the name of the file through the parameter.
For more help,
```
python3 saavndownloader.py --help
```
## Credits:
 - Chrome Driver - The Chromium Project
 - browsermob-proxy - [webmerics](https://github.com/webmetrics) now maintained by [Patrick Lightbody](https://github.com/lightbody)
