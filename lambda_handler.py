from scanners.ebs_scanner import scan as scan_ebs
from scanners.eip_scanner import scan as scan_eip


def handler(event, context):
    print("=== AWS Cost Guardian Scan Started ===")

    scan_ebs(region="ap-southeast-2")

    print("\n" + "=" * 50 + "\n")

    scan_eip(region="ap-southeast-2")

    print("\n=== AWS Cost Guardian Scan Completed ===")

    return {
        "statusCode": 200,
        "body": "Scan complete"
    }