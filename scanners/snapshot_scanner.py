"""
Snapshot Scanner

Scans all EBS snapshots in a given AWS region and identifies snapshots
that may be wasting money because they are orphaned or very old.
"""

import boto3
import argparse
from datetime import datetime, timezone

SNAPSHOT_PRICE_PER_GB_MONTH = 0.055


def get_ec2_client(region: str):
    """Create and return a boto3 EC2 client for the given region."""
    return boto3.client("ec2", region_name=region)


def list_own_snapshots(ec2_client):
    """
    Fetch all snapshots owned by the current AWS account.
    """
    response = ec2_client.describe_snapshots(OwnerIds=["self"])
    return response["Snapshots"]


def is_orphaned(snapshot: dict, existing_volume_ids: set) -> bool:
    """
    Return True if the source volume no longer exists.
    """
    return snapshot.get("VolumeId") not in existing_volume_ids


def is_old(snapshot: dict, days_threshold: int = 90) -> bool:
    """
    Return True if the snapshot is older than the threshold.
    """
    age_days = (
        datetime.now(timezone.utc) - snapshot["StartTime"]
    ).days
    return age_days > days_threshold


def estimate_monthly_cost(snapshot: dict) -> float:
    """
    Estimate monthly storage cost.
    """
    size = snapshot.get("VolumeSize", 0)
    return size * SNAPSHOT_PRICE_PER_GB_MONTH


def scan(region: str = "ap-southeast-2"):
    """Main entry point. Scans, filters, prints a report and returns summary."""

    client = get_ec2_client(region)

    snapshots = list_own_snapshots(client)

    volumes = client.describe_volumes()["Volumes"]
    existing_volume_ids = {v["VolumeId"] for v in volumes}

    findings = []
    total_waste = 0.0

    for snapshot in snapshots:

        orphaned = is_orphaned(snapshot, existing_volume_ids)
        old = is_old(snapshot)

        if not (orphaned or old):
            continue

        cost = estimate_monthly_cost(snapshot)
        total_waste += cost

        snapshot_id = snapshot.get("SnapshotId")
        volume_size = snapshot.get("VolumeSize", 0)
        created_date = snapshot["StartTime"].strftime("%Y-%m-%d")
        age_days = (
            datetime.now(timezone.utc) - snapshot["StartTime"]
        ).days

        if orphaned and old:
            finding_type = "orphaned + old"

            print(
                f"[ORPHANED + OLD] {snapshot_id} "
                f"({volume_size} GB, created {created_date}, "
                f"{age_days} days old, volume no longer exists) "
                f"→ ${cost:.2f}/month wasted"
            )

        elif orphaned:
            finding_type = "orphaned"

            print(
                f"[ORPHANED] {snapshot_id} "
                f"({volume_size} GB, created {created_date}, "
                f"volume no longer exists) "
                f"→ ${cost:.2f}/month wasted"
            )

        else:
            finding_type = "old"

            print(
                f"[OLD] {snapshot_id} "
                f"({volume_size} GB, created {created_date}, "
                f"{age_days} days old) "
                f"→ ${cost:.2f}/month wasted"
            )

        findings.append(
            {
                "type": finding_type,
                "snapshot_id": snapshot_id,
                "volume_id": snapshot.get("VolumeId"),
                "volume_size": volume_size,
                "created": created_date,
                "age_days": age_days,
                "cost": cost,
            }
        )

    print(
        f"\nTotal: {len(findings)} snapshots to review, "
        f"${total_waste:.2f}/month potential savings."
    )

    return {
        "count": len(findings),
        "total_cost": total_waste,
        "findings": findings,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan AWS for orphaned or old EBS snapshots"
    )
    parser.add_argument(
        "--region",
        default="ap-southeast-2",
        help="AWS region to scan",
    )
    args = parser.parse_args()

    scan(region=args.region)