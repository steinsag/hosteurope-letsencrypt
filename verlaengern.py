import json
import os

from shared import domain_list, config_file

with open(config_file('einstellungen.json')) as config_file:
    config = json.load(config_file)
staging = config['staging']

# certbot Kommando zusammenbauen
cmd = 'certbot certonly -n --manual --manual-auth-hook "python3 validate.py" --agree-tos --manual-public-ip-logging-ok'
if staging:
    cmd += ' --staging'
cmd += domain_list

# Sicherheitsabfrage
print(cmd)
answer = input('Zertifikate verlängern? (j/n): ')
if answer != 'j':
    print('Abbruch, es wurde kein Zertifikat verlängert.')
    exit(0)

# neues Zertifikat erstellen
os.system(cmd)
