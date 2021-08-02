from webhook import send_webhook
from datetime import datetime
import configparser
import logging
import psutil
import socket
import schedule
import time
import ast
import sys

log_format = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

CONFIG_FILE = "settings.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# You need to add process IDs to monitoring
initial_pids = ast.literal_eval(config["DETAILS"]["pids"])
logging.info("Start monitoring PIDs: %s", initial_pids)

NOTIFICATION_TITLE = "The process is terminated"
NOTIFICATION_SUBTITLE = "The process is terminated"
WEBHOOK_URL = config["DETAILS"]["webhook_url"]
HOST = socket.gethostname()


class ProcessInfo:
    def __init__(self, pid: int, cmdline: str, start_time: str, host: str):
        self.pid = pid
        self.cmdline = cmdline
        self.start_time = start_time
        self.host = host

    def get_facts(self):
        return {"Process ID": self.pid, "Command": self.cmdline,
                "Host": self.host, "Started": self.start_time}


def convert_create_time(create_time: float):
    d = datetime.fromtimestamp(create_time)
    return d.strftime("%Y-%m-%d %H:%M:%S")


def load_process_info(pid: int):
    if not psutil.pid_exists(pid):
        logging.warning("PID %s does not exist. It will be excluded", pid)
        return
    p = psutil.Process(pid)
    return ProcessInfo(pid, " ".join(p.cmdline()), convert_create_time(p.create_time()), HOST)


def check_settings(pid_info: dict, terminated_pids: list):
    config.read(CONFIG_FILE)
    new_pids = ast.literal_eval(config["DETAILS"]["pids"])
    for pid in new_pids:
        if pid not in pid_info and pid not in terminated_pids:
            pid_info[pid] = load_process_info(pid)


def update_monitor_table(pid_info: dict, terminated_pids: list):
    check_settings(pid_info, terminated_pids)
    logging.info("Checking pids: %s", list(pid_info.keys()))
    for pid in list(pid_info.keys()):
        if not psutil.pid_exists(pid):
            logging.info("PID %s has been terminated", pid)
            process_info = pid_info.pop(pid)
            send_webhook(WEBHOOK_URL, NOTIFICATION_TITLE, NOTIFICATION_SUBTITLE, process_info.get_facts())
            terminated_pids.append(pid)


info = {pid: load_process_info(pid) for pid in initial_pids}
[info.pop(i) for i in list(info.keys()) if info[i] is None]
terminated = [pid for pid in initial_pids if pid not in info]

schedule.every(10).seconds.do(update_monitor_table, info, terminated)
while True:
    schedule.run_pending()
    time.sleep(1)
