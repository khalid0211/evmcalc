
import streamlit as st
from utils.file_utils import read_csv, read_json
import pandas as pd

st.title("Data Input")
st.write("Step 1: Load your project data and configure calculation settings")

# Progress indicator
col1, col2, col3 = st.columns(3)
with col1:
    data_loaded = 'project_data' in st.session_state
    if data_loaded:
        st.success("✓ Data Loaded")
    else:
        st.info("○ Data Not Loaded")
with col2:
    globals_set = 'global_values' in st.session_state
    if globals_set:
        st.success("✓ Settings Configured")
    else:
        st.info("○ Settings Not Set")
with col3:
    if data_loaded and globals_set:
        st.success("✓ Ready to Calculate")
    else:
        st.warning("○ Not Ready")

st.divider()

# File Upload - FIRST STEP
st.header("1. Load Data")

# Use tabs for better organization
tab1, tab2 = st.tabs(["📁 Upload CSV", "📄 Upload JSON"])

with tab1:
    st.write("Upload a CSV file with your project data")
    csv_file = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_uploader")

    if csv_file is not None:
        df = read_csv(csv_file)
        df = df.loc[:, ~df.columns.str.contains('Unnamed:', case=False)]
        st.session_state.raw_data = df
        st.success(f"✓ CSV loaded: {len(df)} rows")

    if 'raw_data' in st.session_state:
        st.subheader("Map CSV Columns")
        df = st.session_state.raw_data
        columns = df.columns.tolist()

        with st.expander("Preview raw data", expanded=False):
            st.dataframe(df.head())

        with st.form("column_mapping_form"):
            st.write("Map your CSV columns to the required fields:")

            required_fields = {
                'project_id': 'Project ID',
                'project_name': 'Project Name',
                'department': 'Department',
                'bac': 'Budget (BAC)',
                'ac': 'Actual Cost (AC)',
                'plan_start_date': 'Plan Start Date',
                'plan_finish_date': 'Plan Finish Date',
                'data_date': 'Data Date'
            }

            optional_fields = {
                'ev': 'Earned Value (EV)',
                'pv': 'Planned Value (PV)',
                'curve': 'Curve',
                'beta': 'Beta',
                'alpha': 'Alpha',
                'inflation_rate': 'Inflation Rate',
                'manual_ev': 'Manual EV',
                'manual_pv': 'Manual PV'
            }

            mapping = {}
            col_left, col_right = st.columns(2)

            with col_left:
                st.write("**Required Fields**")
                for field, name in required_fields.items():
                    mapping[field] = st.selectbox(name, columns, key=f"req_{field}")

            with col_right:
                st.write("**Optional Fields** (select 'None' to skip)")
                for field, name in optional_fields.items():
                    mapping[field] = st.selectbox(name, ['None'] + columns, index=0, key=f"opt_{field}")

            submitted = st.form_submit_button("✓ Confirm Column Mapping", width='stretch')
            if submitted:
                renamed_df = df.rename(columns={v: k for k, v in mapping.items() if v != 'None'})
                st.session_state.project_data = renamed_df
                st.success("✓ Columns mapped successfully! Proceed to configure global settings below.")
                st.rerun()

with tab2:
    st.write("Upload a JSON file (previously exported from this application)")
    json_file = st.file_uploader("Choose a JSON file", type=["json"], key="json_uploader")

    if json_file is not None:
        try:
            data = read_json(json_file)
            st.session_state.project_data = pd.DataFrame(data['projects'])
            st.session_state.global_values = data['global_values']
            st.success(f"✓ JSON loaded: {len(st.session_state.project_data)} projects and global settings")
            st.info("ℹ️ Note: Global values from JSON have been loaded. You can modify them below if needed.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error reading JSON file: {e}")

st.divider()

