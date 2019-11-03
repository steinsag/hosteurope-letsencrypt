#!/usr/bin/env python3
# coding=utf-8
import json
import os

from shared import domain_list, config_file

# certbot tries to write to /var/log/letsencrypt by default; because of this, running as root is required.
# certbot Error Message:
# Either run as root, or set --config-dir, --work-dir, and --logs-dir to writeable paths.
is_root = os.geteuid() == 0
home_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt')
certbot_config_dir = home_dir
certbot_work_dir = home_dir
certbot_logs_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt/logs')
if not is_root and not os.path.exists(certbot_logs_dir):
    os.makedirs(certbot_logs_dir)

# Einstellungen einlesen
with open(config_file('einstellungen.json')) as cfg_file:
    config = json.load(cfg_file)
email = config['email']
staging = config['staging']

challenge = config.get('preferred-challenge', 'http')

# certbot Kommando zusammenbauen
cmd = 'certbot certonly --manual --agree-tos --manual-public-ip-logging-ok'
cmd += ' -m ' + email
cmd += ' --preferred-challenge=' + challenge
if 'http' == challenge:
    cmd += ' --manual-auth-hook "python3 validate.py"'
if staging:
    cmd += ' --staging'

if not is_root:
    cmd += ' --logs-dir ' + certbot_logs_dir
    cmd += ' --work-dir ' + certbot_work_dir
    cmd += ' --config-dir ' + certbot_config_dir

cmd += domain_list

# Sicherheitsabfrage
print(cmd)
answer = input('Für diese Domains ein neues Zertifikat erstellen? (j/n): ')
if answer != 'j':
    print('Abbruch, es wurde kein Zertifikat erstellt.')
    exit(0)

# neues Zertifikat erstellen
os.system(cmd)
