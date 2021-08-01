from webhook import send_webhook
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
configured_pids = ast.literal_eval(config["DETAILS"]["pids"])
logging.info("Start monitoring PIDs: %s", configured_pids)
pids = list(configured_pids)

NOTIFICATION_TITLE = "The process is terminated"
NOTIFICATION_SUBTITLE = "The process is terminated"


def load_process_info(pids: list):
    pid_cmdlines = {}
    for pid in pids[:]:
        if not psutil.pid_exists(pid):
            logging.warning("PID %s does not exist. It will be excluded", pid)
            pids.remove(pid)
            continue

        p = psutil.Process(pid)
        pid_cmdlines[pid] = " ".join(p.cmdline())
    return pid_cmdlines


pid_info = load_process_info(pids)


def check_settings():
    global configured_pids
    global pid_info
    global pids

    config.read(CONFIG_FILE)
    new_pids = ast.literal_eval(config["DETAILS"]["pids"])
    for pid in new_pids:
        if pid not in configured_pids:
            logging.info("PID %s has been added", pid)
            pids.append(pid)
            configured_pids.append(pid)
            pid_info = load_process_info(pids)


def update_monitor_table():
    global pids
    check_settings()
    logging.info("Checking pids: %s", pids)
    for pid in pids[:]:
        if not psutil.pid_exists(pid):
            logging.info("PID %s has been terminated", pid)
            facts = {"Process ID": pid, "Process Command": pid_info[pid], "Host": socket.gethostname()}
            send_webhook(NOTIFICATION_TITLE, NOTIFICATION_SUBTITLE, facts)
            pids.remove(pid)


schedule.every(10).seconds.do(update_monitor_table)
while True:
    schedule.run_pending()
    time.sleep(1)