# Show loaded data
if 'project_data' in st.session_state:
    st.subheader("Loaded Project Data")
    df = st.session_state.project_data
    st.info(f"📊 {len(df)} projects loaded")

    # Data quality check - DETAILED INVESTIGATION
    date_columns = ['plan_start_date', 'plan_finish_date', 'data_date']
    available_date_cols = [col for col in date_columns if col in df.columns]

    # Also check original column names before mapping
    original_date_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['date', 'start', 'finish', 'plan']):
            original_date_cols.append(col)

    # Show data quality check prominently if there are date columns
    has_issues = False

    if available_date_cols or original_date_cols:
        # Check for issues first
        check_cols = available_date_cols if available_date_cols else original_date_cols
        for col in check_cols:
            if col in df.columns:
                try:
                    numeric_check = pd.to_numeric(df[col], errors='coerce')
                    if numeric_check.notna().any():
                        max_val = numeric_check.max()
                        if max_val > 50000:
                            has_issues = True
                            break
                except:
                    pass

        with st.expander("⚠️ Data Quality Check" + (" - ISSUES FOUND!" if has_issues else ""), expanded=has_issues):
            st.write("**Date Column Analysis:**")

            check_cols = available_date_cols if available_date_cols else original_date_cols

            for col in check_cols:
                if col not in df.columns:
                    continue

                st.write(f"\n**Column: `{col}`**")

                # Show all unique values if small dataset
                if len(df) <= 20:
                    st.write("All values:", df[col].tolist())
                else:
                    st.write("First 10 values:", df[col].head(10).tolist())

                # Show data type
                st.write(f"Data type: `{df[col].dtype}`")

                # Check for very large numbers
                try:
                    numeric_check = pd.to_numeric(df[col], errors='coerce')
                    numeric_count = numeric_check.notna().sum()

                    if numeric_count > 0:
                        max_val = numeric_check.max()
                        min_val = numeric_check.min()
                        st.write(f"Numeric values found: {numeric_count}/{len(df)}")
                        st.write(f"Numeric range: {min_val:.2f} to {max_val:.2f}")

                        # Show problem values
                        if max_val > 50000:
                            st.error(f"🚨 PROBLEM: Found very large values (max: {max_val:.0f})")
                            st.write("These are NOT valid Excel dates (Excel dates range from 1 to ~50,000)")

                            problem_mask = numeric_check > 50000
                            problem_df = df[problem_mask][[col]]
                            problem_df['row_index'] = problem_df.index
                            problem_df['numeric_value'] = numeric_check[problem_mask]

                            st.write("**Problematic rows:**")
                            st.dataframe(problem_df)

                            st.warning(f"⚠️ Found {problem_mask.sum()} rows with invalid date values. These will be treated as missing dates in calculations.")
                        elif max_val < 1:
                            st.warning(f"⚠️ Found values < 1 (min: {min_val:.2f}). These are not valid Excel dates.")
                        else:
                            st.success(f"✓ All numeric values are in valid Excel date range (1-50,000)")
                    else:
                        st.info("No numeric values found - will attempt to parse as date strings")

                    # Check for non-numeric values
                    non_numeric = df[col][numeric_check.isna() & df[col].notna()]
                    if len(non_numeric) > 0:
                        st.write(f"Non-numeric values: {len(non_numeric)}")
                        st.write("Sample non-numeric values:", non_numeric.head(5).tolist())

                except Exception as e:
                    st.error(f"Error analyzing column: {e}")

                st.divider()

    st.dataframe(df, width='stretch')

st.divider()

# Global Values Form - SECOND STEP
st.header("2. Configure Global Settings")

# Initialize with existing values if available
existing_values = st.session_state.get('global_values', {})

with st.form("global_values_form"):
    st.write("Set default calculation parameters (applied to projects without specific values)")

    col1, col2 = st.columns(2)

    with col1:
        global_curve = st.selectbox(
            "Curve Type",
            ["linear", "s-curve"],
            index=0 if existing_values.get('curve') == 'linear' else 1
        )
        global_alpha = st.number_input(
            "Alpha (S-curve parameter)",
            value=float(existing_values.get('alpha', 2.0)),
            help="Shape parameter for S-curve distribution"
        )
        global_beta = st.number_input(
            "Beta (S-curve parameter)",
            value=float(existing_values.get('beta', 2.0)),
            help="Shape parameter for S-curve distribution"
        )

    with col2:
        global_inflation_rate = st.number_input(
            "Inflation Rate (%)",
            value=float(existing_values.get('inflation_rate', 3.5)),
            help="Annual inflation rate for present value calculations"
        )
        use_manual_ev = st.checkbox(
            "Use Manual EV",
            value=existing_values.get('use_manual_ev', False),
            help="Use manually entered Earned Value instead of calculated"
        )
        use_manual_pv = st.checkbox(
            "Use Manual PV",
            value=existing_values.get('use_manual_pv', False),
            help="Use manually entered Planned Value instead of calculated"
        )

    submitted = st.form_submit_button("✓ Save Global Settings", width='stretch')
    if submitted:
        st.session_state.global_values = {
            "curve": global_curve,
            "alpha": global_alpha,
            "beta": global_beta,
            "inflation_rate": global_inflation_rate,
            "use_manual_ev": use_manual_ev,
            "use_manual_pv": use_manual_pv,
        }
        st.success("✓ Global settings saved!")
        st.rerun()

# Show current global values
if 'global_values' in st.session_state:
    with st.expander("Current Global Settings", expanded=False):
        st.json(st.session_state.global_values)

st.divider()

# Next steps guidance
if data_loaded and globals_set:
    st.success("✅ Setup complete! Navigate to **EVM Calculations** to run the calculations.")
elif data_loaded:
    st.warning("⚠️ Please configure global settings above before proceeding.")
elif globals_set:
    st.warning("⚠️ Please load data above before proceeding.")
else:
    st.info("ℹ️ Start by loading your data and configuring settings above.")








