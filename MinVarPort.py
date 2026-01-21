import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page configuration ---
st.set_page_config(
    page_title="Optimal Portfolio Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Optimal Portfolio Calculator with Capital Market Line")
st.markdown("Find your personalized optimal portfolio based on risk aversion")

# --- Sidebar inputs ---
st.sidebar.header("📊 Market Data")

r_h = st.sidebar.number_input("Asset 1 Expected Return (%)", value=5.0, help="Expected annual return for Asset 1") / 100
sd_h = st.sidebar.number_input("Asset 1 Standard Deviation (%)", value=9.0, help="Annual volatility for Asset 1") / 100

r_f = st.sidebar.number_input("Asset 2 Expected Return (%)", value=12.0, help="Expected annual return for Asset 2") / 100
sd_f = st.sidebar.number_input("Asset 2 Standard Deviation (%)", value=20.0, help="Annual volatility for Asset 2") / 100

rho_hf = st.sidebar.number_input("Correlation between Assets", min_value=-1.0, max_value=1.0, value=-0.2, 
                                  help="Correlation coefficient between the two assets")

r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0, help="E.g., T-bill rate") / 100

st.sidebar.header("🎛️ Your Risk Preference")
gamma = st.sidebar.slider(
    "Risk Aversion (γ)", 
    min_value=0.1, 
    max_value=10.0, 
    value=5.0,
    step=0.1,
    help="Lower values = more risk-seeking, Higher values = more risk-averse"
)

# Risk interpretation
if gamma < 2:
    risk_profile = "🚀 **Aggressive** - You are comfortable with high risk for potentially higher returns"
elif gamma < 5:
    risk_profile = "📈 **Moderate** - You balance risk and return"
elif gamma < 8:
    risk_profile = "🛡️ **Conservative** - You prefer lower risk with steady returns"
else:
    risk_profile = "💰 **Very Conservative** - You prioritize capital preservation"

st.sidebar.markdown(f"**Your Risk Profile:** {risk_profile}")

# --- Core calculations ---

def portfolio_ret(w1, r1, r2):
    """Calculate portfolio expected return"""
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    """Calculate portfolio standard deviation"""
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2 * rho * w1 * (1-w1) * sd1 * sd2)

def find_tangency_portfolio(r1, r2, sd1, sd2, rho, rf):
    """Find tangency portfolio using grid search"""
    weights = np.linspace(0, 1, 1000)
    sharpe_ratios = []
    
    for w in weights:
        ret = portfolio_ret(w, r1, r2)
        sd = portfolio_sd(w, sd1, sd2, rho)
        if sd > 0:
            sharpe = (ret - rf) / sd
            sharpe_ratios.append(sharpe)
        else:
            sharpe_ratios.append(-np.inf)
    
    max_idx = np.argmax(sharpe_ratios)
    return weights[max_idx], sharpe_ratios[max_idx]

# Find tangency portfolio
w1_tangency, sharpe_tangency = find_tangency_portfolio(r_h, r_f, sd_h, sd_f, rho_hf, r_free)
w2_tangency = 1 - w1_tangency

ret_tangency = portfolio_ret(w1_tangency, r_h, r_f)
sd_tangency = portfolio_sd(w1_tangency, sd_h, sd_f, rho_hf)

# Find optimal portfolio based on utility
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
utility_optimal = ret_optimal - (gamma / 2) * sd_optimal**2

# --- Tabs for organized layout ---
tab1, tab2, tab3 = st.tabs(["🎯 Your Optimal Portfolio", "📈 Visualization", "📋 Detailed Analysis"])

