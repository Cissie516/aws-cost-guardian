"""
EIP Scanner
Scans all Elastic IPs in a given AWS region and identifies idle ones
that are wasting money.
"""

import boto3
import argparse

IDLE_EIP_COST_PER_MONTH = 0.005 * 24 * 30  # $3.60/month


def get_ec2_client(region: str):
    """Create and return a boto3 EC2 client for the given region."""
    return boto3.client('ec2', region_name=region)


def list_all_eips(ec2_client):
    """Fetch all Elastic IPs in the account/region."""
    response = ec2_client.describe_addresses()
    return response["Addresses"]


def is_idle(eip: dict) -> bool:
    """Return True if the Elastic IP is not associated with an EC2 instance."""
    return eip.get("InstanceId") is None


def scan(region: str = "ap-southeast-2"):
    """Main entry point. Scans, filters, and prints a report."""
    client = get_ec2_client(region)
    eips = list_all_eips(client)

    idle_eips = []
    total_waste = 0.0

    for eip in eips:
        if is_idle(eip):
            idle_eips.append(eip)
            total_waste += IDLE_EIP_COST_PER_MONTH

            public_ip = eip.get("PublicIp")
            allocation_id = eip.get("AllocationId")

            print(
                f"[FOUND] {public_ip} "
                f"(AllocationId: {allocation_id}, idle) "
                f"→ ${IDLE_EIP_COST_PER_MONTH:.2f}/month wasted"
            )

    print(
        f"\nTotal: {len(idle_eips)} idle Elastic IPs, "
        f"${total_waste:.2f}/month potential savings."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan AWS for idle Elastic IPs")
    parser.add_argument(
        "--region",
        default="ap-southeast-2",
        help="AWS region to scan",
    )
    args = parser.parse_args()
    scan(region=args.region)