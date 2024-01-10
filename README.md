Raspberry Pi Home Automations

Instructions are designed for a headless RPi Zero W running RPiOS Legacy Lite and connecting to the internet using WiFi.

First-time setup:
1. Boot up your Raspberry Pi and connect it to the internet.
    - Suggested method is using Raspberry Pi Imager to burn the OS to a micro SD card. Use Advanced Options in Imager to set wifi credentials and enable SSH.
2. SSH into the RPi and clone this repo from GitHub.
    - From another computer, run `ssh <user>@<IPaddress>`, substituting in the username that you configured in Raspberry Pi Imager and the RPi device's IP address. You can find the IP address by inspecting devices connected to your router. You will then need to enter the password that you configured in Imager.
    - Install git by running `sudo apt install git`
    - Clone this repo by running `git clone https://github.com/schwartz721/rpihome.git`
3. Run the setup script to finish the installation and start the server.
    - `cd rpihome` to move into the directory containing the repo.
    - `bash setup` runs a script in the repo that might need your approval for some steps. The whole process will take several minutes to finish.