with tab1:
    st.header("Your Recommended Portfolio")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Expected Return", f"{ret_optimal*100:.2f}%")
    col2.metric("Risk (Std Dev)", f"{sd_optimal*100:.2f}%")
    col3.metric("Utility", f"{utility_optimal:.4f}")
    col4.metric("Sharpe Ratio", f"{(ret_optimal - r_free)/sd_optimal if sd_optimal > 0 else 0:.3f}")
    
    st.subheader("💼 Portfolio Allocation")
    
    # Display weights
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk-Free Asset", f"{w_rf_optimal*100:.2f}%", 
                help="Allocation to risk-free asset (e.g., T-bills)")
    col2.metric("Asset 1 (Risky)", f"{w1_optimal*100:.2f}%",
                help="Allocation to risky Asset 1")
    col3.metric("Asset 2 (Risky)", f"{w2_optimal*100:.2f}%",
                help="Allocation to risky Asset 2")
    
    # Interpretation
    st.markdown("---")
    st.subheader("📝 Interpretation")
    
    if w_tangency_optimal > 1:
        st.info(f"""
        **Leveraged Position:** You are borrowing {(w_tangency_optimal - 1)*100:.1f}% at the risk-free rate 
        to invest {w_tangency_optimal*100:.1f}% in the risky portfolio. This is an aggressive strategy 
        suitable for investors with low risk aversion (γ = {gamma}).
        """)
    elif w_tangency_optimal < 0:
        st.warning(f"""
        **Short Position in Risky Assets:** With very high risk aversion (γ = {gamma}), 
        your optimal allocation suggests going beyond 100% in the risk-free asset, 
        effectively avoiding risky assets entirely.
        """)
    else:
        st.success(f"""
        **Balanced Portfolio:** You allocate {w_tangency_optimal*100:.1f}% to risky assets and 
        {(1-w_tangency_optimal)*100:.1f}% to the risk-free asset. This reflects your risk aversion level (γ = {gamma}).
        """)
    
    # Pie chart
    st.subheader("📊 Visual Allocation")
    
    # Prepare data for pie chart (handle negative weights)
    weights_display = [max(0, w_rf_optimal), max(0, w1_optimal), max(0, w2_optimal)]
    labels_display = ["Risk-Free Asset", "Asset 1", "Asset 2"]
    colors = ["#2ecc71", "#636EFA", "#EF553B"]
    
    # Filter out zero weights
    non_zero = [(w, l, c) for w, l, c in zip(weights_display, labels_display, colors) if w > 0.001]
    if non_zero:
        weights_plot, labels_plot, colors_plot = zip(*non_zero)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(weights_plot,
               labels=labels_plot,
               autopct="%1.1f%%",
               colors=colors_plot,
               startangle=90,
               wedgeprops={'edgecolor': 'black'})
        ax.axis('equal')
        st.pyplot(fig)
    
with tab2:
    st.header("Portfolio Optimization Visualization")
    
    # Generate efficient frontier
    weights = np.linspace(0, 1, 200)
    returns_frontier = [portfolio_ret(w, r_h, r_f) for w in weights]
    sds_frontier = [portfolio_sd(w, sd_h, sd_f, rho_hf) for w in weights]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 1. Efficient frontier
    ax.plot(sds_frontier, returns_frontier, 'b-', linewidth=2.5, label='Efficient Frontier (Risky Assets)')
    
    # 2. Capital Market Line
    sd_max = max(sds_frontier) * 1.3
    sd_cml = np.linspace(0, sd_max, 100)
    ret_cml = r_free + (ret_tangency - r_free) / sd_tangency * sd_cml if sd_tangency > 0 else r_free * np.ones_like(sd_cml)
    ax.plot(sd_cml, ret_cml, 'g--', linewidth=2.5, label='Capital Market Line (CML)', alpha=0.8)
    
    # 3. Tangency portfolio
    ax.scatter(sd_tangency, ret_tangency, color='red', s=300, zorder=5, 
               marker='*', edgecolors='darkred', linewidths=2,
               label=f'Tangency Portfolio (Sharpe={sharpe_tangency:.3f})')
    
    # 4. Optimal portfolio
    ax.scatter(sd_optimal, ret_optimal, color='orange', s=300, zorder=6,
               marker='D', edgecolors='darkorange', linewidths=2,
               label=f'Your Optimal Portfolio (γ={gamma:.1f})')
    
    # 5. Risk-free asset
    ax.scatter(0, r_free, color='green', s=200, zorder=5, marker='s',
               edgecolors='darkgreen', linewidths=2, label='Risk-Free Asset')
    
    # 6. Individual assets
    ax.scatter(sd_h, r_h, color='blue', s=150, zorder=4, marker='o',
               edgecolors='darkblue', linewidths=2, label='Asset 1', alpha=0.7)
    ax.scatter(sd_f, r_f, color='purple', s=150, zorder=4, marker='o',
               edgecolors='darkviolet', linewidths=2, label='Asset 2', alpha=0.7)
    
    # 7. Indifference curve
    sigma_range = np.linspace(0, sd_max, 200)
    indiff_return = utility_optimal + (gamma / 2) * sigma_range**2
    valid_idx = indiff_return <= max(ret_cml) * 1.15
    ax.plot(sigma_range[valid_idx], indiff_return[valid_idx], 'r:', 
            linewidth=3, label=f'Indifference Curve (U={utility_optimal:.4f})', alpha=0.7)
    
    # Formatting
    ax.set_xlabel('Portfolio Standard Deviation (Risk)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Expected Return', fontsize=13, fontweight='bold')
    ax.set_title('Portfolio Optimization: Efficient Frontier, CML & Your Optimal Portfolio', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.01, sd_max)
    ax.set_ylim(min(r_free * 0.8, min(returns_frontier) * 0.95), max(returns_frontier) * 1.1)
    
    # Annotations
    ax.annotate(f'Tangency\nw₁={w1_tangency:.3f}\nw₂={w2_tangency:.3f}', 
                xy=(sd_tangency, ret_tangency), 
                xytext=(sd_tangency + 0.02, ret_tangency - 0.015),
                fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    
    if sd_optimal > 0:
        ax.annotate(f'Your Portfolio\nw₁={w1_optimal:.3f}\nw₂={w2_optimal:.3f}\nwᵣf={w_rf_optimal:.3f}', 
                    xy=(sd_optimal, ret_optimal), 
                    xytext=(sd_optimal + 0.025, ret_optimal + 0.015),
                    fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.5))
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.info("""
    **How to read this chart:**
    - The **blue curve** shows all possible combinations of the two risky assets
    - The **green dashed line** (CML) represents the best risk-return combinations when combining risky assets with the risk-free asset
    - The **red star** is the tangency portfolio (highest Sharpe ratio)
    - The **orange diamond** is YOUR optimal portfolio based on your risk aversion
    - The **red dotted curve** is your indifference curve - combinations of risk and return that give you the same utility
    """)

