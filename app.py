import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Environmental Monitoring Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Fungsi untuk baca gambar drone tempatan
def get_base64_of_bin_file(bin_file):
  try:
    with open(bin_file, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  except Exception:
    return None


img_base64 = get_base64_of_bin_file("header_bg.jpg")

# ==========================================
# SIDEBAR: THEME TOGGLE & CONTROLS
# ==========================================
with st.sidebar:
  st.markdown(
      "<h2 style='font-size: 22px; font-weight: bold; color: white;'>🌊"
      " Mboard</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='font-size: 11px; letter-spacing: 1px; color:"
      " #94a3b8;'>ENVIRONMENTAL SYSTEM</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  # Suis Pilihan Tema (Dark Mode / Light Mode)
  theme_mode = st.radio(
      "🎨 Display Theme", ["Light Mode", "Dark Mode"], index=0
  )

  st.markdown("---")
  st.markdown(
      "<p"
      " style='font-size: 13px; font-weight: bold; color: #38bdf8;"
      " margin-bottom: 5px;'>NAVIGATION</p>",
      unsafe_allow_html=True,
  )
  selected_page = st.radio(
      "Navigation Menu",
      [
          "Overview",
          "Discharge Compliance",
          "River Water Quality",
          "Cases Tracker",
      ],
      label_visibility="collapsed",
  )

  st.markdown("---")
  st.markdown(
      "<p"
      " style='font-size: 13px; font-weight: bold; color: #38bdf8;"
      " margin-bottom: 5px;'>DATA FILTERS</p>",
      unsafe_allow_html=True,
  )

# ==========================================
# DYNAMIC CSS STYLING (LIGHT VS DARK MODE)
# ==========================================
if theme_mode == "Dark Mode":
  bg_color = "#070a13"
  sidebar_bg = "#0f172a"
  text_color = "#f8fafc"
  sub_text = "#94a3b8"
  card_bg = "#1e293b"
  card_border = "1px solid #334155"
  metric_val = "#38bdf8"
  table_bg = "#1e293b"
  table_header = "#0f172a"
  plot_bg = "#1e293b"
else:
  # Stail Light Mode (Seiras Rujukan Korporat Bersih)
  bg_color = "#f4f7fc"
  sidebar_bg = "#121829"  # Sidebar gelap korporat ala rujukan
  text_color = "#1e293b"
  sub_text = "#64748b"
  card_bg = "#ffffff"
  card_border = "1px solid #e2e8f0"
  metric_val = "#0f172a"
  table_bg = "#ffffff"
  table_header = "#f8fafc"
  plot_bg = "#ffffff"

# Konfigurasi Banner Header Gambar Drone
banner_css = (
    f"""
    .custom-banner {{
        background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.8)), 
                    url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 40px 30px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }}
"""
    if img_base64
    else f"""
    .custom-banner {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 40px 30px;
        margin-bottom: 25px;
        border: {card_border};
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    }}
"""
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        color: #ffffff;
    }}
    
    [data-testid="stSidebar"] label {{
        color: #e2e8f0 !important;
        font-weight: 500;
    }}

    h1, h2, h3, h4 {{
        color: {text_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    p, span, label {{
        color: {sub_text};
    }}

    {banner_css}

    /* Stail Kad KPI Korporat Bersih Berkotak */
    div[data-testid="stMetric"] {{
        background: {card_bg};
        border: {card_border};
        padding: 20px 24px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        transition: all 0.2s ease-in-out;
    }}
    
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.06);
    }}

    [data-testid="stMetricValue"] {{
        font-size: 30px !important;
        font-weight: 700 !important;
        color: {metric_val} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 13px !important;
        color: {sub_text} !important;
        font-weight: 600 !important;
    }}

    /* Styling Badge Status Matriks */
    .badge-pass {{
        background-color: #d1fae5;
        color: #065f46;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }}
    .badge-alert {{
        background-color: #fef3c7;
        color: #92400e;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }}
    .badge-breach {{
        background-color: #fee2e2;
        color: #991b1b;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=0&single=true&output=csv"


@st.cache_data
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


try:
  df_raw = load_data()
except Exception as e:
  st.error(f"Error loading data: {e}")
  st.stop()

# Tapis Data Mengikut Sidebar
df = df_raw.copy()
years = sorted(df["Year"].unique(), reverse=True)
selected_year = st.sidebar.selectbox(
    "Select Year", options=["All"] + list(years), index=1
)
if selected_year != "All":
  df = df[df["Year"] == selected_year]

months = [m for m in df["Month"].unique() if pd.notna(m)]
selected_month = st.sidebar.multiselect(
    "Select Month", options=months, default=months
)
if selected_month:
  df = df[df["Month"].isin(selected_month)]

if not df.empty:
  min_d = df["Date"].min().date()
  max_d = df["Date"].max().date()
  selected_date_range = st.sidebar.date_input(
      "Select Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d
  )
  if len(selected_date_range) == 2:
    s_date, e_date = selected_date_range
    df = df[(df["Date"].dt.date >= s_date) & (df["Date"].dt.date <= e_date)]

# ==========================================
# MAIN CONTENT AREA
# ==========================================
if selected_page == "Overview":
  # Header Banner Gambar Drone Bergaya Rujukan
  st.markdown(
      """
    <div class="custom-banner">
        <h1 style="font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 2px;">Welcome Back, Officer 🤖</h1>
        <h3 style="font-size: 16px; font-weight: 300; color: #cbd5e1; margin-top: 0;">Your environmental telemetry control room - monitoring stations, compliance, and actions.</h3>
        <p style="color: #38bdf8; font-size: 12px; margin-top: 10px; font-weight: 600;">
            📡 RBA Engineering Active Site Telemetry
        </p>
    </div>
""",
      unsafe_allow_html=True,
  )

  # --- PENGIRAAN METRIK TULEN ---
  last_sample_date = (
      df["Date"].max().strftime("%d %b %Y") if not df.empty else "N/A"
  )

  open_cases = (
      int(df["Ongoing case"].dropna().iloc[-1])
      if "Ongoing case" in df.columns and not df["Ongoing case"].dropna().empty
      else 0
  )

  f_ph = (
      "Avg pH FDP"
      if "Avg pH FDP" in df.columns
      else [c for c in df.columns if "ph" in c.lower()][-1]
  )
  f_ntu = (
      "Avg NTU FDP"
      if "Avg NTU FDP" in df.columns
      else [c for c in df.columns if "ntu" in c.lower()][-1]
  )

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

  # 4 Kad KPI Berkotak Kemas
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(
        label="Discharge Compliance",
        value=f"{compliance_rate:.1f}%",
        delta="Optimal Range",
    )
  with col2:
    st.metric(
        label="Open Cases", value=open_cases, delta="Requires Action"
    )
  with col3:
    st.metric(label="Last Sample Date", value=last_sample_date)
  with col4:
    st.metric(
        label="BMP Performance (Latest)", value=f"{bmp_performance:.1f}%"
    )

  st.markdown("<br>", unsafe_allow_html=True)

  # ==========================================
  # STATION STATUS MATRIX TABLE
  # ==========================================
  st.subheader("📋 Station Status by Parameter (Latest Sample)")
  st.caption(
      "Dynamically updated evaluation for the latest sample date in the selected"
      " range."
  )

  if not df.empty:
    latest_row = df.sort_values(by="Date").iloc[-1]

    us_ph_col = (
        "Avg pH Sg. Duri US"
        if "Avg pH Sg. Duri US" in df.columns
        else "Sg.Duri US pH AM"
    )
    us_ntu_col = (
        "Avg NTU Sg.Duri US"
        if "Avg NTU Sg.Duri US" in df.columns
        else "Sg.Duri US NTU AM"
    )

    ds_ph_col = (
        "Avg pH Sg. Duri DS"
        if "Avg pH Sg. Duri DS" in df.columns
        else "Sg.Duri DS pH AM"
    )
    ds_ntu_col = (
        "Avg NTU Sg. Duri DS"
        if "Avg NTU Sg. Duri DS" in df.columns
        else "Sg.Duri DS NTU AM"
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

    us_ph_val = latest_row.get(us_ph_col, 0)
    us_ntu_val = latest_row.get(us_ntu_col, 0)

    ds_ph_val = latest_row.get(ds_ph_col, 0)
    ds_ntu_val = latest_row.get(ds_ntu_col, 0)

    matrix_html = f"""
        <table style="width:100%; border-collapse: collapse; background: {table_bg}; border: {card_border}; border-radius: 14px; overflow: hidden; font-family: 'Inter', sans-serif;">
            <tr style="background: {table_header}; border-bottom: 2px solid rgba(100,100,100,0.1); text-align: left;">
                <th style="padding: 16px 20px; color: {sub_text}; font-size: 13px;">Station</th>
                <th style="padding: 16px 20px; color: {sub_text}; font-size: 13px;">pH (Latest: {latest_row['Date'].strftime('%d %b %Y')})</th>
                <th style="padding: 16px 20px; color: {sub_text}; font-size: 13px;">Turbidity (&lt; 250 NTU)</th>
            </tr>
            <tr style="border-bottom: 1px solid rgba(100,100,100,0.05);">
                <td style="padding: 16px 20px; font-weight: 600; color: {text_color};">Final discharge (FDP)</td>
                <td style="padding: 16px 20px;">{get_status_badge(fdp_ph_val, 'pH')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({fdp_ph_val})</span></td>
                <td style="padding: 16px 20px;">{get_status_badge(fdp_ntu_val, 'Turbidity')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({fdp_ntu_val} NTU)</span></td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(100,100,100,0.05);">
                <td style="padding: 16px 20px; font-weight: 600; color: {text_color};">River upstream (Sg. Duri US)</td>
                <td style="padding: 16px 20px;">{get_status_badge(us_ph_val, 'pH')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({us_ph_val})</span></td>
                <td style="padding: 16px 20px;">{get_status_badge(us_ntu_val, 'Turbidity')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({us_ntu_val} NTU)</span></td>
            </tr>
            <tr>
                <td style="padding: 16px 20px; font-weight: 600; color: {text_color};">River downstream (Sg. Duri DS)</td>
                <td style="padding: 16px 20px;">{get_status_badge(ds_ph_val, 'pH')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({ds_ph_val})</span></td>
                <td style="padding: 16px 20px;">{get_status_badge(ds_ntu_val, 'Turbidity')} <span style="font-size: 12px; color: {sub_text}; margin-left: 8px;">({ds_ntu_val} NTU)</span></td>
            </tr>
        </table>
        """
    st.markdown(matrix_html, unsafe_allow_html=True)

  st.markdown("<br><br>", unsafe_allow_html=True)

  # ==========================================
  # GRAPH: FINAL DISCHARGE CONDITION ANALYTICS
  # ==========================================
  st.subheader("📊 Final Discharge Condition Analytics")

  if not df.empty:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df[f_ntu],
            name="Discharge Turbidity (NTU)",
            marker_color="#0284c7" if theme_mode == "Light Mode" else "#38bdf8",
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[f_ph],
            name="pH Level",
            mode="lines+markers",
            line=dict(color="#0f172a" if theme_mode == "Light Mode" else "#fbbf24", width=2.5, shape="spline"),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(15, 23, 42, 0.05)" if theme_mode == "Light Mode" else "rgba(251, 191, 36, 0.1)",
            yaxis="y2",
        )
    )

    fig.update_layout(
        plot_bgcolor=plot_bg,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color),
        xaxis=dict(
            title="Date", showgrid=False, linecolor="#cbd5e1", tickformat="%b %d"
        ),
        yaxis=dict(
            title=dict(text="Turbidity (NTU)", font=dict(size=13)),
            side="left",
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.08)",
        ),
        yaxis2=dict(
            title=dict(text="pH Level", font=dict(size=13)),
            overlaying="y",
            side="right",
            showgrid=False,
            range=[6.0, 8.5],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=40, r=40, t=20, b=50),
        hovermode="x unified",
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)
  else:
    st.warning("No valid data available for the selected filter range.")

  st.markdown("### 📋 Recent Monitoring Log List")
  st.dataframe(df, use_container_width=True)

elif selected_page == "Discharge Compliance":
  st.title("🛡️ Discharge Compliance Details")
  st.caption("In-depth analysis of site compliance against permitted limits.")
  st.markdown("---")

elif selected_page == "River Water Quality":
  st.title("💧 River Water Quality (Upstream vs Downstream)")
  st.caption("Monitoring Sungai Duri upstream and downstream parameters.")
  st.markdown("---")

elif selected_page == "Cases Tracker":
  st.title("⚠️ Environmental Cases Tracker")
  st.caption("Detailed breakdown of ongoing cases and corrective actions.")
  st.markdown("---")