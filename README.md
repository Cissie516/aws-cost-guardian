# AWS Cost Guardian

> An open-source FinOps tool that scans AWS accounts for cost waste and surfaces actionable optimization opportunities.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Boto3-orange.svg)](https://boto3.amazonaws.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What it does

Cloud spend is one of the largest, fastest-growing line items in modern engineering budgets — and a surprising amount of it goes to forgotten resources: detached EBS volumes, idle Elastic IPs, oversized RDS instances, orphaned snapshots.

**Cost Guardian** scans an AWS account for these common waste patterns, estimates the monthly dollar impact, and produces a readable report. It is designed to grow into a scheduled, Slack-integrated tool that runs serverlessly on Lambda.

## Current capabilities (v0.1)

- Scans all EBS volumes in a given AWS region via the EC2 API
- Identifies volumes in `available` state (i.e. not attached to any EC2 instance)
- Estimates monthly waste based on volume size and type (`gp3`, `gp2`, `io1`, `io2`, `st1`, `sc1`, `standard`)
- Gracefully handles unknown volume types with a configurable fallback price and warning

## Sample output

```text
[FOUND] vol-03123c1a10948f49c (100 GB, gp3, available since 2026-05-27) → $9.60/month wasted
[FOUND] vol-0fe55f215fe42ad19 (100 GB, gp3, available since 2026-05-27) → $9.60/month wasted
[FOUND] vol-0dcafc2e2df668100 (100 GB, gp3, available since 2026-05-27) → $9.60/month wasted

Total: 3 unattached volumes, $28.80/month potential savings.
```

## Prerequisites

Before running Cost Guardian, you need:

- **Python 3.10 or higher** ([download](https://www.python.org/downloads/))
- **An AWS account** with at least one EBS volume (a free-tier account works fine)
- **AWS CLI v2 installed** ([install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- **An IAM user with programmatic access** (Access Key ID + Secret Access Key)
- **Required IAM permissions** — see the [IAM Policy](#iam-policy) section below

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Cissie516/aws-cost-guardian.git
cd aws-cost-guardian
```

### 2. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure AWS credentials

If you haven't configured the AWS CLI before:

```bash
aws configure
```

You'll be prompted for:

- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g. `ap-southeast-2`)
- Default output format (`json` recommended)

Verify the setup:

```bash
aws sts get-caller-identity
```

You should see your account ID, user ID, and ARN.

## Usage

Run the EBS volume scanner:

```bash
python3 scanners/ebs_scanner.py
```

By default, the scanner targets the `ap-southeast-2` region. To scan a different region, modify the `scan()` call in `scanners/ebs_scanner.py`:

```python
if __name__ == '__main__':
    scan(region='us-east-1')
```

> **Coming in v0.2:** command-line `--region` argument so you don't need to edit code.

## IAM Policy

Cost Guardian follows the **principle of least privilege**. Do **not** give it `AdministratorAccess` in production. Instead, attach this minimal policy to the IAM user or role running the scanner:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVolumes"
      ],
      "Resource": "*"
    }
  ]
}
```

As more scanners are added (Elastic IPs, snapshots, RDS), this policy will be extended with additional read-only actions such as `ec2:DescribeAddresses`, `ec2:DescribeSnapshots`, and `rds:DescribeDBInstances`.

## Pricing assumptions

The scanner uses hard-coded prices per GB-month, based on AWS public pricing for the **`ap-southeast-2`** (Sydney) region as of **27th May 2026**

| Volume type | Price (USD/GB-month) |
|-------------|----------------------|
| gp3         | $0.096               |
| gp2         | $0.12                |
| io1 / io2   | $0.157               |
| st1         | $0.054               |
| sc1         | $0.018               |
| standard    | $0.08                |

Prices change. Verify against the [official EBS pricing page](https://aws.amazon.com/ebs/pricing/) before relying on the cost figures for budgeting.

## Roadmap

- [x] EBS unattached volume detection
- [x] Command-line `--region` argument (v0.2)
- [x] Idle Elastic IP detection
- [ ] Old / orphaned EBS snapshot detection
- [ ] Oversized RDS instance analysis
- [x] Slack notification integration
- [x] Scheduled execution on AWS Lambda + EventBridge
- [ ] Terraform module for one-command deployment
- [ ] Multi-account scanning via IAM role assumption

## Tech stack

- **Python 3.13** — primary language
- **Boto3** — AWS SDK for Python
- **AWS EC2 API** — for volume inventory
- *(Planned)* **AWS Lambda**, **EventBridge**, **SNS** / **Slack Webhooks**, **Terraform**

## Project structure

```
aws-cost-guardian/
├── scanners/
│   └── ebs_scanner.py        # EBS volume scanner
├── requirements.txt          # Python dependencies
├── README.md                 # You are here
└── .gitignore
```

## Contributing

This is a personal learning project, but feedback and ideas are welcome — feel free to open an issue.

## License

MIT — see [LICENSE](LICENSE) for details.

## Author

Built by **Cissie Chen** ([@Cissie516](https://github.com/Cissie516)) as part of a hands-on cloud engineering learning journey.

This project is also documented in a series of blog posts — *coming soon*.