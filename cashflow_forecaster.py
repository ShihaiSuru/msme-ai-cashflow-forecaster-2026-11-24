#!/usr/bin/env python3
"""
MSME AI Cash Flow Forecaster — Starter Script
==========================================
Simple, transparent tool for Indian MSMEs to:
- Calculate DSO, DPO, Cash Conversion Cycle
- Forecast cash position for next 90 days
- Estimate working capital gap

No external dependencies. Edit SAMPLE_INVOICES / SAMPLE_PAYABLES
or load from your own CSV for real use.

Date: 2026-11-24
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict

# ---------------------------------------------------------------------------
# Sample data — typical small manufacturing MSME (in INR)
# ---------------------------------------------------------------------------
SAMPLE_INVOICES = [
    {"invoice_id": "INV-001", "customer": "Large Corp A", "amount": 250000, "invoice_date": "2026-09-15", "due_date": "2026-11-14", "paid_date": None, "status": "open"},
    {"invoice_id": "INV-002", "customer": "Distributor B", "amount": 180000, "invoice_date": "2026-10-01", "due_date": "2026-11-30", "paid_date": "2026-11-20", "status": "paid"},
    {"invoice_id": "INV-003", "customer": "Retail Chain C", "amount": 320000, "invoice_date": "2026-10-20", "due_date": "2026-12-19", "paid_date": None, "status": "open"},
    {"invoice_id": "INV-004", "customer": "Govt Vendor", "amount": 450000, "invoice_date": "2026-08-10", "due_date": "2026-10-09", "paid_date": None, "status": "overdue"},
    {"invoice_id": "INV-005", "customer": "Local Buyer", "amount": 95000, "invoice_date": "2026-11-05", "due_date": "2026-12-05", "paid_date": None, "status": "open"},
]

SAMPLE_PAYABLES = [
    {"bill_id": "BILL-101", "supplier": "Raw Material Co", "amount": 120000, "due_date": "2026-11-30", "status": "open"},
    {"bill_id": "BILL-102", "supplier": "Logistics", "amount": 45000, "due_date": "2026-12-10", "status": "open"},
    {"bill_id": "BILL-103", "supplier": "Utilities", "amount": 18000, "due_date": "2026-11-25", "status": "paid"},
]

CURRENT_CASH = 85000  # Opening cash balance (INR)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def parse_date(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")

def days_between(start: str, end: str) -> int:
    return (parse_date(end) - parse_date(start)).days

def calculate_dso(invoices: List[Dict], as_of: str = "2026-11-24") -> float:
    """Days Sales Outstanding — weighted average of open receivables."""
    total_open = 0.0
    weighted_days = 0.0
    as_of_dt = parse_date(as_of)
    for inv in invoices:
        if inv["status"] in ("open", "overdue") and not inv.get("paid_date"):
            amount = inv["amount"]
            age = (as_of_dt - parse_date(inv["invoice_date"])).days
            total_open += amount
            weighted_days += amount * age
    if total_open == 0:
        return 0.0
    return weighted_days / total_open

def calculate_dpo(payables: List[Dict], as_of: str = "2026-11-24") -> float:
    """Simple DPO proxy from open payables."""
    total_open = sum(p["amount"] for p in payables if p["status"] == "open")
    if total_open == 0:
        return 0.0
    # Approximate using due dates; in production use actual payment history
    return 30.0  # Conservative default for MSME suppliers

def forecast_cash(invoices: List[Dict], payables: List[Dict], current_cash: float, days: int = 90) -> Dict:
    """Simple daily cash forecast assuming collection on due date (optimistic)."""
    today = parse_date("2026-11-24")
    cash_by_day = defaultdict(float)
    cash_by_day[0] = current_cash

    # Expected inflows (open invoices collected on due date)
    for inv in invoices:
        if inv["status"] in ("open", "overdue") and not inv.get("paid_date"):
            due = parse_date(inv["due_date"])
            delta = (due - today).days
            if 0 <= delta <= days:
                cash_by_day[delta] += inv["amount"]

    # Expected outflows
    for bill in payables:
        if bill["status"] == "open":
            due = parse_date(bill["due_date"])
            delta = (due - today).days
            if 0 <= delta <= days:
                cash_by_day[delta] -= bill["amount"]

    # Running cash position
    running = current_cash
    min_cash = current_cash
    positions = []
    for d in range(days + 1):
        running += cash_by_day.get(d, 0)
        positions.append({"day": d, "cash": running})
        if running < min_cash:
            min_cash = running

    gap = abs(min(0, min_cash))  # Working capital needed if cash goes negative
    return {
        "forecast_days": days,
        "ending_cash": running,
        "minimum_cash": min_cash,
        "working_capital_gap": gap,
        "positions": positions[-5:],  # last 5 days for brevity
    }

def generate_recommendations(dso: float, gap: float, invoices: List[Dict]) -> List[str]:
    recs = []
    if dso > 60:
        recs.append("High DSO detected. Prioritize collections on overdue invoices (MSMED Act 45-day rule may apply for registered MSMEs).")
    if gap > 50000:
        recs.append(f"Working capital gap of ~₹{gap:,.0f} projected. Consider TReDS platforms (M1xchange, RXIL, DTX) or invoice discounting.")
    overdue = [i for i in invoices if i["status"] == "overdue"]
    if overdue:
        recs.append(f"{len(overdue)} overdue invoice(s) totaling ₹{sum(i['amount'] for i in overdue):,.0f}. Review customer credit terms.")
    if not recs:
        recs.append("Cash position looks manageable. Continue monitoring weekly.")
    return recs

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("MSME AI Cash Flow Forecaster — Demo")
    print("=" * 60)

    dso = calculate_dso(SAMPLE_INVOICES)
    dpo = calculate_dpo(SAMPLE_PAYABLES)
    ccc = dso + 45 - dpo  # Assume 45 days inventory for manufacturing

    print(f"\nKey Metrics (as of 2026-11-24):")
    print(f"  Days Sales Outstanding (DSO): {dso:.1f} days")
    print(f"  Days Payable Outstanding (DPO): {dpo:.1f} days")
    print(f"  Estimated Cash Conversion Cycle: {ccc:.1f} days")

    forecast = forecast_cash(SAMPLE_INVOICES, SAMPLE_PAYABLES, CURRENT_CASH, days=90)
    print(f"\n90-Day Cash Forecast:")
    print(f"  Ending cash: ₹{forecast['ending_cash']:,.0f}")
    print(f"  Minimum cash during period: ₹{forecast['minimum_cash']:,.0f}")
    print(f"  Estimated working capital gap: ₹{forecast['working_capital_gap']:,.0f}")

    print("\nRecommendations:")
    for r in generate_recommendations(dso, forecast['working_capital_gap'], SAMPLE_INVOICES):
        print(f"  • {r}")

    print("\n" + "=" * 60)
    print("Edit SAMPLE_INVOICES / SAMPLE_PAYABLES or extend with CSV loading.")
    print("This is a transparent starter — layer AI/ML on top for production.")
    print("=" * 60)

if __name__ == "__main__":
    main()
