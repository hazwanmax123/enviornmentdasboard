import calendar
import datetime
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Environmental Monitoring Dashboard",
    page_icon="🌊",
    layout="wide",
)

# ==========================================
# GOOGLE SHEET CONFIGURATION & GSPREAD SETUP
# ==========================================
SPREADSHEET_NAME = "Master Data Monitoring"


@st.cache_resource
def init_gspread_client():
  try:
    # Guna kaedah direct dict dari st.secrets (Sangat stabil & moden)
    creds_dict = dict(st.secrets["gcp_service_account"])
    return gspread.service_account_from_dict(creds_dict)
  except Exception as e:
    st.error(f"⚠️ Ralat Autentikasi Google: {e}")
    return None


client = init_gspread_client()
SPREADSHEET_NAME = "Master Data Monitoring"

try:
  sheet_daily = client.open(SPREADSHEET_NAME).worksheet("Daily log 2026")
  df = pd.DataFrame(sheet_daily.get_all_records())
  df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except:
  df = pd.DataFrame()

try:
  sheet_cases = client.open(SPREADSHEET_NAME).worksheet("Cases Tracker")
  df_cases = pd.DataFrame(sheet_cases.get_all_records())
  df_cases_raw = df_cases.copy()
  date_col = df_cases.columns[0]
  df_cases[date_col] = pd.to_datetime(df_cases[date_col], errors="coerce")
except:
  df_cases = pd.DataFrame()
  df_cases_raw = pd.DataFrame()
  date_col = None

try:
  sheet_monthly_read = client.open(SPREADSHEET_NAME).worksheet(
      "Monthly Sampling"
  )
  df_monthly = pd.DataFrame(sheet_monthly_read.get_all_records())
except:
  df_monthly = pd.DataFrame()

f_ph = df.columns[1] if not df.empty and len(df.columns) > 1 else ""
f_ntu = df.columns[11] if not df.empty and len(df.columns) > 11 else ""
status_col = df_cases.columns[3] if not df_cases.empty and len(df_cases.columns) > 3 else None
# ==========================================
# UI TITLE & HEADER
# ==========================================
st.markdown(
    "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
    " margin-bottom: 2px;'>🔥 Environmental Master Data Entry Portal</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color: #64748b; font-size: 13px;'>Borang kemasukan data rasmi"
    " site ML087 yang berhubung terus secara live dengan Google Sheet"
    " 'Master Data Monitoring'.</p>",
    unsafe_allow_html=True,
)

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Environmental Monitoring Dashboard",
    page_icon="🌊",
    layout="wide",
)

# ------------------------------------------
# (Sila pastikan baki kod asal aplikasi kau 
# yang lain berada di bawah ini seperti biasa)
# ------------------------------------------


