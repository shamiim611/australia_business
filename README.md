# Australian Business, 2005-06

Open `index.html` in a browser. The dashboard works offline with no build step, server, or external assets. It covers all 31 tables in the six supplied ABS workbooks.

## Deploy with Render

This is a static site. In Render, choose **New > Blueprint** and select this repository; `render.yaml` configures the service automatically. Alternatively, create a Static Site with `.` as the publish directory and no build command. The deployed site starts at `index.html` and includes the survey-year pages.

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

## 2009-10 page

Open `2009-10.html` or choose 2009-10 on any page. All 76 tables from 16 workbooks are available across eight topics. Odd-numbered workbooks include Agriculture, Forestry and Fishing; even-numbered workbooks publish separate estimates excluding that industry. The detailed-chart coverage selector switches between these sets. The headline indicators and innovation overview always use the inclusive coverage, as labelled on the page. CSV notes retain the selected coverage.

```powershell
python scripts/extract_2009_10.py
python scripts/validate_2009_10.py
python scripts/test_2009_10.py
```

The extractor retains workbook-specific IDs, population blocks, source coordinates, units and quality flags. An extra `Total All Industries` row in DO007 Table 2 is grouped with overall totals rather than employment sizes. No totals across coverage sets are added or compared automatically. All 26,841 observations were validated against Excel; browser tests cover all tables, both coverage sets, populations, four chart modes, CSV exports, year navigation and mobile width. Screenshots are in `artifacts/dashboard-2009-10-desktop.png` and `artifacts/dashboard-2009-10-mobile.png`.

## 2010-11 page

Open `2010-11.html` or choose 2010-11 from the year selector. This page includes all 44 tables from eight workbooks, released 13 September 2012. Coverage includes Agriculture, Forestry and Fishing; no separate exclusion set is supplied for this year. The overview, population comparisons, statistical notes, original source cells, CSV exports and dollar units use the shared dashboard components.

```powershell
python scripts/extract_2010_11.py
python scripts/validate_2010_11.py
python scripts/test_2010_11.py
```

All 23,459 observations were checked against Excel. Browser checks cover all tables, populations, four chart modes, reference notes, CSV downloads, year navigation and mobile width. Desktop and mobile screenshots are saved as `artifacts/dashboard-2010-11-desktop.png` and `artifacts/dashboard-2010-11-mobile.png`.

## 2011-12 page

Open `2011-12.html` or choose 2011-12 on any page. The page covers all 44 tables from eight workbooks, released 19 September 2013. Technology data adds social-media presence; the extractor explicitly maps the expanded five-indicator population blocks. Coverage includes Agriculture, Forestry and Fishing.

```powershell
python scripts/extract_2011_12.py
python scripts/validate_2011_12.py
python scripts/test_2011_12.py
```

All 23,525 observations were validated against Excel. Browser checks cover every table, population and chart mode, social-media presence, dollar units, CSV exports, year navigation and mobile width. Screenshots are saved to `artifacts/dashboard-2011-12-desktop.png` and `artifacts/dashboard-2011-12-mobile.png`.

## 2012-13 page

Open `2012-13.html` or select 2012-13 on any page. All 38 tables from seven workbooks are included, released 18 September 2014. This folder adds government procurement and does not supply innovation-type tables; the page uses a technology-adoption overview with internet, web, social-media and online-order indicators. Innovation barriers and population comparisons remain available.

```powershell
python scripts/extract_2012_13.py
python scripts/validate_2012_13.py
python scripts/test_2012_13.py
```

The extractor maps the rearranged workbooks, shifted market tables and shortened performance population headings while retaining original source-cell coordinates and notes. All 21,733 observations passed source validation. Browser tests cover all tables, populations, chart modes, social-media data, CSV exports, dollar units, year navigation and mobile width. Screenshots are in `artifacts/dashboard-2012-13-desktop.png` and `artifacts/dashboard-2012-13-mobile.png`.

## 2013-14 page

Open `2013-14.html` or choose 2013-14 on any page. All 47 tables from eight workbooks are included, released 20 August 2015. Innovation-type tables return, alongside government procurement and a new innovation-collaboration table. The latter uses innovation-active businesses as its denominator.

```powershell
python scripts/extract_2013_14.py
python scripts/validate_2013_14.py
python scripts/test_2013_14.py
```

The extractor maps shifted market tables and reversed barrier table order, preserving source coordinates, flags and units. All 24,673 observations passed Excel checks. Browser tests cover every table and population in four modes, the collaboration denominator, social-media data, CSV exports, dollar units, year navigation and mobile width. Screenshots are in `artifacts/dashboard-2013-14-desktop.png` and `artifacts/dashboard-2013-14-mobile.png`.

## 2014-15 page

Open `2014-15.html` or choose 2014-15 on any page. All 35 tables from seven workbooks are included, released 18 August 2016. The technology overview covers internet access, web and social-media presence, and online orders. Coverage includes Agriculture, Forestry and Fishing. This year supplies general business barriers but no innovation-type or innovation-barrier tables.

```powershell
python scripts/extract_2014_15.py
python scripts/validate_2014_15.py
python scripts/test_2014_15.py
```

The extractor handles the rearranged market and procurement tables, finance assistance measures and business-barrier headings, preserving source coordinates, statistical flags and units. All 19,783 observations were checked against Excel. Browser tests cover every table and population in four modes, denominators, CSV downloads, dollar units, year navigation and mobile width. Screenshots are in `artifacts/dashboard-2014-15-desktop.png` and `artifacts/dashboard-2014-15-mobile.png`.

## 2015-16 page

Open `2015-16.html` or choose 2015-16 on any page. All 47 tables from eight distinct workbooks are included, released 17 August 2017. The innovation overview returns alongside technology, skills, markets and procurement, finance, business arrangements, performance and barriers. Coverage includes Agriculture, Forestry and Fishing.

```powershell
python scripts/extract_2015_16.py
python scripts/validate_2015_16.py
python scripts/test_2015_16.py
```

The extractor verifies that duplicate innovation and skills workbooks are identical before including each once. It handles the reordered population columns, national totals placed before breakdowns, and two additional debt-finance tables. Original source coordinates, statistical flags and units are preserved. All 24,557 observations match Excel. Browser checks cover all tables and populations in four chart modes, CSV exports, denominators, dollar units, year navigation and mobile width. Screenshots are saved to `artifacts/dashboard-2015-16-desktop.png` and `artifacts/dashboard-2015-16-mobile.png`.

## 2016-17 page

Open `2016-17.html` or choose 2016-17 on any page. All 36 tables from seven workbooks are included, released 16 August 2018. The technology overview covers internet access, web and social-media presence, and online orders. This publication includes innovation barriers but supplies no innovation-type or intellectual-property tables. Coverage includes Agriculture, Forestry and Fishing.

```powershell
python scripts/extract_2016_17.py
python scripts/validate_2016_17.py
python scripts/test_2016_17.py
```

The extractor maps the rearranged performance, barriers and skills workbooks while preserving source coordinates, population definitions, statistical flags and units. All 19,315 observations match Excel. Browser checks cover all tables and populations in four chart modes, CSV exports, denominators, dollar units, year navigation and mobile width. Screenshots are saved to `artifacts/dashboard-2016-17-desktop.png` and `artifacts/dashboard-2016-17-mobile.png`.

## 2017-18 page

Open `2017-18.html` or select 2017-18 from any page. All 26 tables from five workbooks are included, released 25 June 2019. This publication reorganises the data into technology access, internet commerce, digital practices, innovation, and finance and competition. The page includes cloud computing, cybersecurity, digital management practices and contextual business counts. Coverage includes Agriculture, Forestry and Fishing.

```powershell
python scripts/extract_2017_18.py
python scripts/validate_2017_18.py
python scripts/test_2017_18.py
```

The extractor preserves population blocks, source cells and statistical flags, and handles the new sparse header spans. Cloud-use and security-impact tables combine measures with different bases; chart notes explain this and retain the original publication notes. All 6,934 observations match Excel. Browser checks cover all 26 tables, populations, four display modes, CSV exports, finance denominators, innovation collaboration, year navigation and mobile width. Screenshots are saved to `artifacts/dashboard-2017-18-desktop.png` and `artifacts/dashboard-2017-18-mobile.png`.

## 2018-19 page

Open `2018-19.html` or select 2018-19 on any page. The page includes 45 published tables from eleven workbooks, released 26 June 2020. The appendix process-conversion table has three sections with different headers, shown separately for 47 explorer sections in total.

```powershell
python scripts/extract_2018_19.py
python scripts/validate_2018_19.py
python scripts/test_2018_19.py
```

Innovation definitions changed under the Oslo Manual in this publication. The overview uses goods/services, processes, development and abandonment measures. The definitions appendix retains its original 2017-18 period in chart sources and CSV exports. Broadband responses now allow multiple connection types. Employment-size breakdowns include an overlapping 0-19 subtotal. Collaboration locations, conditional innovation populations, source coordinates and statistical flags are preserved.

All 20,633 observations were validated against Excel. Browser checks cover all sections, populations, chart modes, historical CSV periods, navigation and mobile width. Screenshots are saved to `artifacts/dashboard-2018-19-desktop.png` and `artifacts/dashboard-2018-19-mobile.png`.

## 2019-20 page

Open `2019-20.html` or select 2019-20 on any page. All 22 tables from five XLSX workbooks are included, released 4 June 2021. Topics cover innovation, technology access, internet commerce, digital practices, performance and working arrangements. Internet indicators no longer include web or social-media presence. Broadband now distinguishes 3G/4G and 5G; source notes identify limits to comparisons with earlier years.

```powershell
python scripts/extract_2019_20.py
python scripts/validate_2019_20.py
python scripts/test_2019_20.py
```

The XLSX reader uses openpyxl and preserves source comments, cell coordinates, population blocks and statistical flags. The income-distribution table begins its first population on the unit row; that heading is retained. Cloud-service and security-impact measures retain their conditional denominators. A blank source cell carrying a caution comment remains missing with its note. Employment breakdowns include an overlapping 0-19 subtotal.

All 9,600 observations were checked against XLSX sources. Browser checks cover all tables, populations, four chart modes, cloud denominators, CSV exports and mobile layout. Screenshots are saved to `artifacts/dashboard-2019-20-desktop.png` and `artifacts/dashboard-2019-20-mobile.png`.

## 2021-22 page

Open `2021-22.html` or choose 2021-22 on any page. All 40 tables from eight workbooks are included, released 22 June 2023. Topics cover business characteristics, performance and work, government, skills, connectivity, online commerce, digital practices and cybersecurity. Selected tables include state/territory and location breakdowns. No 2020-21 page is implied by the year selector.

```powershell
python scripts/extract_2021_22.py
python scripts/validate_2021_22.py
python scripts/test_2021_22.py
```

All 10,263 observations match the XLSX sources. The extractor preserves conditional populations for skills shortages, recruitment, connectivity, cloud services and cybersecurity impacts. Finance outcomes in this publication use all businesses as their base. The shared measure view supports count-only tables while keeping counts separate from percentage measures in mixed tables.

Browser checks cover all 40 tables and four modes, state/territory and location comparisons, CSV downloads, cloud denominators and mobile layout. The 2019-20 browser suite also passes after the shared chart change. Screenshots are saved to `artifacts/dashboard-2021-22-desktop.png` and `artifacts/dashboard-2021-22-mobile.png`.

## 2024-25 page

Open `2024-25.html` or choose 2024-25 on any page. All 61 tables from twelve BCSDC workbooks are included, released 25 June 2026. New topics include clean technology and principal managers, alongside detailed innovation, funding, collaboration, finance, skills, digital practices and cybersecurity.

```powershell
python scripts/extract_2024_25.py
python scripts/validate_2024_25.py
python scripts/test_2024_25.py
```

The extractor uses each workbook's declared table range to exclude stray formatting, reads caution markers from Excel number formats, and preserves suppression and explicit null-as-zero footnotes. It retains the mobile-wireless total despite its blank unit cell. Conditional denominators and original source coordinates are preserved. Connection categories changed from 2021-22; the page identifies this comparison limitation.

All 29,311 observations were checked against XLSX sources. Browser checks cover every table, population, four display modes, conditional finance denominators, CSV exports, state/territory and location breakdowns, and mobile width. Screenshots are saved to `artifacts/dashboard-2024-25-desktop.png` and `artifacts/dashboard-2024-25-mobile.png`.
