# QA Process

## Create stack
[Follow the directions](https://github.com/refinery-platform/refinery-platform/wiki/AWS-deployment) to bring up the stack.
TODO: script this.

## Set up
Create a user account on the instance.

Install tools:
```
NAME=vis-qa
IP=`aws ec2 describe-instances  --filters Name=tag:Name,Values=$NAME --query 'Reservations[].Instances[].PublicIpAddress' --output=text`
ssh -i ~/.ssh/mccalluc.pem ubuntu@$IP
cd /srv/refinery-platform/refinery
workon refinery-platform
GIT_API_URL=https://api.github.com/repos/refinery-platform/visualization-tools/contents/tool-annotations
TOOLS=`python -c 'import requests; print(" ".join([tool["name"].replace(".json","") for tool in requests.get("'$GIT_API_URL'").json()]))'`
./manage.py load_tools --visualizations $TOOLS
```

Load sample data.

## Do the QA

## Destroy stack
