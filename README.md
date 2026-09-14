# Australian Business, 2005-06

Open `index.html` in a browser. The dashboard works offline with no build step, server, or external assets. It covers all 31 tables in the six supplied ABS workbooks.

The national cards and innovation overview use published totals and matched breakdowns. The topic explorer supports category comparisons, measure comparisons, table heatmaps, original notes, workbook links and CSV downloads. Controls are scoped to the selected published table.

## Rebuild data

Requires Python and the dependency in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
python scripts/extract_data.py
python scripts/validate_data.py
```

The extractor writes `data/dashboard.json` and an equivalent JavaScript dataset so direct file opening works without fetch restrictions. Original workbooks are preserved.

## Interpretation

Cell comments are retained for quality flags, suppression and rounded zeros. Unannotated blanks remain missing. Header and row notes retain population definitions. Counts use thousands; percentages use a fixed 0-100 scale. Categories can overlap, so charts do not sum responses. Shading does not encode statistical significance. Industry classifications and survey coverage are those in the historical source.

Optional browser smoke test (requires Playwright and Microsoft Edge): `python scripts/test_browser.py`. Screenshots are saved in `artifacts/`.

## 2006-07 page

Open `2006-07.html`, or use the survey-year selector on either page. It covers all 33 tables from seven workbooks with technology, innovation, markets, finance, ownership, performance and barriers. Both pages share `styles.css` and `app.js`; the new page loads `data/dashboard-2006-07.js`.

Rebuild and validate:

```powershell
python scripts/extract_2006_07.py
python scripts/validate_2006_07.py
python scripts/test_2006_07.py
```

The browser test requires the optional Playwright package and Microsoft Edge. Existing tests (`validate_data.py` and `test_browser.py`) cover the original page. New screenshots are saved in `artifacts/`.

The new extractor uses explicit population metadata and finite spans for sparse headers. Nested industry totals stay within their industry. The supplied files use different industry categories and innovation population labels between years; the pages do not calculate year-on-year differences. No state breakdown is supplied for 2006-07. Source estimates with RSE above 50% are marked `!!` and excluded from bars and rankings, but retained in tables and CSV. Finance, broadband, customer-dependence and internet-income denominators are shown alongside charts.

## 2007-08 page

Open `2007-08.html`, or select 2007-08 from the year selector on any page. This publication contains 44 tables from eight workbooks, including skills, working arrangements, supplier relationships and detailed web activities. The overview uses the four innovation types; national cards show online ordering, goods/services innovation and collaboration for innovation.

```powershell
python scripts/extract_2007_08.py
python scripts/validate_2007_08.py
python scripts/test_2007_08.py
```

The extractor pivots row-based business populations into the shared explorer schema, preserving each original cell's coordinates. It normalizes the source typo `Non Innovation-active businessses` in DO008 Table 3. Internet income retains its `$b` unit and is displayed as billions of Australian dollars, separately from percentage measures. The dataset carries its topic and overview configuration. No new runtime dependency is required.

Validation checks all 17,692 observations against the source files, including population alignment, units and notes. Browser tests cover every table and population in four chart modes, CSV export, year navigation and mobile width. Screenshots are in `artifacts/dashboard-2007-08-desktop.png` and `artifacts/dashboard-2007-08-mobile.png`.

## 2008-09 page

Open `2008-09.html` or choose 2008-09 in the year selector on any page. All 44 tables from eight workbooks are included, with intellectual-property protection, expanded innovation categories, skills, finance, markets, technology and working arrangements.

```powershell
python scripts/extract_2008_09.py
python scripts/validate_2008_09.py
python scripts/test_2008_09.py
```

The extractor normalizes dash and singular/plural variants in population headings, preserves original cell coordinates, and uses this publication's column spans and units. Its overview explicitly selects the expanded organisational and marketing totals. Broadband and Internet-income definitions are shown with their source notes. Validation covers 22,246 observations; browser tests cover all tables, populations, four modes, dollar units, CSV downloads, year navigation and mobile width. Screenshots are saved as `artifacts/dashboard-2008-09-desktop.png` and `artifacts/dashboard-2008-09-mobile.png`.
