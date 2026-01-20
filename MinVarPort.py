import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page configuration ---
st.set_page_config(
    page_title="Minimum Variance Portfolio Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💹 Minimum Variance Portfolio Calculator")

# --- Sidebar inputs ---
st.sidebar.header("Input Data")
r1 = st.sidebar.number_input("Asset 1 Expected Return (%)", value=8.0)
sd1 = st.sidebar.number_input("Asset 1 Standard Deviation (%)", value=15.0)
r2 = st.sidebar.number_input("Asset 2 Expected Return (%)", value=12.0)
sd2 = st.sidebar.number_input("Asset 2 Standard Deviation (%)", value=20.0)
corr = st.sidebar.number_input("Correlation between Asset 1 & 2", min_value=-1.0, max_value=1.0, value=0.2)

# Convert percentages to decimals
r1 /= 100
r2 /= 100
sd1 /= 100
sd2 /= 100

# Covariance
cov12 = corr * sd1 * sd2

# Minimum variance portfolio weights
w_mvp = (sd2**2 - cov12) / (sd1**2 + sd2**2 - 2*cov12)
w_mvp = max(0, min(1, w_mvp))  # ensure weight is between 0 and 1
w_mvp_2 = 1 - w_mvp

# --- Tabs for organized layout ---
tab1, tab2 = st.tabs(["📊 Results", "📈 Efficient Frontier"])

with tab1:
    st.subheader("Minimum Variance Portfolio Weights")
    col1, col2 = st.columns(2)
    col1.metric("Asset 1 Weight", f"{w_mvp:.2f}")
    col2.metric("Asset 2 Weight", f"{w_mvp_2:.2f}")

    st.subheader("Portfolio Allocation")
    fig_alloc = go.Figure(data=[go.Pie(
        labels=["Asset 1", "Asset 2"],
        values=[w_mvp, w_mvp_2],
        hole=0.4,
        marker=dict(colors=["#636EFA", "#EF553B"])
    )])
    fig_alloc.update_layout(showlegend=True)
    st.plotly_chart(fig_alloc, use_container_width=True)

with tab2:
    # Portfolio returns and risk for plotting efficient frontier
    weights = np.linspace(0, 1, 100)
    port_returns = weights * r1 + (1 - weights) * r2
    port_risks = np.sqrt(weights**2 * sd1**2 + (1 - weights)**2 * sd2**2 + 2 * weights * (1 - weights) * cov12)

    # Plot efficient frontier
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=port_risks, y=port_returns, mode="lines", name="Efficient Frontier"))
    fig.add_trace(go.Scatter(
        x=[np.sqrt(w_mvp**2 * sd1**2 + w_mvp_2**2 * sd2**2 + 2*w_mvp*w_mvp_2*cov12)],
        y=[w_mvp*r1 + w_mvp_2*r2],
        mode="markers",
        marker=dict(color="red", size=12),
        name="Minimum Variance Portfolio"
    ))
    fig.update_layout(
        title="Efficient Frontier",
        xaxis_title="Portfolio Standard Deviation",
        yaxis_title="Portfolio Return",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
