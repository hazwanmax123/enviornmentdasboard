import calendar
import datetime
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Tetapan asas paparan Streamlit
st.set_page_config(
    page_title="RBA Environmental Monitoring System",
    page_icon="💧",
    layout="wide",
)


# ==========================================
# 1. FUNGSI SAMBUNGAN GOOGLE SHEETS
# ==========================================
def init_gspread_client():
  try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    return gspread.service_account_from_dict(creds_dict)
  except Exception as e:
    st.error(f"⚠️ Ralat Autentikasi Google: {e}")
    return None


client = init_gspread_client()
SPREADSHEET_NAME = "Master Data Monitoring"

# Muat turun data asal dengan selamat
try:
  sheet_daily = client.open(SPREADSHEET_NAME).worksheet("Daily log 2026")
  df = pd.DataFrame(sheet_daily.get_all_records())
  if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except:
  df = pd.DataFrame()

try:
  sheet_cases = client.open(SPREADSHEET_NAME).worksheet("Cases Tracker")
  df_cases = pd.DataFrame(sheet_cases.get_all_records())
except:
  df_cases = pd.DataFrame()

try:
  sheet_monthly = client.open(SPREADSHEET_NAME).worksheet("Monthly Sampling")
  df_monthly = pd.DataFrame(sheet_monthly.get_all_records())
except:
  df_monthly = pd.DataFrame()


# ==========================================
# 2. SIDEBAR NAVIGATION & PENAPIS TARIKH
# ==========================================
st.sidebar.markdown(
    "<h2 style='color: #ffffff; font-size: 20px;'>🛡️ Mboard System</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='color: #94a3b8; font-size: 12px;'>RBA Engineering (M) Sdn"
    " Bhd</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

selected_page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Discharge Compliance",
        "River Water Quality",
        "Cases Tracker",
        "Monthly Monitoring Record",
    ],
)

# Tombol Refresh Data
if st.sidebar.button("🔄 Refresh Data Terkini"):
  st.cache_data.clear()
  st.rerun()


# ==========================================
# 3. PAPARAN MENGIKUT PAGE
# ==========================================

# ------------------------------------------
# PAGE 1: OVERVIEW
# ------------------------------------------
if selected_page == "Overview":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>📊 System Overview & Summary</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 13px;'>Ringkasan status pemantauan"
      " alam sekitar tapak ML087.</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric(
          label="Jumlah Rekod Harian",
          value=len(df),
          delta="Aktif Beroperasi",
      )
    with col2:
      st.metric(
          label="Jumlah Kes Dilaporkan",
          value=len(df_cases) if not df_cases.empty else 0,
          delta="Cases Tracker",
      )
    with col3:
      st.metric(
          label="Rekod Persampelan Bulanan",
          value=len(df_monthly) if not df_monthly.empty else 0,
          delta="Lab Results",
      )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Data Log Harian Terkini")
    st.dataframe(df.tail(10), use_container_width=True)
  else:
    st.warning(
        "Tiada data dijumpai dalam Google Sheet 'Master Data Monitoring'."
    )


# ------------------------------------------
# PAGE 2: DISCHARGE COMPLIANCE
# ------------------------------------------
elif selected_page == "Discharge Compliance":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>🛡️ Discharge Compliance & Analytics</h1>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  if not df.empty:
    f_ph = df.columns[1] if len(df.columns) > 1 else ""
    f_ntu = df.columns[11] if len(df.columns) > 11 else ""

    limit_val = (
        df["NTU Limit"].dropna().iloc[-1]
        if "NTU Limit" in df.columns and not df["NTU Limit"].dropna().empty
        else 50.0
    )

    if f_ph in df.columns and f_ntu in df.columns:
      compliant_mask = (
          (df[f_ph] >= 6.0) & (df[f_ph] <= 9.0) & (df[f_ntu] <= limit_val)
      )
      compliant_count = df[compliant_mask].shape[0]
      breach_count = df.shape[0] - compliant_count

      col_left, col_right = st.columns([1, 1])

      with col_left:
        st.markdown("#### 📌 Parameter Summary (FDP)")
        st.metric(
            label="Total Sampling Days",
            value=len(df),
            delta="Active Monitoring",
        )
        st.metric(
            label="Compliant Records",
            value=(
                f"{compliant_count} ({compliant_count/len(df)*100:.1f}%)"
                if len(df) > 0
                else "0"
            ),
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
            color_discrete_map={
                "Compliant": "#10b981",
                "Breach / Non-Compliant": "#ef4444",
            },
            hole=0.4,
        )
        fig_pie.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="rgba(0,0,0,0)",
            height=260,
            margin=dict(l=20, r=20, t=10, b=30),
        )
        st.plotly_chart(
            fig_pie, use_container_width=True, config={"responsive": True}
        )
  else:
    st.warning("Tiada data untuk Discharge Compliance.")


