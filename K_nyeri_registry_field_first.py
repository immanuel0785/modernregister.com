#!/usr/bin/env python
# coding: utf-8

# In[6]:


from datetime import datetime, timedelta
import io
import os
import sqlite3
import time
import uuid
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import numpy as np
import pandas as pd
from reportlab.pdfgen import canvas
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="County Government of Nyeri | Digital Registry",
    page_icon="⚖️",
    layout="wide",
)

# --- 0. PROFESSIONAL REGISTRY INTERFACE STYLING ---
# Palette: forest green, deep navy, warm gold, and a light neutral canvas.
nyeri_custom_css = """
<style>
    :root {
        --nyeri-green: #126447;
        --nyeri-green-dark: #0b4934;
        --nyeri-navy: #17324d;
        --nyeri-gold: #d6a84f;
        --nyeri-bg: #f3f6f4;
        --nyeri-text: #1c2b25;
        --nyeri-muted: #61736a;
        --nyeri-border: #dce6df;
    }

    .stApp {
        background: var(--nyeri-bg) !important;
        color: var(--nyeri-text) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(243, 246, 244, 0.92) !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1500px;
    }
    h1, h2, h3, h4 {
        color: var(--nyeri-navy) !important;
        font-weight: 750 !important;
        letter-spacing: -0.02em;
    }
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: var(--nyeri-text);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17324d 0%, #10263b 100%) !important;
        border-right: 3px solid var(--nyeri-gold);
    }
    [data-testid="stSidebar"] * {
        color: #f4f7f5 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: rgba(255,255,255,0.09) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
    }
    .nyeri-top-bar {
        background: linear-gradient(100deg, var(--nyeri-green-dark) 0%, var(--nyeri-green) 72%, #1b7255 100%);
        color: #ffffff !important;
        border-bottom: 4px solid var(--nyeri-gold);
        border-radius: 14px;
        padding: 17px 22px;
        margin: 0 0 22px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        box-shadow: 0 8px 24px rgba(16, 55, 39, 0.12);
    }
    .nyeri-top-bar .brand-title {
        color: #ffffff !important;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.025em;
    }
    .nyeri-top-bar .brand-subtitle {
        color: #e1eee7 !important;
        font-size: 0.83rem;
        text-align: right;
    }
    .prototype-pill {
        display: inline-block;
        background: #fff4d6;
        color: #674a0b !important;
        border: 1px solid #efd38b;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .dashboard-header-card {
        background: linear-gradient(135deg, #ffffff 0%, #edf5f0 100%);
        border: 1px solid var(--nyeri-border);
        border-left: 6px solid var(--nyeri-green);
        border-radius: 16px;
        padding: 26px 28px;
        text-align: left;
        margin: 0 0 18px 0;
        box-shadow: 0 6px 22px rgba(24, 56, 41, 0.06);
    }
    .dashboard-title {
        color: var(--nyeri-navy) !important;
        font-size: clamp(1.45rem, 2.3vw, 2rem);
        font-weight: 800;
        line-height: 1.2;
    }
    .dashboard-subtitle {
        color: var(--nyeri-muted) !important;
        font-size: 0.96rem;
        margin-top: 8px;
        line-height: 1.5;
    }
    .section-eyebrow {
        color: var(--nyeri-green) !important;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .module-intro {
        color: var(--nyeri-muted) !important;
        font-size: 0.94rem;
        margin-top: -5px;
        margin-bottom: 14px;
    }
    .db-card {
        background: #ffffff;
        border: 1px solid var(--nyeri-border);
        border-top: 4px solid var(--nyeri-gold);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        margin-top: 22px;
        box-shadow: 0 5px 18px rgba(24, 56, 41, 0.05);
    }
    .flow-arrow {
        text-align: center;
        font-size: 14px;
        color: var(--nyeri-muted) !important;
        margin: 12px 0 18px;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid var(--nyeri-border);
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 112px;
        box-shadow: 0 4px 15px rgba(24, 56, 41, 0.045);
    }
    .kpi-label {
        color: var(--nyeri-muted) !important;
        font-size: 0.82rem;
        font-weight: 650;
    }
    .kpi-value {
        color: var(--nyeri-navy) !important;
        font-size: 1.65rem;
        font-weight: 800;
        margin-top: 7px;
        line-height: 1.2;
    }
    div.stButton > button {
        width: 100% !important;
        min-height: 78px;
        background: #ffffff !important;
        color: var(--nyeri-navy) !important;
        border: 1px solid var(--nyeri-border) !important;
        border-left: 5px solid var(--nyeri-green) !important;
        border-radius: 12px !important;
        padding: 14px 17px !important;
        text-align: left !important;
        font-size: 0.96rem !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 12px rgba(24, 56, 41, 0.035);
        transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
    }
    div.stButton > button:hover {
        background: #f1f8f3 !important;
        color: var(--nyeri-green-dark) !important;
        border-color: #9ecab3 !important;
        border-left-color: var(--nyeri-gold) !important;
        box-shadow: 0 7px 18px rgba(24, 56, 41, 0.09);
        transform: translateY(-1px);
    }
    div.stButton > button:focus {
        outline: 3px solid rgba(214, 168, 79, 0.45) !important;
        outline-offset: 2px;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--nyeri-border);
        border-radius: 13px;
        padding: 14px 16px;
        box-shadow: 0 3px 12px rgba(24, 56, 41, 0.035);
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--nyeri-muted) !important;
        font-weight: 650 !important;
    }
    div[data-testid="stMetricValue"] {
        color: var(--nyeri-green) !important;
        font-weight: 800 !important;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid var(--nyeri-border);
        border-radius: 14px;
        padding: 18px 20px 10px;
    }
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        background: #ffffff !important;
        border-color: #cbd9d0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--nyeri-border);
        border-radius: 10px;
        overflow: hidden;
    }
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        background: var(--nyeri-green) !important;
        color: #ffffff !important;
        border: 1px solid var(--nyeri-green) !important;
        border-radius: 9px !important;
        font-weight: 750 !important;
    }
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background: var(--nyeri-green-dark) !important;
        border-color: var(--nyeri-green-dark) !important;
    }
    hr {
        border-color: var(--nyeri-border) !important;
    }
    @media (max-width: 700px) {
        .nyeri-top-bar { align-items: flex-start; flex-direction: column; }
        .nyeri-top-bar .brand-subtitle { text-align: left; }
        .dashboard-header-card { padding: 20px; }
    }
</style>
"""
st.markdown(nyeri_custom_css, unsafe_allow_html=True)

# --- 1. SQLITE PERMANENT DATABASE ENGINE ---
DB_FILE = os.environ.get(
    "NYERI_REGISTRY_DB_PATH",
    str(Path(__file__).resolve().parent / "nyeri_registry_field_first.db"),
)


def get_db_connection():
  return sqlite3.connect(DB_FILE, timeout=5.0)


def init_db():
  """Create prototype tables and safely add link columns to older databases."""
  with get_db_connection() as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_sheet TEXT,
            date_entry TEXT,
            serial_no TEXT,
            trader_name TEXT,
            trader_id INTEGER,
            phone_no TEXT,
            station TEXT,
            stamped_pumps INTEGER DEFAULT 0,
            stamped_scales INTEGER DEFAULT 0,
            stamped_weights INTEGER DEFAULT 0,
            total_amount REAL DEFAULT 0,
            mpesa_code TEXT,
            inspector_logged TEXT,
            inspection_outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trader_id) REFERENCES traders_registry(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traders_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trader_name TEXT NOT NULL COLLATE NOCASE UNIQUE,
            phone_no TEXT NOT NULL,
            station TEXT NOT NULL,
            category TEXT,
            physical_address TEXT,
            registered_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_code TEXT UNIQUE,
            trader_id INTEGER NOT NULL,
            equipment_type TEXT NOT NULL,
            make_model TEXT,
            serial_number TEXT,
            location TEXT,
            status TEXT NOT NULL DEFAULT 'Registered - not yet inspected',
            registered_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trader_id) REFERENCES traders_registry(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inspection_equipment (
            inspection_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            PRIMARY KEY (inspection_id, equipment_id),
            FOREIGN KEY (inspection_id) REFERENCES ledger_entries(id) ON DELETE CASCADE,
            FOREIGN KEY (equipment_id) REFERENCES equipment_registry(id)
        )
    """)
    # Migrate an older prototype database without deleting its existing records.
    ledger_cols = {row[1] for row in cursor.execute("PRAGMA table_info(ledger_entries)").fetchall()}
    if "trader_id" not in ledger_cols:
      cursor.execute("ALTER TABLE ledger_entries ADD COLUMN trader_id INTEGER")
    if "inspection_outcome" not in ledger_cols:
      cursor.execute("ALTER TABLE ledger_entries ADD COLUMN inspection_outcome TEXT")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT NOT NULL,
            station TEXT NOT NULL,
            inspection_month TEXT NOT NULL,
            trader_id INTEGER,
            trader_name TEXT NOT NULL,
            phone_no TEXT NOT NULL,
            message_text TEXT NOT NULL,
            provider TEXT NOT NULL,
            delivery_status TEXT NOT NULL,
            provider_response TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trader_id) REFERENCES traders_registry(id)
        )
    """)
    conn.commit()


init_db()


def save_trader_to_db(name, phone, station, category, address, registered_by):
  try:
    with get_db_connection() as conn:
      conn.execute("PRAGMA foreign_keys = ON")
      cursor = conn.cursor()
      cursor.execute(
          """INSERT INTO traders_registry
             (trader_name, phone_no, station, category, physical_address, registered_by)
             VALUES (?, ?, ?, ?, ?, ?)""",
          (name.strip(), phone.strip(), station, category, address.strip(), registered_by.strip() or "Field officer"),
      )
      conn.commit()
    return True, "Trader registered in the local prototype database."
  except sqlite3.IntegrityError:
    return False, "A trader with this business name already exists. Search the directory before creating another record."


def load_traders_from_db():
  with get_db_connection() as conn:
    return pd.read_sql_query("SELECT * FROM traders_registry ORDER BY trader_name", conn)


def save_equipment_to_db(trader_id, equipment_type, make_model, serial_number, location, registered_by):
  """Create an equipment record under an existing trader."""
  serial_number = serial_number.strip()
  try:
    with get_db_connection() as conn:
      conn.execute("PRAGMA foreign_keys = ON")
      cursor = conn.cursor()
      if serial_number:
        exists = cursor.execute(
            "SELECT 1 FROM equipment_registry WHERE lower(serial_number)=lower(?) LIMIT 1",
            (serial_number,),
        ).fetchone()
        if exists:
          return False, "That equipment serial number is already registered. Check the existing equipment record."
      cursor.execute(
          """INSERT INTO equipment_registry
             (equipment_code, trader_id, equipment_type, make_model, serial_number, location, registered_by)
             VALUES (NULL, ?, ?, ?, ?, ?, ?)""",
          (int(trader_id), equipment_type, make_model.strip(), serial_number or None,
           location.strip(), registered_by.strip() or "Field officer"),
      )
      equipment_id = cursor.lastrowid
      equipment_code = f"EQ-{equipment_id:06d}"
      cursor.execute("UPDATE equipment_registry SET equipment_code=? WHERE id=?", (equipment_code, equipment_id))
      conn.commit()
    return True, f"Equipment registered as {equipment_code}."
  except sqlite3.IntegrityError as exc:
    return False, f"Equipment could not be saved: {exc}"


def load_equipment_from_db(trader_id=None):
  query = """SELECT e.*, t.trader_name, t.station AS trader_station
             FROM equipment_registry e
             JOIN traders_registry t ON t.id=e.trader_id"""
  params = ()
  if trader_id is not None:
    query += " WHERE e.trader_id=?"
    params = (int(trader_id),)
  query += " ORDER BY t.trader_name, e.equipment_type, e.equipment_code"
  with get_db_connection() as conn:
    return pd.read_sql_query(query, conn, params=params)


def save_record_to_db(record):
  """Save an inspection and its equipment links in one transaction."""
  with get_db_connection() as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO ledger_entries
           (year_sheet, date_entry, serial_no, trader_name, trader_id, phone_no, station,
            stamped_pumps, stamped_scales, stamped_weights, total_amount, mpesa_code, inspector_logged, inspection_outcome)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (record["year_sheet"], record["date"], str(record["s_no"]), record["trader"],
         int(record["trader_id"]), record["phone"], record["station"], record["pumps"],
         record["scales"], record["weights"], record["fee"], record["code"], record["inspector"], record.get("outcome", "Not specified")),
    )
    inspection_id = cursor.lastrowid
    for equipment_id in record["equipment_ids"]:
      cursor.execute(
          "INSERT INTO inspection_equipment (inspection_id, equipment_id) VALUES (?, ?)",
          (inspection_id, int(equipment_id)),
      )
      cursor.execute(
          "UPDATE equipment_registry SET status=? WHERE id=?",
          (record.get("outcome", "Not specified"), int(equipment_id)),
      )
    conn.commit()
    return inspection_id


def load_all_db_records():
  with get_db_connection() as conn:
    return pd.read_sql_query("SELECT * FROM ledger_entries ORDER BY date_entry DESC, id DESC", conn)


def normalize_kenyan_phone(value):
  """Normalize common Kenyan mobile formats to +254... for SMS providers."""
  digits = "".join(ch for ch in str(value or "") if ch.isdigit())
  if digits.startswith("254") and len(digits) == 12:
    return "+" + digits
  if digits.startswith("0") and len(digits) == 10:
    return "+254" + digits[1:]
  if len(digits) == 9 and digits.startswith(("7", "1")):
    return "+254" + digits
  return None


