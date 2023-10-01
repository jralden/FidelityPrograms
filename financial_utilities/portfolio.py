# import os
import numpy as np
from financial_utilities.bond import Bond
# import datetime
# from typing import Tuple
from financial_utilities.pdf_document import PDFDocument
# from financial_utilities.format import Format as F
import financial_utilities.constants as K
# from financial_utilities.payment_source import PaymentSource
from financial_utilities.portfolio_item import PortfolioItem
from financial_utilities.portfolio_reporter import PortfolioReporter


class Portfolio:

    def __init__(self):
        super().__init__()
        self._portfolio_items = []
        self._portfolio_changed: bool = False
        self._removed_bonds = []
        self._file_path = None
        self._title = None

    @property
    def file_path(self): return self._file_path

    @file_path.setter
    def file_path(self, path: str):
        self._file_path = path

    @property
    def title(self): return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def portfolio_changed(self): return self._portfolio_changed

    @portfolio_changed.setter
    def portfolio_changed(self, value):
        self._portfolio_changed = value

    @property
    def portfolio_items(self): return self._portfolio_items

    @property
    def removed_bonds(self): return self._removed_bonds

    abbreviated_bond_line = [
        ["cusip", 12, lambda item: item.cusip],
        ["description", 30, lambda item: item.description],
        ["maturity", 12, lambda item: item.maturity_date],
        ["rating", 10, lambda item: item.rating],
        ["num", 7, lambda item: str(item.quantity)],
        ["ask", 10, lambda item: str(item.ask)],
        ["total cost", 12, lambda item: "${:,.2f}".format(item.total_cost)],
    ]

    bond_line = [
        ["cusip", 12, lambda item: item.cusip],
        ["description", 40, lambda item: item.description],
        ["coupon", 10, lambda item: item.coupon],
        ["maturity", 12, lambda item: item.maturity_date],
        ["rating", 10, lambda item: item.rating],
        ["num", 7, lambda item: str(item.quantity)],
        ["ask", 10, lambda item: str(item.ask)],
        ["total cost", 12, lambda item: "${:,.2f}".format(item.total_cost)],
        ["lop", 14, lambda item: "${:,.2f}".format(item.lop)],
    ]

    def add_bond(self, theBond: Bond, quantity: int) -> PortfolioItem:
        theItem = PortfolioItem.portfolio_item_from_bond(theBond, quantity)
        self._portfolio_items.append(theItem)
        self._portfolio_changed = True
        return theItem

    def add_item(self, theItem: PortfolioItem) -> PortfolioItem:
        self._portfolio_items.append(theItem)
        self._portfolio_changed = True
        return theItem

    # def remove_bond(self, theBond: Bond) -> None:
    #     thePortfolioItem = self.find_portfolio_item_by_bond(theBond)
    #     if thePortfolioItem is not None:
    #         self._removed_bonds.append(thePortfolioItem)
    #         self._portfolio_items.remove(thePortfolioItem)

    def remove_item(self, theItem: PortfolioItem) -> None:
        self._removed_bonds.append(theItem)
        self._portfolio_items.remove(theItem)
        self._portfolio_changed = True

    def clear_portfolio(self) -> None:
        self.__init__()
        self._portfolio_changed = True

    @property
    def total_invested(self) -> float:
        spend = 0.0
        for aPortfolioItem in self._portfolio_items:
            spend += aPortfolioItem.total_cost
        return spend

    @property
    def total_interest(self) -> float:
        sum_of_coupons = np.zeros([K.YEARS + 1, 13], float)
        for thePortfolio_item in self.portfolio_items:
            sum_of_coupons = np.add(sum_of_coupons, thePortfolio_item.coupon_matrix)
        return sum_of_coupons.sum()

    def find_portfolio_item_by_cusip(self, cusip: str) -> PortfolioItem | None:
        # sourcery skip: use-next
        for aPortfolioItem in self._portfolio_items:
            if aPortfolioItem.cusip == cusip:
                return aPortfolioItem
        return None

    def find_portfolio_item_by_position(self, position: int) -> PortfolioItem | None:
        return self._portfolio_items[position-1] if position <= self.length else None

    # def find_portfolio_item_by_bond(self, bond: Bond) -> PortfolioItem | None:
    #     for aPortfolioItem in self._portfolio_items:
    #         if aPortfolioItem == bond:
    #             return aPortfolioItem
    #     return None

    def find_portfolio_item_containing_text_in_description(self, text: str) -> PortfolioItem | None:
        # sourcery skip: use-next
        for aPortfolioItem in self._portfolio_items:
            if text in aPortfolioItem.description:
                return aPortfolioItem
        return None

    @property
    def total_profit(self) -> float:
        profit = 0.0
        for aPortfolioItem in self._portfolio_items:
            profit += aPortfolioItem.profit * aPortfolioItem.quantity
        return profit

    @property
    def yearly_income(self) -> float:
        yearly_income = 0.0
        for aPortfolioItem in self._portfolio_items:
            yearly_income += aPortfolioItem.yearly_income * aPortfolioItem.quantity
        return yearly_income

    @property
    def total_par_value(self) -> float:
        number_of_bonds = 0.0
        for thePortfolio_item in self.portfolio_items:
            number_of_bonds += float(thePortfolio_item.quantity) * 1000
        return number_of_bonds

    @property
    def total_LOP(self) -> float:
        return self.total_invested - self.total_par_value

    @property
    def length(self) -> int:
        return len(self._portfolio_items)

    def get_combined_income_matrix(self) -> np.ndarray:
        """
            add all the bond's coupon matrices together creating a single matrix
            with all bond income for the portfolio
        """
        sum_of_coupons = np.zeros([K.YEARS + 1, 13], float)
        for thePortfolio_item in self.portfolio_items:
            sum_of_coupons = np.add(sum_of_coupons, thePortfolio_item.coupon_matrix)
        return sum_of_coupons

    def make_analysis_report(self, doc: PDFDocument, theTitle: str, detail: bool = False) -> None:
        reporter = PortfolioReporter(self)
        reporter.make_analysis_report(pdf_document=doc, title=theTitle, detail=detail)

    # region --------------------------  Print portfolio contents to Console --------------------------#

    # def print_bonds(self, bond_line_definition) -> None:
    #     self.print_bond_heading(bond_line_definition)
    #     for count, item in enumerate(self.portfolio_items, start=1):
    #         line_number = str(count).ljust(2)
    #         line = f"{line_number} "
    #         for field in bond_line_definition:
    #             getter = field[2]
    #             length = field[1]
    #             data = str(getter(item))  # execute lambda
    #             data = data[:length - 1]  # truncate to length - 1
    #             line += data.ljust(length)
    #         print(line)
    #     print('')

    @staticmethod
    def print_bond_heading(bond_line_definition) -> None:
        line = "    "
        for field in bond_line_definition:
            title = field[0]
            length = field[1]
            line += title.ljust(length)
        print(line)

        line = ""
        for field in bond_line_definition:
            length = field[1]
            data = "-" * length
            line += data
        print(line)

    def print_bonds(self, bond_line_definition) -> None:
        self.print_bond_heading(bond_line_definition)
        for count, item in enumerate(self.portfolio_items, start=1):
            line_number = str(count).ljust(2)
            line = f"{line_number} "
            for field in bond_line_definition:
                getter = field[2]
                length = field[1]
                data = str(getter(item))  # execute lambda
                data = data[:length - 1]  # truncate to length - 1
                line += data.ljust(length)
            print(line)
        print('')

    def print_yearly_interest(self) -> None:

        def hasIncome(theYear) -> bool:
            return any(interest_matrix[theYear, theMonth] != 0.0 for theMonth in range(1, 13))

        print("                                  Interest Income/Year")
        interest_matrix = self.get_combined_income_matrix()
        yearly_totals = {}
        for year in range(0, K.YEARS + 1):
            if hasIncome(year):
                yearly_total = 0.0
                calendar_year = year + 2022
                for month in range(1, 13):
                    yearly_total += interest_matrix[year, month]
                # save the yearly total
                yearly_totals[calendar_year] = yearly_total
        for year, interest in yearly_totals.items():
            print(f"{year:4}", end=' ')
            print("{:9,.2f}".format(interest), end=' ')
            # print("  ", end=' ')
        print('')

    @classmethod
    def print_income_matrix(cls, income_matrix: np.ndarray) -> None:

        def printTheHeading() -> None:
            print('year', end='')
            for aMonth in range(1, 13):
                value = f"{str(aMonth)}  "
                print(f"{value:>10}", end='')
            print('    total')

        def hasIncome(theYear) -> bool:
            return any(income_matrix[theYear, theMonth] != 0.0 for theMonth in range(1, 13))

        # print the income by month for each year
        printTheHeading()
        total_for_all_years = 0.0
        for year in range(0, K.YEARS + 1):
            if hasIncome(year):
                # print the year line
                yearly_total = 0.0
                calendar_year = year + 2022
                print(f"{calendar_year}", end='')
                for month in range(1, 13):
                    coupons = f"{income_matrix[year, month]:10.2f}"
                    yearly_total += income_matrix[year, month]
                    print(coupons, end='')
                # print the yearly total
                total_for_all_years += yearly_total
                yt = "${:,.2f}".format(yearly_total)
                print(f"    {yt}", end='')
                print()
        tfay = "${:,.2f}".format(total_for_all_years)
        tfay = ' ' * 122 + tfay
        print(f"total {tfay}")

    # endregion ______________________ Console Printing -------------------------------------------#

# endregion ______________________ Portfolio -------------------------------------------#
