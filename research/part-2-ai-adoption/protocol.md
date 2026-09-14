# Part 2: AI adoption across Australian businesses

Status: implemented as a descriptive public-data study in research-ai.html. Reproduce with scripts/build_ai_research.py. Temporal comparisons and the AI-by-innovation gap remain unapproved where source evidence is insufficient; see comparability_decisions.csv and evidence_decisions.json. No microdata is used.

## Main question

How was reported AI use distributed across Australian businesses in 2024-25, and how did adoption rates differ across published business categories?

The main study is a cross-sectional analysis. Observable associations are differences between published groups; they are not independently adjusted determinants of adoption. AI refers to the survey's broad technology item, not specifically generative AI, intensity of use, sophistication or business impact.

## Available evidence

The supplied BCSDC06 workbook, Table 2, reports AI use by employment size, industry, state/territory and location. Column L is the AI item. The accompanying `available_ai_observations.csv` preserves all 35 observations, original wording, denominator note, source coordinates and reliability flags. Values were checked directly against the original XLSX cells. These categories are separate breakdowns, not a joint industry-by-size dataset.

The national estimate is 12.1%. Size estimates are 10.7% for micro businesses (0-4 persons), 12.3% for small (5-19), 22.3% for medium (20-199), and 34.7% for large (200+). The large-minus-micro gap is 24.0 percentage points; the large-minus-small gap is 22.4 points. Neither is an aggregate SME-versus-large estimate. Industry rates range from 1.0% in Transport, Postal and Warehousing to 38.1% in Information Media and Telecommunications, a descriptive range of 37.1 points. These are adoption rates within groups, not shares of all AI adopters.

The Northern Territory estimate carries a caution. Preserve location subtotals and their components as published; do not add overlapping categories. Geographic estimates are contextual and do not identify geographic effects after controlling industry or size.

## Analysis and dashboard sequence

1. **National context:** report 12.1% and explain the broad AI-use question and survey population.
2. **Size gradient:** show all four employment bands on the same percentage scale, then calculate large-minus-micro and large-minus-small gaps separately. Show underlying rates alongside differences.
3. **Industry spread:** show every industry, its source flag and the national reference line. Report the observed range with a sensitivity analysis excluding flagged values. Rankings are descriptive, not statistically distinct league tables. Do not label one-wave positions persistent leaders or laggards.
4. **Geography:** provide optional state/territory and location views, retaining cautions and overlapping-category notes. Avoid headline rankings of uncertain estimates.
5. **Innovation association:** assess the separately published ABS AI-by-innovation table. Present rounded published values separately from workbook decimals once denominator ambiguity is resolved; do not silently merge sources. Condition on size only where the actual cross-tabulation is published.
6. **Digital context:** show same-wave cloud, analytics and operational-system rates alongside AI using compatible all-business denominators. These are aggregate profiles, not the capabilities of AI adopters. No inference about co-adoption or whether skills/finance explain AI adoption is available from separate margins.
7. **Historical context:** review earlier AI item wording, examples, response lists, scope and reference periods before calculating change. Retain unapproved years as clearly separated snapshots. Missing years remain missing. Do not fit an interrupted time series or attribute changes specifically to generative AI.
8. **Evidence drawer:** offer exact values, source links, population definitions, flags, comparability decisions and CSV downloads.

Use `research-ai.html` as the intended Part 2 page, linked with Part 1 through the research-series navigation when implemented. The page is implemented and linked from Part 1.

## Comparability register before trend analysis

Create one record per item/year/population. Record original wording and examples, all response options, numerator, denominator, unit, business scope and exclusions, size bands, ANZSIC version, observation period, workbook/sheet/cells, source notes, collection changes, reliability treatment, approved comparison years and rationale.

Use the Part 1 gates: A directly comparable; B comparable after a documented adjustment; C definition/context break, separate segments; D insufficient evidence, snapshot only. A decision must name the exact comparison. Within-wave usability does not approve a time trend. Questionnaire redesign alone does not prove every item incomparable; equally, a similar item label alone does not establish comparability.

## Separate public ABS evidence requiring resolution

The [ABS 2024-25 release](https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business/2024-25), section "Use of information and communication technology", reports AI use by innovation status and size. Its narrative reports 20% for innovation-active versus 6% for non-active businesses. The table's denominator footnote appears inconsistent with this narrative, describing businesses that reported using AI. Verify the underlying downloadable chart data or obtain clarification before treating the table as an approved derived comparison. It is not present as an AI-by-innovation column in the currently extracted local workbook tables.

The same release names different historical comparison years in its AI key statistics and detailed discussion. Check the underlying source period before using a headline historical comparison. Do not treat rounded web values as precise workbook observations.

## Statistical boundaries

- Report published rates and percentage-point differences. Without sufficient uncertainty information, make no significance claims. An unflagged cell is not an estimate without sampling error.
- Preserve suppression, blanks and rounded zeros. Exclude very unreliable values from rankings and calculations; retain them in audit exports.
- No survey-weighted logistic regression, causal pathway estimation, firm-level panel analysis or models treating aggregate percentages as individual businesses.
- No clustering of industry-by-size cells unless genuinely joint cells become available. Separate size and industry margins cannot reconstruct them. Named descriptive technology profiles are sufficient for the present study.
- No weighted industry dispersion, overall SME rate or adopter counts without compatible population counts/weights. The range is an explicitly unweighted description of industry rates.
- No claim that ICT constraints are specifically AI-adoption barriers unless the source question actually identifies AI.
- Microdata or custom joint tables are future extensions, not prerequisites for this public-data study.

## Deliverables

A reviewed source/comparability register; reproducible cross-sectional rate and gap tables; an accessible research story page; a concise findings paper; and tests for source values, arithmetic, exclusions, provenance and offline navigation. The implementation provides the research page, findings paper, reproducible tables, item decisions and source/browser tests.
