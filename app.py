import pandas as pd
import plotly.express as px
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

# ==========================================
# SIDEBAR: NAVIGATION & CONTROLS (DARK NAVY)
# ==========================================
with st.sidebar:
  st.markdown(
      "<h2 style='font-size: 22px; font-weight: 700; color: #ffffff; "
      "font-family: Inter, sans-serif;'>🌊 Mboard</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='font-size: 11px; letter-spacing: 1.2px; color:"
      " #94a3b8; font-family: Inter, sans-serif;'>ENVIRONMENTAL SYSTEM</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  st.markdown(
      "<p"
      " style='font-size: 12px; font-weight: 700; color: #38bdf8;"
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
      ],
      label_visibility="collapsed",
  )

  st.markdown("---")
  st.markdown(
      "<p"
      " style='font-size: 12px; font-weight: 700; color: #38bdf8;"
      " letter-spacing: 0.8px; margin-bottom: 5px; font-family: Inter,"
      " sans-serif;'>DATA FILTERS</p>",
      unsafe_allow_html=True,
  )

# ==========================================
# CUSTOM CSS: CLEAN LIGHT CANVAS + DARK SIDEBAR + ENHANCED FONT
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
        padding: 18px 22px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        transition: all 0.2s ease-in-out;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    [data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
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

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=0&single=true&output=csv"
CASES_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6EtvUg9G_4FqGNLdnmMB1yHeid1cW4n3tQu9h8Yjmj3gmU8tcEkc7_ygc_9hhZ-wneiUwHgRLiIxB/pub?gid=1959925791&single=true&output=csv"


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


@st.cache_data
def load_cases_data():
  df_cases = pd.read_csv(CASES_CSV_URL)
  df_cases.columns = df_cases.columns.str.strip()
  if "Date Raised" in df_cases.columns:
    df_cases["Date Raised"] = pd.to_datetime(
        df_cases["Date Raised"], errors="coerce"
    )
  return df_cases


try:
  df_raw = load_data()
  df_cases = load_cases_data()
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
# GLOBAL VARIABLE DEFINITIONS (FDP)
# ==========================================
f_ph = next(
    (
        c
        for c in df.columns
        if "ph" in c.lower()
        and ("fdp" in c.lower() or "discharge" in c.lower())
    ),
    None,
)
if not f_ph:
  f_ph = [c for c in df.columns if "ph" in c.lower()][-1]

f_ntu = next(
    (
        c
        for c in df.columns
        if ("ntu" in c.lower() or "turb" in c.lower())
        and ("fdp" in c.lower() or "discharge" in c.lower())
    ),
    None,
)
if not f_ntu:
  f_ntu = [c for c in df.columns if "ntu" in c.lower()][-1]

# ==========================================
# PAGE 1: OVERVIEW
# ==========================================
if selected_page == "Overview":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px; font-family: Inter, sans-serif;'>Welcome</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #0284c7; font-size: 13px; font-weight: 600; margin-top:"
      " 0; margin-bottom: 2px; font-family: Inter, sans-serif;'>RBA Engineering"
      " | Tin Mining PH ML087</p>",
      unsafe_allow_html=True,
  )

  last_sample_date = (
      df["Date"].max().strftime("%d %b %Y") if not df.empty else "N/A"
  )

  open_cases_count = 0
  if not df_cases.empty and "Status" in df_cases.columns:
    open_cases_count = df_cases[
        df_cases["Status"].astype(str).str.lower().str.contains("open")
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
        label="Open Cases", value=open_cases_count, delta="Requires Action"
    )
  with col3:
    st.metric(label="Last Sample Date", value=last_sample_date)
  with col4:
    st.metric(
        label="BMP Performance (Latest)", value=f"{bmp_performance:.1f}%"
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader("📋 Station Status by Parameter (Latest Sample)")
  st.caption(
      "Dynamically updated evaluation for the latest sample date in the selected"
      " range."
  )

  if not df.empty:
    latest_row = df.sort_values(by="Date").iloc[-1]
    us_ph_col = next(
        (
            c
            for c in df.columns
            if "ph" in c.lower()
            and ("us" in c.lower() or "upstream" in c.lower())
        ),
        df.columns[3],
    )
    us_ntu_col = next(
        (
            c
            for c in df.columns
            if ("ntu" in c.lower() or "turb" in c.lower())
            and ("us" in c.lower() or "upstream" in c.lower())
            and "am" in c.lower()
        ),
        df.columns[5],
    )
    ds_ph_col = next(
        (
            c
            for c in df.columns
            if "ph" in c.lower()
            and ("ds" in c.lower() or "downstream" in c.lower())
        ),
        df.columns[7],
    )
    ds_ntu_col = next(
        (
            c
            for c in df.columns
            if ("ntu" in c.lower() or "turb" in c.lower())
            and ("ds" in c.lower() or "downstream" in c.lower())
            and "am" in c.lower()
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
    us_ph_val = latest_row.get(us_ph_col, 0)
    us_ntu_val = latest_row.get(us_ntu_col, 0)
    ds_ph_val = latest_row.get(ds_ph_col, 0)
    ds_ntu_val = latest_row.get(ds_ntu_col, 0)

    matrix_html = f"""
        <div class="table-container">
        <table style="width:100%; border-collapse: collapse; font-family: 'Inter', sans-serif; white-space: nowrap;">
            <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; text-align: left;">
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">Station</th>
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">pH (Latest: {latest_row['Date'].strftime('%d %b %Y')})</th>
                <th style="padding: 14px 18px; color: #64748b; font-size: 12px; font-weight: 600;">Turbidity (&lt; 250 NTU)</th>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">Final discharge (FDP)</td>
                <td style="padding: 14px 18px;">{get_status_badge(fdp_ph_val, 'pH')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({fdp_ph_val})</span></td>
                <td style="padding: 14px 18px;">{get_status_badge(fdp_ntu_val, 'Turbidity')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({fdp_ntu_val} NTU)</span></td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">River upstream (Sg. Duri US)</td>
                <td style="padding: 14px 18px;">{get_status_badge(us_ph_val, 'pH')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({us_ph_val})</span></td>
                <td style="padding: 14px 18px;">{get_status_badge(us_ntu_val, 'Turbidity')} <span style="font-size: 11px; color: #64748b; margin-left: 6px;">({us_ntu_val} NTU)</span></td>
            </tr>
            <tr>
                <td style="padding: 14px 18px; font-weight: 600; color: #0f172a; font-size: 13px;">River downstream (Sg. Duri DS)</td>
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
                text="Turbidity (NTU)", font=dict(color="#0284c7", size=11)
            ),
            tickfont=dict(color="#0284c7", size=10),
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
  else:
    st.warning("No valid data available for the selected filter range.")

# ==========================================
# PAGE 2: DISCHARGE COMPLIANCE
# ==========================================
elif selected_page == "Discharge Compliance":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px; font-family: Inter, sans-serif;'>🛡️ Discharge"
      " Compliance</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 13px; margin-top: 0; margin-bottom:"
      " 25px; font-family: Inter, sans-serif;'>In-depth breakdown of Final"
      " Discharge (FDP) AM and PM readings for pH and Turbidity.</p>",
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
      None,
  )
  if not ph_am_col:
    ph_am_col = [c for c in df.columns if "ph" in c.lower()][0]

  ph_pm_col = next(
      (
          c
          for c in df.columns
          if "ph" in c.lower()
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("pm" in c.lower() or "petang" in c.lower())
      ),
      None,
  )
  if not ph_pm_col:
    ph_pm_col = [c for c in df.columns if "ph" in c.lower()][-1]

  ntu_am_col = next(
      (
          c
          for c in df.columns
          if ("ntu" in c.lower() or "turb" in c.lower())
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("am" in c.lower() or "pagang" in c.lower())
      ),
      None,
  )
  if not ntu_am_col:
    ntu_am_col = [c for c in df.columns if "ntu" in c.lower()][0]

  ntu_pm_col = next(
      (
          c
          for c in df.columns
          if ("ntu" in c.lower() or "turb" in c.lower())
          and ("fdp" in c.lower() or "discharge" in c.lower())
          and ("pm" in c.lower() or "petang" in c.lower())
      ),
      None,
  )
  if not ntu_pm_col:
    ntu_pm_col = [c for c in df.columns if "ntu" in c.lower()][-1]

  if not df.empty:
    df_ph_stacked = pd.melt(
        df,
        id_vars=["Date"],
        value_vars=[ph_am_col, ph_pm_col],
        value_name="pH",
    )
    df_ph_stacked = df_ph_stacked.dropna(subset=["pH"])
    min_ph_val = (
        df_ph_stacked["pH"].min() if not df_ph_stacked.empty else 0.0
    )
    min_ph_date = (
        df_ph_stacked.loc[df_ph_stacked["pH"].idxmin(), "Date"].strftime(
            "%d %b %Y"
        )
        if not df_ph_stacked.empty
        else "N/A"
    )

    df_ntu_stacked = pd.melt(
        df,
        id_vars=["Date"],
        value_vars=[ntu_am_col, ntu_pm_col],
        value_name="NTU",
    )
    df_ntu_stacked = df_ntu_stacked.dropna(subset=["NTU"])
    max_ntu_val = (
        df_ntu_stacked["NTU"].max() if not df_ntu_stacked.empty else 0.0
    )
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
          delta="Critical Acidic Value",
          delta_color="inverse",
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

# ==========================================
# PAGE 3: RIVER WATER QUALITY
# ==========================================
elif selected_page == "River Water Quality":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px; font-family: Inter, sans-serif;'>💧 River Water"
      " Quality (Upstream vs Downstream)</h1>",
      unsafe_allow_html=True,
  )
  latest_date_str = (
      df["Date"].max().strftime("%d %b %Y") if not df.empty else "N/A"
  )
  st.markdown(
      f"<p style='color: #64748b; font-size: 13px; margin-top: 0;"
      f" margin-bottom: 25px; font-family: Inter, sans-serif;'>Comparison and"
      f" net impact analysis based on latest dataset date: "
      f"<b>{latest_date_str}</b>.</p>",
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

    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
      st.metric(
          label="pH Level (Upstream vs Downstream Latest Avg)",
          value=f"Upstream: {us_ph_latest}  |  Downstream: {ds_ph_latest}",
      )
    with row1_c2:
      st.metric(
          label="Turbidity (Upstream vs Downstream Latest Avg)",
          value=(
              f"Upstream: {us_ntu_latest} NTU  |  Downstream:"
              f" {ds_ntu_latest} NTU"
          ),
      )

# ==========================================
# PAGE 4: CASES TRACKER (DENGAN "PROPOSED IN MEETING" & DATE RANGE)
# ==========================================
elif selected_page == "Cases Tracker":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px; font-family: Inter, sans-serif;'>⚠️ Environmental"
      " Cases Tracker</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 13px; margin-top: 0; margin-bottom:"
      " 25px; font-family: Inter, sans-serif;'>Comprehensive overview of site"
      " incidents, locations, and closure status.</p>",
      unsafe_allow_html=True,
  )

  if not df_cases.empty:
    df_cases.columns = df_cases.columns.str.strip()
    status_col = next(
        (c for c in df_cases.columns if "status" in c.lower()), None
    )
    date_col = next(
        (
            c
            for c in df_cases.columns
            if "date" in c.lower() or "raised" in c.lower()
        ),
        None,
    )

    total_cases = len(df_cases)

    # Mengira kes mengikut status (Open, Closed, Proposed in meeting)
    open_cases = (
        len(
            df_cases[
                df_cases[status_col].astype(str).str.lower().str.contains("open")
            ]
        )
        if status_col
        else 0
    )
    closed_cases = (
        len(
            df_cases[
                df_cases[status_col]
                .astype(str)
                .str.lower()
                .str.contains("closed")
            ]
        )
        if status_col
        else 0
    )
    proposed_cases = (
        len(
            df_cases[
                df_cases[status_col]
                .astype(str)
                .str.lower()
                .str.contains("proposed")
            ]
        )
        if status_col
        else 0
    )

    # Dapatkan Julat Tarikh (Date Range) untuk Kes
    if date_col and pd.api.types.is_datetime64_any_dtype(df_cases[date_col]):
      min_c_date = df_cases[date_col].min().strftime("%d %b %Y")
      max_c_date = df_cases[date_col].max().strftime("%d %b %Y")
      date_range_label = f"Range: {min_c_date} – {max_c_date}"
    else:
      date_range_label = "All Records"

    # Paparan Kad KPI Kes (4 Kolum termasuk Proposed in meeting)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.metric(label="Total Cases", value=total_cases, delta=date_range_label)
    with c2:
      st.metric(
          label="Open Cases", value=open_cases, delta="Requires Action"
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
    st.subheader("📋 Cases Tracker Records & Location Breakdown")
    st.dataframe(df_cases, use_container_width=True)
  else:
    st.warning("No data found in Cases Tracker sheet.")
