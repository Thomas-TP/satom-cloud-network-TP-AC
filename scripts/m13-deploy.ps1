# Module 13 - Deploiement en UNE commande : certificat auto-signe (si absent) + stack complete.
# Usage : pwsh scripts/m13-deploy.ps1 [-Env prod|dev] [-Cidr 10.30.0.0/22] [-Stack stack-portail-leman-TP-AC]
# Prerequis : profil AWS CLI TP-AC connecte (aws login), openssl (Git for Windows). Aucune autre etape manuelle.
param([ValidateSet('prod','dev')][string]$Env = 'prod', [string]$Cidr = '10.30.0.0/22', [string]$Stack = 'stack-portail-leman-TP-AC')
$ErrorActionPreference = 'Stop'
$aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'; $p = @('--profile','TP-AC','--region','eu-north-1')
# 1. certificat auto-signe importe dans ACM (la cle privee n'est jamais conservee)
$cert = & $aws acm list-certificates --query "CertificateSummaryList[?DomainName=='portefeuilles.leman-finance.example'].CertificateArn | [0]" --output text @p
if (-not $cert -or $cert -eq 'None') {
  $ossl = 'C:\Program Files\Git\usr\bin\openssl.exe'; $cd = Join-Path $env:TEMP 'tpac-cert-deploy'; New-Item -ItemType Directory -Force $cd | Out-Null
  & $ossl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout "$cd\k.pem" -out "$cd\c.pem" -subj '/CN=portefeuilles.leman-finance.example' -addext 'subjectAltName=DNS:portefeuilles.leman-finance.example' 2>$null
  $cert = & $aws acm import-certificate --certificate "fileb://$cd\c.pem" --private-key "fileb://$cd\k.pem" --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' --query CertificateArn --output text @p
  Remove-Item $cd -Recurse -Force
}
# 2. stack
& $aws cloudformation deploy --stack-name $Stack --template-file "$PSScriptRoot\..\cfn\reseau-leman.yaml" --capabilities CAPABILITY_IAM `
  --parameter-overrides "Environnement=$Env" "CidrVpc=$Cidr" "CertificateArn=$cert" --tags 'Projet=SatomCloudNetwork' 'Equipe=TP-AC' "Environnement=$Env" @p
& $aws cloudformation describe-stacks --stack-name $Stack --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output table @p
