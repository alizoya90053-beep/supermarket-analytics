"""
data_loader.py  —  Steps 1, 2 & 3
===================================
Step 1  Collect & Load  : Read CSV from disk, inspect shape & column names.
Step 2  Data Cleaning   : Missing values, duplicates, type coercion,
                          invalid categories, negative numerics, bad dates.
Step 3  Sales Formula   : Recalculate  Sales = Quantity × Unit price
                          and flag any rows where the stored value differs.
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "supermarket_sales.csv")

# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------
ALLOWED_VALUES = {
    "Customer type": {"Member", "Normal"},
    "Gender"       : {"Male", "Female"},
    "Payment"      : {"Ewallet", "Cash", "Credit card"},
    "Product line" : {
        "Health and beauty",
        "Electronic accessories",
        "Home and lifestyle",
        "Sports and travel",
        "Food and beverages",
        "Fashion accessories",
    },
}

NUMERIC_COLS  = [
    "Unit price", "Quantity", "Tax 5%", "Sales",
    "cogs", "gross margin percentage", "gross income", "Rating",
]
POSITIVE_COLS = ["Unit price", "Quantity", "Sales", "cogs", "gross income", "Rating"]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def load_and_clean(path: str = DATA_PATH):
    """
    Load, clean and enrich the CSV.

    Returns
    -------
    df     : pd.DataFrame   Clean, enriched dataset.
    report : dict           Cleaning report consumed by the Streamlit UI.
    """

    # ── STEP 1 : COLLECT & LOAD ─────────────────────────────────────────────
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    original_rows = len(df)
    original_cols = list(df.columns)

    # ── STEP 2 : DATA CLEANING ──────────────────────────────────────────────

    # 2-A  Strip leading/trailing whitespace from every string cell
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 2-B  Capture missing values BEFORE any row is dropped
    missing_series = df.isnull().sum()
    missing_before = missing_series[missing_series > 0].to_dict()
    total_missing  = int(missing_series.sum())

    # 2-C  Drop rows that contain ANY missing value
    n_before             = len(df)
    df.dropna(inplace=True)
    missing_rows_dropped = n_before - len(df)

    # 2-D  Remove exact-duplicate Invoice IDs (keep first occurrence)
    n_before           = len(df)
    dup_ids            = df[df.duplicated("Invoice ID", keep=False)][["Invoice ID"]].drop_duplicates()
    df.drop_duplicates(subset=["Invoice ID"], keep="first", inplace=True)
    duplicates_dropped = n_before - len(df)

    # 2-E  Parse Date column; drop rows with unparseable dates
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    n_before             = len(df)
    df.dropna(subset=["Date"], inplace=True)
    bad_dates_dropped    = n_before - len(df)

    # 2-F  Cast numeric columns; drop rows with non-numeric values
    n_before = len(df)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=NUMERIC_COLS, inplace=True)
    non_numeric_dropped = n_before - len(df)

    # 2-G  Remove rows with negative values in columns that must be positive
    negative_found = {}
    for col in POSITIVE_COLS:
        n_neg = int((df[col] < 0).sum())
        if n_neg:
            negative_found[col] = n_neg
            df = df[df[col] >= 0].copy()

    # 2-H  Validate categorical columns against allowed value sets
    invalid_categories = {}
    for col, valid_set in ALLOWED_VALUES.items():
        bad_mask = ~df[col].isin(valid_set)
        n_bad    = int(bad_mask.sum())
        if n_bad:
            invalid_categories[col] = {
                "count" : n_bad,
                "values": sorted(df.loc[bad_mask, col].unique().tolist()),
            }
            df = df[~bad_mask].copy()

    # 2-I  Rating range check  (valid: 1 – 10)
    rating_oob = int(((df["Rating"] < 1) | (df["Rating"] > 10)).sum())
    if rating_oob:
        df = df[(df["Rating"] >= 1) & (df["Rating"] <= 10)].copy()

    # ── STEP 3 : CALCULATE  Sales = Quantity × Unit price ───────────────────
    df["Sales_Original"]   = df["Sales"].round(4)
    df["Sales_Calculated"] = (df["Quantity"] * df["Unit price"]).round(4)
    df["Sales_Diff"]       = (df["Sales_Calculated"] - df["Sales_Original"]).abs().round(4)

    mismatched_sales = int((df["Sales_Diff"] > 0.02).sum())

    # Use the formula value as the authoritative Sales figure
    df["Sales"] = df["Sales_Calculated"]

    # ── DERIVED COLUMNS for time analysis ───────────────────────────────────
    df["Month"]       = df["Date"].dt.month_name()
    df["Month_num"]   = df["Date"].dt.month
    df["Day_of_week"] = df["Date"].dt.day_name()
    df["Hour"]        = (
        pd.to_datetime(df["Time"], format="%I:%M:%S %p", errors="coerce").dt.hour
    )

    df.reset_index(drop=True, inplace=True)

    # ── CLEANING REPORT ──────────────────────────────────────────────────────
    report = {
        # Step 1
        "original_rows"       : original_rows,
        "original_cols"       : original_cols,
        # Step 2 – missing
        "missing_before"      : missing_before,
        "total_missing_cells" : total_missing,
        "missing_rows_dropped": missing_rows_dropped,
        # Step 2 – duplicates
        "duplicates_dropped"  : duplicates_dropped,
        "duplicate_ids"       : dup_ids["Invoice ID"].tolist() if not dup_ids.empty else [],
        # Step 2 – type errors
        "bad_dates_dropped"   : bad_dates_dropped,
        "non_numeric_dropped" : non_numeric_dropped,
        # Step 2 – value errors
        "negative_found"      : negative_found,
        "invalid_categories"  : invalid_categories,
        "rating_oob"          : rating_oob,
        # Step 3
        "mismatched_sales"    : mismatched_sales,
        # Summary
        "final_rows"          : len(df),
        "total_dropped"       : original_rows - len(df),
    }

    return df, report
