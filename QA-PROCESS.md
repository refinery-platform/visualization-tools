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
```bash
# Continue in ssh...
# TODO: Use commandline when the bug is fixed:
#
# Meanwhile, download this and load in the UI:
https://raw.githubusercontent.com/refinery-platform/visualization-tools/master/vis-qa-data.csv
```

## Do the QA

For each tool:
- Load all the appropriate data.
- Excercise all the functionality.
- Load some inappropriate data and make sure it fails gracefully.

If there are problems, are they regressions from the currently deployed state that need to be fixed before release, or are they just bugs to be filed?

## Destroy stack

TODO
