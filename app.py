import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine

from config import DATABASE_URL

from utils import (
    calculate_kpis,
    recommendation,
    latest_record
)

from voice import generate_voice
from report_generator import generate_report

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="🌾 AgriPrice Insight",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main{
    background:#f7f9fc;
}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

.dashboard-title{
    font-size:40px;
    font-weight:bold;
    color:#2E7D32;
}

.dashboard-subtitle{
    color:#555;
    font-size:18px;
}

.sell{
    background:#16a34a;
    color:white;
    padding:25px;
    border-radius:15px;
    text-align:center;
    font-size:30px;
    font-weight:bold;
}

.hold{
    background:#dc2626;
    color:white;
    padding:25px;
    border-radius:15px;
    text-align:center;
    font-size:30px;
    font-weight:bold;
}

.watch{
    background:#facc15;
    color:black;
    padding:25px;
    border-radius:15px;
    text-align:center;
    font-size:30px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE
# =====================================================

engine = create_engine(DATABASE_URL)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    analytics = pd.read_sql(
        "SELECT * FROM crop_analytics ORDER BY date",
        engine
    )

    predictions = pd.read_sql(
        "SELECT * FROM crop_predictions ORDER BY prediction_date",
        engine
    )

    analytics["date"] = pd.to_datetime(
        analytics["date"]
    )

    predictions["prediction_date"] = pd.to_datetime(
        predictions["prediction_date"]
    )

    return analytics, predictions


analytics, predictions = load_data()

# =====================================================
# CHECK DATABASE
# =====================================================

if analytics.empty:

    st.error("crop_analytics table is empty.")

    st.info("Run data_pipeline.py first.")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.image(
    "https://img.icons8.com/color/96/wheat.png",
    width=70
)

st.sidebar.title("AgriPrice Insight")

language = st.sidebar.selectbox(

    "🌍 Language",

    [

        "English",

        "Hindi",

        "Kannada"

    ]

)

markets = sorted(
    analytics["market"].unique()
)

selected_market = st.sidebar.selectbox(

    "📍 Select Market",

    markets

)

crops = sorted(
    analytics["crop"].unique()
)

selected_crop = st.sidebar.selectbox(

    "🌾 Select Crop",

    crops

)

comparison_crop = st.sidebar.selectbox(

    "🌱 Compare Crop",

    crops,

    index=1 if len(crops) > 1 else 0

)

# =====================================================
# FILTER DATA
# =====================================================

crop_data = analytics[

    (analytics["market"] == selected_market)

    &

    (analytics["crop"] == selected_crop)

]

forecast_data = predictions[

    predictions["crop"] == selected_crop

]

# =====================================================
# CHECK FILTERED DATA
# =====================================================

if crop_data.empty:

    st.warning("No records available.")

    st.stop()

# =====================================================
# PAGE HEADER
# =====================================================

st.markdown(

    "<div class='dashboard-title'>🌾 AgriPrice Insight</div>",

    unsafe_allow_html=True

)

st.markdown(

    "<div class='dashboard-subtitle'>Advanced Market Analytics Platform for Farmers</div>",

    unsafe_allow_html=True

)

st.divider()
# =====================================================
# LATEST RECORD
# =====================================================

latest = latest_record(crop_data)

if latest is None:
    st.error("No latest market record found.")
    st.stop()

current_price = float(latest["price"])
moving_average = float(latest["moving_average"])

# =====================================================
# KPI CALCULATIONS
# =====================================================

kpi = calculate_kpis(crop_data)

highest_price = kpi["highest"]
lowest_price = kpi["lowest"]
average_price = kpi["average"]
volatility = kpi["volatility"]
growth = kpi["growth"]

# =====================================================
# SMART RECOMMENDATION
# =====================================================

recommendation_text, icon, explanation = recommendation(
    current_price,
    moving_average
)

if recommendation_text == "SELL NOW":
    recommendation_color = "sell"

elif recommendation_text == "HOLD STOCK":
    recommendation_color = "hold"

else:
    recommendation_color = "watch"

st.markdown(
    f"""
    <div class="{recommendation_color}">
        <h1>{icon} {recommendation_text}</h1>
        <p style="font-size:22px;">
            Current Price : ₹{current_price:.2f}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(explanation)

st.write("")

# =====================================================
# KPI CARDS
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "📈 Highest",
    f"₹ {highest_price:.2f}"
)

col2.metric(
    "📉 Lowest",
    f"₹ {lowest_price:.2f}"
)

col3.metric(
    "💰 Average",
    f"₹ {average_price:.2f}"
)

col4.metric(
    "📊 Volatility",
    f"{volatility:.2f}"
)

col5.metric(
    "🚀 Growth",
    f"{growth:.2f}%"
)

st.divider()

# =====================================================
# PRICE TREND
# =====================================================

st.subheader("📈 Historical Price Trend")

history_chart = px.line(
    crop_data,
    x="date",
    y="price",
    markers=True,
    title=f"{selected_crop} Price Trend"
)

history_chart.update_layout(
    template="plotly_white",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(
    history_chart,
    use_container_width=True
)

# =====================================================
# MOVING AVERAGE
# =====================================================

st.subheader("📉 Moving Average")

ma_chart = go.Figure()

ma_chart.add_trace(
    go.Scatter(
        x=crop_data["date"],
        y=crop_data["price"],
        name="Actual Price",
        mode="lines+markers"
    )
)

ma_chart.add_trace(
    go.Scatter(
        x=crop_data["date"],
        y=crop_data["moving_average"],
        name="7-Day Moving Average",
        mode="lines"
    )
)

ma_chart.update_layout(
    template="plotly_white",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(
    ma_chart,
    use_container_width=True
)

st.divider()
# =====================================================
# 7-DAY PRICE FORECAST
# =====================================================

st.subheader("🔮 7-Day Price Forecast")

if forecast_data.empty:

    st.warning("Prediction data not available.")

else:

    forecast_chart = px.line(

        forecast_data,

        x="prediction_date",

        y="predicted_price",

        markers=True,

        title=f"Next 7 Days Forecast - {selected_crop}"

    )

    forecast_chart.update_layout(

        template="plotly_white",

        height=450,

        hovermode="x unified"

    )

    st.plotly_chart(

        forecast_chart,

        use_container_width=True

    )

st.divider()

# =====================================================
# MARKET COMPARISON
# =====================================================

st.subheader("🌍 Market Comparison")

market_df = analytics[
    analytics["crop"] == selected_crop
]

market_summary = (

    market_df

    .groupby("market")["price"]

    .mean()

    .reset_index()

)

market_chart = px.bar(

    market_summary,

    x="market",

    y="price",

    color="price",

    text_auto=".2f",

    title=f"Average {selected_crop} Price Across Markets"

)

market_chart.update_layout(

    template="plotly_white",

    height=500,

    xaxis_title="Market",

    yaxis_title="Average Price (₹)"

)

st.plotly_chart(

    market_chart,

    use_container_width=True

)

st.divider()

# =====================================================
# CROP COMPARISON
# =====================================================

st.subheader("🌱 Crop Comparison")

comparison_data = analytics[

    (analytics["market"] == selected_market)

    &

    (

        (analytics["crop"] == selected_crop)

        |

        (analytics["crop"] == comparison_crop)

    )

]

comparison_chart = px.line(

    comparison_data,

    x="date",

    y="price",

    color="crop",

    markers=True,

    title=f"{selected_crop} vs {comparison_crop}"

)

comparison_chart.update_layout(

    template="plotly_white",

    height=500,

    hovermode="x unified"

)

st.plotly_chart(

    comparison_chart,

    use_container_width=True

)

st.divider()

# =====================================================
# RECENT RECORDS
# =====================================================

st.subheader("📋 Recent Records")

recent = crop_data.sort_values(

    "date",

    ascending=False

).head(15)

st.dataframe(

    recent,

    use_container_width=True,

    hide_index=True

)

st.divider()
# =====================================================
# EXPORT & REPORTS
# =====================================================

st.subheader("📤 Export & Reports")

col1, col2, col3 = st.columns(3)

# -----------------------------------------------------
# VOICE RECOMMENDATION
# -----------------------------------------------------

with col1:

    st.markdown("### 🔊 Voice Recommendation")

    if st.button("Speak Recommendation"):

        try:

            audio_file = generate_voice(
                recommendation_text,
                language
            )

            with open(audio_file, "rb") as audio:

                st.audio(audio.read())

        except Exception as e:

            st.error(f"Voice Error: {e}")

# -----------------------------------------------------
# PDF REPORT
# -----------------------------------------------------

with col2:

    st.markdown("### 📄 PDF Report")

    if st.button("Generate PDF"):

        try:

            pdf_file = generate_report(

                crop=selected_crop,

                market=selected_market,

                highest=highest_price,

                lowest=lowest_price,

                average=average_price,

                volatility=volatility,

                recommendation=recommendation_text

            )

            with open(pdf_file, "rb") as pdf:

                st.download_button(

                    label="⬇ Download PDF",

                    data=pdf,

                    file_name=f"{selected_crop}_Report.pdf",

                    mime="application/pdf"

                )

        except Exception as e:

            st.error(f"PDF Error: {e}")

# -----------------------------------------------------
# CSV EXPORT
# -----------------------------------------------------

with col3:

    st.markdown("### 📥 CSV Export")

    csv = crop_data.to_csv(index=False)

    st.download_button(

        label="Download CSV",

        data=csv,

        file_name=f"{selected_crop}.csv",

        mime="text/csv"

    )

st.divider()

# =====================================================
# DASHBOARD SUMMARY
# =====================================================

st.subheader("📊 Dashboard Summary")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:

    st.success(f"Current Recommendation: {recommendation_text}")

    st.write(f"📍 Market : {selected_market}")

    st.write(f"🌾 Crop : {selected_crop}")

    st.write(f"💰 Current Price : ₹ {current_price:.2f}")

with summary_col2:

    st.info("Model Information")

    st.write("Prediction Model : Random Forest / Linear Regression")

    st.write("Forecast Period : Next 7 Days")

    st.write("Database : PostgreSQL")

    st.write("Dashboard : Streamlit")

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown("""

---

### 🌾 AgriPrice Insight

**Advanced Market Analytics Platform for Farmers**

**Technology Stack**

- 🐍 Python
- 📊 Pandas
- 🤖 Scikit-Learn
- 🗄 PostgreSQL
- 📈 Plotly
- 🌐 Streamlit

Developed as a **Final Year BCA Data Analytics Project**.

""")