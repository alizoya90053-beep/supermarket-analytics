"""
analysis.py  —  Step 4
========================
Group & Summarise: produce totals, counts and averages across every
analytical dimension.  Each function takes the clean DataFrame from
data_loader.py and returns a ready-to-display summary DataFrame.
"""

import pandas as pd


# ---------------------------------------------------------------------------
# 1. Scalar KPIs  (for header metric cards)
# ---------------------------------------------------------------------------
def overall_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_transactions" : len(df),
        "total_sales"        : round(float(df["Sales"].sum()), 2),
        "total_gross_income" : round(float(df["gross income"].sum()), 2),
        "total_units_sold"   : int(df["Quantity"].sum()),
        "total_tax"          : round(float(df["Tax 5%"].sum()), 2),
        "total_cogs"         : round(float(df["cogs"].sum()), 2),
        "avg_sales_per_txn"  : round(float(df["Sales"].mean()), 2),
        "avg_unit_price"     : round(float(df["Unit price"].mean()), 2),
        "avg_quantity"       : round(float(df["Quantity"].mean()), 2),
        "avg_rating"         : round(float(df["Rating"].mean()), 2),
    }


# ---------------------------------------------------------------------------
# 2. Sales formula sample table  (Step 3 display)
# ---------------------------------------------------------------------------
def sales_formula_sample(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Show Qty × Unit Price vs stored Sales for the first n rows."""
    cols = [
        "Invoice ID", "Branch", "Product line",
        "Quantity", "Unit price",
        "Sales_Calculated", "Sales_Original", "Sales_Diff",
    ]
    return (
        df[cols]
        .head(n)
        .rename(columns={
            "Sales_Calculated" : "Qty × Unit Price",
            "Sales_Original"   : "Original Sales",
            "Sales_Diff"       : "Difference",
        })
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 3. By Branch
# ---------------------------------------------------------------------------
def sales_by_branch(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Branch", as_index=False)
        .agg(
            Total_Sales        = ("Sales",        "sum"),
            Transactions       = ("Invoice ID",   "count"),
            Total_Units_Sold   = ("Quantity",     "sum"),
            Avg_Sales_per_Txn  = ("Sales",        "mean"),
            Avg_Qty_per_Txn    = ("Quantity",     "mean"),
            Avg_Unit_Price     = ("Unit price",   "mean"),
            Total_Gross_Income = ("gross income", "sum"),
            Avg_Rating         = ("Rating",       "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 4. By Product Line
# ---------------------------------------------------------------------------
def sales_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product line", as_index=False)
        .agg(
            Total_Sales        = ("Sales",      "sum"),
            Transactions       = ("Invoice ID", "count"),
            Total_Units_Sold   = ("Quantity",   "sum"),
            Avg_Unit_Price     = ("Unit price", "mean"),
            Avg_Sales_per_Txn  = ("Sales",      "mean"),
            Avg_Rating         = ("Rating",     "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 5. By Customer Type
# ---------------------------------------------------------------------------
def sales_by_customer_type(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Customer type", as_index=False)
        .agg(
            Total_Sales       = ("Sales",      "sum"),
            Transactions      = ("Invoice ID", "count"),
            Total_Units_Sold  = ("Quantity",   "sum"),
            Avg_Sales_per_Txn = ("Sales",      "mean"),
            Avg_Rating        = ("Rating",     "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 6. By Gender
# ---------------------------------------------------------------------------
def sales_by_gender(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Gender", as_index=False)
        .agg(
            Total_Sales       = ("Sales",      "sum"),
            Transactions      = ("Invoice ID", "count"),
            Total_Units_Sold  = ("Quantity",   "sum"),
            Avg_Sales_per_Txn = ("Sales",      "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 7. By Payment Method
# ---------------------------------------------------------------------------
def sales_by_payment(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Payment", as_index=False)
        .agg(
            Total_Sales       = ("Sales",      "sum"),
            Transactions      = ("Invoice ID", "count"),
            Avg_Sales_per_Txn = ("Sales",      "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 8. Monthly Trend
# ---------------------------------------------------------------------------
def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Month_num", "Month"], as_index=False)
        .agg(
            Total_Sales       = ("Sales",      "sum"),
            Transactions      = ("Invoice ID", "count"),
            Total_Units_Sold  = ("Quantity",   "sum"),
            Avg_Sales_per_Txn = ("Sales",      "mean"),
        )
        .round(2)
        .sort_values("Month_num")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 9. By Day of Week
# ---------------------------------------------------------------------------
def sales_by_day(df: pd.DataFrame) -> pd.DataFrame:
    ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    result = (
        df.groupby("Day_of_week", as_index=False)
        .agg(
            Total_Sales  = ("Sales",      "sum"),
            Transactions = ("Invoice ID", "count"),
            Avg_Sales    = ("Sales",      "mean"),
        )
        .round(2)
    )
    result["Day_of_week"] = pd.Categorical(result["Day_of_week"], categories=ORDER, ordered=True)
    return result.sort_values("Day_of_week").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 10. By Hour of Day
# ---------------------------------------------------------------------------
def sales_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Hour", as_index=False)
        .agg(
            Total_Sales  = ("Sales",      "sum"),
            Transactions = ("Invoice ID", "count"),
            Avg_Sales    = ("Sales",      "mean"),
        )
        .round(2)
        .sort_values("Hour")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 11. Product × Branch pivot  (heatmap source)
# ---------------------------------------------------------------------------
def product_branch_pivot(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pivot_table(index="Product line", columns="Branch",
                       values="Sales", aggfunc="sum")
        .round(2)
    )


# ---------------------------------------------------------------------------
# 12. Gender × Product Line
# ---------------------------------------------------------------------------
def gender_product_sales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Product line", "Gender"], as_index=False)["Sales"]
        .sum()
        .round(2)
        .sort_values("Sales", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 13. Rating by Product Line
# ---------------------------------------------------------------------------
def rating_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product line")["Rating"]
        .agg(Avg_Rating="mean", Min_Rating="min", Max_Rating="max", Reviews="count")
        .round(2)
        .reset_index()
        .sort_values("Avg_Rating", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 14. Full cross-tab summary  (totals + counts + averages in one table)
# ---------------------------------------------------------------------------
def full_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(
            ["Branch", "Product line", "Customer type", "Gender", "Payment"],
            as_index=False,
        )
        .agg(
            Total_Sales       = ("Sales",      "sum"),
            Transactions      = ("Invoice ID", "count"),
            Total_Units_Sold  = ("Quantity",   "sum"),
            Avg_Sales_per_Txn = ("Sales",      "mean"),
            Avg_Unit_Price    = ("Unit price", "mean"),
            Avg_Rating        = ("Rating",     "mean"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )
