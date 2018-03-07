import json
import os

from shared import domain_list, config_file

# Einstellungen einlesen
with open(config_file('einstellungen.json')) as cfg_file:
    config = json.load(cfg_file)
email = config['email']
staging = config['staging']

# certbot Kommando zusammenbauen
cmd = 'certbot certonly --manual --manual-auth-hook "python3 validate.py" --agree-tos --manual-public-ip-logging-ok'
cmd += ' -m ' + email
if staging:
    cmd += ' --staging'
cmd += domain_list

# Sicherheitsabfrage
print(cmd)
answer = input('Für diese Domains ein neues Zertifikat erstellen? (j/n): ')
if answer != 'j':
    print('Abbruch, es wurde kein Zertifikat erstellt.')
    exit(0)

# neues Zertifikat erstellen
os.system(cmd)
