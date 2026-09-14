# Part 1: Long-run digital-capability study

Status: implemented as a source-checked descriptive study in `research.html`, with reproducible outputs from `scripts/build_digital_research.py`. Two recent item comparisons are approved; historical harmonisation remains open. See `findings.md` and `comparability_decisions.csv` for the actual evidence boundary.

## Main question

How have the breadth and distribution of digital capabilities among Australian businesses changed since 2005-06, and how have these changes differed by business size and industry?

The supplied publications span 2005-06 to 2019-20, 2021-22 and 2024-25. These are repeated aggregate snapshots, not a panel following the same businesses. Missing publication years must remain gaps; do not interpolate them as observations.

## What breadth means in this study

The main analysis describes the spread of individual activities across the business population and the profile of adoption across dimensions. It does not infer the number of capabilities held by each business from separate marginal percentages. Website adoption and cloud adoption, for example, cannot establish how many businesses use both.

A business-level capability count requires joint response data or suitable microdata. A fixed-item average of published adoption rates could describe average item adoption, but would not establish the distribution of business maturity or the share of businesses above a maturity threshold.

## Dimensions and operational definitions

| Dimension | Candidate indicators | Rules |
| --- | --- | --- |
| Basic connectivity | Internet access, broadband, website, online presence | Keep access, connection type, connection performance and outward-facing presence as separate subseries. Website and website/app are not automatically equivalent. |
| Digital transactions | Orders placed, orders received, online-order channels, internet-income bands, electronic invoicing | Distinguish buying from selling. Businesses receiving orders is not a share of sales. Income bands retain their conditional population. |
| Operational systems | ERP, CRM, EDI, automated system links | Preserve named systems and integration measures; do not treat them as interchangeable. |
| Data capability | Collecting/analysing data, analytics, predictive analysis | Separate data skills from actual use. Preserve wording and purpose. |
| Advanced technologies | Cloud, IoT, AI, blockchain, 3D printing | Each technology is its own series. Paid cloud, general cloud technology and cloud-service mix have different meanings and bases. |
| Digital management | Digital strategy, measuring digital contribution, ICT training, security practices | Separate planning, investment, workforce practices and security. Incidents are risks/outcomes, not evidence of greater capability. |
| Digital value | ICT-associated customer, workflow, market and innovation outcomes | Report the stated denominator and subjective nature of outcomes; do not call these causal effects. |
| Constraints | Infrastructure, technology, cost/finance, skills, knowledge, uncertainty about benefits | Distinguish general business barriers from ICT-specific and cloud-specific barriers. Multiple responses are not additive. |

The automated candidate inventory is deliberately broad and may assign several dimensions to a column. It is a discovery aid, not a final classification. Some broad barrier matches are not digital measures and must be rejected on review.

## Comparability gate

Every proposed series must have an item-level crosswalk reviewed against the original workbook and, where needed, the questionnaire and explanatory notes. Dashboard JSON is a discovery layer; extractor-generated labels and denominators are not independent evidence of comparability.

Record the exact question/label, unit, numerator, denominator, reference period, survey universe, industry classification, employment bands, response options, collection mode where documented, flags, source coordinates and any questionnaire change. Record uncertainty rather than filling missing metadata with assumptions.

Assign one of four decisions:

- A: directly comparable based on documented evidence.
- B: comparable after an explicit, reproducible adjustment, with sensitivity results.
- C: related concept with a definition break; show separate segments, never a joined trend.
- D: insufficient evidence or non-comparable; descriptive snapshot only.

Until reviewed, every inventory row remains UNREVIEWED. Year availability and identical labels do not establish comparability. Never average including-agriculture and excluding-agriculture versions of the same publication. Select a common universe or report separate coverage segments. The 2018-19 publication includes recast 2017-18 appendix observations: use their observation period and avoid double counting them.

Priority audit points from the supplied files: earlier coverage and industry changes; changed online-order wording; website versus website/app; main broadband connection versus multiple connection types; wireless response changes; paid cloud versus broader cloud; innovation definitions introduced in 2018-19; conditional skill, cloud and security-impact populations; and the 2024-25 table footnotes and number-format flags.

## Analysis plan

| Question | Primary analysis | Interpretation limit |
| --- | --- | --- |
| Which activities diffused most widely? | Adoption percentage at each observed wave; percentage-point changes within approved segments; rank activities with the same denominator. | Do not compare the magnitude of changes over unequal intervals without showing dates. Do not rank conditional shares against all-business shares. |
| Are smaller businesses catching up? | Compare 0-4, 5-19, 20-199 and 200+ employee groups where compatible. Report the large-minus-small percentage-point gap and its change. | A narrowing gap is descriptive convergence, not proof that individual small firms caught up. Combined 0-19 subtotals overlap their components. |
| Which industries persistently lag? | For each item, plot industry adoption and gaps to the national rate; report repeated below-benchmark positions over comparable waves. | Specify the item, benchmark and number of waves. Rankings without uncertainty do not establish statistically distinct performance. |
| Have constraints shifted? | Track matched barrier shares within the same question and respondent universe; compare infrastructure/cost with skills/knowledge/benefit uncertainty. | Questionnaire additions cannot be treated as newly emerging barriers. Missing items are not zero; changes in rank alone are weak evidence. |
| Is capability associated with innovation? | Where published, compare the same digital item for innovation-active and non-innovation-active businesses, within size or industry strata. | Aggregate association is not a firm-level or causal effect. Separate size and industry tables cannot jointly adjust for both. Reverse causality and confounding remain possible. |

For comparable strata, let p be the published adoption percentage. The size gap is p(200+) minus p(0-4); change in this gap between two observed waves measures widening or narrowing in percentage points. Also show both underlying adoption rates so saturation is visible.

National changes can reflect both adoption within groups and shifts in business composition. If compatible counts and rates exist, calculate a fixed-weight standardised rate using one pre-specified reference distribution. Otherwise present unadjusted totals alongside group-specific results. Never weight by sample size or use an unweighted industry mean as a national estimate. Do not claim joint size-industry adjustment without joint cells.

## Uncertainty and missingness

Retain published cautions, suppression and source-specific rounded-zero rules. NP is not zero. Blank cells remain missing unless the source explicitly defines them otherwise. Very unreliable estimates are excluded from headline rankings and retained in the audit data.

If standard errors and the necessary covariance information are available, report uncertainty for changes and gaps. RSE categories alone do not supply exact standard errors. Without sufficient design information, report descriptive differences and avoid significance claims. Repeated observations may not be statistically independent.

Use complete comparable waves as the primary analysis; do not impute unavailable questionnaire items. Report the number of observations/waves behind each conclusion and whether endpoints are sensitive to flags or definition breaks.

## Composite index decision

No composite digital maturity index in the primary study. Reconsider only if a stable common item set, common universe, comparable response definitions and adequate time coverage are demonstrated. Pre-specify items, weights, missingness rules and sensitivity analyses before examining composite trends. Do not let more questions in later surveys mechanically increase a score. Distinguish an aggregate item-adoption average from business-level maturity.

## Planned outputs

1. Reviewed availability and comparability matrix, with source-linked decisions.
2. Separate dimension-level small-multiple charts; gaps where years are missing and visible breaks where definitions change.
3. Size-gap trajectories and industry-by-year heatmaps for approved series.
4. Matched barrier profiles and innovation-status comparisons where supported.
5. A findings paper with an explicit evidence-strength assessment and reproducible tables.

No headline trend is considered established simply because a dashboard line could be drawn. The immediate next stage is review of connectivity and transaction series, followed by systems, data, advanced technology, management, value and constraints.

## Files and reproduction

Run `python scripts/inventory_digital_capability.py` from the repository root.

- `indicator_inventory.csv`: every published dashboard column, including non-digital context.
- `candidate_digital_indicators.csv`: keyword-screened candidates, all awaiting review.
- `availability_screen.csv`: candidate column counts by publication and dimension. These are NOT adoption values, distinct-item counts or comparable-series counts; population versions and related tables may repeat concepts.
- `comparability_decisions.csv`: populated selected-item review register, regenerated by `scripts/build_digital_research.py`; includes original header cells, source notes and explicit A/C/D decisions.

Record IDs combine publication year, table ID and zero-based header index. Excel column numbers are one-based. Original workbook paths and sheet names are retained. Inventory regeneration is deterministic and does not modify dashboards or source workbooks.
