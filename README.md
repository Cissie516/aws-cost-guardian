# aws-cost-guardian

# AWS Cost Guardian

An open-source tool that scans AWS accounts for cost waste and surfaces optimization opportunities.

## What it does

Cost Guardian connects to an AWS account and identifies common sources of cloud waste — unattached EBS volumes, idle Elastic IPs, oversized RDS instances, and more — then estimates the monthly dollar impact.

Built as a learning project to explore FinOps practices and the AWS SDK (Boto3), with the goal of growing into a Slack-integrated, scheduled report.

## Current capabilities (v0.1)

- Scans all EBS volumes in a given AWS region
- Identifies volumes in `available` state (i.e. not attached to any EC2 instance)
- Estimates monthly cost waste based on volume size and type (gp3, gp2, io1, io2, st1, sc1)
- Handles unknown volume types gracefully with a fallback price and warning

## Usage

```bash
pip install -r requirements.txt
aws configure  # if you haven't already
python3 scanners/ebs_scanner.py
```

Sample output:

```
[FOUND] vol-03123c1a10948f49c (100 GB, gp3, available since 2026-05-27) → $9.60/month wasted
[FOUND] vol-0fe55f215fe42ad19 (100 GB, gp3, available since 2026-05-27) → $9.60/month wasted

Total: 2 unattached volumes, $19.20/month potential savings.
```

## Roadmap

- [x] EBS unattached volume detection
- [ ] Idle Elastic IP detection
- [ ] Old EBS snapshot detection
- [ ] RDS oversizing analysis
- [ ] Slack notification integration
- [ ] Scheduled execution via AWS Lambda + EventBridge
- [ ] Infrastructure as Code (Terraform) deployment

## Tech stack

Python 3.13 · Boto3 · AWS EC2 API · (planned) AWS Lambda · EventBridge · Terraform

## Author

Built by Cissie ([@Cissie516](https://github.com/Cissie516)) as part of a cloud engineering learning journey.