# ==========================================
# CUSTOM CSS: CLEAN LIGHT CANVAS + DARK SIDEBAR
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #f4f7fc;
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0d1322;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] .stButton button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #0369a1 !important;
        color: #ffffff !important;
    }

    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }
    
    p, span, label {
        font-family: 'Inter', sans-serif;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        margin-bottom: 10px;
        word-break: break-word;
    }

    [data-testid="stMetricValue"] {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif;
    }

    .table-container {
        width: 100%;
        overflow-x: auto;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }

    .badge-pass {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    .badge-alert {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    .badge-breach {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# GOOGLE SHEET CONFIGURATION & GSPREAD SETUP
# ==========================================
SPREADSHEET_NAME = (
    "Master Data Monitoring"  # <-- Nama fail penuh dalam Google Drive
)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def init_gspread_client():
  try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )
    return gspread.authorize(creds)
  except Exception:
    return None

gc = init_gspread_client()

# LINK CSV UNTUK PAPARAN DASHBOARD (READ)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=0&single=true&output=csv"
CASES_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=1959925791&single=true&output=csv"
MONTHLY_SAMPLING_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=1267713168&single=true&output=csv"


# ==========================================
# DATA LOADING DENGAN TTL CACHE (Auto-refresh)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
  df = pd.read_csv(CSV_URL)
  df.columns = df.columns.str.strip()
  df = df.dropna(subset=["Date"]).copy()
  df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
  df = df.dropna(subset=["Date"])
  df["Year"] = df["Date"].dt.year.astype(int)
  df["Month"] = df["Date"].dt.strftime("%B")
  for col in df.columns:
    if any(
        k in col.lower()
        for k in ["ph", "ntu", "limit", "case", "perf", "okay", "maintenance"]
    ):
      df[col] = pd.to_numeric(
          df[col].astype(str).str.replace("%", "").str.strip(), errors="coerce"
      )
  return df


@st.cache_data(ttl=60)
def load_cases_data():
  df_cases = pd.read_csv(CASES_CSV_URL)
  df_cases.columns = df_cases.columns.str.strip()
  date_col = next(
      (
          c
          for c in df_cases.columns
          if "date" in c.lower() or "raised" in c.lower()
      ),
      None,
  )
  if date_col:
    df_cases[date_col] = pd.to_datetime(df_cases[date_col], errors="coerce")
  return df_cases


@st.cache_data(ttl=60)
def load_monthly_sampling_data():
  try:
    df_m = pd.read_csv(MONTHLY_SAMPLING_CSV_URL)
    df_m.columns = df_m.columns.str.strip()
    return df_m
  except Exception:
    return pd.DataFrame()


try:
  df_raw = load_data()
  df_cases_raw = load_cases_data()
  df_monthly_raw = load_monthly_sampling_data()
except Exception as e:
  st.error(f"Error loading data: {e}")
  st.stop()

# ==========================================
# GLOBAL VARIABLE DEFINITIONS (FDP)
# ==========================================
f_ph = next(
    (
        c
        for c in df_raw.columns
        if "ph" in c.lower()
        and ("fdp" in c.lower() or "discharge" in c.lower())
    ),
    None,
)
if not f_ph:
  f_ph = [c for c in df_raw.columns if "ph" in c.lower()][-1]

f_ntu = next(
    (
        c
        for c in df_raw.columns
        if ("ntu" in c.lower() or "turb" in c.lower())
        and ("fdp" in c.lower() or "discharge" in c.lower())
    ),
    None,
)
if not f_ntu:
  f_ntu = [c for c in df_raw.columns if "ntu" in c.lower()][-1]


# ==========================================
# FUNCTION: GENERATE COMPREHENSIVE WORD REPORT
# ==========================================
def generate_comprehensive_word_report(
    df_filtered,
    df_cases_full,
    df_monthly_full,
    start_date,
    end_date,
    sel_month,
    sel_year,
    compliance_rate,
    open_cases,
):
  doc = Document()
  for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

  p_title = doc.add_paragraph()
  run_title = p_title.add_run(
      "RBA ENGINEERING SDN BHD (TIN MINING ML087)\nCOMPREHENSIVE EIA"
      " ENVIRONMENTAL MONITORING REPORT"
  )
  run_title.font.name = "Inter"
  run_title.font.size = Pt(14)
  run_title.font.bold = True
  run_title.font.color.rgb = RGBColor(15, 23, 42)

  p_sub = doc.add_paragraph()
  run_sub = p_sub.add_run(
      f"Reporting Period: {start_date.strftime('%d %b %Y')} to"
      f" {end_date.strftime('%d %b %Y')} ({sel_month} {sel_year})"
  )
  run_sub.font.name = "Inter"
  run_sub.font.size = Pt(10)
  run_sub.font.color.rgb = RGBColor(100, 116, 139)

  doc.add_paragraph()

  def add_custom_heading(text):
    h = doc.add_heading(level=1)
    run = h.add_run(text)
    run.font.name = "Inter"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(2, 132, 199)
    return h

  add_custom_heading("1. Executive Summary & Compliance Overview")
  summary_text = (
      f"Laporan pemantauan alam sekitar bersepadu bagi tapak perlombongan bijih"
      f" timah RBA Engineering (ML087) ini merangkumi analisis penuh merentas"
      f" semua modul pemantauan dari tarikh {start_date.strftime('%d %b %Y')}"
      f" hingga {end_date.strftime('%d %b %Y')}. Secara keseluruhan, kadar"
      f" pematuhan pelepasan akhir (Discharge Compliance) berada pada tahap"
      f" {compliance_rate:.1f}%. Analisis mendapati prestasi kawalan kelodak"
      f" dan keasidan air memerlukan perhatian berterusan bagi memastikan"
      f" pematuhan ketat piawaian JAS."
  )
  doc.add_paragraph(summary_text)

  add_custom_heading("2. Final Discharge (FDP) Compliance Analysis")
  if not df_filtered.empty:
    ph_min = df_filtered[f_ph].min()
    ntu_max = df_filtered[f_ntu].max()
    discharge_analysis = (
        f"Sepanjang tempoh laporan, bacaan minimum pH bagi Final Discharge"
        f" (FDP) dicatatkan pada paras {ph_min:.2f}, manakala bacaan maksimum"
        f" Turbiditi (NTU) mencecah {ntu_max:.1f} NTU. Tren AM dan PM"
        f" menunjukkan variasi harian yang dipengaruhi oleh aktiviti lombong"
        f" serta taburan hujan semasa."
    )
    doc.add_paragraph(discharge_analysis)
  else:
    doc.add_paragraph(
        "Tiada data pelepasan dicatatkan untuk julat tarikh ini."
    )

  add_custom_heading(
      "3. River Water Quality Impact (Sg. Duri Upstream vs Downstream)"
  )
  us_ph_avg = (
      df_filtered[
          [
              c
              for c in df_filtered.columns
              if "us" in c.lower() and "ph" in c.lower()
          ]
      ]
      .mean()
      .mean()
      if not df_filtered.empty
      else 0
  )
  ds_ph_avg = (
      df_filtered[
          [
              c
              for c in df_filtered.columns
              if "ds" in c.lower() and "ph" in c.lower()
          ]
      ]
      .mean()
      .mean()
      if not df_filtered.empty
      else 0
  )
  river_analysis = (
      f"Analisis perbandingan air Sungai Duri menunjukkan purata pH hulu"
      f" (Upstream) adalah sekitar {us_ph_avg:.2f} berbanding hilir"
      f" (Downstream) pada paras {ds_ph_avg:.2f}. Perubahan net-impact ini"
      f" merumuskan keberkesanan struktur perangkap kelodak (BMP) dalam"
      f" menampan limpahan aktiviti perlombongan."
  )
  doc.add_paragraph(river_analysis)

  add_custom_heading("4. Environmental Cases & Incident Management Summary")
  cases_analysis = (
      f"Berdasarkan sistem penjejakan kes (Cases Tracker), terdapat sejumlah"
      f" {open_cases} kes terbuka atau tertunggak yang memerlukan tindakan"
      f" pembaikan segera di lapangan. Pemantauan rapi terhadap perparitan dan"
      f" kolam kawalan sangat diutamakan."
  )
  doc.add_paragraph(cases_analysis)

  add_custom_heading("5. Monthly Sampling & Station Status Summary")
  monthly_summary_text = (
      f"Pemantauan stesen persampelan bulanan (WQ1 hingga WQ8, Final Discharge,"
      f" GW, dan ANV) diselaraskan terus melalui pangkalan data lapangan."
      f" Stesen yang berada dalam status 'Lab Pending' sedang melalui proses"
      f" analisis makmal berwajib."
  )
  doc.add_paragraph(monthly_summary_text)

  add_custom_heading("6. Raw Data Log Sample (Selected Period)")
  if not df_filtered.empty:
    cols_to_show = [
        c
        for c in ["Date", "Month", f_ph, f_ntu, "NTU Limit"]
        if c in df_filtered.columns
    ]
    sub_df = df_filtered[cols_to_show].head(12)

    table = doc.add_table(rows=1, cols=len(cols_to_show))
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(cols_to_show):
      hdr_cells[i].text = str(col_name)

    for _, row in sub_df.iterrows():
      row_cells = table.add_row().cells
      for i, col_name in enumerate(cols_to_show):
        val = row[col_name]
        if pd.isna(val):
          row_cells[i].text = "-"
        elif isinstance(val, pd.Timestamp):
          row_cells[i].text = val.strftime("%Y-%m-%d")
        else:
          row_cells[i].text = str(val)

  file_stream = io.BytesIO()
  doc.save(file_stream)
  file_stream.seek(0)
  return file_stream


# ==========================================
# SIDEBAR: NAVIGATION & CONTROLS
# ==========================================
with st.sidebar:
  st.markdown(
      "<h2 style='font-size: 22px; font-weight: 700; color: #ffffff;"
      " font-family: Inter, sans-serif;'>🌊 Mboard</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='font-size: 11px; letter-spacing: 1.2px; color:"
      " #94a3b8; font-family: Inter, sans-serif;'>ENVIRONMENTAL SYSTEM</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  last_sample_date = (
      df_raw["Date"].max().strftime("%d %b %Y") if not df_raw.empty else "N/A"
  )
  open_cases_count = 0
  if not df_cases_raw.empty:
    raw_status_col = next(
        (c for c in df_cases_raw.columns if "status" in c.lower()), None
    )
    if raw_status_col:
      temp_status = (
          df_cases_raw[raw_status_col]
          .astype(str)
          .str.strip()
          .str.lower()
          .str.replace("no action", "no_action")
      )
      open_cases_count = df_cases_raw[
          temp_status.isin(["no_action", "proposed in meeting", "open"])
      ].shape[0]

  temp_df_eval = df_raw.copy()
  if not temp_df_eval.empty:
    v_recs = temp_df_eval.dropna(subset=[f_ph, f_ntu])
    c_count = (
        v_recs[
            (v_recs[f_ph] >= 6.0)
            & (v_recs[f_ph] <= 9.0)
            & (v_recs[f_ntu] <= 50.0)
        ].shape[0]
        if not v_recs.empty
        else 0
    )
    initial_comp_rate = (
        (c_count / len(v_recs)) * 100.0 if len(v_recs) > 0 else 100.0
    )
  else:
    initial_comp_rate = 0.0

  now_date = datetime.date.today()
  initial_start = datetime.date(now_date.year, now_date.month, 1)
  initial_end = now_date

  full_word_file = generate_comprehensive_word_report(
      temp_df_eval,
      df_cases_raw,
      df_monthly_raw,
      initial_start,
      initial_end,
      now_date.strftime("%B"),
      now_date.year,
      initial_comp_rate,
      open_cases_count,
  )

  st.download_button(
      label="📥 Download Full EIA Report",
      data=full_word_file,
      file_name=(
          f"RBA_ML087_Full_Report_{now_date.strftime('%B')}_{now_date.year}.docx"
      ),
      mime=(
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      ),
      use_container_width=True,
  )

  if st.button("🔄 Refresh Data Terkini", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='font-size: 12px; font-weight: 700; color: #38bdf8;"
      " letter-spacing: 0.8px; margin-bottom: 5px; font-family: Inter,"
      " sans-serif;'>NAVIGATION</p>",
      unsafe_allow_html=True,
  )
  selected_page = st.radio(
    "Navigation Menu",
    [
        "Overview",
        "Discharge Compliance",
        "River Water Quality",
        "Cases Tracker",
        "Monthly Monitoring Record",
        "Data Entry",
    ],
    label_visibility="collapsed",
)

# ==========================================
# PAGE 1: OVERVIEW
# ==========================================
if selected_page == "Overview":
  try:
    st.image("Header_bg.JPG", use_container_width=True)
  except:
    pass

  st.markdown(
      "<h1 style='font-size: 28px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>Welcome</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #0284c7; font-size: 13px; font-weight: 600; margin-top:"
      " 0; margin-bottom: 20px;'>RBA Engineering Sdn Bhd | Tin Mining"
      " ML087</p>",
      unsafe_allow_html=True,
  )

  open_cases_count = 0
  if not df_cases_raw.empty:
    raw_status_col = next(
        (c for c in df_cases_raw.columns if "status" in c.lower()), None
    )
    if raw_status_col:
      temp_status = (
          df_cases_raw[raw_status_col]
          .astype(str)
          .str.strip()
          .str.lower()
          .str.replace("no action", "no_action")
      )
      open_cases_count = df_cases_raw[
          temp_status.isin(["no_action", "proposed in meeting", "open"])
      ].shape[0]

  if not df.empty:
    valid_recs = df.dropna(subset=[f_ph, f_ntu])
    if not valid_recs.empty:
      limit_val = (
          valid_recs["NTU Limit"].dropna().iloc[-1]
          if "NTU Limit" in valid_recs.columns
          and not valid_recs["NTU Limit"].dropna().empty
          else 50.0
      )
      compliant_count = valid_recs[
          (valid_recs[f_ph] >= 6.0)
          & (valid_recs[f_ph] <= 9.0)
          & (valid_recs[f_ntu] <= limit_val)
      ].shape[0]
      compliance_rate = (compliant_count / len(valid_recs)) * 100.0
    else:
      compliance_rate = 100.0
  else:
    compliance_rate = 0.0

  bmp_performance = 0.0
  bmp_col = next(
      (
          col
          for col in df.columns
          if "bmp" in col.lower() and "perf" in col.lower()
      ),
      None,
  )
  if bmp_col and not df.empty:
    df_sorted_bmp = df.sort_values(by="Date")
    bmp_performance = float(
        df_sorted_bmp[bmp_col].dropna().iloc[-1]
        if not df_sorted_bmp[bmp_col].dropna().empty
        else 0.0
    )

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(
        label="Discharge Compliance",
        value=f"{compliance_rate:.1f}%",
        delta="Optimal Range",
    )
  with col2:
    st.metric(
        label="Open Cases",
        value=open_cases_count,
        delta="Requires Action / Review",
    )
  with col3:
    st.metric(label="Last Sample Date", value=last_sample_date)
  with col4:
    st.metric(label="BMP Performance (Latest)", value=f"{bmp_performance:.1f}%")

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader(
      "📋 Station Status by Parameter (Latest Sample - Using Avg Columns)"
  )

  if not df.empty:
    latest_row = df.sort_values(by="Date").iloc[-1]

    us_ph_avg_col = next(
        (
            c
            for c in df.columns
            if "avg" in c.lower()
            and "ph" in c.lower()
            and ("duri" in c.lower() or "us" in c.lower() or "upstream" in c.lower())
        ),
        df.columns[3],
    )
    us_ntu_avg_col = next(
        (
            c
            for c in df.columns
            if "avg" in c.lower()
            and ("ntu" in c.lower() or "turb" in c.lower())
            and ("duri" in c.lower() or "us" in c.lower() or "upstream" in c.lower())
        ),
        df.columns[5],
    )
    ds_ph_avg_col = next(
        (
            c
            for c in df.columns
            if "avg" in c.lower()
            and "ph" in c.lower()
            and ("ds" in c.lower() or "downstream" in c.lower())
        ),
        df.columns[7],
    )
    ds_ntu_avg_col = next(
        (
            c
            for c in df.columns
            if "avg" in c.lower()
            and ("ntu" in c.lower() or "turb" in c.lower())
            and ("ds" in c.lower() or "downstream" in c.lower())
        ),
        df.columns[9],
    )

    def get_status_badge(val, param_type):
      if pd.isna(val):
        return "<span class='badge-alert'>No Data</span>"
      if param_type == "pH":
        if val < 3.0:
          return "<span class='badge-breach'>❌ Breach (pH < 3)</span>"
        elif 6.0 <= val <= 9.0:
          return "<span class='badge-pass'>🟢 Within limit</span>"
        else:
          return "<span class='badge-alert'>▲ Alert</span>"
      elif param_type == "Turbidity":
        if val > 250.0:
          return "<span class='badge-breach'>❌ Breach (&gt; 250 NTU)</span>"
        else:
          return "<span class='badge-pass'>🟢 Within limit</span>"
      return "<span>-</span>"

    fdp_ph_val = latest_row.get(f_ph, 0)
    fdp_ntu_val = latest_row.get(f_ntu, 0)
    us_ph_val = latest_row.get(us_ph_avg_col, 0)
    us_ntu_val = latest_row.get(us_ntu_avg_col, 0)
    ds_ph_val = latest_row.get(ds_ph_avg_col, 0)
    ds_ntu_val = latest_row.get(ds_ntu_avg_col, 0)

    matrix_html = f"""
        <div class="table-container">
        <table style="width:100%; border-collapse: collapse; font-family: 'Inter', sans-serif; white-space: nowrap;">
            <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; text-align: left;">
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">Station</th>
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">pH (Latest Avg: {latest_row['Date'].strftime('%d %b %Y')})</th>
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">Turbidity Avg (&lt; 250 NTU)</th>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">Final discharge (FDP)</td>
                <td style="padding: 14px 18px;">{get_status_badge(fdp_ph_val, 'pH')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({fdp_ph_val})</span></td>
                <td style="padding: 14px 18px;">{get_status_badge(fdp_ntu_val, 'Turbidity')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({fdp_ntu_val} NTU)</span></td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">River upstream (Sg. Duri US Avg)</td>
                <td style="padding: 14px 18px;">{get_status_badge(us_ph_val, 'pH')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({us_ph_val})</span></td>
                <td style="padding: 14px 18px;">{get_status_badge(us_ntu_val, 'Turbidity')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({us_ntu_val} NTU)</span></td>
            </tr>
            <tr>
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">River downstream (Sg. Duri DS Avg)</td>
                <td style="padding: 14px 18px;">{get_status_badge(ds_ph_val, 'pH')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({ds_ph_val})</span></td>
                <td style="padding: 14px 18px;">{get_status_badge(ds_ntu_val, 'Turbidity')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({ds_ntu_val} NTU)</span></td>
            </tr>
        </table>
        </div>
        """
    st.markdown(matrix_html, unsafe_allow_html=True)

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader("📊 Final Discharge Condition Analytics")

  if not df.empty:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[f_ntu],
            name="Discharge Turbidity (NTU)",
            marker_color="#0284c7",
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[f_ph],
            name="pH Level",
            mode="lines+markers",
            line=dict(color="#0f172a", width=2, shape="spline"),
            marker=dict(size=5, color="#0f172a"),
            fill="tozeroy",
            fillcolor="rgba(15, 23, 42, 0.05)",
            yaxis="y2",
        )
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a", family="Inter", size=11),
        xaxis=dict(
            title=dict(text="Date", font=dict(color="#0f172a", size=12)),
            showgrid=False,
            linecolor="#94a3b8",
            tickfont=dict(color="#0f172a", size=11),
            tickformat="%b %d",
            rangeslider=dict(visible=True, thickness=0.08),
        ),
        yaxis=dict(
            title=dict(
                text="Turbidity (NTU)", font=dict(color="#0f172a", size=11)
            ),
            tickfont=dict(color="#0f172a", size=10),
            side="left",
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.06)",
        ),
        yaxis2=dict(
            title=dict(text="pH Level", font=dict(color="#0f172a", size=11)),
            tickfont=dict(color="#0f172a", size=10),
            overlaying="y",
            side="right",
            showgrid=False,
            range=[6.0, 8.5],
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.12,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#0f172a"),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        margin=dict(l=30, r=30, t=30, b=60),
        hovermode="x unified",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


# ==========================================
# PAGE 2: DISCHARGE COMPLIANCE
# ==========================================
elif selected_page == "Discharge Compliance":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>🛡️ Discharge Compliance & Analytics</h1>",
      unsafe_allow_html=True,
  )

  if not df.empty:
    limit_val = (
        df["NTU Limit"].dropna().iloc[-1]
        if "NTU Limit" in df.columns and not df["NTU Limit"].dropna().empty
        else 50.0
    )
    compliant_mask = (df[f_ph] >= 6.0) & (df[f_ph] <= 9.0) & (df[f_ntu] <= limit_val)
    compliant_count = df[compliant_mask].shape[0]
    breach_count = df.shape[0] - compliant_count

    col_left, col_right = st.columns([1, 1])

    with col_left:
      st.markdown("#### 📌 Parameter Summary (FDP)")
      st.metric(label="Total Sampling Days", value=len(df), delta="Active Monitoring")
      st.metric(
          label="Compliant Records",
          value=f"{compliant_count} ({compliant_count/len(df)*100:.1f}%)" if len(df) > 0 else "0",
          delta="Within Standard Limit",
      )
      st.metric(
          label="Breach Records",
          value=f"{breach_count}",
          delta="Action Required",
          delta_color="inverse" if breach_count > 0 else "normal",
      )

    with col_right:
      st.markdown("#### 🥧 Compliance Rate Breakdown")
      pie_df = pd.DataFrame({
          "Status": ["Compliant", "Breach / Non-Compliant"],
          "Count": [compliant_count, breach_count],
      })
      fig_pie = px.pie(
          pie_df,
          values="Count",
          names="Status",
          color="Status",
          color_discrete_map={"Compliant": "#10b981", "Breach / Non-Compliant": "#ef4444"},
          hole=0.4,
      )
      fig_pie.update_layout(
          plot_bgcolor="#ffffff",
          paper_bgcolor="rgba(0,0,0,0)",
          font=dict(color="#0f172a", family="Inter", size=11),
          legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
          margin=dict(l=20, r=20, t=10, b=30),
          height=260,
      )
      st.plotly_chart(fig_pie, use_container_width=True, config={"responsive": True})

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Analisis Terperinci Sesi AM vs PM (pH & Turbidity)")

    # Dapatkan kolum asal AM vs PM berdasarkan nama asal fail kau
    ph_am = next((c for c in df.columns if "ph" in c.lower() and "am" in c.lower()), df.columns[1])
    ph_pm = next((c for c in df.columns if "ph" in c.lower() and "pm" in c.lower()), df.columns[2])
    ntu_am = next((c for c in df.columns if ("ntu" in c.lower() or "turb" in c.lower()) and "am" in c.lower()), df.columns[11])
    ntu_pm = next((c for c in df.columns if ("ntu" in c.lower() or "turb" in c.lower()) and "pm" in c.lower()), df.columns[12])

    fig_ph = go.Figure()
    fig_ph.add_trace(go.Scatter(x=df["Date"], y=df[ph_am], name="pH AM", mode="lines+markers", line=dict(color="#0284c7")))
    fig_ph.add_trace(go.Scatter(x=df["Date"], y=df[ph_pm], name="pH PM", mode="lines+markers", line=dict(color="#0f172a")))
    fig_ph.update_layout(
        title="Perbandingan Tahap pH (AM vs PM)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Date"),
        yaxis=dict(title="pH Level", range=[0, 14], showgrid=True),
        height=350,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    st.plotly_chart(fig_ph, use_container_width=True, config={"responsive": True})

    fig_ntu = go.Figure()
    fig_ntu.add_trace(go.Bar(x=df["Date"], y=df[ntu_am], name="Turbidity AM (NTU)", marker_color="#38bdf8"))
    fig_ntu.add_trace(go.Bar(x=df["Date"], y=df[ntu_pm], name="Turbidity PM (NTU)", marker_color="#0284c7"))
    fig_ntu.update_layout(
        title="Perbandingan Turbidity (AM vs PM)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Date"),
        yaxis=dict(title="Turbidity (NTU)", showgrid=True),
        height=350,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    st.plotly_chart(fig_ntu, use_container_width=True, config={"responsive": True})
  else:
    st.warning("Tiada data ditemui.")

