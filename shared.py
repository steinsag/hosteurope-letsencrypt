import json

# Domain Mapping einlesen
with open('domains.json') as domain_file:
    domain_map = json.load(domain_file)

# Domains auflisten wie von certbot erwartet
domain_list = ' -d ' + ' -d '.join(domain_map.keys())
