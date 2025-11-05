import streamlit as st

st.set_page_config(
    page_title="EVM Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 EVM Calculator")
st.write("**Earned Value Management Analysis Tool**")

st.divider()

# Welcome and Instructions
st.header("Welcome!")
st.write("""
This application helps you perform Earned Value Management (EVM) calculations
for your projects. Follow the three-step workflow below to get started.
""")

st.divider()

# Workflow Guide
st.header("🔄 Workflow")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ Data Input")
    st.write("""
    - Upload CSV or JSON data
    - Map column names
    - Configure global settings
    - Set calculation parameters
    """)
    if st.button("Go to Data Input →", width='stretch'):
        st.switch_page("pages/1_Data_Input.py")

with col2:
    st.subheader("2️⃣ EVM Calculations")
    st.write("""
    - Run EVM calculations
    - Review summary metrics
    - View detailed results
    - Export data (CSV/JSON)
    """)
    if st.button("Go to Calculations →", width='stretch'):
        st.switch_page("pages/2_EVM_Calculations.py")

with col3:
    st.subheader("3️⃣ Project Analysis")
    st.write("""
    - Select individual projects
    - View performance charts
    - Analyze trends over time
    - Assess project health
    """)
    if st.button("Go to Analysis →", width='stretch'):
        st.switch_page("pages/3_Project_Analysis.py")

st.divider()

# Current Status
st.header("📈 Current Status")

data_loaded = 'project_data' in st.session_state
globals_set = 'global_values' in st.session_state
calculated = 'calculated_data' in st.session_state

col1, col2, col3 = st.columns(3)

with col1:
    if data_loaded:
        st.success("✓ Data Loaded")
        st.info(f"Projects: {len(st.session_state.project_data)}")
    else:
        st.warning("○ No Data Loaded")

with col2:
    if globals_set:
        st.success("✓ Settings Configured")
        settings = st.session_state.global_values
        st.info(f"Curve: {settings.get('curve', 'N/A')}")
    else:
        st.warning("○ Settings Not Configured")

with col3:
    if calculated:
        st.success("✓ Results Available")
        st.info(f"Projects: {len(st.session_state.calculated_data)}")
    else:
        st.info("○ No Results Yet")

st.divider()

# Quick Start Guide
with st.expander("📖 Quick Start Guide", expanded=False):
    st.markdown("""
    ### Getting Started

    **For CSV Files:**
    1. Go to **Data Input** page
    2. Upload your CSV file
    3. Map your columns to required fields
    4. Configure global calculation settings
    5. Proceed to **EVM Calculations** page

    **For JSON Files:**
    1. Go to **Data Input** page
    2. Upload your JSON file (previously exported from this app)
    3. Settings will be loaded automatically
    4. Proceed to **EVM Calculations** page

    ### Required Data Fields
    - Project ID
    - Project Name
    - Department
    - Budget (BAC)
    - Actual Cost (AC)
    - Plan Start Date
    - Plan Finish Date
    - Data Date

    ### Optional Fields
    - Earned Value (EV) - calculated if not provided
    - Planned Value (PV) - calculated if not provided
    - Curve parameters (Alpha, Beta)
    - Inflation Rate

    ### EVM Metrics Calculated
    - Cost Performance Index (CPI)
    - Schedule Performance Index (SPI)
    - Cost Variance (CV)
    - Schedule Variance (SV)
    - Estimate at Completion (EAC)
    - Variance at Completion (VAC)
    - And many more...
    """)

# About section
with st.expander("ℹ️ About EVM", expanded=False):
    st.markdown("""
    ### What is Earned Value Management?

    Earned Value Management (EVM) is a project management technique for measuring
    project performance and progress in an objective manner. It combines measurements
    of scope, schedule, and cost in a single integrated system.

    **Key Metrics:**
    - **PV (Planned Value)**: Budgeted cost for work scheduled
    - **EV (Earned Value)**: Budgeted cost for work performed
    - **AC (Actual Cost)**: Actual cost for work performed
    - **CPI (Cost Performance Index)**: EV / AC (>1 is good)
    - **SPI (Schedule Performance Index)**: EV / PV (>1 is good)
    """)

st.divider()

# Footer
st.caption("EVM Calculator © 2024 | Use the sidebar navigation to access different sections")