def send_africastalking_sms(phone, message):
  """Send one SMS through Africa's Talking only when valid credentials are configured."""
  username = os.environ.get("AT_USERNAME", "").strip()
  api_key = os.environ.get("AT_API_KEY", "").strip()
  sender_id = os.environ.get("AT_SENDER_ID", "").strip()
  if not username or not api_key:
    return False, "SMS is not configured. Set AT_USERNAME and AT_API_KEY before sending."
  normalized_phone = normalize_kenyan_phone(phone)
  if not normalized_phone:
    return False, "Phone number is not in a recognized Kenyan mobile format."
  payload = {"username": username, "to": normalized_phone, "message": message}
  if sender_id:
    payload["from"] = sender_id
  request = Request(
      "https://api.africastalking.com/version1/messaging",
      data=urlencode(payload).encode("utf-8"),
      headers={"apiKey": api_key, "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
      method="POST",
  )
  try:
    with urlopen(request, timeout=20) as response:
      raw = response.read().decode("utf-8", errors="replace")
      parsed = json.loads(raw) if raw else {}
      recipients = parsed.get("SMSMessageData", {}).get("Recipients", [])
      if recipients and str(recipients[0].get("status", "")).lower() in {"success", "sent"}:
        return True, json.dumps(recipients[0], ensure_ascii=False)[:1000]
      return False, raw[:1000] or "Provider returned no recipient confirmation."
  except HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    return False, f"HTTP {exc.code}: {body[:800]}"
  except (URLError, TimeoutError, OSError, ValueError) as exc:
    return False, f"Provider request failed: {exc}"


def save_notification_log(campaign_id, station, month_label, trader, message, status, response):
  with get_db_connection() as conn:
    conn.execute(
        """INSERT INTO notification_logs
           (campaign_id, station, inspection_month, trader_id, trader_name, phone_no,
            message_text, provider, delivery_status, provider_response)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (campaign_id, station, month_label, int(trader["id"]), str(trader["trader_name"]),
         str(trader["phone_no"]), message, "Africa's Talking", status, str(response)[:1000]),
    )
    conn.commit()


def load_notification_logs(limit=500):
  with get_db_connection() as conn:
    return pd.read_sql_query(
        "SELECT sent_at, campaign_id, station, inspection_month, trader_name, phone_no, delivery_status, provider_response "
        "FROM notification_logs ORDER BY id DESC LIMIT ?", conn, params=(int(limit),)
    )


# --- 2. REPORTLAB PDF GENERATORS ---
def generate_pdf_certificate(r):
  buffer = io.BytesIO()
  c = canvas.Canvas(buffer, pagesize=(420, 560))
  c.setFillColorRGB(0, 0.41, 0.22)
  c.rect(20, 520, 380, 25, fill=1, stroke=0)
  c.setFillColorRGB(1, 1, 1)
  c.drawString(35, 528, "COUNTY GOVERNMENT OF NYERI - WEIGHTS & MEASURES")

  c.setFillColorRGB(0, 0, 0)
  c.setFont("Helvetica-Bold", 11)
  c.drawString(30, 490, "DEMONSTRATION VERIFICATION RECORD")
  c.setFont("Helvetica", 10)

  c.drawString(30, 460, f"Record S/NO: {r['s_no']}")
  c.drawString(30, 440, f"Inspection Date: {r['date']}")
  c.drawString(30, 420, f"Business / Trader: {r['trader'][:45]}")
  c.drawString(30, 400, f"Phone Contact: {r['phone'][:35]}")
  c.drawString(30, 380, f"Station / Location: {r['station'][:45]}")
  if r.get("equipment_codes"):
    c.drawString(30, 360, f"Equipment IDs: {', '.join(r['equipment_codes'])[:55]}")
  if r.get("outcome"):
    c.drawString(30, 340, f"Inspection outcome: {r['outcome']}")
  c.drawString(30, 320, f"Fuel pumps recorded: {r['pumps']}")
  c.drawString(30, 300, f"Scales recorded: {r['scales']}")
  c.drawString(30, 280, f"Weights recorded: {r['weights']}")

  c.setFont("Helvetica-Bold", 10)
  c.drawString(30, 250, f"Illustrative Fee Assessment: KES {r['fee']:,.2f}")
  c.setFont("Helvetica", 10)
  c.drawString(30, 230, f"Payment Reference Entered: {str(r['code'])[:45]}")

  c.setFillColorRGB(0.7, 0, 0)
  c.drawString(30, 210, f"Indicative Next Date (confirm rules): {r['due']}")

  c.setFillColorRGB(0, 0, 0)
  c.setFont("Helvetica-Oblique", 8)
  c.drawString(30, 190, "PROTOTYPE OUTPUT — NOT AN OFFICIAL COUNTY CERTIFICATE.")
  c.drawString(30, 175, f"Recorded in prototype by: {r['inspector']}")

  c.save()
  buffer.seek(0)
  return buffer.getvalue()


def generate_pdf_handin_report(
    inspector_name,
    report_date_str,
    summary_df,
    total_rev,
    total_insp,
    amount_in_words,
):
  buffer = io.BytesIO()
  c = canvas.Canvas(buffer, pagesize=(595.27, 841.89))

  c.setFillColorRGB(0, 0.41, 0.22)
  c.rect(40, 780, 515, 35, fill=1, stroke=0)
  c.setFillColorRGB(1, 1, 1)
  c.setFont("Helvetica-Bold", 12)
  c.drawString(
      50, 792, "COUNTY GOVERNMENT OF NYERI - WEIGHTS & MEASURES"
  )

  c.setFillColorRGB(0, 0, 0)
  c.setFont("Helvetica-Bold", 14)
  c.drawString(50, 745, "DEMO DAILY FIELD INSPECTION SUMMARY")
  c.setFont("Helvetica-Bold", 9)
  c.setFillColorRGB(0.65, 0, 0)
  c.drawString(50, 730, "PROTOTYPE OUTPUT — NOT FOR OFFICIAL SUBMISSION")
  c.setFillColorRGB(0, 0, 0)

  c.setFont("Helvetica", 10)
  c.drawString(50, 725, f"Reporting Officer: {inspector_name}")
  c.drawString(50, 710, f"Inspection Date: {report_date_str}")
  c.drawString(
      50,
      695,
      f"Total Inspection Records: {total_insp:,} | Recorded Fee Amounts: KES"
      f" {total_rev:,.2f}",
  )

  c.setFont("Helvetica-Oblique", 9)
  c.drawString(50, 680, f"Amount in Words: {amount_in_words}")

  y = 640
  c.setFillColorRGB(0, 0.41, 0.22)
  c.rect(40, y - 5, 515, 20, fill=1, stroke=0)
  c.setFillColorRGB(1, 1, 1)
  c.setFont("Helvetica-Bold", 9)
  c.drawString(50, y, "Inspection Center / Station")
  c.drawString(240, y, "Traders")
  c.drawString(290, y, "Pumps")
  c.drawString(340, y, "Scales")
  c.drawString(390, y, "Weights")
  c.drawString(450, y, "Recorded Amount (KES)")

  y -= 25
  c.setFillColorRGB(0, 0, 0)
  c.setFont("Helvetica", 9)

  for idx, row in summary_df.iterrows():
    c.drawString(50, y, str(row.iloc[0]))
    c.drawString(240, y, str(row.iloc[1]))
    c.drawString(290, y, str(row.iloc[3]))
    c.drawString(340, y, str(row.iloc[4]))
    c.drawString(390, y, str(row.iloc[5]))
    c.drawString(450, y, f"{row.iloc[2]:,.2f}")
    y -= 20
    if y < 100:
      c.showPage()
      y = 750

  y -= 40
  c.line(40, y, 555, y)
  y -= 30
  c.drawString(50, y, "Officer Signature: _______________________")
  c.drawString(330, y, "Director Approval: _______________________")

  c.save()
  buffer.seek(0)
  return buffer.getvalue()


def number_to_words_kes(amount):
  try:
    from num2words import num2words

    words = num2words(int(amount), lang="en").upper()
    return f"KENYA SHILLINGS {words} ONLY"
  except Exception:
    return f"AMOUNT IN WORDS UNAVAILABLE — KES {amount:,.2f}"


# --- 3. EXCEL PARSER & STATE MANAGEMENT ---
@st.cache_data
def process_uploaded_excel(file_source, sheet_name=0):
  try:
    df_raw = pd.read_excel(file_source, sheet_name=sheet_name, header=None)
    if df_raw.empty:
      return None

    header_row_idx = 0
    for idx, row in df_raw.head(15).iterrows():
      row_str = " ".join(
          [str(val).lower() for val in row.values if pd.notnull(val)]
      )
      if any(
          k in row_str
          for k in [
              "date",
              "s/no",
              "name",
              "station",
              "stamped",
              "total amount",
              "trader",
          ]
      ):
        header_row_idx = idx
        break

    df = pd.read_excel(file_source, sheet_name=sheet_name, header=header_row_idx)
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all").reset_index(drop=True)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    for col in df.columns:
      if any(p in col.lower() for p in ["phone", "no.", "tel", "contact"]):
        if "s/no" not in col.lower():
          df[col] = (
              df[col].fillna("").astype(str).str.replace(".0", "", regex=False)
          )

    for col in df.columns:
      if any(
          n in col.lower()
          for n in [
              "total",
              "amount",
              "kshs",
              "stamped",
              "rejected",
              "adjusted",
              "fees",
              "charges",
              "expense",
          ]
      ):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in df.columns:
      if "date" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )

    return df
  except Exception as e:
    return None


@st.cache_data
def load_workbook_from_source(file_source):
  sheets = {}
  try:
    if isinstance(file_source, str):
      with open(file_source, "rb") as f:
        file_bytes = f.read()
    else:
      file_bytes = file_source.getvalue()

    xl_workbook = pd.ExcelFile(io.BytesIO(file_bytes))
    for s_name in xl_workbook.sheet_names:
      parsed_s = process_uploaded_excel(
          io.BytesIO(file_bytes), sheet_name=s_name
      )
      if parsed_s is not None and not parsed_s.empty:
        sheets[str(s_name)] = parsed_s
  except Exception:
    pass
  return sheets


if "active_module" not in st.session_state:
  st.session_state["active_module"] = "Dashboard"

# No bundled workbook or synthetic records are loaded. The operational registry starts empty
# and is populated only by records entered by a user in the application.
if "sheets_dict" not in st.session_state:
  st.session_state["sheets_dict"] = {}

available_sheets = []

# --- 4. TOP OFFICIAL BANNER & SIDEBAR CONTROL ---
st.markdown(
    """
<div class="nyeri-top-bar">
    <div>
        <div class="brand-title">⚖️ NYERI WEIGHTS &amp; MEASURES</div>
        <div class="brand-subtitle" style="text-align:left;">Digital Registry &amp; Field Operations</div>
    </div>
    <div style="text-align:right;">
        <div class="brand-subtitle">County Government of Nyeri · Department of Trade</div>
        <span class="prototype-pill">Prototype for review</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.header("🔍 Digital Registry Nav")
st.sidebar.markdown("👤 **Operator:** Field officer (prototype; no login yet)")
st.sidebar.markdown(f"📍 **Active Module:** `{st.session_state['active_module']}`")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Return to Opening Dashboard"):
  st.session_state["active_module"] = "Dashboard"
  st.rerun()

if st.sidebar.button("📨 Trader Notifications"):
  st.session_state["active_module"] = "Notifications"
  st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Records are entered by users; no bundled synthetic dataset is loaded.")


# --- 5. TUESDAY OPENING INTERFACE (DASHBOARD ROUTER) ---
if st.session_state["active_module"] == "Dashboard":
  st.markdown(
      """
    <div class="dashboard-header-card">
        <div class="section-eyebrow">Field operations workspace</div>
        <div class="dashboard-title">Weights &amp; Measures Digital Registry</div>
        <div class="dashboard-subtitle">A central workspace for trader records, equipment verification, inspection activity and management reporting.</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Dashboard figures are read from the configured SQLite database only.
  # They are not populated from the optional workbook demonstration data.
  dash_traders = load_traders_from_db()
  dash_records = load_all_db_records()
  dash_revenue = (
      pd.to_numeric(dash_records["total_amount"], errors="coerce").fillna(0).sum()
      if not dash_records.empty and "total_amount" in dash_records.columns else 0
  )
  k1, k2, k3, k4 = st.columns(4)
  k1.metric("Registered traders", f"{len(dash_traders):,}")
  k2.metric("Inspection records", f"{len(dash_records):,}")
  k3.metric("Recorded fee amounts (KES)", f"{dash_revenue:,.2f}")
  equipment_count = len(load_equipment_from_db())
  k4.metric("Registered equipment", f"{equipment_count:,}")
  if dash_traders.empty and dash_records.empty and equipment_count == 0:
    st.info("The registry is empty and ready for user-entered records. No synthetic or bundled sample records are loaded. Use real records only when authorized and handle personal information under the County's approved procedures.")
  st.caption("Storage is a local SQLite database. Set NYERI_REGISTRY_DB_PATH to a managed persistent path when testing a suitable environment; this setting alone does not make hosting production-ready.")

  st.markdown("### Choose a workspace")
  st.markdown('<div class="module-intro">Open a module to complete a task or review records.</div>', unsafe_allow_html=True)
  col1, col2 = st.columns(2, gap="large")

  with col1:
    if st.button("👥 Trader Registry\n\nBusinesses and contacts"):
      st.session_state["active_module"] = "Trader Registry"
      st.rerun()

    if st.button("📋 Inspections\n\nVisits and verification history"):
      st.session_state["active_module"] = "Inspections"
      st.rerun()

    if st.button("📊 Reports\n\nPeriodic summaries and exports"):
      st.session_state["active_module"] = "Reports"
      st.rerun()

  with col2:
    if st.button("⚖️ Equipment Registry\n\nEquipment IDs and status"):
      st.session_state["active_module"] = "Equipment Registry"
      st.rerun()

    if st.button("💳 Fee Records\n\nAssessments and payment references"):
      st.session_state["active_module"] = "Fee Records"
      st.rerun()

    if st.button("🛡️ Audit & Administration\n\nUsers, permissions and change history"):
      st.session_state["active_module"] = "Audit & Administration"
      st.rerun()

    if st.button("📨 Trader Notifications\n\nBatch inspection notices by station"):
      st.session_state["active_module"] = "Notifications"
      st.rerun()

  st.markdown(
      """
    <div class="flow-arrow">↓</div>
    <div class="db-card">
        <div style="font-size: 24px; margin-bottom: 5px;">🗄️</div>
        <div style="font-size: 18px; font-weight: 750; color: #17324d;">Local Prototype Database</div>
        <div style="font-size: 13px; color: #61736a; margin-top: 4px;">Prototype storage only; confirm approved hosting, backup and access controls before any operational use.</div>
    </div>
    """,
      unsafe_allow_html=True,
  )


# --- 6. MODULE 1: TRADER REGISTRY ---
elif st.session_state["active_module"] == "Trader Registry":
  st.title("👥 Trader Registry Workspace")
  st.markdown(
      "*Create a trader record once, then attach equipment and future inspections to that record.*"
  )
  st.markdown("---")

  t_tab1, t_tab2 = st.tabs(
      ["➕ Register New Trader", "📂 View Registered Traders Directory"]
  )

  with t_tab1:
    st.subheader("Add New Trader / Business Profile")
    with st.form("trader_reg_form"):
      c1, c2 = st.columns(2)
      with c1:
        t_name = st.text_input(
            "Business / Trader Name *", placeholder="e.g. DEKUT COFFEE MILLERS"
        )
        t_phone = st.text_input(
            "Primary Contact Phone *", placeholder="0722000111"
        )
        t_station = st.selectbox(
            "Sub-County / Station *",
            [
                "NYERI TOWN",
                "OTHAYA",
                "MUKURWEINI",
                "TETU",
                "KIENI EAST",
                "KIENI WEST",
                "MATHIRA EAST",
                "MATHIRA WEST",
            ],
        )
      with c2:
        t_cat = st.selectbox(
            "Trade Category",
            [
                "Petrol Station / Fuel Depot",
                "Retail Shop / Butchery",
                "Supermarket / Wholesale",
                "Coffee / Tea Factory",
                "Hardware / Agri-Vet",
                "Other Commercial Establishment",
            ],
        )
        t_address = st.text_input(
            "Physical Address / Plot No.", placeholder="e.g. Main Street, Plot 14"
        )
        t_officer = st.text_input("Registering Officer / field officer", value="Field officer")

      reg_btn = st.form_submit_button("Register Trader in Local Prototype")

      if reg_btn:
        if t_name.strip() == "" or t_phone.strip() == "":
          st.error("⚠️ Please fill in all required fields (Trader Name & Phone).")
        else:
          success, msg = save_trader_to_db(
              t_name.strip().upper(),
              t_phone.strip(),
              t_station,
              t_cat,
              t_address.strip(),
              t_officer,
          )
          if success:
            st.success(f"✅ {msg}")
            st.rerun()
          else:
            st.error(f"⚠️ {msg}")

  with t_tab2:
    st.subheader("Registered Traders Ledger")
    traders_df = load_traders_from_db()
    if not traders_df.empty:
      search_t = st.text_input(
          "Filter by trader name, phone or station:", placeholder="Search..."
      )
      if search_t:
        mask = traders_df.astype(str).apply(
            lambda x: x.str.contains(search_t, case=False, na=False)
        )
        traders_df = traders_df[mask.any(axis=1)]
      st.dataframe(traders_df, use_container_width=True)
    else:
      st.info("No registered traders found in DB yet. Add one above!")


# --- 7. MODULE 2: INSPECTIONS & FIELD VERIFICATION ENGINE ---
elif st.session_state["active_module"] == "Inspections":
  st.title("📋 Field Inspections & Record Generator")
  st.markdown("*Select an existing trader and the equipment registered to that trader. Each saved inspection is linked to both records.*")
  st.markdown("---")

  if "last_receipt_data" not in st.session_state:
    st.session_state["last_receipt_data"] = None

  registered_traders_df = load_traders_from_db()
  saved_records_for_serial = load_all_db_records()
  serial_values = pd.to_numeric(saved_records_for_serial.get("serial_no", pd.Series(dtype=float)), errors="coerce").dropna()
  default_sno = int(serial_values.max()) + 1 if not serial_values.empty else 1

  if registered_traders_df.empty:
    st.warning("No traders are registered yet. Register a trader first, then add their equipment before recording an inspection.")
    if st.button("Open Trader Registry"):
      st.session_state["active_module"] = "Trader Registry"
      st.rerun()
  else:
    trader_labels = {
        f"{row.trader_name} — {row.station} (Trader ID {row.id})": int(row.id)
        for row in registered_traders_df.itertuples()
    }
    selected_trader_label = st.selectbox("Select registered trader", list(trader_labels.keys()), key="inspection_trader")
    selected_trader_id = trader_labels[selected_trader_label]
    trader_row = registered_traders_df.loc[registered_traders_df["id"] == selected_trader_id].iloc[0]
    equipment_df = load_equipment_from_db(selected_trader_id)

    if equipment_df.empty:
      st.warning("This trader has no registered equipment yet. Register the equipment before logging its inspection.")
      if st.button("Open Equipment Registry"):
        st.session_state["active_module"] = "Equipment Registry"
        st.rerun()
    else:
      equipment_labels = {
          f"{row.equipment_code} — {row.equipment_type}"
          + (f" — Serial: {row.serial_number}" if pd.notna(row.serial_number) and str(row.serial_number).strip() else ""):
          {"id": int(row.id), "type": row.equipment_type, "code": row.equipment_code}
          for row in equipment_df.itertuples()
      }
      with st.form("inspection_entry_form"):
        st.subheader("Log a field inspection")
        st.info("Prototype only: fee rates are illustrative, not an approved fee schedule. Payment references are stored as text and are not verified.")
        c1, c2 = st.columns(2)
        with c1:
          st.text_input("Trader", value=str(trader_row["trader_name"]), disabled=True)
          st.text_input("Trader ID", value=str(selected_trader_id), disabled=True)
          selected_equipment_labels = st.multiselect("Equipment inspected *", list(equipment_labels.keys()))
          inspection_station = st.selectbox(
              "Inspection station / sub-county",
              ["NYERI TOWN", "OTHAYA", "MUKURWEINI", "TETU", "KIENI EAST", "KIENI WEST", "MATHIRA EAST", "MATHIRA WEST"],
              index=["NYERI TOWN", "OTHAYA", "MUKURWEINI", "TETU", "KIENI EAST", "KIENI WEST", "MATHIRA EAST", "MATHIRA WEST"].index(str(trader_row["station"])) if str(trader_row["station"]) in ["NYERI TOWN", "OTHAYA", "MUKURWEINI", "TETU", "KIENI EAST", "KIENI WEST", "MATHIRA EAST", "MATHIRA WEST"] else 0,
          )
          inspection_date = st.date_input("Inspection date", value=datetime.today().date())
          outcome = st.selectbox("Inspection outcome", ["Passed", "Failed", "Adjustment required", "Not completed"])
        with c2:
          st.text_input("Prototype record serial", value=str(default_sno), disabled=True)
          target_sheet = str(inspection_date.year)
          payment_reference = st.text_input("Optional payment reference (not verified)", placeholder="Enter only if provided")
          inspector_name = st.text_input("Inspector / field officer", value="Field officer")
          st.caption("Illustrative fee rates used only for the demo: fuel pump KES 2,400; scale KES 2,000; weight KES 500. Confirm official rates before operational use.")

        submit_inspection = st.form_submit_button("Save Inspection Record")
        if submit_inspection:
          selected_equipment = [equipment_labels[label] for label in selected_equipment_labels]
          if not selected_equipment:
            st.error("Select at least one registered equipment item inspected during this visit.")
          else:
            equipment_types = [item["type"] for item in selected_equipment]
            pumps = sum(1 for x in equipment_types if x == "Fuel pump")
            scales = sum(1 for x in equipment_types if x == "Scale")
            weights = sum(1 for x in equipment_types if x == "Weight")
            # Equipment categories outside the illustrative fee categories are recorded but not assigned an invented rate.
            calc_fee = pumps * 2400 + scales * 2000 + weights * 500
            date_str = inspection_date.strftime("%Y-%m-%d")
            rec_payload = {
                "year_sheet": str(target_sheet),
                "s_no": default_sno,
                "trader": str(trader_row["trader_name"]).strip().upper(),
                "trader_id": selected_trader_id,
                "phone": str(trader_row["phone_no"]),
                "station": inspection_station,
                "pumps": pumps,
                "scales": scales,
                "weights": weights,
                "fee": calc_fee,
                "code": payment_reference.strip().upper() or "Not provided",
                "date": date_str,
                "due": (inspection_date + timedelta(days=365)).strftime("%Y-%m-%d"),
                "inspector": inspector_name.strip() or "Field officer",
                "equipment_ids": [item["id"] for item in selected_equipment],
                "equipment_codes": [item["code"] for item in selected_equipment],
                "outcome": outcome,
            }
            try:
              save_record_to_db(rec_payload)
              st.session_state["last_receipt_data"] = rec_payload
              st.success(f"Inspection saved and linked to {len(selected_equipment)} equipment item(s). Illustrative fee amount: KES {calc_fee:,.2f}. Payment has not been verified.")
              st.rerun()
            except Exception as exc:
              st.error(f"The inspection could not be saved. No success is claimed. Details: {exc}")

  if st.session_state["last_receipt_data"]:
    r = st.session_state["last_receipt_data"]
    st.markdown("---")
    st.subheader("📄 Prototype Inspection Record PDF — Not an Official Certificate")
    st.caption("Equipment: " + ", ".join(r.get("equipment_codes", [])) + " | Outcome: " + r.get("outcome", "Not specified"))
    try:
      pdf_bytes = generate_pdf_certificate(r)
      st.download_button(
          label="📥 Download Prototype Record PDF (.pdf)",
          data=pdf_bytes,
          file_name=f"DEMO_Record_{r['s_no']}_{r['trader'].replace(' ', '_')}.pdf",
          mime="application/pdf",
      )
    except Exception as e:
      st.error(f"Could not generate the prototype PDF: {e}")


# --- 8. MODULE 3: REPORTS WORKSPACE (HAND-IN REPORT TO DIRECTOR) ---
elif st.session_state["active_module"] == "Reports":
  st.title("📊 Daily Field Hand-In Report Workspace")
  st.markdown(
      "*Generate a daily summary from saved prototype records. Verify figures and source records before any official use.*"
  )
  st.markdown("---")

  report_date = st.date_input(
      "Select Report Date:", value=datetime.today().date()
  )
  report_date_str = report_date.strftime("%Y-%m-%d")

  db_records = load_all_db_records()
  if not db_records.empty:
    daily_mask = db_records["date_entry"] == report_date_str
    daily_df = db_records[daily_mask]

    st.markdown(f"### 📋 Hand-In Report Summary: `{report_date_str}`")

    d_m1, d_m2, d_m3 = st.columns(3)
    total_inspections_day = len(daily_df)
    total_revenue_day = (
        daily_df["total_amount"].sum()
        if not daily_df.empty and "total_amount" in daily_df.columns
        else 0
    )
    total_pumps_day = (
        daily_df["stamped_pumps"].sum()
        if not daily_df.empty and "stamped_pumps" in daily_df.columns
        else 0
    )
    total_scales_day = (
        daily_df["stamped_scales"].sum()
        if not daily_df.empty and "stamped_scales" in daily_df.columns
        else 0
    )
    total_weights_day = (
        daily_df["stamped_weights"].sum()
        if not daily_df.empty and "stamped_weights" in daily_df.columns
        else 0
    )

    d_m1.metric("Total Inspections Logged", f"{total_inspections_day:,}")
    d_m2.metric("Recorded Fee Assessments", f"KES {total_revenue_day:,.2f}")
    d_m3.metric(
        "Equipment Stamped",
        f"Pumps: {total_pumps_day} | Scales: {total_scales_day} | Wts:"
        f" {total_weights_day}",
    )

    st.markdown("---")
    st.markdown("### 🏢 Station-Wise Hand-In Summary Table")

    if not daily_df.empty:
      station_summary = (
          daily_df.groupby("station")
          .agg(
              Inspection_Records=("trader_name", "count"),
              Total_Fee=("total_amount", "sum"),
              Stamped_Pumps=("stamped_pumps", "sum"),
              Stamped_Scales=("stamped_scales", "sum"),
              Stamped_Weights=("stamped_weights", "sum"),
          )
          .reset_index()
      )

      station_summary.columns = [
          "Inspection Center / Station",
          "Inspection Records",
          "Recorded Fee Assessments (KES)",
          "Stamped Pumps",
          "Stamped Scales",
          "Stamped Weights",
      ]

      st.dataframe(station_summary, use_container_width=True)

      rev_in_words = number_to_words_kes(total_revenue_day)
      st.info(
          f"📝 **Recorded fee amount in words (if conversion is available):**\n`{rev_in_words}`"
      )

      st.markdown("---")

      pdf_handin_bytes = generate_pdf_handin_report(
          "Insp. Field Officer",
          report_date_str,
          station_summary,
          total_revenue_day,
          total_inspections_day,
          rev_in_words,
      )

      st.download_button(
          label="📥 Download Demo Daily Summary PDF (.pdf)",
          data=pdf_handin_bytes,
          file_name=f"DEMO_Daily_Summary_{report_date_str}.pdf",
          mime="application/pdf",
      )

      st.markdown("---")
      st.markdown("**Detailed Field Inspection Entries:**")
      report_cols = [c for c in [
          "serial_no", "date_entry", "trader_name", "station", "stamped_pumps",
          "stamped_scales", "stamped_weights", "total_amount", "mpesa_code", "inspector_logged", "inspection_outcome"
      ] if c in daily_df.columns]
      st.dataframe(daily_df[report_cols], use_container_width=True, hide_index=True)
    else:
      st.info(f"No inspection entries recorded in database for {report_date_str}.")
  else:
    st.info("No field inspection records logged in database yet.")


# --- 9. MODULE 4: EQUIPMENT REGISTRY WORKSPACE ---
elif st.session_state["active_module"] == "Equipment Registry":
  st.title("⚖️ Equipment Registry")
  st.markdown("*Register each item against an existing trader. Inspections then select equipment from this register.*")
  st.markdown("---")
  traders_df = load_traders_from_db()
  if traders_df.empty:
    st.warning("Register a trader before registering equipment.")
    if st.button("Open Trader Registry", key="equipment_open_traders"):
      st.session_state["active_module"] = "Trader Registry"
      st.rerun()
  else:
    trader_labels = {
        f"{row.trader_name} — {row.station} (Trader ID {row.id})": int(row.id)
        for row in traders_df.itertuples()
    }
    tab_add, tab_view = st.tabs(["➕ Register Equipment", "📂 Equipment Directory"])
    with tab_add:
      with st.form("equipment_registration_form"):
        selected_trader_label = st.selectbox("Trader / business *", list(trader_labels.keys()))
        equipment_type = st.selectbox("Equipment type *", ["Fuel pump", "Scale", "Weight", "Measuring instrument", "Other"])
        make_model = st.text_input("Make / model", placeholder="Manufacturer or model, if known")
        serial_number = st.text_input("Manufacturer serial number / local identifier", placeholder="Leave blank only if none is available")
        equipment_location = st.text_input("Equipment location", placeholder="Premises, pump island, shop floor, etc.")
        equipment_officer = st.text_input("Registering officer / field officer", value="Field officer")
        add_equipment = st.form_submit_button("Save Equipment Record")
        if add_equipment:
          if not equipment_type:
            st.error("Select an equipment type.")
          else:
            ok, message = save_equipment_to_db(
                trader_labels[selected_trader_label], equipment_type, make_model,
                serial_number, equipment_location, equipment_officer
            )
            if ok:
              st.success(message)
              st.rerun()
            else:
              st.error(message)
    with tab_view:
      equipment_df = load_equipment_from_db()
      if equipment_df.empty:
        st.info("No equipment has been registered yet. Add the first item above.")
      else:
        search_equipment = st.text_input("Search equipment code, trader, type or serial number", key="equipment_search")
        if search_equipment:
          mask = equipment_df.astype(str).apply(lambda col: col.str.contains(search_equipment, case=False, na=False))
          equipment_df = equipment_df[mask.any(axis=1)]
        visible_cols = [c for c in ["equipment_code", "trader_name", "trader_id", "equipment_type", "make_model", "serial_number", "location", "status", "created_at"] if c in equipment_df.columns]
        st.dataframe(equipment_df[visible_cols], use_container_width=True, hide_index=True)
        with get_db_connection() as conn:
          history_df = pd.read_sql_query(
              """SELECT l.serial_no AS inspection_record, l.date_entry AS inspection_date,
                        t.trader_name, e.equipment_code, e.equipment_type,
                        l.inspection_outcome, l.total_amount AS illustrative_fee_assessment,
                        l.inspector_logged
                 FROM inspection_equipment ie
                 JOIN ledger_entries l ON l.id=ie.inspection_id
                 JOIN equipment_registry e ON e.id=ie.equipment_id
                 JOIN traders_registry t ON t.id=e.trader_id
                 ORDER BY l.date_entry DESC, l.id DESC""", conn)
        st.markdown("#### Linked inspection history")
        if history_df.empty:
          st.info("No inspections have been linked to registered equipment yet.")
        else:
          st.dataframe(history_df, use_container_width=True, hide_index=True)

  st.markdown("---")
  st.caption("Equipment records are stored locally in SQLite. This is a single-environment prototype, not a shared multi-device field system.")


# --- 10. MODULE 5: BULK TRADER NOTIFICATIONS ---
elif st.session_state["active_module"] == "Notifications":
  st.title("📨 Inspection Notifications")
  st.markdown("*Prepare a station-wide inspection notice and send it to registered trader contacts in one action. The app logs each provider response; a send request is not a guarantee of handset delivery.*")
  st.markdown("---")
  traders_df = load_traders_from_db()
  if traders_df.empty:
    st.info("No traders are registered yet. Add real trader records in Trader Registry before creating a notification campaign.")
    if st.button("Open Trader Registry", key="notify_open_traders"):
      st.session_state["active_module"] = "Trader Registry"
      st.rerun()
  else:
    stations = sorted(traders_df["station"].dropna().astype(str).unique().tolist())
    today = datetime.today().date()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    col1, col2 = st.columns(2)
    with col1:
      target_station = st.selectbox("Target station / sub-county", stations, key="notify_station")
    with col2:
      inspection_month = st.date_input("Inspection month (choose any date in that month)", value=next_month, key="notify_month")
    month_start = inspection_month.replace(day=1)
    month_label = month_start.strftime("%B %Y")
    eligible_df = traders_df[traders_df["station"].astype(str) == target_station].copy()
    eligible_df["normalized_phone"] = eligible_df["phone_no"].map(normalize_kenyan_phone)
    st.metric("Registered traders in selected station", len(eligible_df))
    valid_count = int(eligible_df["normalized_phone"].notna().sum())
    st.metric("Contacts with recognizable Kenyan mobile numbers", valid_count)
    st.caption("Review this recipient list before sending. Numbers are normalized for SMS; invalid formats are excluded from sending and shown below.")
    st.dataframe(eligible_df[[c for c in ["trader_name", "phone_no", "station", "category", "normalized_phone"] if c in eligible_df.columns]], use_container_width=True, hide_index=True)
    invalid_df = eligible_df[eligible_df["normalized_phone"].isna()]
    if not invalid_df.empty:
      st.warning(f"{len(invalid_df)} trader contact(s) will not receive SMS because their phone number format could not be recognized.")
    default_message = (
        "Nyeri County Weights & Measures: inspection activities are planned for {month} in {station}. "
        "Please prepare for inspection and confirm the applicable fee with the County office in advance. "
        "This notice is not a payment demand or proof of payment. For queries, contact the relevant County office."
    )
    message_template = st.text_area("SMS message", value=default_message, height=130, help="Available placeholders: {business}, {month}, {station}. Keep the message concise; SMS length may affect cost.")
    template_error = None
    if not message_template.strip():
      template_error = "The SMS message cannot be blank."
    try:
      message_template.format(business="Business name", month=month_label, station=target_station)
    except (KeyError, ValueError, IndexError) as exc:
      template_error = f"Invalid message template ({exc}). Use only {{business}}, {{month}}, and {{station}} placeholders."
    if template_error:
      st.error(template_error)
    preview_trader = eligible_df.iloc[0] if not eligible_df.empty else None
    if preview_trader is not None and not template_error:
      preview_message = message_template.format(business=str(preview_trader["trader_name"]), month=month_label, station=target_station)
      st.markdown("#### Message preview")
      st.code(preview_message)
    sms_configured = bool(os.environ.get("AT_USERNAME", "").strip() and os.environ.get("AT_API_KEY", "").strip())
    if sms_configured:
      st.success("SMS provider credentials detected. The Send button will make real provider requests and may incur charges.")
    else:
      st.warning("SMS sending is not configured. No message can be sent until AT_USERNAME and AT_API_KEY are set in the environment. The app will not pretend a preview is a sent SMS.")
    confirm_send = st.checkbox("I have reviewed the recipient list and message, and I am authorized to send this operational notice.", key="notify_confirm_send")
    if st.button("📨 Send SMS to selected station", type="primary", disabled=(not sms_configured or valid_count == 0 or not confirm_send or bool(template_error))):
      campaign_id = uuid.uuid4().hex[:12].upper()
      sent_count = 0
      failed_count = 0
      progress = st.progress(0.0)
      status_box = st.empty()
      valid_df = eligible_df[eligible_df["normalized_phone"].notna()].copy()
      for index, (_, trader_row) in enumerate(valid_df.iterrows(), start=1):
        try:
          message = message_template.format(business=str(trader_row["trader_name"]), month=month_label, station=target_station)
        except (KeyError, ValueError, IndexError) as exc:
          st.error(f"Message template is invalid ({exc}); processing stopped. Review the campaign log for any messages already processed.")
          break
        ok, response_text = send_africastalking_sms(str(trader_row["phone_no"]), message)
        save_notification_log(campaign_id, target_station, month_label, trader_row, message,
                              "Provider accepted" if ok else "Failed", response_text)
        if ok:
          sent_count += 1
        else:
          failed_count += 1
        progress.progress(index / max(len(valid_df), 1))
        status_box.write(f"Processed {index} of {len(valid_df)} recipient(s)…")
      st.session_state["last_notification_campaign"] = campaign_id
      st.success(f"Campaign {campaign_id} processed. Provider accepted: {sent_count}; failed or unconfirmed: {failed_count}. Check the log below; accepted is not the same as confirmed delivery.")
      st.rerun()
    st.markdown("---")
    st.subheader("Notification history")
    notification_history = load_notification_logs()
    if notification_history.empty:
      st.info("No notification attempts have been logged yet.")
    else:
      st.dataframe(notification_history, use_container_width=True, hide_index=True)
      csv_bytes = notification_history.to_csv(index=False).encode("utf-8")
      st.download_button("Download notification log (CSV)", data=csv_bytes, file_name="nyeri_notification_log.csv", mime="text/csv")
    st.caption("SMS integration uses Africa's Talking when credentials are configured. Provider credentials, sender ID approval, message pricing, privacy review and authorized operational use must be confirmed before live sending. No delivery rate is guaranteed.")


# --- 11. MODULE 6: FEE RECORDS WORKSPACE ---
elif st.session_state["active_module"] == "Fee Records":
  st.title("💳 Fee Assessments & Payment References")
  st.markdown(
      "*Prototype fee assessments and payment references entered by the operator. References are not independently verified.*"
  )
  st.markdown("---")

  db_all = load_all_db_records()
  if not db_all.empty:
    st.dataframe(db_all, use_container_width=True)
  else:
    st.info("No prototype fee records found in the local database yet.")


# --- 11. MODULE 6: AUDIT & ADMINISTRATION WORKSPACE ---
elif st.session_state["active_module"] == "Audit & Administration":
  st.title("🛡️ Summary & Administration Notes")
  st.markdown(
      "*Summary metrics and saved prototype records. Security controls and a full change log are not implemented.*"
  )
  st.markdown("---")
  st.warning("This page provides summary views only. It does not authenticate users, enforce permissions, or maintain a complete audit trail.")

  db_records = load_all_db_records()
  traders_reg = load_traders_from_db()

  total_audited_revenue = (
      pd.to_numeric(db_records["total_amount"], errors="coerce").sum()
      if not db_records.empty
      else 0
  )
  total_audited_inspections = len(db_records) if not db_records.empty else 0
  total_registered_businesses = (
      len(traders_reg) if not traders_reg.empty else 0
  )

  a_col1, a_col2, a_col3 = st.columns(3)
  a_col1.metric("Recorded Fee Assessments", f"KES {total_audited_revenue:,.2f}")
  a_col2.metric("Total Inspections Logged", f"{total_audited_inspections:,}")
  a_col3.metric("Registered Businesses", f"{total_registered_businesses:,}")

  st.markdown("---")
  st.markdown("### 📈 Recorded Fee Amounts & Inspection Volume by Station")

  if not db_records.empty and "station" in db_records.columns:
    col_v1, col_v2 = st.columns(2)
    with col_v1:
      st.markdown("**Recorded Fee Amounts per Station (KES)**")
      station_rev = db_records.groupby("station")["total_amount"].sum()
      st.bar_chart(station_rev)
    with col_v2:
      st.markdown("**Inspection Volume per Station**")
      station_vol = db_records.groupby("station").size()
      st.bar_chart(station_vol)
  else:
    st.info("Insufficient inspection records in database to render charts.")

  st.markdown("---")
  st.markdown("### 👥 Illustrative Staff Directory (not authenticated users)")
  staff_data = pd.DataFrame({
      "Example Role": ["County administrator", "Senior field inspector", "Field inspector"],
      "Purpose": ["Manage approved configuration", "Review field activity", "Record field visits"],
      "Implementation status": ["Not implemented", "Not implemented", "Not implemented"],
  })
  st.dataframe(staff_data, use_container_width=True)
  st.caption("These are proposed roles for discussion, not real staff accounts. No login or role-based permission system is implemented in this prototype.")

  st.markdown("---")
  st.markdown("### 📋 Saved Inspection Records (not a change-by-change audit trail)")
  if not db_records.empty:
    st.dataframe(db_records, use_container_width=True)
  else:
    st.info("No inspection records have been saved in the local prototype database yet.")


# In[ ]:




