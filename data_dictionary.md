# Data Dictionary

This document provides a detailed breakdown of all calculated fields in the Portfolio Analysis Suite.

## Duration and Value Metrics

### `actual_duration_months`
- **Description**: The duration from the project's start date to the data date, measured in months.
- **Calculation Method**:
  ```
  (data_date - plan_start_date).days / 30.44
  ```

### `original_duration_months`
- **Description**: The total planned duration of the project, measured in months.
- **Calculation Method**:
  ```
  (plan_finish_date - plan_start_date).days / 30.44
  ```

### `present_value`
- **Description**: The present value of the actual costs incurred to date, adjusted for inflation.
- **Calculation Method**: This is calculated using the standard present value formula for an annuity.
  ```
  monthly_rate = (1 + annual_inflation_rate)^(1/12) - 1
  pmt = ac / actual_duration_months
  factor = (1 - (1 + monthly_rate)^(-actual_duration_months)) / monthly_rate
  present_value = pmt * factor
  ```

### `pv` (Planned Value)
- **Description**: The budgeted cost for work scheduled to be completed by the data date.
- **Calculation Method**:
  - **Linear:**
    ```
    bac * (actual_duration_months / original_duration_months)
    ```
  - **S-Curve:**
    ```
    bac * scurve_cdf(actual_duration_months / original_duration_months, alpha, beta)
    ```
    where `scurve_cdf` is the cumulative distribution function of the beta distribution.

## EVM Core Metrics

### `percent_complete`
- **Description**: The percentage of the project's budget that has been earned to date.
- **Calculation Method**:
  ```
  (ev / bac) * 100
  ```

### `ev` (Earned Value)
- **Description**: The value of the work actually completed to date.
- **Calculation Method**:
  ```
  bac * (present_value / bac)
  ```
  If `use_manual_ev` is true, the manually entered `manual_ev` is used instead.

### `cv` (Cost Variance)
- **Description**: The difference between the earned value and the actual cost. A positive value indicates a cost underrun.
- **Calculation Method**:
  ```
  ev - ac
  ```

### `sv` (Schedule Variance)
- **Description**: The difference between the earned value and the planned value. A positive value indicates being ahead of schedule.
- **Calculation Method**:
  ```
  ev - pv
  ```

## Performance Indices

### `cpi` (Cost Performance Index)
- **Description**: A measure of the cost efficiency of the project. A value greater than 1 indicates that the project is under budget.
- **Calculation Method**:
  ```
  ev / ac
  ```

### `spi` (Schedule Performance Index)
- **Description**: A measure of the schedule efficiency of the project. A value greater than 1 indicates that the project is ahead of schedule.
- **Calculation Method**:
  ```
  ev / pv
  ```

### `tcpi` (To-Complete Performance Index)
- **Description**: The cost performance that must be achieved on the remaining work to meet the budget at completion.
- **Calculation Method**:
  ```
  (bac - ev) / (bac - ac)
  ```

## Forecasting

### `eac` (Estimate at Completion)
- **Description**: The expected total cost of the project at completion.
- **Calculation Method**:
  ```
  bac / cpi
  ```

### `etc` (Estimate to Complete)
- **Description**: The expected cost to finish the remaining work.
- **Calculation Method**:
  ```
  eac - ac
  ```

### `vac` (Variance at Completion)
- **Description**: The difference between the budget at completion and the estimate at completion. A positive value indicates a projected cost underrun.
- **Calculation Method**:
  ```
  bac - eac
  ```

## Earned Schedule Metrics

### `es` (Earned Schedule)
- **Description**: The point in time when the project's current earned value was scheduled to be achieved.
- **Calculation Method**:
  - **Linear:**
    ```
    (ev / bac) * original_duration_months
    ```
  - **S-Curve:** Found by solving `scurve_cdf(es / original_duration_months) = ev / bac` for `es`.

### `spie` (Schedule Performance Index - Earned Schedule)
- **Description**: A measure of schedule performance using earned schedule. A value greater than 1 indicates being ahead of schedule.
- **Calculation Method**:
  ```
  es / actual_duration_months
  ```

### `tve` (Time Variance - Earned Schedule)
- **Description**: The difference between the earned schedule and the actual duration, in months.
- **Calculation Method**:
  ```
  es - actual_duration_months
  ```

### `ld` (Likely Duration)
- **Description**: The forecasted project duration at completion.
- **Calculation Method**:
  ```
  original_duration_months / spie
  ```
  Capped at 2.5 times the original duration.

### `likely_completion`
- **Description**: The forecasted project completion date.
- **Calculation Method**:
  ```
  plan_start_date + ld (in months)
  ```

## Percentage Metrics

### `percent_budget_used`
- **Description**: The percentage of the total budget that has been spent to date.
- **Calculation Method**:
  ```
  (ac / bac) * 100
  ```

### `percent_time_used`
- **Description**: The percentage of the total planned duration that has elapsed to date.
- **Calculation Method**:
  ```
  (actual_duration_months / original_duration_months) * 100
  ```

## Advanced Financial Metrics

### `planned_value_project`
- **Description**: The present value of the entire project's budget (BAC), adjusted for inflation over the original duration.
- **Calculation Method**: Similar to `present_value`, but using `bac` and `original_duration_months`.
  ```
  monthly_rate = (1 + annual_inflation_rate)^(1/12) - 1
  pmt = bac / original_duration_months
  factor = (1 - (1 + monthly_rate)^(-original_duration_months)) / monthly_rate
  planned_value_project = pmt * factor
  ```

### `likely_value_project`
- **Description**: The present value of the entire project's budget (BAC), adjusted for inflation over the likely duration.
- **Calculation Method**: Similar to `present_value`, but using `bac` and `ld`.
  ```
  monthly_rate = (1 + annual_inflation_rate)^(1/12) - 1
  pmt = bac / ld
  factor = (1 - (1 + monthly_rate)^(-ld)) / monthly_rate
  likely_value_project = pmt * factor
  ```

### `percent_present_value_project`
- **Description**: The `planned_value_project` as a percentage of the `bac`.
- **Calculation Method**:
  ```
  (planned_value_project / bac) * 100
  ```

### `percent_likely_value_project`
- **Description**: The `likely_value_project` as a percentage of the `bac`.
- **Calculation Method**:
  ```
  (likely_value_project / bac) * 100
  ```