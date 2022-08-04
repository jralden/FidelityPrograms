from __future__ import annotations
from typing import TYPE_CHECKING
import datetime
import numpy as np
import constants as K
if TYPE_CHECKING:
    from portfolio import PortfolioItem
    from bond import Bond


class PaymentSource:
    """
        PaymentSource can be either a Bond or a PortfolioItem.
        They need to implement an interface (informal) that allows
        them to be treated the same for the fairly large amount of code
        that they have in common.

        Candidate for a real interface when I have the time
   """

    def __init__(self, purchase_date) -> None:
        self._cusip: str
        self._description: str

        self._maturity_date: str
        self._maturity_year: int
        self._maturity_day_of_month: int
        self._maturity_month: int
        self._first_coupon_month: int
        # self.process_maturity_date(self)

        self._purchase_year: int
        self._purchase_day_of_month: int
        self._purchase_month: int
        self._purchase_date: str
        # self.process_purchase_date(self, purchase_date)

        self._coupon: float
        self._yearly_income: float
        self._ask: float
        self._sp_rating: str
        self._payment_schedule: np.ndarray
        self._total_interest: float
        self._coupon_matrix: np.ndarray
        self._total_return_pretax: float
        self._total_return_posttax: float
        self._profit: float

    @property
    def cusip(self) -> str:
        return self._cusip

    @property
    def description(self) -> str:
        return self._description

    @property
    def coupon(self) -> float:
        return self._coupon

    @property
    def maturity(self) -> str: return self._maturity_date

    @property
    def maturity_date(self) -> str:
        return self._maturity_date

    @property
    def maturity_year(self) -> int:
        return self._maturity_year

    @property
    def maturity_month(self) -> int:
        return self._maturity_month

    @property
    def maturity_day_of_month(self) -> int:
        return self._maturity_day_of_month

    @property
    def first_coupon_month(self) -> int:
        return self._first_coupon_month

    @property
    def purchase_month(self) -> int:
        return self._purchase_month

    @property
    def purchase_date(self) -> str:
        return self._purchase_date

    @property
    def purchase_day_of_month(self) -> int:
        return self._purchase_day_of_month

    @property
    def sp_rating(self) -> str:
        return self._sp_rating

    @property
    def rating(self): return self._sp_rating

    @property
    def ask(self) -> float:
        return self._ask

    @property
    def payment_schedule(self): return self._payment_schedule             # matrix per year X month  => coupon/2

    @property
    def coupon_matrix(self) -> np.ndarray: return self._coupon_matrix

    @property
    def yearly_income(self) -> float:
        return float(self.coupon / 100 * 1000)                    # per 1000 bonds

    @property
    def profit(self) -> float: return self._profit                # per 1000 bonds

    @property
    def total_return_pretax(self) -> float:                        # per 1000 bonds
        return self._total_return_pretax

    @property
    def total_return_posttax(self) -> float:                         # per 1000 bonds
        return self._total_return_posttax

    def get_coupon_months(self) -> Tuple[int, int]:
        """return the months that coupons are paid in lowest to the highest order"""
        fcm = self.first_coupon_month
        if fcm >= 7: return fcm - 6, fcm
        return fcm, fcm + 6

    @staticmethod
    def process_maturity_date(payment_source: Bond | PortfolioItem) -> None:
        # maturity_year
        _s = payment_source.maturity_date.split("/")
        payment_source._maturity_year = int(_s[2])
        payment_source._maturity_day_of_month = int(_s[1])
        payment_source._maturity_month = int(_s[0])

        # first_coupon_month
        mm = payment_source.maturity_month
        payment_source._first_coupon_month = mm - 6 if mm >= 7 else mm

    # @staticmethod
    def process_purchase_date(self, date: str) -> None:
        if date is None:
            self._purchase_date = datetime.datetime.now().strftime("%m/%d/%Y")
        else:
            self._purchase_date = date
        _s = self.purchase_date.split("/")
        self._purchase_year = int(_s[2])
        self._purchase_day_of_month = int(_s[1])
        self._purchase_month = int(_s[0])

    def make_payment_schedule(self) -> np.ndarray:
        """
            make matrix containing payments/1000 bonds
            arranged as year X month.
        """

        def first_coupon_date_is_before_purchase_date() -> bool:
            if first_coupon_month < self.purchase_month: return True
            if first_coupon_month > self.purchase_month: return False
            # same month as maturity
            if self.maturity_day_of_month >= self.purchase_day_of_month: return False
            return True

        def maturity_date_is_in_first_half_of_year():
            return int(self.maturity_month) < 7

        def set_both_coupons() -> None:
            payment_schedule[year, first_coupon_month] = six_month_coupon
            payment_schedule[year, second_coupon_month] = six_month_coupon

        def evaluate_first_year() -> None:
            if first_coupon_date_is_before_purchase_date():
                payment_schedule[year, second_coupon_month] = six_month_coupon
            else: set_both_coupons()

        def evaluate_last_year() -> None:
            if maturity_date_is_in_first_half_of_year():
                # no last coupon
                payment_schedule[year, first_coupon_month] = six_month_coupon
            else: set_both_coupons()

        # main line logic for building the matrix[year,month] = coupon
        six_month_coupon = self.coupon / 2
        payment_schedule = np.zeros([K.YEARS + 1, 13], float)      # Use base 1 indexing for years and months
        first_coupon_month, second_coupon_month = self.get_coupon_months()
        ending_year = self.maturity_year - K.BEGINNING_YEAR

        for year in range(0, ending_year + 1):
            if year == 0: evaluate_first_year()
            elif year == ending_year: evaluate_last_year()
            else: set_both_coupons()

        return payment_schedule

    def calculate_profit(self) -> None:

        def tax_savings() -> float:
            premium = self.ask * 10.0 - 1000.0
            return 0 if premium <= 0.0 else premium * .40

        if K.IS_TAXABLE:
            tax_savings = tax_savings()
            self._total_return_pretax = 1000 + self.total_interest(1000) + tax_savings
            self._total_return_posttax = 1000 + (self.total_interest(1000) * (1.0 - K.TAX_RATE)) + tax_savings
            self._profit = self.total_return_posttax - (self.ask * 10)
        else:
            self._total_return_pretax = 1000 + self.total_interest(1000)
            self._total_return_posttax = self.total_return_pretax
            self._profit = self.total_return_posttax - (self.ask * 10)


