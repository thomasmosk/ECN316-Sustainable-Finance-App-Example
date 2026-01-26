import streamlit as st
import numpy as np

st.title("🎯 Portfolio Optimizer")

# Sidebar inputs
st.sidebar.header("Asset Data")

r_h = st.sidebar.number_input("Asset 1 Expected Return (%)", value=5.0) / 100
sd_h = st.sidebar.number_input("Asset 1 Standard Deviation (%)", value=9.0) / 100

r_f = st.sidebar.number_input("Asset 2 Expected Return (%)", value=12.0) / 100
sd_f = st.sidebar.number_input("Asset 2 Standard Deviation (%)", value=20.0) / 100

rho_hf = st.sidebar.number_input("Correlation", min_value=-1.0, max_value=1.0, value=-0.2)

r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0) / 100

st.sidebar.header("Your Preferences")
gamma = st.sidebar.slider("Risk Aversion (γ)", min_value=0.1, max_value=10.0, value=5.0, step=0.1)

# Functions
def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2 * rho * w1 * (1-w1) * sd1 * sd2)

# Find tangency portfolio
weights = np.linspace(0, 1, 1000)
sharpe_ratios = []

for w in weights:
    ret = portfolio_ret(w, r_h, r_f)
    sd = portfolio_sd(w, sd_h, sd_f, rho_hf)
    if sd > 0:
        sharpe = (ret - r_free) / sd
        sharpe_ratios.append(sharpe)
    else:
        sharpe_ratios.append(-np.inf)

max_idx = np.argmax(sharpe_ratios)
w1_tangency = weights[max_idx]
w2_tangency = 1 - w1_tangency

ret_tangency = portfolio_ret(w1_tangency, r_h, r_f)
sd_tangency = portfolio_sd(w1_tangency, sd_h, sd_f, rho_hf)

# Find optimal portfolio
if sd_tangency > 0:
    w_tangency_optimal = (ret_tangency - r_free) / (gamma * sd_tangency**2)
else:
    w_tangency_optimal = 0

# Complete portfolio weights
w1_optimal = w_tangency_optimal * w1_tangency
w2_optimal = w_tangency_optimal * w2_tangency
w_rf_optimal = 1 - w_tangency_optimal

# Optimal portfolio characteristics
ret_optimal = r_free + w_tangency_optimal * (ret_tangency - r_free)
sd_optimal = abs(w_tangency_optimal) * sd_tangency

# Display results
st.header("Your Optimal Portfolio")

col1, col2, col3 = st.columns(3)
col1.metric("Risk-Free Asset", f"{w_rf_optimal*100:.2f}%")
col2.metric("Asset 1", f"{w1_optimal*100:.2f}%")
col3.metric("Asset 2", f"{w2_optimal*100:.2f}%")

st.write("")
col1, col2 = st.columns(2)
col1.metric("Expected Return", f"{ret_optimal*100:.2f}%")
col2.metric("Risk (Std Dev)", f"{sd_optimal*100:.2f}%")
