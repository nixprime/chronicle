#!/usr/bin/python

"""Simple machine reporting script."""

import datetime
import email.mime.text
import json
import pipes
import smtplib
import socket
import subprocess
import types


CONFIG_FILENAME = "/etc/chronicle.conf"


def load_configuration(filename=CONFIG_FILENAME):
    with open(filename) as f:
        return json.load(f)


def name_cmd(cmd):
    if isinstance(cmd, types.StringTypes):
        return cmd
    return " ".join(pipes.quote(part) for part in cmd)


def run(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        p.wait()
        return p.stdout.read()
    except Exception as ex:
        return str(ex)


def main():
    cfg = load_configuration()

    cmd_results = { name_cmd(cmd): run(cmd) for cmd in cfg["commands"] }
    body_cmds = []
    for cmd in cfg["commands"]:
        cmd = name_cmd(cmd)
        body_cmd = "# " + cmd + "\n"
        body_cmd += cmd_results[cmd]
        body_cmds.append(body_cmd)
    body = "\n\n".join(body_cmds)

    mail_cfg = cfg["mail"]
    if "port" not in mail_cfg:
        mail_cfg["port"] = smtplib.SMTP_SSL_PORT
    msg = email.mime.text.MIMEText(body)
    msg["Subject"] = "[Chronicle] %s %s" % (socket.gethostname(),
                                            str(datetime.datetime.now()))
    msg["From"] = mail_cfg["from_addr"]
    msg["To"] = ", ".join(mail_cfg["to_addrs"])
    smtp = smtplib.SMTP_SSL(mail_cfg["host"], mail_cfg["port"])
    smtp.login(mail_cfg["username"], mail_cfg["password"])
    smtp.sendmail(mail_cfg["from_addr"], mail_cfg["to_addrs"], msg.as_string())
    smtp.quit()


if __name__ == "__main__":
    main()
