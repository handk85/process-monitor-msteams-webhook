# Process Monitor MS Teams Webhook

This package contains two python scripts:
* **Webhook**: You can send a message to MS Teams via webhook 
* **Process monitor**: It monitors whether processes are running or not based on their PIDs. If a PID is terminated (i.e., no longer exists), it sends a message

## Dependencies
* requests
* psutil
* schedule

You can install the dependencies via `pip`
```
> pip install requests psutil schedule
```

## How to use
* Please [create an incoming webhook in your MS Teams channel](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
* Please create `setting.ini` by referring `settings.sample.ini`.
You need to specify Webhook url and the process ids (i.e., PIDs) in the file.
* Run `monitor.py` in a screen session. For example,
```
> screen -S monitor # it will start a screen session with the name, monitor.
> python3 monitor.py # Run the monitor script
# Press Ctrl+A d to detach the screen session
```
* If you want to modify `pids` in `settings.ini`, you don't need to stop the monitor. The monitor will automatically recognize the updated `pids` in config.