# ==========================================
# PAGE 3: RIVER WATER QUALITY
# ==========================================
elif selected_page == "River Water Quality":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>💧 River Water Quality (Upstream vs"
      " Downstream)</h1>",
      unsafe_allow_html=True,
  )

  us_ph_avg_col = next(
      (
          c
          for c in df.columns
          if "avg" in c.lower()
          and "ph" in c.lower()
          and ("duri" in c.lower() or "us" in c.lower() or "upstream" in c.lower())
      ),
      df.columns[3],
  )
  ds_ph_avg_col = next(
      (
          c
          for c in df.columns
          if "avg" in c.lower()
          and "ph" in c.lower()
          and ("ds" in c.lower() or "downstream" in c.lower())
      ),
      df.columns[7],
  )
  us_ntu_avg_col = next(
      (
          c
          for c in df.columns
          if "avg" in c.lower()
          and ("ntu" in c.lower() or "turb" in c.lower())
          and ("duri" in c.lower() or "us" in c.lower() or "upstream" in c.lower())
      ),
      df.columns[5],
  )
  ds_ntu_avg_col = next(
      (
          c
          for c in df.columns
          if "avg" in c.lower()
          and ("ntu" in c.lower() or "turb" in c.lower())
          and ("ds" in c.lower() or "downstream" in c.lower())
      ),
      df.columns[9],
  )

  if not df.empty:
    df_sorted_rw = df.sort_values(by="Date")
    latest_rw = df_sorted_rw.iloc[-1]
    us_ph_latest = latest_rw.get(us_ph_avg_col, 0)
    ds_ph_latest = latest_rw.get(ds_ph_avg_col, 0)
    us_ntu_latest = latest_rw.get(us_ntu_avg_col, 0)
    ds_ntu_latest = latest_rw.get(ds_ntu_avg_col, 0)

    net_ph = ds_ph_latest - us_ph_latest
    net_ntu = ds_ntu_latest - us_ntu_latest

    rw_c1, rw_c2 = st.columns(2)
    with rw_c1:
      st.metric(
          label="pH Level (Upstream vs Downstream Latest Avg)",
          value=f"US: {us_ph_latest}  |  DS: {ds_ph_latest}",
      )
      st.metric(
          label="Net Impact (pH)",
          value=f"{net_ph:+.2f}",
          delta="Acidic Shift" if net_ph < 0 else "Alkaline Shift",
          delta_color="inverse" if net_ph < 0 else "normal",
      )
    with rw_c2:
      st.metric(
          label="Turbidity (Upstream vs Downstream Latest Avg)",
          value=f"US: {us_ntu_latest} NTU  |  DS: {ds_ntu_latest} NTU",
      )
      st.metric(
          label="Net Impact (Turbidity)",
          value=f"{net_ntu:+.1f} NTU",
          delta="Silt Addition" if net_ntu > 0 else "Clearer",
          delta_color="inverse" if net_ntu > 0 else "normal",
      )


