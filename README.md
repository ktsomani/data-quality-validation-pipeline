# Data Validation Pipeline with Release-Readiness Checklist

Checks a CSV dataset for common data quality problems and produces a
release-readiness report that says what passed, what failed, and what must be
fixed before the data goes live.

## Run

```bash
pip install -r requirements.txt
python validate.py data/orders.csv --out report/
```

Outputs:
- `report/failures.csv`: every failing row with the rule that failed
- `report/RELEASE_CHECKLIST.md`: pass/fail summary and go/no-go decision

## Rules checked

| Rule                       | Column(s)        |
|----------------------------|------------------|
| Required field not null    | order_id, amount |
| No duplicate keys          | order_id         |
| Range check               | amount >= 0      |
| Allowed values            | status           |
| Referential match         | customer_id must exist in customers.csv |

## Sample data

`data/orders.csv` and `data/customers.csv` contain deliberate errors so the
checks have something to catch.

## Sample result

Running on the included data reports NO-GO with failures in six rules:
duplicate order IDs, a missing order ID, a missing amount, a negative amount,
an unrecognised status, and a customer ID that does not exist in the customer
table. Each failing row is listed in `report/failures.csv`.

## Project layout

- `validate.py`: rule checks and report generation
- `data/`: sample orders and customers with deliberate errors
- `report/`: generated outputs (not committed)
