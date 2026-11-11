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

  st.markdown("---")
  st.markdown(
      "<p style='font-size: 12px; font-weight: 700; color: #38bdf8;"
      " letter-spacing: 0.8px; margin-bottom: 5px; font-family: Inter,"
      " sans-serif;'>DATA FILTERS</p>",
      unsafe_allow_html=True,
  )

df = df_raw.copy()
df_cases = df_cases_raw.copy()

status_col = next((c for c in df_cases.columns if "status" in c.lower()), None)
date_col = next(
    (c for c in df_cases.columns if "date" in c.lower() or "raised" in c.lower()),
    None,
)
issue_col = next((c for c in df_cases.columns if "issue" in c.lower()), None)
loc_col = next((c for c in df_cases.columns if "location" in c.lower()), None)

if status_col:
  df_cases[status_col] = (
      df_cases[status_col].astype(str).str.strip().str.title()
  )

# 1. Filter Year
years = sorted(df["Year"].unique(), reverse=True)
current_year_val = datetime.date.today().year
default_year_idx = (
    years.index(current_year_val) + 1
    if current_year_val in years
    else (1 if len(years) > 0 else 0)
)

selected_year = st.sidebar.selectbox(
    "Select Year", options=["All"] + list(years), index=default_year_idx
)
if selected_year != "All":
  df = df[df["Year"] == selected_year]

# 2. Filter Month
all_months_options = list(calendar.month_name)[1:]
current_month_name = datetime.date.today().strftime("%B")
default_month_idx = (
    all_months_options.index(current_month_name)
    if current_month_name in all_months_options
    else 9
)

selected_month = st.sidebar.selectbox(
    "Select Month", options=all_months_options, index=default_month_idx
)

if selected_month:
  df = df[df["Month"] == selected_month]

# 3. Date Range Terkawal
selected_year_int = (
    int(selected_year)
    if selected_year != "All"
    else (df["Year"].max() if not df.empty else datetime.date.today().year)
)
selected_month_num = list(calendar.month_name).index(selected_month)

num_days = calendar.monthrange(selected_year_int, selected_month_num)[1]
month_start_date = datetime.date(selected_year_int, selected_month_num, 1)
today_d = datetime.date.today()
if (
    selected_year_int == today_d.year
    and selected_month_num == today_d.month
    and today_d.day <= num_days
):
  month_end_date = today_d
else:
  month_end_date = datetime.date(selected_year_int, selected_month_num, num_days)

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(month_start_date, month_end_date),
    min_value=datetime.date(selected_year_int, selected_month_num, 1),
    max_value=datetime.date(selected_year_int, selected_month_num, num_days),
)

