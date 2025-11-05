
import streamlit as st
import pandas as pd
from core.evm_engine import calculate_evm
import json

st.title("EVM Calculations")
st.write("Step 2: Calculate EVM metrics and export results")

# Check prerequisites
data_loaded = 'project_data' in st.session_state
globals_set = 'global_values' in st.session_state
calculated = 'calculated_data' in st.session_state

# Status indicators
col1, col2, col3 = st.columns(3)
with col1:
    if data_loaded:
        st.success("✓ Data Loaded")
    else:
        st.error("✗ No Data")
with col2:
    if globals_set:
        st.success("✓ Settings Ready")
    else:
        st.error("✗ No Settings")
with col3:
    if calculated:
        st.success("✓ Calculated")
    else:
        st.info("○ Not Calculated")

st.divider()

# Prerequisites check
if not globals_set or not data_loaded:
    st.error("⚠️ Prerequisites not met!")
    if not data_loaded:
        st.warning("📋 Please load data in the **Data Input** page first.")
    if not globals_set:
        st.warning("⚙️ Please configure global settings in the **Data Input** page first.")
    st.stop()

# Show summary of input data
with st.expander("📊 Input Data Summary", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Projects", len(st.session_state.project_data))
        st.write("**Global Settings:**")
        st.json(st.session_state.global_values)
    with col2:
        st.write("**Data Preview:**")
        st.dataframe(st.session_state.project_data.head(3), use_container_width=True)

st.divider()

# Calculation Section
st.header("1. Calculate EVM Metrics")

if calculated:
    st.info("ℹ️ Calculations have already been performed. Click below to recalculate.")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🔄 Calculate EVM Metrics", use_container_width=True, type="primary"):
        with st.spinner("Calculating EVM metrics..."):
            import warnings

            # Capture warnings
            warning_list = []
            def warning_handler(message, category, filename, lineno, file=None, line=None):
                warning_list.append(str(message))

            old_showwarning = warnings.showwarning
            warnings.showwarning = warning_handler

            try:
                st.session_state.calculated_data = calculate_evm(
                    st.session_state.project_data.copy(),
                    st.session_state.global_values
                )

                # Restore warning handler
                warnings.showwarning = old_showwarning

                # Show any warnings
                if warning_list:
                    st.warning("⚠️ Calculation completed with warnings:")
                    for warn in warning_list:
                        st.write(f"- {warn}")
                    st.info("💡 Check the Data Quality section in Data Input page for details.")

                st.success("✅ EVM calculations completed successfully!")
                st.rerun()
            except ValueError as e:
                warnings.showwarning = old_showwarning
                st.error(f"❌ Data validation error: {e}")
                st.info("💡 Tip: Check that all required columns are mapped and contain valid data.")
                st.stop()
            except Exception as e:
                warnings.showwarning = old_showwarning
                st.error(f"❌ Calculation error: {e}")
                st.error("**Error details:** " + str(type(e).__name__))

                # Show stack trace for debugging
                import traceback
                with st.expander("🔍 Error Details (for debugging)"):
                    st.code(traceback.format_exc())

                with st.expander("💡 Troubleshooting Tips"):
                    st.markdown("""
                    **Common issues:**
                    - **Date format errors**: Ensure dates are in YYYY-MM-DD format or valid Excel serial numbers
                    - **Missing data**: Check that all required fields have values
                    - **Invalid numbers**: Ensure BAC and AC are positive numbers
                    - **Column mapping**: Verify all required columns are properly mapped in Data Input

                    **Date format examples:**
                    - ✅ Good: `2024-01-15`, `2024/01/15`, `44940` (Excel serial)
                    - ❌ Bad: `15-01-2024`, `15/01/24`, very large numbers

                    **Action items:**
                    1. Go back to Data Input page
                    2. Open "Data Quality Check" section
                    3. Look for columns with problematic values
                    4. Fix the source CSV file or adjust column mapping
                    """)
                st.stop()

with col2:
    if calculated:
        if st.button("🗑️ Clear Results", use_container_width=True):
            del st.session_state.calculated_data
            st.rerun()

st.divider()

# Results Section
if calculated:
    st.header("2. Review Results")

    df = st.session_state.calculated_data

    # Key metrics summary
    st.subheader("Key Metrics Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_cpi = df['cpi'].mean()
        st.metric(
            "Avg CPI",
            f"{avg_cpi:.2f}",
            delta=f"{avg_cpi - 1:.2f}",
            delta_color="normal"
        )

    with col2:
        avg_spi = df['spi'].mean()
        st.metric(
            "Avg SPI",
            f"{avg_spi:.2f}",
            delta=f"{avg_spi - 1:.2f}",
            delta_color="normal"
        )

    with col3:
        total_cv = df['cv'].sum()
        st.metric(
            "Total CV",
            f"${total_cv:,.0f}",
            delta_color="normal" if total_cv >= 0 else "inverse"
        )

    with col4:
        avg_complete = df['percent_complete'].mean()
        st.metric("Avg % Complete", f"{avg_complete:.1f}%")

    st.divider()

    # Full results table
    st.subheader("Detailed Results")

    # Column selector
    all_columns = df.columns.tolist()
    default_columns = ['project_id', 'project_name', 'bac', 'ac', 'ev', 'pv',
                      'cpi', 'spi', 'cv', 'sv', 'percent_complete']
    available_defaults = [col for col in default_columns if col in all_columns]

    selected_columns = st.multiselect(
        "Select columns to display",
        all_columns,
        default=available_defaults,
        help="Choose which columns to show in the results table"
    )

    if selected_columns:
        st.dataframe(df[selected_columns], use_container_width=True, height=400)
    else:
        st.warning("Please select at least one column to display")

    # Option to show all columns
    with st.expander("Show All Columns", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)

    st.divider()

    # Export Section
    st.header("3. Export Results")

    col1, col2 = st.columns(2)

    with col1:
        file_name = st.text_input(
            "File name (without extension)",
            "evm_results",
            help="Enter a name for your export file"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        include_settings = st.checkbox(
            "Include settings in JSON export",
            value=True,
            help="Include global values in JSON export"
        )

    # Export buttons
    col1, col2 = st.columns(2)

    with col1:
        # Export to CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{file_name}.csv",
            mime='text/csv',
            use_container_width=True,
            help="Download results as CSV (data only)"
        )

    with col2:
        # Export to JSON
        calculated_data_for_json = df.copy()
        for col in calculated_data_for_json.select_dtypes(include=['datetime64[ns]']).columns:
            calculated_data_for_json[col] = calculated_data_for_json[col].dt.strftime('%Y-%m-%d')

        if include_settings:
            export_data = {
                'global_values': st.session_state.global_values,
                'projects': calculated_data_for_json.to_dict(orient='records')
            }
        else:
            export_data = {
                'projects': calculated_data_for_json.to_dict(orient='records')
            }

        json_data = json.dumps(export_data, indent=4).encode('utf-8')
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{file_name}.json",
            mime='application/json',
            use_container_width=True,
            help="Download results as JSON (includes settings if selected)"
        )

    st.divider()
    st.success("✅ Ready to analyze! Navigate to **Project Analysis** for detailed project views.")

else:
    st.info("👆 Click 'Calculate EVM Metrics' above to generate results.")
