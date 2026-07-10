import argparse

from scanners.ebs_scanner import scan as scan_ebs
from scanners.eip_scanner import scan as scan_eip


def main():
    parser = argparse.ArgumentParser(description="AWS Cost Guardian")
    parser.add_argument(
        "--region",
        default="ap-southeast-2",
        help="AWS region to scan"
    )
    args = parser.parse_args()

    print("=== EBS Volume Scanner ===")
    scan_ebs(region=args.region)

    print("\n" + "=" * 50 + "\n")

    print("=== Elastic IP Scanner ===")
    scan_eip(region=args.region)


if __name__ == "__main__":
    main()