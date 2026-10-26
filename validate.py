"""Validate an orders CSV and produce a release-readiness report.

Usage:
    python validate.py data/orders.csv --out report/
"""
import argparse
import os

import pandas as pd

ALLOWED_STATUS = {"pending", "shipped", "delivered", "cancelled"}


def check(df, customers, rule, mask, column):
    """Return failing rows as a list of dicts tagged with the rule name."""
    bad = df[mask].copy()
    bad["rule"] = rule
    bad["column"] = column
    return bad[["order_id", "column", "rule"]]


def run_checks(orders, customers):
    failures = []

    failures.append(check(orders, customers, "required: order_id",
                          orders["order_id"].isna(), "order_id"))
    failures.append(check(orders, customers, "required: amount",
                          orders["amount"].isna(), "amount"))

    dup_mask = orders["order_id"].duplicated(keep=False) & orders["order_id"].notna()
    failures.append(check(orders, customers, "unique: order_id", dup_mask, "order_id"))

    failures.append(check(orders, customers, "range: amount >= 0",
                          orders["amount"] < 0, "amount"))

    failures.append(check(orders, customers, "allowed: status",
                          ~orders["status"].isin(ALLOWED_STATUS), "status"))

    missing_customer = ~orders["customer_id"].isin(customers["customer_id"])
    failures.append(check(orders, customers, "reference: customer_id exists",
                          missing_customer, "customer_id"))

    all_failures = pd.concat(failures, ignore_index=True)
    return all_failures


def write_report(orders, failures, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    failures.to_csv(os.path.join(out_dir, "failures.csv"), index=False)

    rules = failures.groupby("rule").size().reset_index(name="failing_rows")
    total_rules = 6
    failed_rules = len(rules)
    passed_rules = total_rules - failed_rules
    decision = "GO" if failed_rules == 0 else "NO-GO"

    lines = [
        "# Release Readiness Checklist",
        "",
        f"- Rows checked: {len(orders)}",
        f"- Rules passed: {passed_rules} / {total_rules}",
        f"- Decision: **{decision}**",
        "",
        "## Failed rules",
        "",
    ]
    if rules.empty:
        lines.append("None.")
    else:
        for _, row in rules.iterrows():
            lines.append(f"- {row['rule']}: {row['failing_rows']} row(s)")
    lines.append("")
    lines.append("## Required before release")
    lines.append("")
    lines.append("- Fix every failing row listed in failures.csv, then re-run.")

    with open(os.path.join(out_dir, "RELEASE_CHECKLIST.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return decision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orders_csv")
    parser.add_argument("--customers", default="data/customers.csv")
    parser.add_argument("--out", default="report")
    args = parser.parse_args()

    orders = pd.read_csv(args.orders_csv)
    customers = pd.read_csv(args.customers)

    failures = run_checks(orders, customers)
    decision = write_report(orders, failures, args.out)
    print(f"Decision: {decision}. See {args.out}/RELEASE_CHECKLIST.md")


if __name__ == "__main__":
    main()
