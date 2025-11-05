# CSV Export Column Documentation

This document provides a comprehensive reference for all columns included in the CSV data export from the Portfolio Management Suite.

**Last Updated:** 2025-11-03
**Version:** 1.0

---

## Table of Contents
1. [Input Data Columns](#input-data-columns)
2. [Basic Calculation Columns](#basic-calculation-columns)
3. [EVM Metrics Columns](#evm-metrics-columns)
4. [Earned Schedule Metrics Columns](#earned-schedule-metrics-columns)
5. [Financial Forecasting Columns](#financial-forecasting-columns)
6. [Metadata Columns](#metadata-columns)

---

## Input Data Columns

These columns are provided by the user through CSV/JSON upload or manual data entry.

### 1. Project ID
- **Type:** String
- **Description:** Unique identifier for the project
- **Source:** User input
- **Required:** Yes
- **Example:** "PRJ-001", "PROJ_2024_123"

### 2. Project
- **Type:** String
- **Description:** Project name or title
- **Source:** User input
- **Required:** Yes
- **Example:** "Website Redesign", "Database Migration"

### 3. Organization
- **Type:** String
- **Description:** Organization or department name
- **Source:** User input
- **Required:** Yes
- **Example:** "IT Department", "Marketing Division"

### 4. Project Manager
- **Type:** String
- **Description:** Name of the project manager
- **Source:** User input
- **Required:** Yes
- **Example:** "John Smith", "Jane Doe"

### 5. Plan Start
- **Type:** Date (YYYY-MM-DD)
- **Description:** Planned project start date
- **Source:** User input
- **Required:** Yes
- **Example:** "2024-01-01"

### 6. Plan Finish
- **Type:** Date (YYYY-MM-DD)
- **Description:** Planned project finish date
- **Source:** User input
- **Required:** Yes
- **Example:** "2024-12-31"

### 7. BAC (Budget at Completion)
- **Type:** Numeric (Currency)
- **Description:** Total planned budget for the project
- **Source:** User input
- **Required:** Yes
- **Unit:** Currency (as configured in Controls)
- **Example:** 100000.00

### 8. AC (Actual Cost)
- **Type:** Numeric (Currency)
- **Description:** Actual cost incurred to date
- **Source:** User input
- **Required:** Yes
- **Unit:** Currency (as configured in Controls)
- **Example:** 45000.00

### 9. Manual_PV
- **Type:** Numeric (Currency)
- **Description:** Manually entered Planned Value (overrides calculated PV)
- **Source:** User input (optional)
- **Required:** No
- **Default:** 0.0
- **Note:** Only used when Use_Manual_PV is True

### 10. Manual_EV
- **Type:** Numeric (Currency)
- **Description:** Manually entered Earned Value (overrides calculated EV)
- **Source:** User input (optional)
- **Required:** No
- **Default:** 0.0
- **Note:** Only used when Use_Manual_EV is True

### 11. Use_Manual_PV
- **Type:** Boolean
- **Description:** Flag indicating whether to use Manual_PV instead of calculated PV
- **Source:** User input (optional)
- **Required:** No
- **Default:** False
- **Values:** True/False

### 12. Use_Manual_EV
- **Type:** Boolean
- **Description:** Flag indicating whether to use Manual_EV instead of calculated EV
- **Source:** User input (optional)
- **Required:** No
- **Default:** False
- **Values:** True/False

### 13. Curve Type
- **Type:** String
- **Description:** Per-project curve type for PV calculation
- **Source:** User input (optional)
- **Required:** No
- **Default:** Uses global setting if blank
- **Values:** "linear", "s-curve"

### 14. Alpha
- **Type:** Numeric
- **Description:** Per-project alpha parameter for S-curve calculation
- **Source:** User input (optional)
- **Required:** No (only used for S-curve)
- **Default:** Uses global setting if blank
- **Range:** 0.1 - 10.0
- **Typical:** 2.0

### 15. Beta
- **Type:** Numeric
- **Description:** Per-project beta parameter for S-curve calculation
- **Source:** User input (optional)
- **Required:** No (only used for S-curve)
- **Default:** Uses global setting if blank
- **Range:** 0.1 - 10.0
- **Typical:** 2.0

### 16. Inflation Rate
- **Type:** Numeric (Percentage)
- **Description:** Per-project annual inflation rate
- **Source:** User input (optional)
- **Required:** No
- **Default:** Uses global setting if blank
- **Unit:** Percentage (%)
- **Example:** 3.5 (for 3.5%)

### 17. Completion %
- **Type:** Numeric (Percentage)
- **Description:** Manual completion percentage (if tracked separately)
- **Source:** User input (optional)
- **Required:** No
- **Note:** Not directly used in EVM calculations; EV-based completion is calculated automatically

---

## Basic Calculation Columns

These columns contain fundamental calculations derived from input data.

### 18. data_date
- **Type:** Date (YYYY-MM-DD)
- **Description:** The "as-of" date used for all calculations
- **Calculation:** Set in Controls section (B. Controls)
- **Purpose:** Represents the point in time at which project status is measured
- **Example:** "2024-06-15"

### 19. actual_duration_months (AD)
- **Type:** Numeric (Months)
- **Description:** Duration from Plan Start to Data Date
- **Calculation:** `AD = (data_date - plan_start) / 30.44 days`
- **Formula:** Time elapsed in months using average month length (30.44 days)
- **Unit:** Months
- **Example:** 6.5

### 20. original_duration_months (OD)
- **Type:** Numeric (Months)
- **Description:** Total planned project duration
- **Calculation:** `OD = (plan_finish - plan_start) / 30.44 days`
- **Formula:** Total planned duration in months
- **Unit:** Months
- **Example:** 12.0

### 21. present_value
- **Type:** Numeric (Currency)
- **Description:** Actual Cost adjusted for inflation
- **Calculation:** `PresentValue = AC × (1 + inflation_rate)^(AD/12)`
- **Formula:** Compound interest formula applied to actual cost
- **Purpose:** Adjusts AC for time value of money
- **Example:** 46575.00

### 22. pv (Planned Value)
- **Type:** Numeric (Currency)
- **Description:** Planned value at the data date
- **Calculation:**
  - **If Use_Manual_PV = True:** `PV = Manual_PV`
  - **If Curve Type = "linear":** `PV = BAC × (AD / OD)`
  - **If Curve Type = "s-curve":** `PV = BAC × S(AD/OD, α, β)` where S is the S-curve function
- **S-Curve Formula:** `S(t) = t^α / (t^α + (1-t)^β)` where t = AD/OD
- **Example:** 50000.00

### 23. percent_budget_used
- **Type:** Numeric (Percentage)
- **Description:** Percentage of total budget consumed
- **Calculation:** `% Budget Used = (AC / BAC) × 100`
- **Purpose:** Shows budget consumption rate
- **Example:** 45.0 (45%)

### 24. percent_time_used
- **Type:** Numeric (Percentage)
- **Description:** Percentage of planned time elapsed
- **Calculation:** `% Time Used = (AD / OD) × 100`
- **Purpose:** Shows schedule progression
- **Example:** 54.17 (54.17%)

---

## EVM Metrics Columns

Standard Earned Value Management metrics as defined by PMI standards.

### 25. percent_complete
- **Type:** Numeric (Percentage)
- **Description:** Project completion percentage based on earned value
- **Calculation:** `% Complete = (EV / BAC) × 100`
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 42.5 (42.5%)

### 26. ev (Earned Value)
- **Type:** Numeric (Currency)
- **Description:** Value of work actually completed
- **Calculation:**
  - **If Use_Manual_EV = True:** `EV = Manual_EV`
  - **Otherwise:** `EV = BAC × (PresentValue / BAC) = PresentValue`
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 42500.00

### 27. cv (Cost Variance)
- **Type:** Numeric (Currency)
- **Description:** Difference between earned value and actual cost
- **Calculation:** `CV = EV - AC`
- **Interpretation:**
  - Positive: Under budget (good)
  - Negative: Over budget (bad)
  - Zero: On budget
- **Standard:** PMI/ANSI EVM Standard
- **Example:** -2500.00 (over budget by 2,500)

### 28. sv (Schedule Variance)
- **Type:** Numeric (Currency)
- **Description:** Difference between earned value and planned value
- **Calculation:** `SV = EV - PV`
- **Interpretation:**
  - Positive: Ahead of schedule (good)
  - Negative: Behind schedule (bad)
  - Zero: On schedule
- **Standard:** PMI/ANSI EVM Standard
- **Example:** -7500.00 (behind schedule)

### 29. cpi (Cost Performance Index)
- **Type:** Numeric (Ratio)
- **Description:** Efficiency of cost utilization
- **Calculation:** `CPI = EV / AC`
- **Interpretation:**
  - CPI > 1.0: Under budget (good)
  - CPI = 1.0: On budget
  - CPI < 1.0: Over budget (bad)
- **Special Cases:**
  - If AC = 0 and EV = 0: Returns N/A
  - If AC = 0 and EV > 0: Returns ∞ (perfect efficiency)
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 0.944 (for every $1 spent, getting $0.944 of value)

### 30. spi (Schedule Performance Index)
- **Type:** Numeric (Ratio)
- **Description:** Efficiency of time utilization
- **Calculation:** `SPI = EV / PV`
- **Interpretation:**
  - SPI > 1.0: Ahead of schedule (good)
  - SPI = 1.0: On schedule
  - SPI < 1.0: Behind schedule (bad)
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 0.850 (performing at 85% of planned rate)

### 31. tcpi (To Complete Performance Index)
- **Type:** Numeric (Ratio)
- **Description:** Required cost efficiency for remaining work to meet BAC
- **Calculation:** `TCPI = (BAC - EV) / (BAC - AC)`
- **Interpretation:**
  - TCPI > CPI: Need to improve efficiency
  - TCPI = CPI: Can maintain current efficiency
  - TCPI < CPI: Can reduce efficiency and still meet BAC
- **Special Cases:**
  - If BAC = AC: Returns N/A or ∞ (no budget remaining)
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 1.048 (need 104.8% efficiency on remaining work)

### 32. eac (Estimate at Completion)
- **Type:** Numeric (Currency)
- **Description:** Forecasted total cost at project completion
- **Calculation:** `EAC = BAC / CPI`
- **Purpose:** Projects final cost based on current performance
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 105926.00

### 33. etc (Estimate to Complete)
- **Type:** Numeric (Currency)
- **Description:** Forecasted cost to finish remaining work
- **Calculation:** `ETC = EAC - AC`
- **Purpose:** Estimates additional funds needed
- **Standard:** PMI/ANSI EVM Standard
- **Example:** 60926.00

### 34. vac (Variance at Completion)
- **Type:** Numeric (Currency)
- **Description:** Expected variance at project completion
- **Calculation:** `VAC = BAC - EAC`
- **Interpretation:**
  - Positive: Expected to finish under budget
  - Negative: Expected to finish over budget
  - Zero: Expected to finish on budget
- **Standard:** PMI/ANSI EVM Standard
- **Example:** -5926.00 (expected to exceed budget by 5,926)

---

## Earned Schedule Metrics Columns

Advanced scheduling metrics based on Earned Schedule theory.

### 35. es (Earned Schedule)
- **Type:** Numeric (Months)
- **Description:** Time value of work completed
- **Calculation:**
  - **Linear:** `ES = (EV / BAC) × OD`
  - **S-Curve:** Inverse of S-curve function to find time t where S(t) = EV/BAC
- **Purpose:** Translates earned value into time-based metric
- **Reference:** Earned Schedule by Walt Lipke
- **Unit:** Months
- **Example:** 5.1 months

### 36. spie (Schedule Performance Index - Earned Schedule)
- **Type:** Numeric (Ratio)
- **Description:** Schedule efficiency based on earned schedule
- **Calculation:** `SPIe = ES / AD`
- **Interpretation:**
  - SPIe > 1.0: Ahead of schedule (good)
  - SPIe = 1.0: On schedule
  - SPIe < 1.0: Behind schedule (bad)
- **Advantage:** More stable than SPI for late-stage projects
- **Reference:** Earned Schedule by Walt Lipke
- **Example:** 0.785 (performing at 78.5% of time efficiency)

### 37. tve (Time Variance - Earned Schedule)
- **Type:** Numeric (Months)
- **Description:** Schedule variance expressed in time units
- **Calculation:** `TVe = ES - AD`
- **Interpretation:**
  - Positive: Ahead of schedule (time saved)
  - Negative: Behind schedule (time overrun)
  - Zero: On schedule
- **Unit:** Months
- **Example:** -1.4 (1.4 months behind)

### 38. ld (Likely Duration)
- **Type:** Numeric (Months)
- **Description:** Forecasted total project duration
- **Calculation:** `LD = OD / SPIe`
- **Constraint:** `LD ≤ 2.5 × OD` (maximum 250% of original duration)
- **Purpose:** Projects final duration based on current schedule performance
- **Reference:** Earned Schedule by Walt Lipke
- **Unit:** Months
- **Example:** 15.3 months

### 39. likely_completion
- **Type:** Date (DD/MM/YYYY)
- **Description:** Forecasted project completion date
- **Calculation:** `Likely Completion = Plan Start + LD months`
- **Purpose:** Date-based projection of project finish
- **Example:** "31/03/2025"

---

## Financial Forecasting Columns

Advanced financial projections considering inflation and time value of money.

### 40. planned_value_project
- **Type:** Numeric (Currency)
- **Description:** Total planned value of project adjusted for inflation over original duration
- **Calculation:** `PVP = BAC × (1 + inflation_rate)^(OD/12)`
- **Purpose:** Shows total project value in future dollars at planned completion
- **Example:** 103000.00

### 41. likely_value_project
- **Type:** Numeric (Currency)
- **Description:** Total likely value of project adjusted for inflation over likely duration
- **Calculation:** `LVP = BAC × (1 + inflation_rate)^(LD/12)`
- **Purpose:** Shows total project value in future dollars at forecasted completion
- **Note:** Typically higher than PVP if project is delayed (more time for inflation)
- **Example:** 104500.00

### 42. percent_present_value_project
- **Type:** Numeric (Percentage)
- **Description:** Percentage increase from BAC to planned value project
- **Calculation:** `% PVP = (PVP / BAC) × 100`
- **Purpose:** Shows impact of inflation over planned duration
- **Example:** 103.0 (3% increase due to inflation)

### 43. percent_likely_value_project
- **Type:** Numeric (Percentage)
- **Description:** Percentage increase from BAC to likely value project
- **Calculation:** `% LVP = (LVP / BAC) × 100`
- **Purpose:** Shows impact of inflation over forecasted duration
- **Example:** 104.5 (4.5% increase due to inflation and delay)

---

## Metadata Columns

System-generated metadata for tracking and auditing.

### 44. calculation_date
- **Type:** ISO DateTime (YYYY-MM-DD HH:MM:SS)
- **Description:** Timestamp when the EVM calculations were performed
- **Source:** System-generated
- **Purpose:** Audit trail and version control
- **Format:** ISO 8601 format
- **Example:** "2024-11-03T14:30:45.123456"

---

## Calculation Dependencies

### Dependency Chain
```
Input Data
  ↓
Basic Calculations (AD, OD, Present Value, PV)
  ↓
EVM Metrics (EV, CV, SV, CPI, SPI, TCPI, EAC, ETC, VAC)
  ↓
Earned Schedule Metrics (ES, SPIe, TVe, LD, Likely Completion)
  ↓
Financial Forecasting (PVP, LVP)
```

### Key Formulas Summary

**Duration Calculations:**
- `AD = (data_date - plan_start) / 30.44`
- `OD = (plan_finish - plan_start) / 30.44`

**Value Calculations:**
- `PV_linear = BAC × (AD / OD)`
- `PV_scurve = BAC × [t^α / (t^α + (1-t)^β)]` where t = AD/OD
- `EV = PresentValue` or `Manual_EV`
- `PresentValue = AC × (1 + r)^(AD/12)` where r = inflation_rate

**EVM Metrics:**
- `CPI = EV / AC`
- `SPI = EV / PV`
- `TCPI = (BAC - EV) / (BAC - AC)`
- `EAC = BAC / CPI`
- `ETC = EAC - AC`
- `VAC = BAC - EAC`

**Earned Schedule:**
- `ES = (EV/BAC) × OD` (linear)
- `SPIe = ES / AD`
- `TVe = ES - AD`
- `LD = OD / SPIe` (capped at 2.5 × OD)

**Financial Forecasting:**
- `PVP = BAC × (1 + r)^(OD/12)`
- `LVP = BAC × (1 + r)^(LD/12)`

---

## Notes and Best Practices

### Data Quality
- Ensure all required input fields are complete and accurate
- Validate dates are in correct chronological order (Plan Start < Plan Finish < Data Date for completed work)
- Verify BAC and AC values are non-negative
- Check that inflation rates are reasonable (typically 0-20%)

### Interpretation Guidelines
- **CPI and SPI:** Values close to 1.0 indicate good performance
- **CV and SV:** Small variances (±5% of BAC) are typically acceptable
- **TCPI:** If significantly higher than CPI, corrective action may be needed
- **SPIe:** More reliable than SPI for projects >50% complete

### Special Values
- **N/A:** Appears when calculation is undefined (e.g., 0/0)
- **∞ (Infinity):** Appears when dividing by zero with non-zero numerator
- **Negative values:** Normal for variances (CV, SV, VAC) when underperforming

### Performance Indicators
| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| CPI | ≥ 1.0 | 0.95 - 1.0 | < 0.95 |
| SPI | ≥ 1.0 | 0.95 - 1.0 | < 0.95 |
| SPIe | ≥ 1.0 | 0.95 - 1.0 | < 0.95 |
| TCPI | < CPI | = CPI | > CPI |

---

## References

1. **PMI Practice Standard for Earned Value Management** - Project Management Institute
2. **ANSI/EIA-748-C** - Earned Value Management Systems Standard
3. **Earned Schedule** by Walt Lipke - Advanced schedule analysis method
4. **A Guide to the Project Management Body of Knowledge (PMBOK Guide)** - PMI

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-03 | Initial documentation |

---

**Document Prepared By:** Portfolio Management Suite
**For Questions or Clarifications:** Refer to application help or user manual