# ------------------------------------------
# PAGE 3: RIVER WATER QUALITY (Struktur Asal Penuh)
# ------------------------------------------
elif selected_page == "River Water Quality":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>💧 River Water Quality (Upstream vs Downstream)</h1>",
      unsafe_allow_html=True,
  )

  if not df.empty and "Date" in df.columns:
    # Sidebar Penapis Masa: Tahun (Atas), Bulan (Tengah), Date Range (Bawah)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Penapis Tarikh & Masa")

    df["Year"] = df["Date"].dt.year
    available_years = sorted(
        df["Year"].dropna().unique().astype(int).tolist(), reverse=True
    )

    selected_year = st.sidebar.selectbox(
        "Pilih Tahun", options=["Kesemua Tahun"] + available_years
    )

    df_temp = df.copy()
    if selected_year != "Kesemua Tahun":
      df_temp = df_temp[df_temp["Year"] == selected_year]

    available_months = df_temp["Date"].dt.strftime("%B").unique().tolist()
    selected_month = st.sidebar.selectbox(
        "Pilih Bulan", options=["Kesemua Bulan"] + available_months
    )

    if selected_month != "Kesemua Bulan":
      df_temp = df_temp[df_temp["Date"].dt.strftime("%B") == selected_month]

    st.sidebar.markdown("---")
    min_d = (
        df_temp["Date"].min().date()
        if not df_temp.empty and pd.notnull(df_temp["Date"].min())
        else datetime.date.today() - datetime.timedelta(days=30)
    )
    max_d = (
        df_temp["Date"].max().date()
        if not df_temp.empty and pd.notnull(df_temp["Date"].max())
        else datetime.date.today()
    )

    selected_date_range = st.sidebar.date_input(
        "Pilih Julat Tarikh Khusus", value=[min_d, max_d]
    )

    # Dropdown Sesi AM / PM di atas page
    selected_session = st.selectbox(
        "Pilih Sesi Persampelan (AM / PM)",
        ["Sesi Pagi (AM)", "Sesi Petang (PM)"],
    )
    st.markdown("---")

    df_filtered = df_temp.copy()
    if len(selected_date_range) == 2:
      start_date, end_date = selected_date_range
      df_filtered = df_filtered[
          (df_filtered["Date"].dt.date >= start_date)
          & (df_filtered["Date"].dt.date <= end_date)
      ]

    if not df_filtered.empty:
      # Tentukan kolum US & DS mengikut sesi
      if "Sesi Pagi" in selected_session:
        ph_us_col = next(
            (
                c
                for c in df_filtered.columns
                if "ph" in c.lower()
                and (
                    "us" in c.lower()
                    or "upstream" in c.lower()
                    or "duri 1" in c.lower()
                )
                and "am" in c.lower()
            ),
            df_filtered.columns[1],
        )
        ph_ds_col = next(
            (
                c
                for c in df_filtered.columns
                if "ph" in c.lower()
                and (
                    "ds" in c.lower()
                    or "downstream" in c.lower()
                    or "duri 2" in c.lower()
                )
                and "am" in c.lower()
            ),
            df_filtered.columns[2],
        )
        ntu_us_col = next(
            (
                c
                for c in df_filtered.columns
                if ("ntu" in c.lower() or "turb" in c.lower())
                and ("us" in c.lower() or "upstream" in c.lower())
                and "am" in c.lower()
            ),
            df_filtered.columns[11],
        )
        ntu_ds_col = next(
            (
                c
                for c in df_filtered.columns
                if ("ntu" in c.lower() or "turb" in c.lower())
                and ("ds" in c.lower() or "downstream" in c.lower())
                and "am" in c.lower()
            ),
            df_filtered.columns[12],
        )
      else:
        ph_us_col = next(
            (
                c
                for c in df_filtered.columns
                if "ph" in c.lower()
                and ("us" in c.lower() or "upstream" in c.lower())
                and "pm" in c.lower()
            ),
            df_filtered.columns[1],
        )
        ph_ds_col = next(
            (
                c
                for c in df_filtered.columns
                if "ph" in c.lower()
                and ("ds" in c.lower() or "downstream" in c.lower())
                and "pm" in c.lower()
            ),
            df_filtered.columns[2],
        )
        ntu_us_col = next(
            (
                c
                for c in df_filtered.columns
                if ("ntu" in c.lower() or "turb" in c.lower())
                and ("us" in c.lower() or "upstream" in c.lower())
                and "pm" in c.lower()
            ),
            df_filtered.columns[11],
        )
        ntu_ds_col = next(
            (
                c
                for c in df_filtered.columns
                if ("ntu" in c.lower() or "turb" in c.lower())
                and ("ds" in c.lower() or "downstream" in c.lower())
                and "pm" in c.lower()
            ),
            df_filtered.columns[12],
        )

      # KPI Cards dengan Nilai, Tarikh & Net Impact
      st.markdown("#### 📌 River Water Quality KPI Summary")

      min_ph_val = (
          df_filtered[ph_ds_col].min()
          if ph_ds_col in df_filtered.columns
          else 0.0
      )
      min_ph_row = (
          df_filtered.loc[df_filtered[ph_ds_col] == min_ph_val]
          if ph_ds_col in df_filtered.columns
          else pd.DataFrame()
      )
      min_ph_date = (
          min_ph_row["Date"].dt.strftime("%d %b %Y").values[0]
          if not min_ph_row.empty and "Date" in min_ph_row.columns
          else "N/A"
      )

      max_ntu_val = (
          df_filtered[ntu_ds_col].max()
          if ntu_ds_col in df_filtered.columns
          else 0.0
      )
      max_ntu_row = (
          df_filtered.loc[df_filtered[ntu_ds_col] == max_ntu_val]
          if ntu_ds_col in df_filtered.columns
          else pd.DataFrame()
      )
      max_ntu_date = (
          max_ntu_row["Date"].dt.strftime("%d %b %Y").values[0]
          if not max_ntu_row.empty and "Date" in max_ntu_row.columns
          else "N/A"
      )

      ph_impact = (
          (df_filtered[ph_ds_col] - df_filtered[ph_us_col]).mean()
          if ph_ds_col in df_filtered.columns
          and ph_us_col in df_filtered.columns
          else 0.0
      )
      ntu_impact = (
          (df_filtered[ntu_ds_col] - df_filtered[ntu_us_col]).mean()
          if ntu_ds_col in df_filtered.columns
          and ntu_us_col in df_filtered.columns
          else 0.0
      )

      col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
      with col_kpi1:
        st.metric(
            label="Lowest pH Record",
            value=f"{min_ph_val:.2f}",
            delta=f"Tarikh: {min_ph_date}",
            delta_color="inverse" if min_ph_val < 6.0 else "normal",
        )
      with col_kpi2:
        st.metric(
            label="Highest NTU Record",
            value=f"{max_ntu_val:.1f}",
            delta=f"Tarikh: {max_ntu_date}",
            delta_color="inverse" if max_ntu_val > 250 else "normal",
        )
      with col_kpi3:
        st.metric(
            label="pH Net Impact (DS - US)",
            value=f"{ph_impact:+.2f}",
            delta="Acidity Shift",
        )
      with col_kpi4:
        st.metric(
            label="NTU Net Impact (DS - US)",
            value=f"{ntu_impact:+.1f} NTU",
            delta="Silt Load Effect",
            delta_color="inverse" if ntu_impact > 20 else "normal",
        )

      st.markdown("<br>", unsafe_allow_html=True)

      # Graf 1: pH Level (US vs DS)
      st.subheader(f"📈 Analisis Tahap pH Sg. Duri ({selected_session})")
      fig_river_ph = go.Figure()
      if ph_us_col in df_filtered.columns:
        fig_river_ph.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[ph_us_col],
                name="Sg Duri Upstream (US)",
                mode="lines+markers",
                line=dict(color="#0284c7", width=2),
            )
        )
      if ph_ds_col in df_filtered.columns:
        fig_river_ph.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[ph_ds_col],
                name="Sg Duri Downstream (DS)",
                mode="lines+markers",
                line=dict(color="#0f172a", width=2),
            )
        )
      fig_river_ph.update_layout(
          plot_bgcolor="#ffffff",
          paper_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(showgrid=False, title="Date"),
          yaxis=dict(title="pH Level", range=[0, 14], showgrid=True),
          height=380,
          margin=dict(l=30, r=30, t=40, b=30),
      )
      st.plotly_chart(
          fig_river_ph, use_container_width=True, config={"responsive": True}
      )

      st.markdown("<br>", unsafe_allow_html=True)

      # Graf 2: Turbidity / NTU (US vs DS + Limit 250)
      st.subheader(
          f"📊 Analisis Turbidity Sg. Duri & Had Standard ({selected_session})"
      )
      fig_river_ntu = go.Figure()
      if ntu_us_col in df_filtered.columns:
        fig_river_ntu.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[ntu_us_col],
                name="Sg Duri Upstream (US NTU)",
                mode="lines+markers",
                line=dict(color="#38bdf8", width=2),
            )
        )
      if ntu_ds_col in df_filtered.columns:
        fig_river_ntu.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[ntu_ds_col],
                name="Sg Duri Downstream (DS NTU)",
                mode="lines+markers",
                line=dict(color="#ef4444", width=2),
            )
        )

      fig_river_ntu.add_hline(
          y=250,
          line_dash="dash",
          line_color="#ef4444",
          annotation_text="Standard Limit (250 NTU)",
          annotation_position="top right",
          annotation_font_color="#ef4444",
      )
      fig_river_ntu.update_layout(
          plot_bgcolor="#ffffff",
          paper_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(showgrid=False, title="Date"),
          yaxis=dict(title="Turbidity (NTU)", showgrid=True),
          height=380,
          margin=dict(l=30, r=30, t=40, b=30),
      )
      st.plotly_chart(
          fig_river_ntu, use_container_width=True, config={"responsive": True}
      )

      st.markdown("---")
      st.markdown("#### 📋 Jadual Rekod Mentah Kualiti Air Sungai")
      st.dataframe(df_filtered, use_container_width=True)
  else:
    st.warning("Tiada data untuk River Water Quality.")


# ------------------------------------------
# PAGE 4: CASES TRACKER
# ------------------------------------------
elif selected_page == "Cases Tracker":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>⚠️ Environmental Cases Tracker</h1>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  if not df_cases.empty:
    st.dataframe(df_cases, use_container_width=True)
  else:
    st.info("Tiada rekod kes dilaporkan.")


# ------------------------------------------
# PAGE 5: MONTHLY MONITORING RECORD
# ------------------------------------------
elif selected_page == "Monthly Monitoring Record":
  st.markdown(
      "<h1 style='font-size: 26px; font-weight: 700; color: #0f172a;"
      " margin-bottom: 2px;'>📅 Monthly Sampling & Lab Results</h1>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  if not df_monthly.empty:
    st.dataframe(df_monthly, use_container_width=True)
  else:
    st.info("Tiada rekod persampelan bulanan.")
