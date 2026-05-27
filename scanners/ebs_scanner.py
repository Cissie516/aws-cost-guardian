"""
EBS Volume Scanner
Scans all EBS volumes in a given AWS region and identifies unattached ones
that are wasting money.
"""

import boto3
import json
from datetime import datetime, timezone

# Pricing reference (ap-southeast-2, as of May 2026)
# Source: https://aws.amazon.com/ebs/pricing/

EBS_PRICE_PER_GB_MONTH = {
    'gp3': 0.096,
    'gp2': 0.12,
    'io1': 0.157,
    'io2': 0.157,
    'st1': 0.054,
    'sc1': 0.018,
    'standard': 0.08,  # legacy magnetic
}


def get_ec2_client(region: str):
    """Create and return a boto3 EC2 client for the given region."""
    return boto3.client('ec2', region_name=region)


def list_all_volumes(ec2_client):
    """
    Fetch all EBS volumes in the account/region.
    Returns a list of volume dicts as returned by the AWS API.
    """
    response = ec2_client.describe_volumes()
    return response['Volumes']


def is_unattached(volume: dict) -> bool:
    """
    Return True if the volume is not attached to any instance.
    A volume's State is 'available' when it exists but is not attached.
    """
    return volume.get("State") == "available"


def estimate_monthly_cost(volume: dict) -> float:
    """
    Estimate the monthly cost (USD) of this volume based on its
    size (GB) and volume type.
    """
    size = volume.get("Size", 0)
    volume_type = volume.get("VolumeType")

    # Fallback to a default price if an unknown volume type appears,
    # so the scanner keeps running while alerting on coverage gaps.
    price_per_gb = EBS_PRICE_PER_GB_MONTH.get(volume_type)
    if price_per_gb is None:
        print(f"[WARN] Unknown volume type '{volume_type}', using default $0.10/GB")
        price_per_gb = 0.10

    return size * price_per_gb


def scan(region: str = 'ap-southeast-2'):
    """Main entry point. Scans, filters, and prints a report."""
    client = get_ec2_client(region)
    volumes = list_all_volumes(client)

    unattached = []
    total_waste = 0.0

    for vol in volumes:
        if is_unattached(vol):
            cost = estimate_monthly_cost(vol)
            unattached.append((vol, cost))
            total_waste += cost
            volume_id = vol.get("VolumeId")
            size = vol.get("Size")
            volume_type = vol.get("VolumeType")
            create_time = vol.get("CreateTime")

            # Convert datetime object to YYYY-MM-DD
            created_date = create_time.strftime("%Y-%m-%d") if create_time else "unknown"

            print(
                f"[FOUND] {volume_id} "
                f"({size} GB, {volume_type}, available since {created_date}) "
                f"→ ${cost:.2f}/month wasted"
            )

    print(
        f"\nTotal: {len(unattached)} unattached volumes, "
        f"${total_waste:.2f}/month potential savings."
    )

if __name__ == '__main__':
    scan()