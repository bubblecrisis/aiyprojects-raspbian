
# Branch

All customization are made to the *release* branch. The main and other branch
are to be used for pulling from upstream changes.

# Installation

```
cd AIY-voice-kit-python
git checkout release
git pull
```

## Run as service

Create a symbolic link ``voicekit.service`` for systemctl.

```
sudo ln -s /etc/systemd/system/multi-user.target.wants/voicekit.service  /home/pi/AIY-voice-kit-python/src/examples/voice/assistant_custom.service
```

Reload, start, stop and check status systemctl commands:

```
sudo systemctl reload-daemon
sudo systemctl start voicekit
sudo systemctl stop voicekit
system status voicekit
```

# Troubleshoot

### Failed to add edge detection error

If you are getting error:
```
GPIO.add_event_detect(self.channel, self.polarity)
RuntimeError: Failed to add edge detection
```

Resolution is:

```
echo 23 > /sys/class/gpio/unexport
``` 


