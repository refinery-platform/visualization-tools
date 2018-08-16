# QA Process

## Create stack
[Follow the directions](https://github.com/refinery-platform/refinery-platform/wiki/AWS-deployment) to bring up the stack.
TODO: script this.

## Set up
Create a user account on the instance:
```bash
NAME=vis-qa
IP=`aws ec2 describe-instances  --filters Name=tag:Name,Values=$NAME --query 'Reservations[].Instances[].PublicIpAddress' --output=text`
ssh -i ~/.ssh/mccalluc.pem ubuntu@$IP
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
