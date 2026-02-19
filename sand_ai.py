# ==========================================================
# SMART SAND REUSABILITY PREDICTOR - PRO VERSION
# WITH DATA UPLOAD + INTELLIGENT RECOMMENDATION
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Smart Sand AI", layout="wide")

# ==========================================================
# DARK THEME
# ==========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
div[data-testid="stMetric"] {
    background-color: #1f2937;
    padding: 20px;
    border-radius: 15px;
}
button[kind="primary"] {
    background-color: #00f2fe !important;
    color: black !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SESSION HISTORY
# ==========================================================
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================================
# DATA UPLOAD SECTION
# ==========================================================
st.sidebar.header("📂 Upload Sand Dataset (Optional)")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom Dataset Loaded Successfully!")
else:
    # Default synthetic dataset
    np.random.seed(42)
    data_size = 500
    data = pd.DataFrame({
        "moisture": np.random.uniform(2, 6, data_size),
        "temperature": np.random.uniform(25, 80, data_size),
        "clay": np.random.uniform(5, 12, data_size),
        "grain_size": np.random.uniform(0.15, 0.35, data_size),
        "loi": np.random.uniform(1, 5, data_size),
        "permeability": np.random.uniform(80, 150, data_size),
        "cycles": np.random.randint(1, 10, data_size)
    })

    data["reuse_left"] = (
        15
        - data["cycles"]
        - data["moisture"] * 0.5
        - data["loi"] * 0.8
        + data["permeability"] * 0.02
    )

# ==========================================================
# TRAIN MODEL
# ==========================================================
if "reuse_left" in data.columns:
    X = data.drop("reuse_left", axis=1)
    y = data["reuse_left"]

    model = RandomForestRegressor()
    model.fit(X, y)
else:
    st.error("Uploaded dataset must contain 'reuse_left' column.")
    st.stop()

# ==========================================================
# UI HEADER
# ==========================================================
st.title("🏭 Smart Sand Reusability Predictor")
st.markdown("### AI Powered Foundry Intelligence System")

col1, col2 = st.columns(2)

with col1:
    moisture = st.slider("Moisture (%)", 2.0, 6.0, 3.5)
    clay = st.slider("Clay Content (%)", 5.0, 12.0, 8.0)
    loi = st.slider("Loss on Ignition (%)", 1.0, 5.0, 2.5)
    cycles = st.slider("Reuse Cycles Completed", 1, 15, 3)

with col2:
    temp = st.slider("Temperature (°C)", 25.0, 80.0, 40.0)
    grain = st.slider("Grain Size (mm)", 0.15, 0.35, 0.25)
    perm = st.slider("Permeability", 80.0, 150.0, 100.0)

# ==========================================================
# PREDICTION
# ==========================================================
input_data = pd.DataFrame([{
    "moisture": moisture,
    "temperature": temp,
    "clay": clay,
    "grain_size": grain,
    "loi": loi,
    "permeability": perm,
    "cycles": cycles
}])

prediction = model.predict(input_data)[0]
reuse_left = max(0, round(prediction, 2))

health_score = max(0, round(100 - (cycles * 5 + loi * 4 + moisture * 3), 2))
defect_risk = min(100, round(100 - health_score, 2))

# ==========================================================
# METRICS
# ==========================================================
st.subheader("📊 AI Prediction Results")

m1, m2, m3 = st.columns(3)
m1.metric("♻ Reuse Cycles Left", reuse_left)
m2.metric("🧪 Sand Health Score", f"{health_score} %")
m3.metric("⚠ Defect Risk", f"{defect_risk} %")

# ==========================================================
# FINAL RECOMMENDATION MESSAGE
# ==========================================================
st.subheader("🧠 AI Recommendation")

if reuse_left > 8:
    st.success(f"✅ Sand can be safely reused approximately {int(reuse_left)} more times.")
elif 4 <= reuse_left <= 8:
    st.warning(f"⚠ Sand can be reused around {int(reuse_left)} more times, but monitor quality closely.")
else:
    st.error(f"❌ Sand should NOT be reused further. Replacement recommended.")

# ==========================================================
# VISUALIZATION
# ==========================================================
st.subheader("📈 Live Parameter Visualization")

chart_df = pd.DataFrame({
    "Parameter": ["Moisture", "Temperature", "Clay", "LOI", "Permeability"],
    "Value": [moisture, temp, clay, loi, perm]
})

fig = px.bar(
    chart_df,
    x="Parameter",
    y="Value",
    color="Parameter",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# SAVE HISTORY
# ==========================================================
record = {
    "Moisture (%)": moisture,
    "Temperature (°C)": temp,
    "Clay (%)": clay,
    "Grain Size (mm)": grain,
    "LOI (%)": loi,
    "Permeability": perm,
    "Cycles Completed": cycles,
    "Reuse Left": reuse_left,
    "Health Score (%)": health_score,
    "Defect Risk (%)": defect_risk
}

if st.button("💾 Save Prediction"):
    st.session_state.history.append(record)
    st.success("Prediction Saved!")

# ==========================================================
# HISTORY
# ==========================================================
st.subheader("📜 Prediction History")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df)

    csv = history_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download CSV", csv, "sand_history.csv")

else:
    st.info("No history yet.")

st.markdown("---")
st.markdown("🚀 Hackathon Ultra Edition | AI Powered Sustainable Foundry System")
