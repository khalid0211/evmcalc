
import pandas as pd
import numpy as np
from scipy.stats import beta as beta_dist
from datetime import datetime, timedelta

def scurve_cdf(t, alpha, beta):
    """Cumulative distribution function for the s-curve."""
    return beta_dist.cdf(t, alpha, beta)

def safe_convert_to_datetime(value):
    """
    Safely convert a single value to datetime.
    Returns NaT if conversion fails or value is out of bounds.
    """
    if pd.isna(value) or value is None:
        return pd.NaT

    # Convert to string
    val_str = str(value).strip()

    if val_str in ['', 'nan', 'NaT', 'None', '<NA>']:
        return pd.NaT

    # Try to parse as number first (Excel date)
    try:
        num_val = float(val_str)
        # Check if it's in valid Excel date range
        if 1 <= num_val <= 50000:
            # Convert Excel serial date (epoch: 1899-12-30)
            base_date = datetime(1899, 12, 30)
            result_date = base_date + timedelta(days=num_val)
            return pd.Timestamp(result_date)
        else:
            # Out of bounds numeric value
            return pd.NaT
    except (ValueError, OverflowError):
        # Not a number, try parsing as date string
        pass

    # Try standard date parsing
    try:
        return pd.to_datetime(val_str, errors='raise')
    except:
        return pd.NaT

def convert_date_column(series):
    """
    Convert a pandas Series to datetime, handling bad values gracefully.
    """
    result = pd.Series(index=series.index, dtype='datetime64[ns]')

    for idx in series.index:
        result[idx] = safe_convert_to_datetime(series[idx])

    return result

