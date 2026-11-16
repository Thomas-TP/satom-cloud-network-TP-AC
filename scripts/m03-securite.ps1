# Module 3 - Security Groups et NACL (TP-AC)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State

# --- Services de test (nginx 80/443 sur web-01, mini API 8080 sur app-01), installes via SSM ---
$webScript = @'
set -e
dnf install -y nginx openssl >/dev/null 2>&1
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout /etc/nginx/ssl/web.key -out /etc/nginx/ssl/web.crt -subj "/CN=portefeuilles.leman-finance.example" 2>/dev/null
cat > /etc/nginx/conf.d/tpac.conf <<'EOC'
server { listen 80; location /health { return 200 "ok\n"; } location / { return 200 "web-01 TP-AC\n"; } }
server { listen 443 ssl; ssl_certificate /etc/nginx/ssl/web.crt; ssl_certificate_key /etc/nginx/ssl/web.key; location /health { return 200 "ok\n"; } location / { return 200 "web-01 TP-AC (https)\n"; } }
EOC
systemctl enable --now nginx; systemctl restart nginx
curl -sk https://localhost/
'@
$appScript = @'
mkdir -p /opt/tpac
cat > /opt/tpac/app.py <<'EOP'
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path in ('/health','/api/health','/') else 404)
        self.end_headers(); self.wfile.write(b'app-01 TP-AC ' + self.path.encode() + b'\n')
HTTPServer(('0.0.0.0', 8080), H).serve_forever()
EOP
cat > /etc/systemd/system/tpac-app.service <<'EOS'
[Unit]
Description=TP-AC app
[Service]
ExecStart=/usr/bin/python3 /opt/tpac/app.py
Restart=always
[Install]
WantedBy=multi-user.target
EOS
systemctl daemon-reload; systemctl enable --now tpac-app; sleep 1; curl -s localhost:8080/api/health
'@
"web: " + (Invoke-Ssm $s.web $webScript 180)
"app: " + (Invoke-Ssm $s.app $appScript 60)

# --- TP1 : Security Groups ---
# (AWS interdit les noms de groupe commencant par "sg-" : le nom logique est dans le tag Name)
$s.sgWeb = Aws ec2 create-security-group --group-name web-TP-AC --description 'TP-AC web' --vpc-id $s.vpc --tag-specifications (Tags 'security-group' 'sg-web-TP-AC') --query GroupId
$s.sgApp = Aws ec2 create-security-group --group-name app-TP-AC --description 'TP-AC app' --vpc-id $s.vpc --tag-specifications (Tags 'security-group' 'sg-app-TP-AC') --query GroupId
# 443 public ; 22 depuis la "salle d'exploitation" (plage de documentation 203.0.113.0/24, l'adresse reelle n'est pas fournie)
Aws ec2 authorize-security-group-ingress --group-id $s.sgWeb --ip-permissions 'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTPS public}]' 'IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=203.0.113.0/24,Description=Salle exploitation (plage doc)}]' | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions "IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=$($s.sgWeb),Description=API depuis sg-web}]" "IpProtocol=tcp,FromPort=22,ToPort=22,UserIdGroupPairs=[{GroupId=$($s.sgWeb),Description=SSH depuis sg-web}]" "IpProtocol=icmp,FromPort=-1,ToPort=-1,UserIdGroupPairs=[{GroupId=$($s.sgWeb),Description=ping diagnostic depuis sg-web}]" | Out-Null
Aws ec2 modify-instance-attribute --instance-id $s.web --groups $s.sgWeb
Aws ec2 modify-instance-attribute --instance-id $s.app --groups $s.sgApp
Save-State $s

# --- TP2 : NACL de sous-reseau public (sans etat) ---
$newNacl = -not $s.naclPublic
if ($newNacl) { $s.naclPublic = Aws ec2 create-network-acl --vpc-id $s.vpc --tag-specifications (Tags 'network-acl' 'nacl-public-TP-AC') --query NetworkAcl.NetworkAclId }
function Nacl($num,$egress,$proto,$cidr,$from,$to,$action='allow') {
  $a = @('ec2','create-network-acl-entry','--network-acl-id',$s.naclPublic,'--rule-number',$num,'--protocol',$proto,'--cidr-block',$cidr,'--rule-action',$action)
  if ($egress) { $a += '--egress' } else { $a += '--ingress' }
  if ($from) { $a += @('--port-range',"From=$from,To=$to") }
  Aws @a
}
if ($newNacl) {
  Nacl 100 $false 6 0.0.0.0/0 443 443
  Nacl 110 $false 6 0.0.0.0/0 1024 65535
  Nacl 120 $false -1 10.20.0.0/22 $null $null
  Nacl 100 $true 6 0.0.0.0/0 443 443
  Nacl 110 $true 6 0.0.0.0/0 1024 65535
  Nacl 120 $true -1 10.20.0.0/22 $null $null
}
$q = 'NetworkAcls[0].Associations[?SubnetId==`' + $s.subPublic + '`].NetworkAclAssociationId'
$assoc = Aws ec2 describe-network-acls --filters "Name=vpc-id,Values=$($s.vpc)" "Name=association.subnet-id,Values=$($s.subPublic)" --query $q
Aws ec2 replace-network-acl-association --association-id $assoc --network-acl-id $s.naclPublic | Out-Null
Save-State $s
$s | ConvertTo-Json
