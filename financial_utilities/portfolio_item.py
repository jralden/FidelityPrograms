from financial_utilities.payment_source import PaymentSource
from financial_utilities.bond import Bond
import numpy as np


# region -------------------------  class  PortfolioItem ---------------------------------#


class PortfolioItem(PaymentSource):
    _quantity: int = 0
    _coupon_matrix = None

    def __init__(self, theList: list[str], quantity: int, purchase_date=None) -> None:
        """
            create a portfolio item from a list of properties
                :param theList: the list of properties that define a bond
                :param quantity: the number of shares of the bond to be held in the portfolio
                :param purchase_date: the date the bond was purchased, if None, use today's date
        """
        super().__init__(purchase_date)
        self._cusip: str = theList[0]
        self._description: str = theList[1]

        self._maturity_date: str = theList[2]
        self.process_maturity_date(self)

        self._purchase_year: int
        self._purchase_day_of_month: int
        self._purchase_month: int
        self._purchase_date: str
        self.process_purchase_date(purchase_date)
        self._coupon: float = float(theList[3])
        self._yearly_income: float = self._coupon / 100 * 1000
        self._ask: float = float(theList[4])
        self._sp_rating: str = theList[5]
        self._available: int = int(theList[6])
        self._payment_schedule: np.ndarray = self.make_payment_schedule()
        self._quantity: int = quantity
        self._total_interest: float = 0.0
        self._coupon_matrix = self.make_coupon_matrix()
        self._total_return_pretax: float
        self._total_return_posttax: float
        self._profit: float

        self.calculate_profit()

    @classmethod
    def portfolio_item_from_bond(cls, bond: Bond, quantity: int) -> 'PortfolioItem':
        value_list = [bond.cusip, bond.description, bond.maturity_date, bond.coupon,
                      bond.ask, bond.sp_rating, bond.ask_quantity]
        return cls(value_list, quantity)

    @classmethod
    def portfolio_item_from_csv(cls, csv_line: list[str], quantity, purchase_date) -> 'PortfolioItem':
        """
            create a portfolio item from a csv line. line comes from Excel portfolio
            definition file
                :param csv_line: a csv line from a portfolio definition Excel file
                :param quantity: the number of shares of the bond held in the portfolio
                :param purchase_date: the date the bond was purchased

                :return: a portfolio item
        """
        value_list = [csv_line[0], csv_line[1], csv_line[2], csv_line[4], csv_line[8], csv_line[5], 0]
        return cls(value_list, quantity, purchase_date)

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, num):
        self._quantity = num
        self._coupon_matrix = self.make_coupon_matrix()
        self.calculate_profit()

    @property
    def total_cost(self) -> float:
        return self.ask / 100 * self.quantity * 1000

    @property
    def available(self) -> int:
        return self._available

    @property
    def lop(self):  # lop = loss of principle
        return self.total_cost - (self.quantity * 1000)

    def total_interest(self, number_bonds: int) -> float:  # multiply by number of shares to get $ interest amount
        total_percent = self.payment_schedule.sum()
        return total_percent / 100.0 * float(number_bonds)

    def make_coupon_matrix(self) -> np.ndarray:
        """
            make a matrix of actual payments in Year X Month format
            by applying the quantity of each portfolio item to the
            elements of the payment schedule
                :return: the payments matrix
        """
        # bond_coupons = self.payment_schedule
        # new_array = bond_coupons.copy()
        new_array = self.payment_schedule.copy()
        for (year, month), value in np.ndenumerate(new_array):
            if value != 0.0:
                new_array[year, month] = value / 100 * self.quantity * 1000
        return new_array

# endregion ______________________ PortfolioItem -------------------------------------------#
