#!/bin/bash
# Affiche : quota, vCPU utilises par les instances en cours (toute la classe), statut de la demande. Code retour 0 si on peut lancer nos 2 t3.micro (4 vCPU).
P="--profile TP-AC --region eu-north-1"
Q=$(aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A $P --query Quota.Value --output text 2>/dev/null); Q=${Q%.*}
S=$(aws service-quotas list-requested-service-quota-change-history-by-quota --service-code ec2 --quota-code L-1216C47A $P --query "RequestedQuotas[0].Status" --output text 2>/dev/null)
USED=$(aws ec2 describe-instances --filters Name=instance-state-name,Values=running,pending $P --query "Reservations[].Instances[].InstanceType" --output text 2>/dev/null | tr '\t' '\n' | python -c "
import sys
v={'t3.micro':2,'t3.nano':2,'t3.small':2,'t3.medium':2,'t3.large':2,'t3a.micro':2,'t2.micro':1,'t2.nano':1,'t2.small':1,'t2.medium':2}
print(sum(v.get(l.strip(),2) for l in sys.stdin if l.strip()))")
echo "quota=$Q utilises=$USED demande=$S"
[ -n "$Q" ] && [ -n "$USED" ] && [ $((USED + 4)) -le "$Q" ]