with tab3:
    st.header("Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Tangency Portfolio")
        st.markdown(f"""
        The tangency portfolio has the highest Sharpe ratio and represents 
        the optimal risky portfolio for all investors (before considering individual risk preferences).
        
        - **Weight in Asset 1:** {w1_tangency*100:.2f}%
        - **Weight in Asset 2:** {w2_tangency*100:.2f}%
        - **Expected Return:** {ret_tangency*100:.2f}%
        - **Standard Deviation:** {sd_tangency*100:.2f}%
        - **Sharpe Ratio:** {sharpe_tangency:.4f}
        """)
        
    with col2:
        st.subheader("💼 Your Optimal Portfolio")
        st.markdown(f"""
        Based on your risk aversion (γ = {gamma:.1f}), your optimal portfolio combines 
        the tangency portfolio with the risk-free asset.
        
        - **Weight in Risk-Free:** {w_rf_optimal*100:.2f}%
        - **Weight in Asset 1:** {w1_optimal*100:.2f}%
        - **Weight in Asset 2:** {w2_optimal*100:.2f}%
        - **Expected Return:** {ret_optimal*100:.2f}%
        - **Standard Deviation:** {sd_optimal*100:.2f}%
        - **Utility:** {utility_optimal:.4f}
        """)
    
    st.markdown("---")
    st.subheader("📐 Mathematical Details")
    
    st.markdown(f"""
    **Utility Function:** U = E(W) - (γ/2) × Var(W)
    
    **Optimal Weight in Tangency Portfolio:**  
    w* = [E(Rₜ) - Rf] / [γ × σₜ²] = [{ret_tangency:.4f} - {r_free:.4f}] / [{gamma:.1f} × {sd_tangency**2:.6f}] = {w_tangency_optimal:.4f}
    
    **Complete Portfolio Weights:**
    - w_Risk-Free = 1 - w* = {w_rf_optimal:.4f}
    - w_Asset1 = w* × w₁ᵗᵃⁿᵍᵉⁿᶜʸ = {w_tangency_optimal:.4f} × {w1_tangency:.4f} = {w1_optimal:.4f}
    - w_Asset2 = w* × w₂ᵗᵃⁿᵍᵉⁿᶜʸ = {w_tangency_optimal:.4f} × {w2_tangency:.4f} = {w2_optimal:.4f}
    """)
    
    # Sensitivity analysis
    st.markdown("---")
    st.subheader("🔍 Sensitivity Analysis: Impact of Risk Aversion")
    
    gamma_range = np.linspace(0.5, 10, 50)
    w_tangency_range = [(ret_tangency - r_free) / (g * sd_tangency**2) if sd_tangency > 0 else 0 for g in gamma_range]
    ret_range = [r_free + w * (ret_tangency - r_free) for w in w_tangency_range]
    sd_range = [abs(w) * sd_tangency for w in w_tangency_range]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left plot: Allocation vs gamma
    ax1.plot(gamma_range, [w*100 for w in w_tangency_range], 'b-', linewidth=2, label='Risky Assets')
    ax1.plot(gamma_range, [(1-w)*100 for w in w_tangency_range], 'g-', linewidth=2, label='Risk-Free Asset')
    ax1.axvline(gamma, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Your γ = {gamma:.1f}')
    ax1.set_xlabel('Risk Aversion (γ)', fontweight='bold')
    ax1.set_ylabel('Allocation (%)', fontweight='bold')
    ax1.set_title('Portfolio Allocation vs Risk Aversion', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Right plot: Risk-Return vs gamma
    ax2.plot([s*100 for s in sd_range], [r*100 for r in ret_range], 'purple', linewidth=2.5)
    ax2.scatter(sd_optimal*100, ret_optimal*100, color='red', s=200, zorder=5, 
                label=f'Your Portfolio (γ={gamma:.1f})')
    ax2.set_xlabel('Risk - Standard Deviation (%)', fontweight='bold')
    ax2.set_ylabel('Expected Return (%)', fontweight='bold')
    ax2.set_title('Your Portfolio on the CML', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
st.markdown("**Note:** This tool is for educational purposes. Consult a financial advisor for investment decisions.")