def calculate_evm(data, global_values):
    """
    Performs EVM calculations on the input data.

    Args:
        data (pd.DataFrame): The input project data.
        global_values (dict): The global values for the calculations.

    Returns:
        pd.DataFrame: The data with the calculated EVM metrics.
    """

    # CRITICAL FIX: Convert all columns to object/string dtype BEFORE copying
    # This prevents OutOfBoundsDatetime errors from datetime columns
    data_dict = {}
    problematic_columns = []

    for col in data.columns:
        try:
            # Check if this might be a date column with bad values
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['date', 'start', 'finish']):
                # This is likely a date column - check for problematic values
                try:
                    test_numeric = pd.to_numeric(data[col], errors='coerce')
                    if test_numeric.notna().any():
                        max_val = test_numeric.max()
                        if max_val > 50000:
                            problematic_columns.append({
                                'column': col,
                                'max_value': max_val,
                                'count': (test_numeric > 50000).sum()
                            })
                except:
                    pass

            # Convert each column to string/object to break any datetime dtype
            data_dict[col] = data[col].astype(str).values
        except Exception as e:
            # If conversion fails, use raw values
            import warnings
            warnings.warn(f"Could not convert column {col} to string: {e}")
            try:
                data_dict[col] = data[col].values
            except:
                # Last resort - skip this column
                pass

    # Report problematic columns
    if problematic_columns:
        import warnings
        for prob in problematic_columns:
            warnings.warn(
                f"Column '{prob['column']}' has {prob['count']} values > 50,000 "
                f"(max: {prob['max_value']:.0f}). These are not valid dates and will be treated as missing."
            )

    # Create fresh dataframe from dict (no datetime dtypes)
    data = pd.DataFrame(data_dict, index=data.index)

    # Rename columns to be more pythonic
    column_mapping = {
        'Project ID': 'project_id',
        'Project Name': 'project_name',
        'Department': 'department',
        'Budget (BAC)': 'bac',
        'Actual Cost (AC)': 'ac',
        'Plan Start Date': 'plan_start_date',
        'Plan Finish Date': 'plan_finish_date',
        'Data Date': 'data_date',
        'Earned Value (EV)': 'ev',
        'Planned Value (PV)': 'pv',
        'Curve': 'curve',
        'Beta': 'beta',
        'Alpha': 'alpha',
        'Inflation Rate': 'inflation_rate'
    }

    # Only rename columns that exist
    existing_mappings = {k: v for k, v in column_mapping.items() if k in data.columns}
    data = data.rename(columns=existing_mappings)

    # Convert date columns safely
    date_columns = ['plan_start_date', 'plan_finish_date', 'data_date']

    for col in date_columns:
        if col in data.columns:
            # Use our safe converter
            data[col] = convert_date_column(data[col])
        else:
            raise ValueError(f"Required date column '{col}' not found in data")

    # Validate that we have at least some valid dates
    valid_dates = 0
    for col in date_columns:
        valid_dates += data[col].notna().sum()

    if valid_dates == 0:
        raise ValueError(
            "No valid dates found in data. Please check your date columns. "
            "Expected formats: YYYY-MM-DD, MM/DD/YYYY, or Excel serial numbers (1-50000)"
        )

    # Duration and Value Metrics
    data['actual_duration_months'] = (data['data_date'] - data['plan_start_date']).dt.days / 30.44
    data['original_duration_months'] = (data['plan_finish_date'] - data['plan_start_date']).dt.days / 30.44

    # Replace negative or zero durations with NaN
    data.loc[data['actual_duration_months'] <= 0, 'actual_duration_months'] = np.nan
    data.loc[data['original_duration_months'] <= 0, 'original_duration_months'] = np.nan

    # Fill missing optional columns with global values
    for col, value in global_values.items():
        if col in data.columns:
            # Convert to numeric if it's a numeric global value
            if col in ['alpha', 'beta', 'inflation_rate']:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            # Fill NaN values in existing columns with global values
            data[col] = data[col].fillna(value)
        else:
            # Create column with global value if it doesn't exist
            data[col] = value

    # Convert numeric columns
    numeric_cols = ['bac', 'ac', 'alpha', 'beta', 'inflation_rate']
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')

    # Present Value Calculation
    annual_inflation_rate = data['inflation_rate'] / 100
    monthly_rate = (1 + annual_inflation_rate)**(1/12) - 1

    # Avoid division by zero for actual_duration_months
    safe_duration = data['actual_duration_months'].replace(0, np.nan)
    pmt = data['ac'] / safe_duration

    # Avoid division by zero for monthly_rate
    safe_monthly_rate = monthly_rate.replace(0, 0.0001)

    # Calculate present value factor
    with np.errstate(invalid='ignore', divide='ignore'):
        factor = (1 - (1 + safe_monthly_rate)**(-safe_duration)) / safe_monthly_rate

    data['present_value'] = pmt * factor

    # Fill NaN values with AC where duration is 0
    data['present_value'] = data['present_value'].fillna(data['ac'])

    # Planned Value (PV)
    if global_values.get('use_manual_pv') and 'manual_pv' in data.columns:
        data['pv'] = pd.to_numeric(data['manual_pv'], errors='coerce')
    elif 'pv' not in data.columns or data['pv'].isnull().all():
        t = data['actual_duration_months'] / data['original_duration_months']
        t = t.fillna(0).clip(0, 1)  # Ensure t is between 0 and 1

        if global_values.get('curve') == 'linear':
            data['pv'] = data['bac'] * t
        else:  # s-curve
            # Calculate s-curve for each row
            pv_values = []
            for idx in data.index:
                try:
                    alpha = data.loc[idx, 'alpha']
                    beta = data.loc[idx, 'beta']
                    bac = data.loc[idx, 'bac']
                    t_val = t.loc[idx]

                    if pd.notna(alpha) and pd.notna(beta) and pd.notna(bac) and pd.notna(t_val):
                        pv_val = bac * scurve_cdf(t_val, alpha, beta)
                        pv_values.append(pv_val)
                    else:
                        pv_values.append(np.nan)
                except:
                    pv_values.append(np.nan)

            data['pv'] = pv_values

    # Earned Value (EV)
    if global_values.get('use_manual_ev') and 'manual_ev' in data.columns:
        data['ev'] = pd.to_numeric(data['manual_ev'], errors='coerce')
    elif 'ev' not in data.columns or data['ev'].isnull().all():
        # Use the same percentage completion as time elapsed
        t = data['actual_duration_months'] / data['original_duration_months']
        t = t.fillna(0).clip(0, 1)

        if global_values.get('curve') == 'linear':
            data['ev'] = data['bac'] * t
        else:  # s-curve
            ev_values = []
            for idx in data.index:
                try:
                    alpha = data.loc[idx, 'alpha']
                    beta = data.loc[idx, 'beta']
                    bac = data.loc[idx, 'bac']
                    t_val = t.loc[idx]

                    if pd.notna(alpha) and pd.notna(beta) and pd.notna(bac) and pd.notna(t_val):
                        ev_val = bac * scurve_cdf(t_val, alpha, beta)
                        ev_values.append(ev_val)
                    else:
                        ev_values.append(np.nan)
                except:
                    ev_values.append(np.nan)

            data['ev'] = ev_values

    # EVM Core Metrics
    data['percent_complete'] = np.where(data['bac'] > 0, (data['ev'] / data['bac']) * 100, np.nan)
    data['cv'] = data['ev'] - data['ac']
    data['sv'] = data['ev'] - data['pv']

    # Performance Indices (avoid division by zero)
    data['cpi'] = np.where(data['ac'] > 0, data['ev'] / data['ac'], np.nan)
    data['spi'] = np.where(data['pv'] > 0, data['ev'] / data['pv'], np.nan)
    data['tcpi'] = np.where(
        (data['bac'] - data['ac']) > 0,
        (data['bac'] - data['ev']) / (data['bac'] - data['ac']),
        np.nan
    )

    # Forecasting
    data['eac'] = np.where(data['cpi'] > 0, data['bac'] / data['cpi'], np.nan)
    data['etc'] = data['eac'] - data['ac']
    data['vac'] = data['bac'] - data['eac']

    # Earned Schedule Metrics
    if global_values.get('curve') == 'linear':
        data['es'] = np.where(
            data['bac'] > 0,
            (data['ev'] / data['bac']) * data['original_duration_months'],
            np.nan
        )
    else:  # s-curve (using approximation)
        data['es'] = np.where(
            data['bac'] > 0,
            (data['ev'] / data['bac']) * data['original_duration_months'],
            np.nan
        )

    data['spie'] = np.where(
        data['actual_duration_months'] > 0,
        data['es'] / data['actual_duration_months'],
        np.nan
    )
    data['tve'] = data['es'] - data['actual_duration_months']

    data['ld'] = np.where(
        data['spie'] > 0,
        data['original_duration_months'] / data['spie'],
        np.nan
    )

    # Cap likely duration at 2.5x original
    data['ld'] = np.minimum(data['ld'], 2.5 * data['original_duration_months'])

    # Calculate likely completion date
    data['likely_completion'] = pd.NaT
    for idx in data.index:
        try:
            start_date = data.loc[idx, 'plan_start_date']
            ld = data.loc[idx, 'ld']
            if pd.notna(start_date) and pd.notna(ld):
                data.loc[idx, 'likely_completion'] = start_date + pd.Timedelta(days=ld * 30.44)
        except:
            pass

    # Percentage Metrics
    data['percent_budget_used'] = np.where(
        data['bac'] > 0,
        (data['ac'] / data['bac']) * 100,
        np.nan
    )
    data['percent_time_used'] = np.where(
        data['original_duration_months'] > 0,
        (data['actual_duration_months'] / data['original_duration_months']) * 100,
        np.nan
    )

    # Advanced Financial Metrics
    with np.errstate(invalid='ignore', divide='ignore'):
        pmt_planned = data['bac'] / data['original_duration_months']
        factor_planned = (1 - (1 + safe_monthly_rate)**(-data['original_duration_months'])) / safe_monthly_rate
        data['planned_value_project'] = pmt_planned * factor_planned

        pmt_likely = data['bac'] / data['ld']
        factor_likely = (1 - (1 + safe_monthly_rate)**(-data['ld'])) / safe_monthly_rate
        data['likely_value_project'] = pmt_likely * factor_likely

    data['percent_present_value_project'] = np.where(
        data['bac'] > 0,
        (data['planned_value_project'] / data['bac']) * 100,
        np.nan
    )
    data['percent_likely_value_project'] = np.where(
        data['bac'] > 0,
        (data['likely_value_project'] / data['bac']) * 100,
        np.nan
    )

    return data