if len(selected_date_range) == 2:
  s_date, e_date = selected_date_range
  df = df[(df["Date"].dt.date >= s_date) & (df["Date"].dt.date <= e_date)]


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
      " margin-bottom: 2px;'>🛡️ Discharge Compliance</h1>",
      unsafe_allow_html=True,
  )

  ph_am_col = next(
      (
          c
          for c in df.columns
          if "ph" in c.lower()
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("am" in c.lower() or "pagang" in c.lower())
      ),
      df.columns[1],
  )
  ph_pm_col = next(
      (
          c
          for c in df.columns
          if "ph" in c.lower()
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("pm" in c.lower() or "petang" in c.lower())
      ),
      df.columns[2],
  )
  ntu_am_col = next(
      (
          c
          for c in df.columns
          if ("ntu" in c.lower() or "turb" in c.lower())
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("am" in c.lower() or "pagang" in c.lower())
      ),
      df.columns[11],
  )
  ntu_pm_col = next(
      (
          c
          for c in df.columns
          if ("ntu" in c.lower() or "turb" in c.lower())
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("pm" in c.lower() or "petang" in c.lower())
      ),
      df.columns[12],
  )

  if not df.empty:
    df_ph_stacked = pd.melt(
        df,
        id_vars=["Date"],
        value_vars=[ph_am_col, ph_pm_col],
        value_name="pH",
    ).dropna(subset=["pH"])
    min_ph_val = df_ph_stacked["pH"].min() if not df_ph_stacked.empty else 0.0
    min_ph_date = (
        df_ph_stacked.loc[df_ph_stacked["pH"].idxmin(), "Date"].strftime(
            "%d %b %Y"
        )
        if not df_ph_stacked.empty
        else "N/A"
    )

    if min_ph_val < 6.0:
      ph_delta_label = "⚠️ Warning Alert (Acidic)"
      ph_delta_color = "inverse"
    else:
      ph_delta_label = "Optimal Range"
      ph_delta_color = "normal"

    df_ntu_stacked = pd.melt(
        df,
        id_vars=["Date"],
        value_vars=[ntu_am_col, ntu_pm_col],
        value_name="NTU",
    ).dropna(subset=["NTU"])
    max_ntu_val = df_ntu_stacked["NTU"].max() if not df_ntu_stacked.empty else 0.0
    max_ntu_date = (
        df_ntu_stacked.loc[df_ntu_stacked["NTU"].idxmax(), "Date"].strftime(
            "%d %b %Y"
        )
        if not df_ntu_stacked.empty
        else "N/A"
    )

    start_date_str = df["Date"].min().strftime("%d %b %Y")
    end_date_str = df["Date"].max().strftime("%d %b %Y")

    limit_val = (
        df["NTU Limit"].dropna().iloc[-1]
        if "NTU Limit" in df.columns and not df["NTU Limit"].dropna().empty
        else 50.0
    )
    compliant_mask = (
        (df[f_ph] >= 6.0) & (df[f_ph] <= 9.0) & (df[f_ntu] <= limit_val)
    )
    compliant_count = df[compliant_mask].shape[0]
    breach_count = df.shape[0] - compliant_count

    col_left, col_right = st.columns([1, 1])

    with col_left:
      st.markdown(
          f"#### 📌 Parameter Extremes ({start_date_str} – {end_date_str})"
      )
      st.markdown("<br>", unsafe_allow_html=True)
      st.metric(
          label=f"Lowest pH Recorded (FDP) • {min_ph_date}",
          value=f"{min_ph_val:.2f}",
          delta=ph_delta_label,
          delta_color=ph_delta_color,
      )
      st.markdown("<br>", unsafe_allow_html=True)
      st.metric(
          label=f"Max Turbidity Recorded (FDP) • {max_ntu_date}",
          value=f"{max_ntu_val:.1f} NTU",
          delta="Peak Turbidity",
          delta_color="inverse" if max_ntu_val > 250 else "normal",
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
          color_discrete_map={
              "Compliant": "#10b981",
              "Breach / Non-Compliant": "#ef4444",
          },
          hole=0.4,
      )
      fig_pie.update_layout(
          plot_bgcolor="#ffffff",
          paper_bgcolor="rgba(0,0,0,0)",
          font=dict(color="#0f172a", family="Inter", size=11),
          legend=dict(
              orientation="h",
              yanchor="bottom",
              y=-0.1,
              xanchor="center",
              x=0.5,
              font=dict(size=10, color="#0f172a"),
          ),
          margin=dict(l=20, r=20, t=10, b=30),
          height=260,
      )
      st.plotly_chart(
          fig_pie, use_container_width=True, config={"responsive": True}
      )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("pH of Final Discharge (AM vs PM)")

    fig_ph = go.Figure()
    fig_ph.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[ph_am_col],
            name="AM Reading",
            mode="lines+markers",
            line=dict(color="#0f172a", width=2, shape="spline"),
        )
    )
    fig_ph.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[ph_pm_col],
            name="PM Reading",
            mode="lines+markers",
            line=dict(color="#d97706", width=2, shape="spline"),
        )
    )
    fig_ph.update_layout(
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
            title=dict(text="pH Level", font=dict(color="#0f172a", size=11)),
            tickfont=dict(color="#0f172a", size=10),
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.06)",
        ),
        margin=dict(l=30, r=30, t=30, b=60),
        height=380,
    )
    st.plotly_chart(
        fig_ph, use_container_width=True, config={"responsive": True}
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Turbidity AM Reading and PM Reading by Day (NTU)")

    fig_ntu = go.Figure()
    fig_ntu.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[ntu_am_col],
            name="AM Reading",
            marker_color="#0f172a",
        )
    )
    fig_ntu.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[ntu_pm_col],
            name="PM Reading",
            marker_color="#d97706",
        )
    )
    fig_ntu.update_layout(
        barmode="group",
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
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.06)",
        ),
        margin=dict(l=30, r=30, t=30, b=60),
        height=380,
    )
    st.plotly_chart(
        fig_ntu, use_container_width=True, config={"responsive": True}
    )

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

  us_ph_am = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "us" in c.lower()
          and "ph" in c.lower()
          and "am" in c.lower()
      ),
      df.columns[3],
  )
  us_ph_pm = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "us" in c.lower()
          and "ph" in c.lower()
          and "pm" in c.lower()
      ),
      df.columns[4],
  )
  ds_ph_am = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "ds" in c.lower()
          and "ph" in c.lower()
          and "am" in c.lower()
      ),
      df.columns[7],
  )
  ds_ph_pm = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "ds" in c.lower()
          and "ph" in c.lower()
          and "pm" in c.lower()
      ),
      df.columns[8],
  )

  us_ntu_am = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "us" in c.lower()
          and "ntu" in c.lower()
          and "am" in c.lower()
      ),
      df.columns[5],
  )
  us_ntu_pm = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "us" in c.lower()
          and "ntu" in c.lower()
          and "pm" in c.lower()
      ),
      df.columns[6],
  )
  ds_ntu_am = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "ds" in c.lower()
          and "ntu" in c.lower()
          and "am" in c.lower()
      ),
      df.columns[9],
  )
  ds_ntu_pm = next(
      (
          c
          for c in df.columns
          if "duri" in c.lower()
          and "ds" in c.lower()
          and "ntu" in c.lower()
          and "pm" in c.lower()
      ),
      df.columns[10],
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("pH of Sg. Duri")

    ph_session_filter = st.selectbox(
        "Select Session for pH", options=["AM", "PM"], key="ph_session"
    )

    selected_us_ph = us_ph_am if ph_session_filter == "AM" else us_ph_pm
    selected_ds_ph = ds_ph_am if ph_session_filter == "AM" else ds_ph_pm

    fig_river_ph = go.Figure()
    fig_river_ph.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[selected_us_ph],
            name="Sg. Duri Upstream",
            mode="lines+markers",
            line=dict(color="#0284c7", width=2, shape="spline"),
        )
    )
    fig_river_ph.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[selected_ds_ph],
            name="Sg. Duri Downstream",
            mode="lines+markers",
            line=dict(color="#0f172a", width=2, shape="spline"),
        )
    )
    fig_river_ph.update_layout(
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
            title=dict(text="pH Level", font=dict(color="#0f172a", size=11)),
            tickfont=dict(color="#0f172a", size=10),
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.06)",
        ),
        margin=dict(l=30, r=30, t=30, b=60),
        height=380,
    )
    st.plotly_chart(
        fig_river_ph, use_container_width=True, config={"responsive": True}
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Turbidity of Sg. Duri")

    ntu_session_filter = st.selectbox(
        "Select Session for Turbidity", options=["AM", "PM"], key="ntu_session"
    )

    selected_us_ntu = us_ntu_am if ntu_session_filter == "AM" else us_ntu_pm
    selected_ds_ntu = ds_ntu_am if ntu_session_filter == "AM" else ds_ntu_pm

    us_colors = [
        "#ef4444" if val > 250 else "#0284c7" for val in df[selected_us_ntu]
    ]
    ds_colors = [
        "#ef4444" if val > 250 else "#0f172a" for val in df[selected_ds_ntu]
    ]

    fig_river_ntu = go.Figure()
    fig_river_ntu.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[selected_us_ntu],
            name="Sg. Duri Upstream",
            marker_color=us_colors,
        )
    )
    fig_river_ntu.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[selected_ds_ntu],
            name="Sg. Duri Downstream",
            marker_color=ds_colors,
        )
    )
    fig_river_ntu.add_hline(
        y=250,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Max Limit (250 NTU)",
        annotation_position="top right",
        annotation_font=dict(color="#ef4444", size=10),
    )
    fig_river_ntu.update_layout(
        barmode="group",
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
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.06)",
        ),
        margin=dict(l=30, r=30, t=30, b=60),
        height=380,
    )
    st.plotly_chart(
        fig_river_ntu, use_container_width=True, config={"responsive": True}
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
    proposed_cases = (
        len(
            df_filtered_cases[
                df_filtered_cases[status_col]
                .str.lower()
                .str.contains("proposed")
            ]
        )
        if status_col
        else 0
    )
    closed_cases = (
        len(
            df_filtered_cases[
                df_filtered_cases[status_col].str.lower().str.contains("closed")
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
      st.metric(
          label="Proposed in Meeting",
          value=proposed_cases,
          delta="Under Review",
          delta_color="off",
      )
    with c4:
      st.metric(
          label="Closed Cases",
          value=closed_cases,
          delta="Action Completed",
          delta_color="normal",
      )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    col_t, col_d = st.columns([1.2, 1])

    with col_t:
      st.subheader("📋 Cases Summary Matrix Table (Selected Period)")
      if not df_filtered_cases.empty and loc_col and issue_col and status_col:
        matrix_table = pd.crosstab(
            index=[df_filtered_cases[loc_col], df_filtered_cases[issue_col]],
            columns=df_filtered_cases[status_col],
            margins=True,
            margins_name="Total",
        )
        st.dataframe(matrix_table, use_container_width=True)
      else:
        st.info("No cases found within the selected date filter range.")

    with col_d:
      st.subheader("🍩 Case Status Distribution (Month)")
      if len(selected_date_range) == 2:
        st.caption(
            f"📅 Date Range Evaluated:"
            f" **{selected_date_range[0].strftime('%d %b %Y')} to"
            f" {selected_date_range[1].strftime('%d %b %Y')}**"
        )
      else:
        st.caption("📅 Date Range Evaluated: **All Records**")

      if not df_filtered_cases.empty and status_col:
        status_counts = (
            df_filtered_cases[status_col].value_counts().reset_index()
        )
        status_counts.columns = ["Status", "Count"]

        fig_donut = px.pie(
            status_counts,
            values="Count",
            names="Status",
            hole=0.5,
            color="Status",
            color_discrete_map={
                "No Action": "#ef4444",
                "Proposed In Meeting": "#f59e0b",
                "Closed": "#10b981",
            },
        )
        fig_donut.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0f172a", family="Inter", size=11),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=20, r=20, t=20, b=30),
            height=320,
        )
        st.plotly_chart(
            fig_donut, use_container_width=True, config={"responsive": True}
        )
      else:
        st.warning("No data available for donut chart in this date range.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📌 Carried Forward / Outstanding Cases from Previous Months")

    if len(selected_date_range) == 2:
      prev_open_cases = df_cases[
          (df_cases[date_col].dt.date < selected_date_range[0])
          & (
              df_cases[status_col].isin(
                  ["No Action", "Proposed In Meeting", "Open"]
              )
          )
      ]

      if not prev_open_cases.empty:
        st.dataframe(prev_open_cases, use_container_width=True)
      else:
        st.success(
            "Syabas! Tiada kes tertunggak (carried forward cases) dari bulan"
            " sebelumnya."
        )
    else:
      st.info("Sila pastikan julat tarikh dipilih dengan betul.")

  else:
    st.warning("No data found in Cases Tracker sheet.")

# ==========================================
# PAGE 5: MONTHLY MONITORING RECORD
# ==========================================
elif selected_page == "Monthly Monitoring Record":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>🗺️ RBA Mining EIA Master Topography Map</h1>",
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
      "WQ8": (5.61956, 101.08815, "River Monitoring"),
      "Final Discharge": (5.63367, 101.07182, "Discharge Point"),
      "GW": (5.63561, 101.07193, "Groundwater"),
      "ANV": (5.63692, 101.09836, "Ambient Noise/Air"),
  }

  stations_list = list(master_coords.keys())

  selected_station = st.selectbox(
      "🔍 Pilih Stesen untuk Zoom Lokasi & Semakan Keputusan Makmal:",
      options=stations_list,
  )

  st_lat, st_lon, st_type = master_coords[selected_station]

  station_data = pd.DataFrame()
  raw_status_val = "Non-Active"

  try:
    if not df_monthly_raw.empty:
      stat_id_col = next(
          (c for c in df_monthly_raw.columns if "station" in c.lower()), None
      )
      stat_status_col = next(
          (c for c in df_monthly_raw.columns if "status" in c.lower()), None
      )
      month_col_monthly = next(
          (c for c in df_monthly_raw.columns if "month" in c.lower()), None
      )

      if stat_id_col:
        matched_rows = df_monthly_raw[
            df_monthly_raw[stat_id_col]
            .astype(str)
            .str.strip()
            .str.upper()
            == selected_station.upper()
        ]

        if month_col_monthly and not matched_rows.empty:
          matched_rows = matched_rows[
              matched_rows[month_col_monthly]
              .astype(str)
              .str.strip()
              .str.title()
              == selected_month.title()
          ]

        if not matched_rows.empty:
          station_data = matched_rows
          if stat_status_col:
            raw_status_val = str(
                matched_rows[stat_status_col].iloc[0]
            ).strip()
  except Exception:
    pass

  m = folium.Map(
      location=[st_lat, st_lon],
      zoom_start=14,
      tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
      attr="OpenTopoMap",
  )

  for st_name, (lat, lon, s_type) in master_coords.items():
    st_status_str = "Non-Active"
    try:
      if not df_monthly_raw.empty:
        stat_id_col = next(
            (c for c in df_monthly_raw.columns if "station" in c.lower()), None
        )
        stat_status_col = next(
            (c for c in df_monthly_raw.columns if "status" in c.lower()), None
        )
        month_col_monthly = next(
            (c for c in df_monthly_raw.columns if "month" in c.lower()), None
        )

        if stat_id_col:
          m_rows = df_monthly_raw[
              df_monthly_raw[stat_id_col]
              .astype(str)
              .str.strip()
              .str.upper()
              == st_name.upper()
          ]
          if month_col_monthly and not m_rows.empty:
            m_rows = m_rows[
                m_rows[month_col_monthly]
                .astype(str)
                .str.strip()
                .str.title()
                == selected_month.title()
            ]

          if not m_rows.empty and stat_status_col:
            st_status_str = str(m_rows[stat_status_col].iloc[0]).strip()
    except:
      pass

    st_is_active = (
        "active" in st_status_str.lower() or "pending" in st_status_str.lower()
    )
    icon_color = "green" if st_is_active else "red"
    popup_txt = (
        f"<b>Stesen: {st_name}</b><br>Kategori: {s_type}<br>Status:"
        f" {st_status_str} ({selected_month})"
    )

    if st_name == selected_station:
      folium.Marker(
          location=[lat, lon],
          popup=popup_txt,
          tooltip=f"🎯 SELECTED: {st_name}",
          icon=folium.Icon(color="blue", icon="star"),
      ).add_to(m)
    else:
      folium.Marker(
          location=[lat, lon],
          popup=popup_txt,
          tooltip=st_name,
          icon=folium.Icon(color=icon_color, icon="info-sign"),
      ).add_to(m)

  st_folium(m, width="100%", height=450)

  st.markdown("<br>", unsafe_allow_html=True)

  if "pending" in raw_status_val.lower():
    status_badge = (
        f"<span class='badge-alert'>🟡 {raw_status_val} (Sampled)</span>"
    )
  elif "active" in raw_status_val.lower():
    status_badge = f"<span class='badge-pass'>🟢 {raw_status_val}</span>"
  else:
    status_badge = f"<span class='badge-breach'>🔴 {raw_status_val}</span>"

  c_m1, c_m2, c_m3, c_m4 = st.columns(4)
  with c_m1:
    st.metric(label="Station ID", value=selected_station)
  with c_m2:
    st.metric(label="Category", value=st_type)
  with c_m3:
    st.markdown(
        f"<div style='background: #ffffff; border: 1px solid #e2e8f0; padding:"
        f" 16px; border-radius: 14px;'><p style='font-size: 11px; color:"
        f" #64748b; font-weight: 600; margin: 0;'>SAMPLING STATUS"
        f" ({selected_month})</p><div"
        f" style='margin-top: 6px;'>{status_badge}</div></div>",
        unsafe_allow_html=True,
    )
  with c_m4:
    st.metric(
        label="GPS Coordinates", value=f"{st_lat:.4f}°N, {st_lon:.4f}°E"
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader(
      f"📈 Keputusan Analisis Parameter Makmal — Stesen {selected_station}"
      f" ({selected_month})"
  )

  if not station_data.empty:
    st.dataframe(station_data, use_container_width=True)
  else:
    st.info(
        f"📌 Tiada rekod bagi stesen **{selected_station}** untuk bulan"
        f" **{selected_month}**. Status ditanda sebagai **Non-Active** (Tiada"
        " Dummy Data)."
    )

# ==========================================
# PAGE 6: DATA ENTRY (LIVE LIVE SYNC TO 3 TABS)
# ==========================================
elif selected_page == "Data Entry":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>✍️ Environmental Master Data Entry Portal</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 13px;'>Borang kemasukan data rasmi"
      " site ML087 yang berhubung terus secara live dengan Google Sheet"
      " 'Master Data Monitoring'.</p>",
      unsafe_allow_html=True,
  )

  # --------------------------------------------------------------------------
  # SUB-SECTION 1: RIVER WATER & FDP DATA ENTRY (TAB: Daily log 2026)
  # --------------------------------------------------------------------------
  st.markdown("<br>", unsafe_allow_html=True)
st.subheader("1️⃣ Sub-Section 1: River Water Quality & FDP Entry (Daily Log)")
st.caption(
    "Nilai Average (Purata) dikira automatik dan dihantar terus ke tab"
    " 'Daily log 2026'."
)

with st.form("sub_sec_1_water_form"):
  col_m1, col_m2, col_m3 = st.columns(3)
  with col_m1:
    entry_date_w = st.date_input(
        "Tarikh Rekod", value=datetime.date.today(), key="w_date"
    )
    weather_in = st.selectbox(
        "Cuaca (Weather)", ["Sunny", "Rainy", "Cloudy", "Storm"], key="w_weather"
    )
    us_ph_am_in = st.number_input(
        "Upstream pH (AM)", value=7.0, format="%.2f", key="w_us_ph_am"
    )
    us_ph_pm_in = st.number_input(
        "Upstream pH (PM)", value=7.0, format="%.2f", key="w_us_ph_pm"
    )

  with col_m2:
    us_ntu_am_in = st.number_input(
        "Upstream Turbidity NTU (AM)", value=0.0, format="%.2f", key="w_us_ntu_am"
    )
    us_ntu_pm_in = st.number_input(
        "Upstream Turbidity NTU (PM)", value=0.0, format="%.2f", key="w_us_ntu_pm"
    )
    ds_ph_am_in = st.number_input(
        "Downstream pH (AM)", value=7.0, format="%.2f", key="w_ds_ph_am"
    )
    ds_ph_pm_in = st.number_input(
        "Downstream pH (PM)", value=7.0, format="%.2f", key="w_ds_ph_pm"
    )

  with col_m3:
    ds_ntu_am_in = st.number_input(
        "Downstream Turbidity NTU (AM)",
        value=0.0,
        format="%.2f",
        key="w_ds_ntu_am",
    )
    ds_ntu_pm_in = st.number_input(
        "Downstream Turbidity NTU (PM)",
        value=0.0,
        format="%.2f",
        key="w_ds_ntu_pm",
    )
    fdp_ph_am_in = st.number_input(
        "FDP pH (AM)", value=7.0, format="%.2f", key="w_fdp_ph_am"
    )
    fdp_ph_pm_in = st.number_input(
        "FDP pH (PM)", value=7.0, format="%.2f", key="w_fdp_ph_pm"
    )

  col_m4, col_m5 = st.columns(2)
  with col_m4:
    fdp_ntu_am_in = st.number_input(
        "FDP Turbidity NTU (AM)", value=0.0, format="%.2f", key="w_fdp_ntu_am"
    )
  with col_m5:
    fdp_ntu_pm_in = st.number_input(
        "FDP Turbidity NTU (PM)", value=0.0, format="%.2f", key="w_fdp_ntu_pm"
    )

  bmp_perf_in = st.number_input(
      "BMP Performance (%)", value=100.0, format="%.2f", key="w_bmp_perf"
  )

  submit_sec1 = st.form_submit_button(
      "💾 Simpan Data Harian ke Google Sheet"
  )

  if submit_sec1:
    if client:
      try:
        sheet_tab = client.open(SPREADSHEET_NAME).worksheet("Daily log 2026")

        # Pengiraan purata automatik
        us_ph_avg = round((us_ph_am_in + us_ph_pm_in) / 2.0, 2)
        ds_ph_avg = round((ds_ph_am_in + ds_ph_pm_in) / 2.0, 2)
        fdp_ph_avg = round((fdp_ph_am_in + fdp_ph_pm_in) / 2.0, 2)
        us_ntu_avg = round((us_ntu_am_in + us_ntu_pm_in) / 2.0, 2)
        ds_ntu_avg = round((ds_ntu_am_in + ds_ntu_pm_in) / 2.0, 2)
        fdp_ntu_avg = round((fdp_ntu_am_in + fdp_ntu_pm_in) / 2.0, 2)

# Susunan TEPAT 30 kolum mengikut susunan dalam Google Sheet
        row_data = [
            str(entry_date_w),  # 1. Date
            int(entry_date_w.year),  # 2. Year
            str(weather_in),  # 3. Weather
            us_ph_am_in,  # 4. Sg.Duri US pH AM
            us_ph_pm_in,  # 5. Sg.Duri US pH PM
            us_ntu_am_in,  # 6. Sg.Duri US NTU AM
            us_ntu_pm_in,  # 7. Sg.Duri US NTU PM
            ds_ph_am_in,  # 8. Sg.Duri DS pH AM
            ds_ph_pm_in,  # 9. Sg.Duri DS pH PM
            ds_ntu_am_in,  # 10. Sg.Duri DS NTU AM
            ds_ntu_pm_in,  # 11. Sg.Duri DS NTU PM
            fdp_ph_am_in,  # 12. FDP pH AM
            fdp_ph_pm_in,  # 13. FDP pH PM
            fdp_ntu_am_in,  # 14. FDP NTU AM
            fdp_ntu_pm_in,  # 15. FDP NTU PM
            "",  # 16. Issue found
            "",  # 17. Remarks
            "",  # 18. Ongoing case
            "",  # 19. Corrective action
            "",  # 20. Case Closed
            us_ph_avg,  # 21. Avg pH Sg. Duri US
            ds_ph_avg,  # 22. Avg pH Sg. Duri DS
            fdp_ph_avg,  # 23. Avg pH FDP
            us_ntu_avg,  # 24. Avg NTU Sg.Duri US
            ds_ntu_avg,  # 25. Avg NTU Sg. Duri DS
            fdp_ntu_avg,  # 26. Avg NTU FDP
            250.0,  # 27. NTU Limit
            1.0,  # 28. BMP Okay (Tukar ikut keperluan)
            0.0,  # 29. BMP Need Maintenance (Tukar ikut keperluan)
            bmp_perf_in,  # 30. BMP Perfomance
        ]

        sheet_tab.append_row(row_data)

        # PENTING: Kosongkan cache supaya dashboard tarik data terbaru live dari Google Sheet!
        st.cache_data.clear()

        st.success(
            f"Berjaya! Data harian {entry_date_w.strftime('%d %b %Y')} telah"
            " dihantar & dashboard dikemaskini."
        )
        st.rerun()
      except Exception as e:
        st.error(f"Gagal hantar ke Google Sheet: {e}")
    else:
      st.error("Ralat: Sambungan client Google Sheet gagal diinisialisasi.")
      

  # --------------------------------------------------------------------------
  # SUB-SECTION 2: CASES TRACKER ENTRY (TAB: Cases tracker)
  # --------------------------------------------------------------------------
  st.markdown("<br><hr><br>", unsafe_allow_html=True)
  st.subheader("2️⃣ Sub-Section 2: Environmental Cases Tracker Entry")
  st.caption(
      "Jika tiada kes baharu, data dalam sheet kekal bersambung dari hari"
      " sebelumnya."
  )

  has_new_case = st.radio(
      "Ada Kes Isu Lapangan Baharu Hari Ini?",
      ["Tiada Kes Baharu (Kekalkan Data)", "Ada Kes Baharu"],
      horizontal=True,
  )

  if has_new_case == "Ada Kes Baharu":
    with st.form("sub_sec_2_cases_form"):
      col_c1, col_c2 = st.columns(2)
      with col_c1:
        case_date_raised = st.date_input(
            "Date Raised", datetime.date.today(), key="case_date"
        )
        case_location = st.text_input(
            "Location", placeholder="Cth: Toe of Bukit Rayyan"
        )
      with col_c2:
        case_issue = st.text_area(
            "Issue", placeholder="Cth: Slope Erosion / Clogged Drain"
        )
        case_status = st.selectbox(
            "Status", ["No action", "Proposed in meeting", "Closed"]
        )

      submit_sec2 = st.form_submit_button(
          "💾 Simpan Kes Baharu ke Cases tracker"
      )

      if submit_sec2:
        if client:
          try:
            sheet_cases = client.open(SPREADSHEET_NAME).worksheet("Cases tracker")
            case_row = [
                str(case_date_raised),
                case_issue,
                case_location,
                case_status,
            ]
            sheet_cases.append_row(case_row)
            st.success(
                "Berjaya! Kes baharu telah direkodkan ke tab 'Cases tracker'."
            )
          except Exception as e:
            st.error(f"Gagal hantar kes ke Google Sheet: {e}")
        else:
          st.warning("Kredensial Google Cloud tidak dikesan.")
  else:
    st.info(
        "ℹ️ Status: **Tiada kes baharu hari ini.** Data kes sebelumnya dalam"
        " pangkalan data dikekalkan."
    )

  # --------------------------------------------------------------------------
  # SUB-SECTION 3: MONTHLY MONITORING RECORD ENTRY (TAB: Monthly Sampling)
  # --------------------------------------------------------------------------
st.markdown("### 3️⃣ Sub-Section 3: Monthly Sampling & Lab Results Entry")

# 1. Pastikan senarai stesen wujud (kalau kod asal kau dah ada stations_all di atas, boleh kekalkan)
if "stations_all" not in locals() and "stations_all" not in globals():
  stations_all = ["WQ1", "WQ2", "WQ3", "FDP"]

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
      help="Analisis makmal hanya terbuka jika status ditetapkan sebagai Active.",
  )

st.markdown("---")
st.markdown("#### 🔬 Keputusan Analisis Parameter Makmal")

# Nilai ni akan bertukar secara LIVE serta-merta bila dropdown status diubah
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
      sheet_monthly = client.open(SPREADSHEET_NAME).worksheet("Monthly Sampling")
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
