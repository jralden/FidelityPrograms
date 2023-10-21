# Global Constants

YEARS = 30                              # Controls bond coupon matrix size - i.e. 30 X 12 months
BEGINNING_YEAR = 2022                   # The first year for reporting
TAX_RATE = .40                          # Our cumulative tax rate
CALL_PROTECTED = True                   # When loading bonds load only if call protection status matches this
MAX_YEAR = 2036                         # When loading bonds, filter out bonds with maturity year greater than this
SHOW_PER_1000_DETAIL = False            # When printing portfolio, show per-1000 detail
USE_EXCLUSIONS = False                  # When loading bonds, filter out bonds with excluded status
SHOW_EXCLUSIONS = True                  # When  loading bonds table, show excluded bonds
NUMBER_RANKED_BONDS_TO_PRINT = 50       # Number of bonds to print in ranked bond list
ORDER_QUANTITY = 50                     # Default number of bonds to order
PORTFOLIO_MIN_QUANTITY = 10             # Minimum number of bonds to include in portfolio
PORTFOLIO_TOTAL_COST = 350000.00        # Default total cost of portfolio
ANALYSING_EXISTING_PORTFOLIO = True     # Disable the availability check
IS_TAXABLE = True                       # When calculating bond profit, consider tax consequences
SHOW_AVAILABILITY = True                # When printing bonds, show availability

Ratings = {'AAA': 99, 'AA+': 98, 'AA': 97, 'AA-': 96, 'A+': 95, 'A': 94, 'A-': 93, 'BBB+': 92,
           'BBB': 91, 'BBB-': 90, 'NR': 50, '--': 50}
