# Part 1: Connected, but unevenly capable

Status: source-checked descriptive analysis; historical harmonisation remains open.

## Findings
Internet connectivity reaches 99.6% in 2024-25, while online ordering received is 32.2%, CRM 17.7%, analytics technology 5.2% and AI 12.1%. Connectivity is more widespread than these individual uses; this does not measure joint business-level breadth.

Historical snapshots show internet access of 86.5% in 2006-07 and 97.0% in 2018-19. They suggest diffusion, but are not an approved continuous series. Coverage and questionnaire audit remains incomplete; no historical percentage-point change is reported.

Social media presence: 46.7% (2021-22) to 50.9% (2024-25), +4.2 percentage points. The 200+ minus 0-4 size gap is 40.4 then 44.3 points (change +3.9). Descriptive only; excluding flagged inputs leaves this result unchanged: True.

Orders received online: 30.4% (2021-22) to 32.2% (2024-25), +1.8 percentage points. The 200+ minus 0-4 size gap is 16.3 then 20.6 points (change +4.3). Descriptive only; excluding flagged inputs leaves this result unchanged: True.

Social media presence: industries below the national benchmark in both approved recent waves: Agriculture, Forestry and Fishing, Construction, Health Care and Social Assistance, Mining, Transport, Postal and Warehousing. Two waves establish recent recurrence, not persistent long-run disadvantage. See industry_persistence.csv for flag sensitivity.

Orders received online: industries below the national benchmark in both approved recent waves: Administrative and Support Services, Agriculture, Forestry and Fishing, Construction, Financial and Insurance Services, Mining, Professional, Scientific and Technical Services, Rental, Hiring and Real Estate Services, Transport, Postal and Warehousing. Two waves establish recent recurrence, not persistent long-run disadvantage. See industry_persistence.csv for flag sensitivity.

In 2024-25, skills (16.3%), funds (12.6%), and cost/benefit uncertainty (13.5%) coexist as ICT constraints. The source review does not establish a long-run transition from infrastructure to skills. Recent constraint profiles are separate C snapshots.

2018-19, 0–4 persons: innovation-active businesses receiving online orders 46.1%, non-active 29.1%; difference 17.0 points (published).
2018-19, 5–19 persons: innovation-active businesses receiving online orders 56.6%, non-active 43.4%; difference 13.2 points (published).
2018-19, 20–199 persons: innovation-active businesses receiving online orders 55.7%, non-active 43.7%; difference 12.0 points (published).
2018-19, 200 or more persons: innovation-active businesses receiving online orders 67.0%, non-active 65.3%; difference 1.7 points (published).

These within-size associations do not control industry simultaneously and do not identify causality.

## Evidence and reproduction
All 2,790 selected numeric cells were checked directly against the original workbooks. Exact headers and source notes are retained in comparability_decisions.csv. observations.csv preserves the source workbook, sheet, cell, denominator and flags.

[ABS recent-wave comparisons](https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business/2024-25); [2021-22 methodology](https://www.abs.gov.au/methodologies/characteristics-australian-business-methodology/2021-22); [2024-25 methodology](https://www.abs.gov.au/methodologies/characteristics-australian-business-methodology/2024-25).

Run `python scripts/build_digital_research.py` and `python scripts/test_digital_research.py`. Open `research.html` offline.

## Interpretation limits
- 2005-06 has no selected connectivity or transaction measures in the supplied dashboard tables. This is an evidence gap, not zero adoption.
- Historical item-level equivalence remains unapproved (D); known recent redevelopment breaks are C. Only social presence and orders received in 2021-22 and 2024-25 are A-approved temporal comparisons.
- A applies to the named two-wave comparison, not the entire history. No B adjustments are made.
- National rates are unadjusted. Compatible fixed population weights have not been established. Separate size and industry tables do not jointly adjust composition.
- No confidence intervals or significance claims: exact uncertainty and covariance for the full comparison set are unavailable. Cautions remain visible; very unreliable values are excluded from charts and differences.
- Barriers and digital outcomes allow multiple responses. Reported ICT outcomes are subjective, not causal effects.
- Marginal percentages cannot establish how many capabilities each business holds. No maturity index is constructed.
