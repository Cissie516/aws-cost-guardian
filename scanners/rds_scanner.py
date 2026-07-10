"""
RDS Scanner

Scans all RDS instances in a given AWS region and identifies oversized
instances based on average CPU utilization over the past 7 days.
"""

import argparse
from datetime import datetime, timezone, timedelta

import boto3

# Pricing reference (ap-southeast-2, On-Demand, as of 2026)

RDS_HOURLY_PRICE = {
    "db.t3.micro": 0.028,
    "db.t3.small": 0.056,
    "db.t3.medium": 0.112,
    "db.t3.large": 0.224,
    "db.r5.large": 0.240,
    "db.r5.xlarge": 0.480,
    "db.r5.2xlarge": 0.960,
}

HOURS_PER_MONTH = 24 * 30


def get_clients(region: str):
    """
    Create and return boto3 RDS and CloudWatch clients.
    """
    rds_client = boto3.client("rds", region_name=region)
    cw_client = boto3.client("cloudwatch", region_name=region)
    return rds_client, cw_client


def list_db_instances(rds_client):
    """
    Fetch all RDS instances in the account/region.
    """
    response = rds_client.describe_db_instances()
    return response["DBInstances"]


def get_avg_cpu(cw_client, db_id: str, days: int = 7):
    """
    Return the average CPU utilization over the past N days.
    Returns None if no CloudWatch data is available.
    """

    response = cw_client.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "DBInstanceIdentifier",
                "Value": db_id,
            }
        ],
        StartTime=datetime.now(timezone.utc) - timedelta(days=days),
        EndTime=datetime.now(timezone.utc),
        Period=86400,
        Statistics=["Average"],
    )

    datapoints = response["Datapoints"]

    if not datapoints:
        return None

    avg_cpu = sum(d["Average"] for d in datapoints) / len(datapoints)

    return avg_cpu


def is_oversized(avg_cpu: float, threshold: float = 10.0):
    """
    Return True if the average CPU utilization is below the threshold.
    """

    return avg_cpu < threshold


def estimate_monthly_cost(instance: dict):
    """
    Estimate the monthly running cost of an RDS instance.
    """

    instance_class = instance.get("DBInstanceClass")

    hourly_price = RDS_HOURLY_PRICE.get(instance_class)

    if hourly_price is None:
        print(
            f"[WARN] Unknown RDS instance class '{instance_class}', "
            "using default $0.10/hour"
        )
        hourly_price = 0.10

    return hourly_price * HOURS_PER_MONTH


def scan(region: str = "ap-southeast-2"):
    """
    Main entry point. Scans, filters, prints a report and returns summary.
    """

    rds_client, cw_client = get_clients(region)

    instances = list_db_instances(rds_client)

    findings = []
    total_waste = 0.0

    for instance in instances:

        db_id = instance["DBInstanceIdentifier"]

        avg_cpu = get_avg_cpu(cw_client, db_id)

        if avg_cpu is None:
            print(f"[INFO] Skipping {db_id} (no CloudWatch CPU metrics)")
            continue

        if not is_oversized(avg_cpu):
            continue

        cost = estimate_monthly_cost(instance)

        total_waste += cost

        instance_class = instance["DBInstanceClass"]

        print(
            f"[OVERSIZED] {db_id} "
            f"({instance_class}, avg CPU {avg_cpu:.1f}% over 7 days) "
            f"→ ${cost:.2f}/month, consider downsizing"
        )

        findings.append(
            {
                "db_instance_identifier": db_id,
                "instance_class": instance_class,
                "avg_cpu": round(avg_cpu, 2),
                "monthly_cost": round(cost, 2),
            }
        )

    print(
        f"\nTotal: {len(findings)} oversized instances, "
        f"${total_waste:.2f}/month potential savings."
    )

    return {
        "count": len(findings),
        "total_cost": total_waste,
        "findings": findings,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan AWS for oversized RDS instances"
    )

    parser.add_argument(
        "--region",
        default="ap-southeast-2",
        help="AWS region to scan",
    )

    args = parser.parse_args()

    scan(region=args.region)