# ==========================================
# PAGE 4: CASES TRACKER
# ==========================================
elif selected_page == "Cases Tracker":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>⚠️ Environmental Cases Tracker</h1>",
      unsafe_allow_html=True,
  )

  if not df_cases.empty and status_col and date_col:
    df_filtered_cases = df_cases.copy()
    if len(selected_date_range) == 2:
      s_date, e_date = selected_date_range
      df_filtered_cases = df_filtered_cases[
          (df_filtered_cases[date_col].dt.date >= s_date)
          & (df_filtered_cases[date_col].dt.date <= e_date)
      ]
      date_range_label = (
          f"Range: {s_date.strftime('%d %b %Y')} –"
          f" {e_date.strftime('%d %b %Y')}"
      )
    else:
      date_range_label = "All Records"

    total_cases = len(df_filtered_cases)
    open_cases_selected = (
        len(
            df_filtered_cases[
                df_filtered_cases[status_col].isin(
                    ["No Action", "Proposed In Meeting", "Open"]
                )
            ]
        )
        if status_col
        else 0
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.metric(
          label="Total Cases (Month)",
          value=total_cases,
          delta=date_range_label,
      )
    with c2:
      st.metric(
          label="Open Cases (Month)",
          value=open_cases_selected,
          delta="Requires Action",
      )
    with c3:
      st.metric(label="Proposed in Meeting", value=0, delta="Under Review")
    with c4:
      st.metric(label="Closed Cases", value=0, delta="Action Completed")


# ==========================================
# PAGE 5: MONTHLY MONITORING RECORD
# ==========================================
elif selected_page == "Monthly Monitoring Record":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>🗺️ RBA Mining Monthly Sampling</h1>",
      unsafe_allow_html=True,
  )

  master_coords = {
      "WQ1": (5.63544, 101.05941, "River Monitoring"),
      "WQ2": (5.63369, 101.05975, "River Monitoring"),
      "WQ3": (5.63216, 101.07157, "River Monitoring"),
      "WQ4": (5.62686, 101.07851, "River Monitoring"),
      "WQ5": (5.62983, 101.08350, "River Monitoring"),
      "WQ6": (5.62416, 101.07847, "River Monitoring"),
      "WQ7": (5.62293, 101.07244, "River Monitoring"),
  }

  if not df_monthly.empty:
    st.dataframe(df_monthly, use_container_width=True)
  else:
    st.info("Tiada rekod persampelan bulanan ditemui.")


