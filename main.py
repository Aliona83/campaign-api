"""
Skin Clinic Campaign Analysis - FastAPI app
Endpoint: /campaign-analysis  (HTML tables)
          /campaign-analysis?format=json  (raw JSON)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

# ---------------------------------------------------------------------------
# 1. CONFIG - change these to match the column names in YOUR dataset
# ---------------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data.csv"   # use .xlsx too (see load_data)

COL_GENDER = "Gender"                       # Male / Female
COL_AGE = "AgeGroup"                        # already grouped: <30 / 30-50 / >50
COL_LAST_QTR = "Purchase_Last_Quarter"      # Yes / No
COL_PRODUCTS = "Unique_Products_Purchased"  # numeric count (last year)
COL_RESPONSE = "Response_to_Campaign"       # Yes / No

app = FastAPI(title="Skin Clinic Campaign Analysis")


# ---------------------------------------------------------------------------
# 2. Load & clean data
# ---------------------------------------------------------------------------
def to_binary(series: pd.Series) -> pd.Series:
    """Convert Yes/No, Y/N, True/False, 1/0 to 1/0."""
    mapping = {"yes": 1, "y": 1, "true": 1, "1": 1,
               "no": 0, "n": 0, "false": 0, "0": 0}
    return series.astype(str).str.strip().str.lower().map(mapping)


def load_data() -> pd.DataFrame:
    if DATA_FILE.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.strip()

    df["_response"] = to_binary(df[COL_RESPONSE])
    df["_gender"] = df[COL_GENDER].astype(str).str.strip().str.title()
    df["_last_qtr"] = to_binary(df[COL_LAST_QTR]).map({1: "Yes", 0: "No"})

    age_raw = df[COL_AGE]
    age = pd.to_numeric(age_raw, errors="coerce")
    if age.notna().mean() > 0.9:   # numeric ages -> bin them
        df["_age_group"] = np.select(
            [age < 30, (age >= 30) & (age <= 50), age > 50],
            ["<30", "30–50", ">50"], default=None)
    else:                          # already grouped labels like "30-50"
        df["_age_group"] = (age_raw.astype(str).str.replace(" ", "")
                            .str.replace("-", "–"))

    prods = pd.to_numeric(df[COL_PRODUCTS], errors="coerce")
    df["_product_group"] = np.select(
        [(prods >= 1) & (prods <= 4), (prods >= 5) & (prods <= 8), prods > 8],
        ["1–4", "5–8", ">8"], default=None)
    return df


# ---------------------------------------------------------------------------
# 3. Analysis
# ---------------------------------------------------------------------------
def response_table(df: pd.DataFrame, col: str, label: str, order: list) -> list[dict]:
    t = (df.dropna(subset=[col, "_response"])
           .groupby(col)["_response"]
           .agg(Customers="count", Responders="sum"))
    t = t.reindex([o for o in order if o in t.index])
    t["Response Rate (%)"] = (t["Responders"] / t["Customers"] * 100).round(2)
    t = t.reset_index().rename(columns={col: label})
    t["Responders"] = t["Responders"].astype(int)
    return t.to_dict(orient="records")


def run_analysis() -> dict:
    df = load_data()
    return {
        "total_customers": int(len(df)),
        "overall_response_rate": round(float(df["_response"].mean() * 100), 2),
        "tables": {
            "1. Gender vs Campaign Response":
                response_table(df, "_gender", "Gender", ["Male", "Female"]),
            "2. Age Group vs Campaign Response":
                response_table(df, "_age_group", "Age Group", ["<30", "30–50", ">50"]),
            "3. Purchase in Last Quarter vs Campaign Response":
                response_table(df, "_last_qtr", "Purchased Last Quarter", ["Yes", "No"]),
            "4. Product Usage vs Campaign Response":
                response_table(df, "_product_group", "Unique Products (Last Year)",
                               ["1–4", "5–8", ">8"]),
        },
    }


# ---------------------------------------------------------------------------
# 4. HTML rendering
# ---------------------------------------------------------------------------
CSS = """
body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:30px auto;padding:0 16px;color:#222;background:#fafafa}
h1{color:#2c3e50;margin-bottom:4px}
.sub{color:#666;margin-top:0}
h2{color:#34495e;font-size:1.1rem;margin-top:32px}
table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08)}
th,td{padding:10px 14px;border:1px solid #ddd;text-align:center}
th{background:#2c3e50;color:#fff}
tr:nth-child(even){background:#f4f6f8}
td.rate{font-weight:600;color:#1a7f5a}
"""


def html_table(rows: list[dict]) -> str:
    if not rows:
        return "<p>No data.</p>"
    head = "".join(f"<th>{k}</th>" for k in rows[0])
    body = ""
    for r in rows:
        cells = ""
        for k, v in r.items():
            cls = ' class="rate"' if "Rate" in k else ""
            val = f"{v:.2f}%" if "Rate" in k else v
            cells += f"<td{cls}>{val}</td>"
        body += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


# ---------------------------------------------------------------------------
# 5. Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return ("<h2>Skin Clinic Campaign API</h2>"
            "<p>See <a href='/campaign-analysis'>/campaign-analysis</a> "
            "or <a href='/docs'>/docs</a>.</p>")


@app.get("/campaign-analysis")
def campaign_analysis(format: str = "html"):
    result = run_analysis()
    if format.lower() == "json":
        return JSONResponse(result)

    sections = "".join(f"<h2>{title}</h2>{html_table(rows)}"
                       for title, rows in result["tables"].items())
    page = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Campaign Analysis</title><style>{CSS}</style></head><body>
<h1>Skin Clinic – Campaign Response Analysis</h1>
<p class="sub">Total customers: <b>{result['total_customers']:,}</b> &nbsp;|&nbsp;
Overall response rate: <b>{result['overall_response_rate']:.2f}%</b></p>
{sections}
</body></html>"""
    return HTMLResponse(page)
