import os
import json
import urllib.request

from scanners.ebs_scanner import scan as scan_ebs
from scanners.eip_scanner import scan as scan_eip
from scanners.snapshot_scanner import scan as scan_snapshots
from scanners.rds_scanner import scan as scan_rds


def send_slack_message(message: str):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
   
    if not webhook_url:
        print("[WARN] SLACK_WEBHOOK_URL not set, skipping Slack notification")
        return

    payload = json.dumps({"text": message}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        urllib.request.urlopen(req)
        print("[INFO] Slack notification sent successfully")
    except Exception as e:
        print(f"[ERROR] Failed to send Slack message: {e}")


def handler(event, context):
    print("=== AWS Cost Guardian Scan Started ===")

    ebs_result = scan_ebs(region="ap-southeast-2")

    print("\n" + "=" * 50 + "\n")

    eip_result = scan_eip(region="ap-southeast-2")
    print("\n" + "=" * 50 + "\n")
    
    snapshot_result = scan_snapshots(region="ap-southeast-2")
    print("\n" + "=" * 50 + "\n")
    rds_result = scan_rds(region="ap-southeast-2")
    
    

    total_savings = (
        ebs_result["total_cost"] +
        eip_result["total_cost"] +
        snapshot_result["total_cost"] +
        rds_result["total_cost"]
    )

    # Build Slack message
    message_lines = [
    "🔍 *AWS Cost Guardian Weekly Report*",
    "Region: ap-southeast-2",
    "",
    f"💾 *EBS Volumes*: {ebs_result['count']} unattached → ${ebs_result['total_cost']:.2f}/month",
    f"📍 *Elastic IPs*: {eip_result['count']} idle → ${eip_result['total_cost']:.2f}/month",
    f"📸 *Snapshots*: {snapshot_result['count']} to review → ${snapshot_result['total_cost']:.2f}/month",
    f"🗄️ *RDS Instances*: {rds_result['count']} oversized → ${rds_result['total_cost']:.2f}/month",
    "",
    f"💰 *Total estimated waste: ${total_savings:.2f}/month*",
]
    
    send_slack_message("\n".join(message_lines))

    print("\n=== AWS Cost Guardian Scan Completed ===")

    return {
        "statusCode": 200,
        "body": "Scan complete"
    }