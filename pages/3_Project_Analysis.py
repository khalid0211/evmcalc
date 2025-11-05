
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("Project Analysis")
st.write("Step 3: Analyze individual project performance")

# Check prerequisites
if 'calculated_data' not in st.session_state:
    st.error("⚠️ No calculated data available!")
    st.warning("📊 Please run calculations in the **EVM Calculations** page first.")
    st.stop()

df = st.session_state.calculated_data

st.divider()

# Project Selection
st.header("Select Project")

# Create project list with better formatting
if 'project_id' in df.columns and 'project_name' in df.columns:
    project_list = df['project_id'].astype(str) + " - " + df['project_name'].astype(str)
else:
    st.error("Required columns 'project_id' or 'project_name' not found in data")
    st.stop()

selected_project = st.selectbox(
    "Choose a project to analyze",
    project_list.unique(),
    help="Select a project to view detailed metrics and analysis"
)

if selected_project:
    project_id = selected_project.split(" - ")[0]
    project_data = df[df['project_id'].astype(str) == project_id].copy()

    # Sort by Data Date if available
    if 'data_date' in project_data.columns:
        project_data = project_data.sort_values(by='data_date', ascending=True)

    st.divider()

    # Project Overview
    st.header(f"📋 {selected_project}")

    # Key Performance Indicators
    st.subheader("Key Performance Indicators")

    if len(project_data) > 0:
        latest = project_data.iloc[-1]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if 'percent_complete' in latest:
                st.metric("% Complete", f"{latest['percent_complete']:.1f}%")
            else:
                st.metric("% Complete", "N/A")

        with col2:
            if 'cpi' in latest and pd.notna(latest['cpi']):
                delta = latest['cpi'] - 1
                st.metric(
                    "CPI",
                    f"{latest['cpi']:.2f}",
                    delta=f"{delta:.2f}",
                    delta_color="normal" if delta >= 0 else "inverse"
                )
            else:
                st.metric("CPI", "N/A")

        with col3:
            if 'spi' in latest and pd.notna(latest['spi']):
                delta = latest['spi'] - 1
                st.metric(
                    "SPI",
                    f"{latest['spi']:.2f}",
                    delta=f"{delta:.2f}",
                    delta_color="normal" if delta >= 0 else "inverse"
                )
            else:
                st.metric("SPI", "N/A")

        with col4:
            if 'cv' in latest and pd.notna(latest['cv']):
                st.metric(
                    "Cost Variance",
                    f"${latest['cv']:,.0f}",
                    delta_color="normal" if latest['cv'] >= 0 else "inverse"
                )
            else:
                st.metric("Cost Variance", "N/A")

        with col5:
            if 'sv' in latest and pd.notna(latest['sv']):
                st.metric(
                    "Schedule Variance",
                    f"${latest['sv']:,.0f}",
                    delta_color="normal" if latest['sv'] >= 0 else "inverse"
                )
            else:
                st.metric("Schedule Variance", "N/A")

        st.divider()

        # Financial Overview
        st.subheader("Financial Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if 'bac' in latest:
                st.metric("Budget (BAC)", f"${latest['bac']:,.0f}")

        with col2:
            if 'ac' in latest:
                st.metric("Actual Cost (AC)", f"${latest['ac']:,.0f}")

        with col3:
            if 'eac' in latest and pd.notna(latest['eac']):
                st.metric("Est. at Completion", f"${latest['eac']:,.0f}")
            else:
                st.metric("Est. at Completion", "N/A")

        with col4:
            if 'vac' in latest and pd.notna(latest['vac']):
                st.metric(
                    "Variance at Completion",
                    f"${latest['vac']:,.0f}",
                    delta_color="normal" if latest['vac'] >= 0 else "inverse"
                )
            else:
                st.metric("Variance at Completion", "N/A")

        st.divider()

        # Visualizations
        st.subheader("Performance Trends")

        # EVM Chart (AC, PV, EV)
        if all(col in project_data.columns for col in ['ac', 'pv', 'ev']):
            fig = go.Figure()

            if 'data_date' in project_data.columns:
                x_data = project_data['data_date']
                x_label = 'Date'
            else:
                x_data = range(len(project_data))
                x_label = 'Data Point'

            fig.add_trace(go.Scatter(
                x=x_data, y=project_data['ac'],
                name='Actual Cost (AC)',
                line=dict(color='red', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=x_data, y=project_data['pv'],
                name='Planned Value (PV)',
                line=dict(color='blue', width=3, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=x_data, y=project_data['ev'],
                name='Earned Value (EV)',
                line=dict(color='green', width=3)
            ))

            fig.update_layout(
                title='EVM Performance Over Time',
                xaxis_title=x_label,
                yaxis_title='Value ($)',
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, width='stretch')

        # Performance Indices
        if all(col in project_data.columns for col in ['cpi', 'spi']):
            col1, col2 = st.columns(2)

            with col1:
                fig_cpi = go.Figure()

                if 'data_date' in project_data.columns:
                    x_data = project_data['data_date']
                else:
                    x_data = range(len(project_data))

                fig_cpi.add_trace(go.Scatter(
                    x=x_data,
                    y=project_data['cpi'],
                    name='CPI',
                    line=dict(color='purple', width=3),
                    fill='tozeroy'
                ))
                fig_cpi.add_hline(y=1, line_dash="dash", line_color="gray",
                                 annotation_text="Target (1.0)")
                fig_cpi.update_layout(
                    title='Cost Performance Index (CPI)',
                    yaxis_title='CPI',
                    height=300
                )
                st.plotly_chart(fig_cpi, width='stretch')

            with col2:
                fig_spi = go.Figure()
                fig_spi.add_trace(go.Scatter(
                    x=x_data,
                    y=project_data['spi'],
                    name='SPI',
                    line=dict(color='orange', width=3),
                    fill='tozeroy'
                ))
                fig_spi.add_hline(y=1, line_dash="dash", line_color="gray",
                                 annotation_text="Target (1.0)")
                fig_spi.update_layout(
                    title='Schedule Performance Index (SPI)',
                    yaxis_title='SPI',
                    height=300
                )
                st.plotly_chart(fig_spi, width='stretch')

        st.divider()

        # Detailed Data Table
        st.subheader("Detailed Project Data")

        # Select key columns if they exist
        key_columns = ['data_date', 'bac', 'ac', 'pv', 'ev', 'cpi', 'spi', 'cv', 'sv',
                      'percent_complete', 'eac', 'vac']
        available_columns = [col for col in key_columns if col in project_data.columns]

        if available_columns:
            st.dataframe(
                project_data[available_columns],
                width='stretch',
                height=300
            )
        else:
            st.dataframe(project_data, width='stretch', height=300)

        # Option to show all columns
        with st.expander("Show All Columns", expanded=False):
            st.dataframe(project_data, width='stretch', height=400)

        st.divider()

        # Health Status
        st.subheader("Project Health Assessment")

        health_col1, health_col2 = st.columns(2)

        with health_col1:
            st.write("**Cost Performance:**")
            if 'cpi' in latest and pd.notna(latest['cpi']):
                if latest['cpi'] >= 1.0:
                    st.success(f"✅ Under Budget (CPI: {latest['cpi']:.2f})")
                elif latest['cpi'] >= 0.9:
                    st.warning(f"⚠️ Slightly Over Budget (CPI: {latest['cpi']:.2f})")
                else:
                    st.error(f"❌ Significantly Over Budget (CPI: {latest['cpi']:.2f})")
            else:
                st.info("No CPI data available")

        with health_col2:
            st.write("**Schedule Performance:**")
            if 'spi' in latest and pd.notna(latest['spi']):
                if latest['spi'] >= 1.0:
                    st.success(f"✅ Ahead of Schedule (SPI: {latest['spi']:.2f})")
                elif latest['spi'] >= 0.9:
                    st.warning(f"⚠️ Slightly Behind Schedule (SPI: {latest['spi']:.2f})")
                else:
                    st.error(f"❌ Significantly Behind Schedule (SPI: {latest['spi']:.2f})")
            else:
                st.info("No SPI data available")

        st.divider()

        # Time-Series Analysis Table
        st.subheader("📊 Time-Series Analysis by Data Date")
        st.write("View all calculated metrics over time, organized by category")

        # Define variable categories (reorganized logically)
        variable_categories = {
            'Mandatory Inputs': {
                'bac': {'label': 'Budget at Completion (BAC)', 'format': 'currency'},
                'ac': {'label': 'Actual Cost (AC)', 'format': 'currency'},
                'plan_start_date': {'label': 'Plan Start Date', 'format': 'date'},
                'plan_finish_date': {'label': 'Plan Finish Date', 'format': 'date'},
                'data_date': {'label': 'Data Date', 'format': 'date'},
            },
            'Optional Inputs': {
                'alpha': {'label': 'Alpha', 'format': 'decimal2'},
                'beta': {'label': 'Beta', 'format': 'decimal2'},
                'inflation_rate': {'label': 'Inflation Rate (%)', 'format': 'decimal2'},
            },
            'Estimated Variables': {
                'pv': {'label': 'Planned Value (PV)', 'format': 'currency'},
                'ev': {'label': 'Earned Value (EV)', 'format': 'currency'},
                'present_value': {'label': 'Present Value', 'format': 'currency'},
            },
            'Duration Calculations': {
                'actual_duration_months': {'label': 'Actual Duration (months)', 'format': 'decimal2'},
                'original_duration_months': {'label': 'Original Duration (months)', 'format': 'decimal2'},
            },
            'EVM Core Metrics': {
                'percent_complete': {'label': 'Percent Complete (%)', 'format': 'decimal1'},
                'cv': {'label': 'Cost Variance (CV)', 'format': 'currency'},
                'sv': {'label': 'Schedule Variance (SV)', 'format': 'currency'},
                'cpi': {'label': 'Cost Performance Index (CPI)', 'format': 'decimal2'},
                'spi': {'label': 'Schedule Performance Index (SPI)', 'format': 'decimal2'},
                'tcpi': {'label': 'To-Complete Performance Index (TCPI)', 'format': 'decimal2'},
            },
            'Forecasting Metrics': {
                'eac': {'label': 'Estimate at Completion (EAC)', 'format': 'currency'},
                'etc': {'label': 'Estimate to Complete (ETC)', 'format': 'currency'},
                'vac': {'label': 'Variance at Completion (VAC)', 'format': 'currency'},
            },
            'Earned Schedule Metrics': {
                'es': {'label': 'Earned Schedule (ES)', 'format': 'decimal2'},
                'spie': {'label': 'Schedule Performance Index - ES (SPIE)', 'format': 'decimal2'},
                'tve': {'label': 'Time Variance - ES (TVE)', 'format': 'decimal2'},
                'ld': {'label': 'Likely Duration (months)', 'format': 'decimal2'},
                'likely_completion': {'label': 'Likely Completion Date', 'format': 'date'},
            },
            'Percentage Metrics': {
                'percent_budget_used': {'label': 'Percent Budget Used (%)', 'format': 'decimal1'},
                'percent_time_used': {'label': 'Percent Time Used (%)', 'format': 'decimal1'},
            },
            'Advanced Financial Metrics': {
                'planned_value_project': {'label': 'Planned Value Project (PV)', 'format': 'currency'},
                'likely_value_project': {'label': 'Likely Value Project (PV)', 'format': 'currency'},
                'percent_present_value_project': {'label': 'Percent Present Value Project (%)', 'format': 'decimal1'},
                'percent_likely_value_project': {'label': 'Percent Likely Value Project (%)', 'format': 'decimal1'},
            }
        }

        def format_value(value, format_type):
            """Format a value based on the specified format type"""
            if pd.isna(value):
                return "N/A"

            if format_type == 'currency':
                return f"${value:,.0f}"
            elif format_type == 'decimal1':
                return f"{value:.1f}"
            elif format_type == 'decimal2':
                return f"{value:.2f}"
            elif format_type == 'date':
                if isinstance(value, str):
                    return value
                try:
                    return pd.to_datetime(value).strftime('%Y-%m-%d')
                except:
                    return str(value)
            else:
                return str(value)

        # Check if we have multiple data dates
        if len(project_data) > 1 and 'data_date' in project_data.columns:
            st.info(f"ℹ️ Showing {len(project_data)} data points for this project")

            # Normalized Progress Chart
            st.subheader("📈 Normalized Progress Over Time")

            # Calculate normalized values
            chart_data = project_data.copy()
            chart_data['normalized_time'] = chart_data['actual_duration_months'] / chart_data['original_duration_months']
            chart_data['normalized_ev'] = chart_data['ev'] / chart_data['bac']
            chart_data['normalized_ac'] = chart_data['ac'] / chart_data['bac']

            # Create plotly figure
            fig = go.Figure()

            # Add EV line/points
            fig.add_trace(go.Scatter(
                x=chart_data['normalized_time'],
                y=chart_data['normalized_ev'],
                mode='lines+markers',
                name='EV (Earned Value)',
                line=dict(color='green', width=3),
                marker=dict(size=10, symbol='circle')
            ))

            # Add AC line/points
            fig.add_trace(go.Scatter(
                x=chart_data['normalized_time'],
                y=chart_data['normalized_ac'],
                mode='lines+markers',
                name='AC (Actual Cost)',
                line=dict(color='red', width=3),
                marker=dict(size=10, symbol='square')
            ))

            # Add vertical lines for each data date
            for idx, row in chart_data.iterrows():
                date_str = pd.to_datetime(row['data_date']).strftime('%Y-%m-%d') if pd.notna(row['data_date']) else ''
                fig.add_vline(
                    x=row['normalized_time'],
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.3,
                    annotation_text=date_str,
                    annotation_position="top"
                )

            # Add diagonal reference line (perfect progress)
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='Planned (Perfect Progress)',
                line=dict(color='blue', width=2, dash='dot'),
                showlegend=True
            ))

            fig.update_layout(
                title='Normalized Progress Chart (0-1 Scale)',
                xaxis_title='Normalized Time (0 = Start, 1 = Planned Finish)',
                yaxis_title='Normalized Value (as fraction of BAC)',
                hovermode='x unified',
                height=500,
                xaxis=dict(range=[-0.05, 1.1]),
                yaxis=dict(range=[-0.05, 1.1])
            )

            st.plotly_chart(fig, width='stretch')

            st.divider()

            # Get data dates as column headers
            data_dates = project_data['data_date'].tolist()
            date_columns = [f"Date {i+1}" if pd.isna(d) else pd.to_datetime(d).strftime('%Y-%m-%d')
                           for i, d in enumerate(data_dates)]

            # Build single comprehensive table with all variables
            st.subheader("📋 Complete Time-Series Data")

            all_rows = []

            # Add category headers and variables
            for category_name, variables in variable_categories.items():
                # Add category header row
                category_header = {'Category': f"📁 {category_name}", 'Metric': ''}
                for col in date_columns:
                    category_header[col] = ''
                all_rows.append(category_header)

                # Add variable rows
                for var_name, var_info in variables.items():
                    if var_name in project_data.columns:
                        row = {'Category': '', 'Metric': var_info['label']}

                        # Add values for each data date
                        for i, col_name in enumerate(date_columns):
                            value = project_data.iloc[i][var_name]
                            row[col_name] = format_value(value, var_info['format'])

                        all_rows.append(row)

            if all_rows:
                complete_df = pd.DataFrame(all_rows)
                st.dataframe(
                    complete_df,
                    width='stretch',
                    hide_index=True,
                    height=600
                )
            else:
                st.info("No data available")

        else:
            st.warning("⚠️ Only one data point available. This view is most useful when you have multiple data dates for the same project.")
            st.info("💡 Tip: To see trends over time, ensure your input data includes multiple rows with the same Project ID but different Data Dates.")

    else:
        st.warning("No data available for selected project")
