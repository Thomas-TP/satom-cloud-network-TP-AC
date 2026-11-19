"""Module 7 : IAM : le role des instances peut lire le secret des cles et decrire les connexions VPN (politique en ligne)."""
from common import *

POL = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:eu-north-1:*:secret:Projet/SatomCloudNetwork/vpn-??????"
    },
    {
      "Effect": "Allow",
      "Action": "ec2:DescribeVpnConnections",
      "Resource": "*"
    }
  ]
}'''

async def run(r):
    await r.goto('https://us-east-1.console.aws.amazon.com/iam/home?region=eu-north-1#/roles/details/TP-AC-ec2-ssm-role?section=permissions', wait=5)
    await r.hold(1.5)
    await r.click(btn('Ajouter des autorisations')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('menuitem', name=re.compile('politique en ligne'))); await r.hold(3.0)
    await r.click(btn('JSON', True)); await r.hold(1.5)
    r.mark('editeur')
    await r.click_xy(900, 330); await r.hold(0.5)
    await r.press('Control+a', 0.3); await r.press('Delete', 0.3)
    await r.page.keyboard.insert_text(POL); await r.hold(2.5)
    r.mark('politique')
    await r.click(btn('Suivant', True)); await r.hold(2.5)
    await r.type(lambda f: f.locator('input[type=text]').first, 'lire-cles-vpn-TP-AC'); await r.hold(1.0)
    r.mark('nom')
    await r.scroll(900); await r.hold(0.8)
    await r.click(btn('Créer une politique', True)); await r.hold(4.0)
    r.mark('creee'); await r.hold(2.0)
