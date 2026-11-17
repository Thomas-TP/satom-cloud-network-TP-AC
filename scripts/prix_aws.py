"""Interroge l'API officielle de prix AWS (Price List, region eu-north-1) pour l'estimation du budget (module 0).
Usage : python prix_aws.py   -> affiche un tableau et ecrit docs/modules/m00/prix.json"""
import json, os, subprocess, sys
AWS = r'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def produits(service, filtres, n=100):
    cmd = [AWS, 'pricing', 'get-products', '--service-code', service, '--region', 'us-east-1', '--profile', 'TP-AC', '--max-results', str(n), '--output', 'json']
    if filtres: cmd += ['--filters'] + [f'Type=TERM_MATCH,Field={k},Value={v}' for k, v in filtres.items()]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if r.returncode: raise RuntimeError(r.stderr[-300:])
    out = []
    for item in json.loads(r.stdout)['PriceList']:
        p = json.loads(item)
        for t in p['terms'].get('OnDemand', {}).values():
            for d in t['priceDimensions'].values():
                out.append((p['product']['attributes'], d['description'], d['unit'], float(d['pricePerUnit'].get('USD', 0))))
    return out

def premier(service, filtres, mot, unite=None):
    for a, desc, u, usd in produits(service, filtres):
        if mot.lower() in desc.lower() and (unite is None or u == unite) and usd > 0: return usd, desc
    return None, 'introuvable'

REG = {'regionCode': 'eu-north-1'}
res = {}
res['EC2 t3.micro Linux (heure)'] = premier('AmazonEC2', {**REG, 'instanceType': 't3.micro', 'operatingSystem': 'Linux', 'tenancy': 'Shared', 'preInstalledSw': 'NA', 'capacitystatus': 'Used'}, 'on demand linux', 'Hrs')
res['NAT Gateway (heure)'] = premier('AmazonEC2', {**REG, 'productFamily': 'NAT Gateway', 'operation': 'NatGateway'}, 'per NAT Gateway Hour', 'Hrs')
res['ALB (heure)'] = premier('AWSELB', {**REG, 'productFamily': 'Load Balancer-Application'}, 'per Application LoadBalancer-hour', 'Hrs')
res['Attachement Transit Gateway (heure)'] = premier('AmazonVPC', {**REG, 'productFamily': 'Transit Gateway'}, 'attachment', 'hour')
res['Connexion VPN (heure)'] = premier('AmazonVPC', {**REG, 'productFamily': 'VPN Connection'}, 'VPN connection-hour', 'Hrs')
res['Network Firewall endpoint (heure)'] = premier('AWSNetworkFirewall', {**REG}, 'endpoint hour', 'Hrs')
res['Adresse IPv4 publique (heure)'] = premier('AmazonVPC', {**REG, 'productFamily': 'IP Addresses'}, 'public IPv4', 'Hrs')
res['Zone hebergee Route 53 (mois)'] = premier('AmazonRoute53', {'productFamily': 'DNS Zone'}, 'hosted zone', None)
for k, (v, d) in res.items(): print('%-40s %s   %s' % (k, ('%.4f USD' % v) if v is not None else '-', d[:90]))
os.makedirs(os.path.join(ROOT, 'docs', 'modules', 'm00'), exist_ok=True)
json.dump({k: {'usd': v, 'description': d} for k, (v, d) in res.items()}, open(os.path.join(ROOT, 'docs', 'modules', 'm00', 'prix.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
