# coding=utf-8
import json
import os


def config_file(name):
    f = os.path.expanduser('~/.config/hosteurope-letsencrypt/' + name)
    return os.path.abspath(name if os.path.isfile(name) or not os.path.isfile(f) else f)


# Domain Mapping einlesen
with open(config_file('domains.json')) as domain_file:
    domain_map = json.load(domain_file)

# Domains auflisten wie von certbot erwartet
domain_list = ' -d ' + ' -d '.join(domain_map.keys())
