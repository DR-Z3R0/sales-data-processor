# Sales Data Cleaning & Analysis Script

## Project Overview
A Python-based data cleaning and analysis pipeline that processes messy sales CSV data, normalizes inconsistent fields, handles invalid entries, logs data quality issues, and generates summary reports.

This project simulates a lightweight ETL-style workflow where raw, inconsistent sales data must be validated and cleaned before analysis.

It demonstrates practical data processing, error handling, and structured logging commonly used in QA and backend automation tasks.

Key features:
- Normalizes dates, customer names, amounts, and statuses.
- Skips rows with invalid amounts.
- Calculates summary statistics:
  - Number of completed orders
  - Total completed sales amount
  - Average completed order value
  - Number of pending orders
  - Number of refunds
- Logs warnings and errors to a separate log file.

## Why This Exists
This project simulates a lightweight ETL-style data cleaning pipeline for a real-world scenario where raw sales data may contain missing, inconsistent, or malformed values that must be cleaned before analysis.

## Example

### Input (`sales_data.csv`)
```csv
order_id,date,customer,amount,status
1001,2024-01-02,John Smith,120.50,Completed
1002,invalid_date,,NaN,Pending
1003,02/16/2024,,96.66,Pending
1004,,Nina Jones,18.60,Completed
```

### Output (Terminal)
```text
===== Sales Summary Report =====

Completed Orders:
  Count                         : 2
  Total Amount                  : $139.10
  Average Order Value           : $69.55

Other Statuses:
  Pending Orders                : 1
  Refunds                       : 0

================================
```

### Output File (`cleaned_sales.csv`)
```csv
order_id,date,customer,amount,status
1001,2024-01-02,John Smith,120.5,Completed
1003,2024-02-16,Unknown,96.66,Pending
1004,Unknown,Nina Jones,18.6,Completed
```

## Error Handling

If a row contains invalid data:

- invalid amount -> row skipped
- invalid date -> replaced with "Unknown"
- missing customer -> replaced with "Unknown"

All issues are logged to `data_warnings.log`.

## Requirements

- **Python**: 3.10+
- **Libraries**:
  - `pandas`
- Standard library modules (`csv`, `sys`, `logging`, `typing`) are included with Python.

All third-party dependencies are listed in `requirements.txt`.

## Setup Instructions

1. **Create a virtual environment (optional but recommended)**

```bash
python -m venv venv
# Activate the environment:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Ensure your input CSV file is named `sales_data.csv` or update the `INPUT_FILE` variable in the script**

## Running the Script

Run the script from the terminal:

```bash
python process_sales.py
```

When executed, the script will:
- Read `sales_data.csv`
- Normalize and clean the data
- Print a summary report in the terminal
- Save cleaned data to `cleaned_sales.csv`
- Log warnings to `data_warnings.log`

## Output Files

- `cleaned_sales.csv` = Cleaned version of your sales data.
- `data_warnings.log` = Log file with warnings for missing or invalid data.

## Customization

You can modify the following configuration variables at the top of the script:

| Variable            | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `INPUT_FILE`        | Path to the input CSV file                                         |
| `OUTPUT_FILE`       | Path to save the cleaned CSV                                       |
| `WARNINGS_LOG_FILE` | Path to save warnings and errors                                   |
| `DEFAULT_COLS`      | Column names to use if input CSV has no header                     |
| `VALID_STATUSES`    | Set of allowed order statuses (`Completed`, `Pending`, `Refunded`) |
| `LABEL_WIDTH`       | Fixed width of the summary's left-hand column                      |

## Notes

- The script automatically handles missing or malformed data and logs any warnings.
- Rows with invalid amounts are skipped to ensure clean reporting.
- The script uses pandas for CSV reading, date handling, and data manipulation.

## Troubleshooting

- **ModuleNotFoundError for pandas**: Make sure you installed dependencies with pip install -r requirements.txt.
- **Python version error**: Ensure you are using Python 3.10 or higher.
- **Permission errors**: Check that the script has write access to the output and log files.
