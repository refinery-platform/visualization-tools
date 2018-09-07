# QA Process

## Create stack
[Follow the directions](https://github.com/refinery-platform/refinery-platform/wiki/AWS-deployment) to bring up the stack.
After the first-time initialization and creation of a virtual environment it should run like this:
```bash
NAME=vis-qa
source activate refinery-deploy

cd refinery-platform/deployment/terraform/live/
terraform workspace select default
terraform workspace delete -force $NAME
# ... but ideally it would be clean and not need -force? 
terraform workspace new $NAME
TF_LOG=DEBUG terraform apply

# Needs to be run from the terraform directory to fill in the template:
erb ../../aws-config/config.yaml.erb > ../../aws-config/config.yaml

cd ../..
perl -i -pne '$_="ADMIN_PASSWORD: admin-password" if /ADMIN_PASSWORD:/' aws-config/config.yaml
perl -i -pne '$_="SSH_USERS: mccalluc jkmarx scottx611x hackdna" if /SSH_USERS:/' aws-config/config.yaml
python stack.py create

# Wait for it to complete:
while true; do aws cloudformation describe-stacks --stack-name $NAME --query 'Stacks[*].[StackStatus]' --output text; sleep 2; done
```
... or keep an eye on the [AWS console](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks?filter=active).

Update DNS: (Because of a virtual host setting or something like that, you can not hit the server directly:
It needs to have the right hostname and go through ELB.)
```bash
ELB_DNS=dualstack.`aws elb describe-load-balancers --load-balancer-names $NAME --query 'LoadBalancerDescriptions[*].DNSName' --output text`
ZONE_ID=`aws elb describe-load-balancers --load-balancer-names $NAME --query 'LoadBalancerDescriptions[*].CanonicalHostedZoneNameID' --output text`
echo '{"Changes": [{"Action": "UPSERT", "ResourceRecordSet": {"Name": "'$NAME'.cloud.refinery-platform.org", "Type": "A", "AliasTarget": {"HostedZoneId": "'$ZONE_ID'", "DNSName": "'$ELB_DNS'", "EvaluateTargetHealth": false}}}]}' > /tmp/dns.json
aws route53 change-resource-record-sets --hosted-zone-id Z1D2YVM2HNPAQB --change-batch file:///tmp/dns.json
```
(Note that this uses two different Zone IDs: on the commandline, it the zone for our own apex domain, which is different from the domain for the ELB DNS.)

## Set up
At this point, puppet may still be running. Log in, tail the log, and wait for `Cloud-init v. x.y.z finished`:
```bash
IP=`aws ec2 describe-instances  --filters Name=tag:Name,Values=$NAME --query 'Reservations[].Instances[].PublicIpAddress' --output=text`
ssh -i ~/.ssh/mccalluc.pem ubuntu@$IP
tail -f /var/log/cloud-init-output.log
```

After puppet completes, create a user account on the instance:
```
cd /srv/refinery-platform/refinery
workon refinery-platform
USERNAME=vis-qa
./manage.py create_user $USERNAME $USERNAME-password mccallucc@gmail.com first last hms True
```

Install tools:
```bash
# Continue in ssh...
# TODO: List from branch, and load from branch.
GIT_API_URL=https://api.github.com/repos/refinery-platform/visualization-tools/contents/tool-annotations
TOOLS=`python -c 'import requests; print(" ".join([tool["name"].replace(".json","") for tool in requests.get("'$GIT_API_URL'").json()]))'`
./manage.py load_tools --visualizations $TOOLS
```

Load sample data:

TODO: Do it in the UI until https://github.com/refinery-platform/refinery-platform/issues/2946 is fixed

```bash
# Continue in ssh...
wget https://raw.githubusercontent.com/refinery-platform/visualization-tools/master/vis-qa-data.csv
./manage.py process_metadata_table --username vis-qa --title vis-qa-data --file_name vis-qa-data.csv --source_column_index 1 --data_file_column 0 --delimiter comma
```

## Do the QA

Visit http://vis-qa.cloud.refinery-platform.org/ and login with `vis-qa`/`vis-qa-password`.

For each tool:
- Load all the appropriate data.
- Excercise all the functionality.
- Load some inappropriate data and make sure it fails gracefully.

If there are problems...
- regressions from the currently deployed state need to be fixed before release
- but other bugs can just be filed, probably in the repo for the appropriate tool.

## Destroy stack

```bash
aws cloudformation delete-stack --stack-name vis-qa
while aws cloudformation describe-stacks --stack-name vis-qa > /dev/null; do echo 'still up'; sleep 10; done
for ID in `aws ec2 describe-snapshots --filters Name=tag:aws:cloudformation:stack-name,Values=vis-qa --query 'Snapshots[].[SnapshotId]' --output=text`; do aws ec2 delete-snapshot --snapshot-id $ID; done
```