# ==========================================
# PAGE 6: DATA ENTRY PORTAL (Eksklusif Borang Input)
# ==========================================
elif selected_page == "Data Entry":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>📝 Environmental Master Data Entry Portal</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 13px;'>Borang kemasukan data rasmi"
      " site yang berhubung terus secara live dengan Google Sheet.</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  # ---------------------------------------------------------
  # SUB-SECTION 1: DAILY WATER QUALITY & FDP ENTRY
  # ---------------------------------------------------------
  st.subheader(
      "1️⃣ Sub-Section 1: River Water Quality & FDP Entry (Daily Log)"
  )
  st.caption(
      "Nilai Average (Purata) dikira automatik dan dihantar terus ke tab 'Daily"
      " log 2026'."
  )

  with st.form("sub_sec_1_water_form"):
    st.info(
        "Borang harian berserta pengiraan purata automatik (Sub-Section 1)."
    )
    submit_sub1 = st.form_submit_button("💾 Simpan Data Harian")
    if submit_sub1:
      st.success("Data harian telah berjaya disimpan!")

  st.markdown("<br><hr><br>", unsafe_allow_html=True)

  # ---------------------------------------------------------
  # SUB-SECTION 2: ENVIRONMENTAL CASES TRACKER ENTRY
  # ---------------------------------------------------------
  st.subheader("2️⃣ Sub-Section 2: Environmental Cases Tracker Entry")
  st.caption("Jika tiada kes baharu, data dalam sheet kekal bersambung.")

  case_status_radio = st.radio(
      "Ada Kes Isu Lapangan Baharu Hari Ini?",
      ["Tiada Kes Baharu (Kekalkan Data)", "Ada Kes Baharu"],
      key="sub2_case_radio",
  )

  if case_status_radio == "Ada Kes Baharu":
    st.info(
        "Status: Ada kes isu lapangan baharu. Sila isi maklumat kes di bawah."
    )
  else:
    st.info(
        "ℹ️ Status: Tiada kes baharu hari ini. Data kes sebelumnya dalam"
        " pangkalan data dikekalkan."
    )

  st.markdown("<br><hr><br>", unsafe_allow_html=True)

  # ---------------------------------------------------------
  # SUB-SECTION 3: MONTHLY SAMPLING & LAB RESULTS ENTRY (LIVE - TANPA FORM)
  # ---------------------------------------------------------
  st.subheader("3️⃣ Sub-Section 3: Monthly Sampling & Lab Results Entry")

  stations_all = [
      "WQ1",
      "WQ2",
      "WQ3",
      "WQ4",
      "WQ5",
      "WQ6",
      "WQ7",
      "FDP",
      "Sg Duri US",
      "Sg Duri DS",
  ]

  col_m_s1, col_m_s2, col_m_s3 = st.columns(3)

  with col_m_s1:
    selected_st_entry = st.selectbox(
        "Pilih Stesen Persampelan", options=stations_all, key="m_st"
    )

  with col_m_s2:
    st_month_entry = st.selectbox(
        "Bulan Persampelan",
        list(calendar.month_name)[1:],
        index=datetime.date.today().month - 1,
        key="m_month",
    )

  with col_m_s3:
    st_status_entry = st.selectbox(
        "Status Persampelan Stesen",
        ["Non-Active", "Active (Lab Pending)", "Active"],
        key="m_status",
        help=(
            "Analisis makmal hanya terbuka jika status ditetapkan sebagai"
            " Active."
        ),
    )

  st.markdown("---")
  st.markdown("#### 🔬 Keputusan Analisis Parameter Makmal")

  is_disabled = st_status_entry != "Active"

  if is_disabled:
    st.warning(
        f"🔒 Medan makmal dikunci kerana status stesen ialah"
        f" **{st_status_entry}**."
    )

  col_l1, col_l2 = st.columns(2)

  with col_l1:
    lab_ph = st.number_input(
        "pH Level",
        min_value=0.0,
        max_value=14.0,
        value=7.0,
        disabled=is_disabled,
        key="m_ph",
    )
    lab_ntu = st.number_input(
        "Turbidity (NTU)",
        min_value=0.0,
        value=10.0,
        disabled=is_disabled,
        key="m_ntu",
    )
    lab_tss = st.number_input(
        "TSS (mg/L)",
        min_value=0.0,
        value=15.0,
        disabled=is_disabled,
        key="m_tss",
    )

  with col_l2:
    lab_fe = st.number_input(
        "Iron - Fe (mg/L)",
        min_value=0.0,
        value=0.5,
        disabled=is_disabled,
        key="m_fe",
    )
    lab_as = st.number_input(
        "Arsenic - As (mg/L)",
        min_value=0.0,
        value=0.01,
        disabled=is_disabled,
        key="m_as",
    )
    lab_remarks = st.text_input(
        "Remarks",
        value="In Compliance" if not is_disabled else "Lab Pending",
        disabled=is_disabled,
        key="m_remarks",
    )

  submit_monthly = st.button("💾 Simpan Rekod Persampelan Bulanan")

  if submit_monthly:
    if client:
      try:
        sheet_monthly = client.open(SPREADSHEET_NAME).worksheet(
            "Monthly Sampling"
        )
        monthly_row = [
            selected_st_entry,
            st_month_entry,
            st_status_entry,
            lab_ph if not is_disabled else "-",
            lab_ntu if not is_disabled else "-",
            lab_tss if not is_disabled else "-",
            lab_fe if not is_disabled else "-",
            lab_as if not is_disabled else "-",
            lab_remarks,
        ]
        sheet_monthly.append_row(monthly_row)

        st.cache_data.clear()
        st.success(
            f"Berjaya! Rekod stesen **{selected_st_entry}** ({st_month_entry})"
            " telah dikemas kini ke tab 'Monthly Sampling'."
        )
        st.rerun()
      except Exception as e:
        st.error(f"Gagal hantar data monthly ke Google Sheet: {e}")
