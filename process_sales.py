# ----------------------------------
# Imports
# ----------------------------------
import csv
import sys
import math
import logging
import pandas as pd
from typing import Any, Optional


# ----------------------------------
# Global Configurations
# ----------------------------------
INPUT_FILE = "sales_data.csv"
WARNINGS_LOG_FILE = "data_warnings.log"
OUTPUT_FILE = "cleaned_sales.csv"
DEFAULT_COLS = ["order_id", "date", "customer", "amount", "status"]
VALID_STATUSES = {"Completed", "Pending", "Refunded"}
LABEL_WIDTH = 30

logging.basicConfig(
    filename=WARNINGS_LOG_FILE,
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ----------------------------------
# Functions
# ----------------------------------
def is_csv_file(file_path: str) -> bool:
    return bool(file_path and file_path.endswith('.csv'))

def validate_configurations():
    configs = {
        "INPUT_FILE": {
            "value": INPUT_FILE,
            "validator": is_csv_file,
            "error_message": "Input file must be a non-empty CSV file"
        },
        "OUTPUT_FILE": {
            "value": OUTPUT_FILE,
            "validator": is_csv_file,
            "error_message": "Output file must be a non-empty CSV file"
        }
    }

    for config_name, config in configs.items():
        if not config["validator"](config["value"]):
            logging.error(config["error_message"])
            sys.exit(1)

def read_csv_file(file_path: str) -> list:
    with open(file_path, newline='') as csvfile:
        first_row = next(csv.reader(csvfile))

    # heuristic: check if first value is numeric (id)
    has_header = not first_row[0].isdigit()

    data_frame = pd.read_csv(
        file_path,
        names=DEFAULT_COLS if not has_header else None,
        header=0 if has_header else None,
        on_bad_lines="warn",
        usecols=range(len(DEFAULT_COLS))
    )

    return data_frame.to_dict(orient='records')

def normalize_date(date_val: Any, row_idx: int, customer: str = "not-given") -> str:
    dt = pd.to_datetime(date_val, errors="coerce")
    if pd.isna(dt):
        logging.warning(f"Row {row_idx}: Invalid date '{date_val}' for customer '{customer}' - set to 'Unknown'")
        return "Unknown"
    return dt.strftime("%Y-%m-%d")

def normalize_customer(customer_val: Any, row_idx: int) -> str:
    stripped_val = str(customer_val).strip()
    if stripped_val == "" or pd.isna(customer_val):
        logging.warning(f"Row {row_idx}: Missing customer name - set to 'Unknown'")
        return "Unknown"
    return stripped_val

def normalize_amount(amount_val: Any, row_idx: int, customer: str = "not-given") -> Optional[float]:
    try:
        amount = float(amount_val)
        if math.isnan(amount):
            logging.warning(f"Row {row_idx}: Amount is NaN for customer '{customer}' - skipping row")
            return None
        if amount < 0:
            logging.warning(f"Row {row_idx}: Negative amount '{amount_val}' for customer '{customer}'")
        return amount
    except ValueError:
        logging.warning(f"Row {row_idx}: Invalid amount '{amount_val}' for customer '{customer}' - skipping row")
        return None

def normalize_status(status_val: Any, row_idx: int, customer: str = "not-given") -> str:
    status_cap = str(status_val).capitalize()
    if status_cap in VALID_STATUSES:
        return status_cap
    else:
        logging.warning(f"Row {row_idx}: Invalid status '{status_val}' for customer '{customer}' - set to 'Unknown'")
        return "Unknown"

def normalize_all_data(data: list) -> list:
    cleaned = []

    for i, row in enumerate(data, start=1):
        new_row = row.copy()

        new_row["customer"] = customer = normalize_customer(new_row.get("customer", ""), i)
        amount = normalize_amount(new_row.get("amount", ""), i, customer=customer)
        if amount is None: continue
        new_row["amount"] = amount
        new_row["date"] = normalize_date(new_row.get("date", ""), i, customer=customer)
        new_row["status"] = normalize_status(new_row.get("status", ""), i, customer=customer)
        
        cleaned.append(new_row)
    
    return cleaned

def calculate_order_summary(summary: dict, order: dict) -> None:
    status = order.get("status")
    amount = order.get("amount")

    match status:
        case "Completed":
            summary["total_completed_amount"] += amount
            summary["completed_orders_count"] += 1
        case "Pending":
            summary["pending_count"] += 1
        case "Refunded":
            summary["refund_count"] += 1


def analyze_data(cleaned_data: list) -> dict:
    summary = {
        "total_completed_amount": 0,
        "completed_orders_count": 0,
        "refund_count": 0,
        "pending_count": 0,
        "average_order_value": 0.0
    }

    for order in cleaned_data:
        calculate_order_summary(summary, order)

    summary["average_order_value"] = (
        summary["total_completed_amount"] / summary["completed_orders_count"]
        if summary["completed_orders_count"] > 0 else 0
    )

    return summary

def print_summary(summary: dict) -> None:
    print("\n===== Sales Summary Report =====")

    fields = {
        "Completed Orders:": [
            ("Count", "completed_orders_count", "{}"),
            ("Total Amount", "total_completed_amount", "${:.2f}"),
            ("Average Order Value", "average_order_value", "${:.2f}")
        ],
        "Other Statuses:": [
            ("Pending Orders", "pending_count", "{}"),
            ("Refunds", "refund_count", "{}")
        ]
    }

    for group, field_list in fields.items():
        print(f"\n{group}")
        for label, key, format_str in field_list:
            print(f"  {label:<{LABEL_WIDTH}}: {format_str.format(summary[key])}")

    print("\n" + "="*32)

def save_cleaned_data(cleaned_data: list, output_file: str):
    data_frame = pd.DataFrame(cleaned_data)
    data_frame.to_csv(output_file, index=False)


# ----------------------------------
# Main Application
# ----------------------------------
if __name__ == "__main__":

    validate_configurations()

    try:
        sales_data = read_csv_file(INPUT_FILE)
        normalized_data = normalize_all_data(sales_data)

        summary = analyze_data(normalized_data)
        print_summary(summary)

        save_cleaned_data(normalized_data, OUTPUT_FILE)

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise
