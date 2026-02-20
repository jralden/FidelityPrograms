# FidelityPrograms

## Description / Purpose

FidelityPrograms is a suite of Python tools for managing and analyzing corporate bond investments held through Fidelity brokerage accounts. The project automates three core workflows:

1. **Bond Holdings Analysis** -- Reads existing bond portfolio positions from CSV exports (IRA and joint accounts), calculates income, profit, and interest projections, and generates detailed PDF analysis reports.
2. **Bond Search & Download** -- Uses Selenium browser automation to log into the Fidelity website, search for investment-grade corporate bonds matching specific criteria (maturity range, Moody's/S&P rating filters), and download the results as CSV files.
3. **Portfolio Builder** -- An interactive command-line application that loads available bonds from CSV, ranks them by income, profit, and a composite score, and lets the user construct optimized bond portfolios through a custom action language (add, delete, increase, decrease bonds; save/open portfolios; generate reports).

## Technologies / Languages

- **Language:** Python 3.11+
- **NumPy** -- Used extensively for payment schedule matrices (year x month coupon calculations), income aggregation, and profit computation.
- **fpdf (FPDF)** -- PDF report generation in landscape letter format with Courier font tables.
- **Selenium / undetected-chromedriver** -- Browser automation to drive Fidelity's website for bond search and position downloads.
- **webdriver-manager** -- Manages ChromeDriver installation for Selenium.
- **tkinter** -- File open/save dialogs in the portfolio builder.
- **csv** -- Parsing bond data from Fidelity CSV exports.
- **IDE:** JetBrains (PyCharm), based on `.idea` project files.

## Key Files / Structure

```
FidelityPrograms/
  .project-definition.json       -- Project metadata; status is "archived"

  financial_utilities/            -- Shared library used by all three applications
    __init__.py
    constants.py                  -- Global configuration (tax rate, max year, ratings, portfolio limits)
    payment_source.py             -- Base class for Bond and PortfolioItem; coupon schedule math
    bond.py                       -- Bond class (parsed from Fidelity CSV), BondGroup, ScoreList ranking
    portfolio_item.py             -- PortfolioItem class wrapping a Bond with quantity and coupon matrix
    portfolio.py                  -- Portfolio class: collection of items, income/profit aggregation, reporting
    portfolio_reporter.py         -- PDF report generation: summary, bond detail, yearly income tables
    pdf_document.py               -- Thin wrapper around FPDF for PDF output
    fidelity_web_access.py        -- FidelityWebAccess class: Selenium-based login, bond/position download

  bond_holdings/                  -- Analyzes existing bond holdings across multiple accounts
    main.py                       -- Loads CSVs for marys_IRA, johns_IRA, joint_account; generates PDF reports
    data/                         -- CSV, PDF, and XLS files for each account

  down_loads/                     -- Selenium script to automate Fidelity website interactions
    main.py                       -- Logs in, navigates bond search, downloads CSV, moves file

  portfolio_builder/              -- Interactive portfolio construction tool
    main.py                       -- REPL loop; parses user actions via PortfolioBuilderEngine
    portfolio_builder_engine.py   -- Action parser, bond ranking, portfolio CRUD, report generation
    data/
      bonds.csv                   -- Source bond data (downloaded from Fidelity)
      exclusions.txt              -- Issuer keywords to exclude (energy/utility companies)
      instructions.txt            -- User-facing help text for the action language
      commands.txt                -- Auto-generated portfolio creation commands
      PortfolioBuilderLogic.txt   -- Design notes
      *.pdf                       -- Generated analysis reports
```

## Current State / Completeness

- **Status: Archived.** The `.project-definition.json` marks the project as archived.
- The git history shows early-stage development with generic commit messages ("Working", "First app working") followed by an archival commit.
- The three sub-applications (bond_holdings, down_loads, portfolio_builder) are all functional but show signs of being personal-use tools rather than production-polished software:
  - Hardcoded file paths (Windows `C:/Users/johnr/...` and `D:/Development/...` paths) appear in `down_loads/main.py` and `fidelity_web_access.py`.
  - Credentials are hardcoded in plain text in `down_loads/main.py`.
  - `fidelity_web_access.py` contains large blocks of commented-out code from iterative debugging of Selenium selectors.
  - No unit tests, no requirements.txt or setup.py, no virtual environment configuration.
- The financial calculation engine (payment schedules, profit, ranking) in `financial_utilities/` is the most complete and well-structured part of the codebase.

## Notable Features

- **Bond Ranking System:** Bonds are ranked independently by yearly income and total profit, then assigned a composite rank (sum of both). The engine can auto-recommend the next best bond to add to a portfolio based on these rankings (`>i`, `>p`, `>c` operators).
- **Custom Action Language:** The portfolio builder uses a semicolon-delimited mini-language for batch operations (e.g., `+CUSIP:50;-3;db:My Portfolio;save`), supporting portfolio serialization to `.pflo` files that can be replayed.
- **Tax-Aware Calculations:** Profit calculations account for taxable vs. tax-exempt accounts, including premium amortization tax savings at a configurable 40% rate.
- **Coupon Payment Matrix:** Income projections are built as NumPy year-by-month matrices, enabling detailed cash flow visualization across the full holding period.
- **PDF Report Generation:** Multi-page landscape PDF reports include portfolio summaries, per-bond detail, yearly income tables, and per-bond income breakdowns.
- **Exclusion Filtering:** The bond loader supports keyword-based exclusion of specific issuers (energy/utility sector companies) from the available bond pool.
