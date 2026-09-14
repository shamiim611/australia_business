# Part 2: AI adoption is unevenly distributed

Status: completed descriptive public-data analysis. Temporal and innovation-status comparisons remain unapproved where source evidence is insufficient.

## Findings
In 2024-25, 12.1% of businesses in the survey scope reported AI use. The item is broad AI use, not specifically generative AI or intensity of use. Source: data_2024-25/BCSDC06_2024–25.xlsx, Table 2, L7.

- 0–4 persons: 10.7% (L9).
- 5–19 persons: 12.3% (L10).
- 20–199 persons: 22.3% (L11).
- 200 or more persons: 34.7% (L12).

Large minus micro: 24.0 percentage points; excluding flagged inputs leaves the comparison unchanged: True.
Large minus small: 22.4 percentage points; excluding flagged inputs leaves the comparison unchanged: True.

The 17 industry rates range from 1% in Transport, Postal and Warehousing to 38.1% in Information Media and Telecommunications: 37.1 points. The unflagged-only range is 37.1 points. These are differences in group adoption rates, not the distribution of AI adopters across industries.

The Northern Territory estimate carries a caution. Geographic differences are unadjusted for business composition; overlapping location categories are not additive.

Cloud, CRM, analytics and ERP provide same-wave context. Separate marginal shares do not measure co-adoption or the capabilities of AI users.

## Historical and innovation evidence
The release names 2022-23 in its AI key statistics and 2021-22 in the detailed ICT discussion. Local workbook periods identify the historical snapshots used here. No continuous trend or growth calculation is approved.

The release narrative describes higher AI adoption among innovation-active businesses. Its chart footnote instead describes a denominator of businesses reporting AI use. The published chart and narrative do not resolve this inconsistency.
No innovation gap or causal inference is calculated. No numeric innovation chart is included until the denominator is confirmed.
See the [ABS release](https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business/2024-25) for the external evidence reviewed.

## Limits
This is a cross-section of aggregate estimates, not a firm-level panel. No causal claims, significance tests, regression, synthetic industry-by-size cells, weighted SME rates or maturity index are produced. Exact uncertainty for these AI comparisons has not been established; source flags are retained. Rankings do not prove statistically distinct performance.

## Reproduce
Run `python scripts/build_ai_research.py` then `python scripts/test_ai_research.py`. The builder verifies 223 numeric workbook cells and writes source-linked observations, item decisions, differences and sensitivity results. No network access is needed to rebuild. Open `research-ai.html` offline.
