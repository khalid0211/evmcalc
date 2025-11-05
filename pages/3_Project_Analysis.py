
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

            st.plotly_chart(fig, use_container_width=True)

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
                st.plotly_chart(fig_cpi, use_container_width=True)

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
                st.plotly_chart(fig_spi, use_container_width=True)

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
                use_container_width=True,
                height=300
            )
        else:
            st.dataframe(project_data, use_container_width=True, height=300)

        # Option to show all columns
        with st.expander("Show All Columns", expanded=False):
            st.dataframe(project_data, use_container_width=True, height=400)

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

    else:
        st.warning("No data available for selected project")
