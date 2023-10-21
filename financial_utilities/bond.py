import datetime
import traceback
# import numpy as np
from enum import Enum
import csv
import financial_utilities.constants as K
from financial_utilities.payment_source import PaymentSource

# region BondFields enum

"""
    BondField is an enum that defines the fields in the bond csv file
    that is downloaded from the Fidelity website. It represents the available
    bonds that can be purchased matching the criteria in the bond screening
    query
"""


class BondField(Enum):
    Cusip = 0
    State = 1
    Description = 2
    Coupon = 3
    Maturity_Date = 4
    Next_Call_Date = 5
    Moody_Rating = 6
    SP_Rating = 7
    Bid = 8
    Ask = 9
    Yield_Bid = 10
    Ask_Yield_Worst = 11
    Ask_Yield_Maturity = 12
    Quantity_Bid = 13
    Quantity_Ask = 14
    Attributes = 15
    
# endregion

# region ------------------------  class  Bond ----------------------------------#


class Bond(PaymentSource):
    
    count = 0

    @staticmethod
    def clean_int(int_string: str) -> int:
        return int(int_string.replace(",", ""))

    def __init__(self, values: list, purchase_date=None) -> None:
        super().__init__(purchase_date)
        if not values: raise Exception("Bond is empty")
        self.values_list = values
        Bond.count += 1
        # initialize instance variables

        # cusip
        _s = self.values_list[BondField.Cusip.value]
        if _s.startswith('='): _s = _s[2:-1]            # sometimes the cusip looks like this ="cusip"
        self._cusip = _s

        # description
        self._description = self.values_list[BondField.Description.value]

        # coupon
        self._coupon = float(self.values_list[BondField.Coupon.value])

        # maturity_date
        self._maturity_date = self.values_list[BondField.Maturity_Date.value]
        self.process_maturity_date(self)

        # next_call_date & callable
        self._callable = False
        _s = self.values_list[BondField.Next_Call_Date.value]
        if ("N/A" in _s) or ("--" in _s):
            self._callable = False
        else:   # there is a next_call_date
            # if the next call date is within a year of maturity, don't consider it callable
            self._next_call_date = datetime.datetime.strptime(_s, '%m/%d/%Y')
            maturity = datetime.datetime.strptime(self._maturity_date, '%m/%d/%Y')
            delta = maturity - self._next_call_date
            self._callable = delta > datetime.timedelta(days=365)

        self._purchase_date = purchase_date or datetime.datetime.now().strftime("%m/%d/%Y")
        self.process_purchase_date(self._purchase_date)

        # sp_rating
        self._sp_rating = self.values_list[BondField.SP_Rating.value]

        # bid
        _s = self.values_list[BondField.Bid.value]
        if _s.__contains__("N/A"): _s = _s = "0.0"
        self._bid = float(_s)

        # ask
        _s = self.values_list[BondField.Ask.value]
        if _s.__contains__("N/A"): _s = _s = "0.0"
        self._ask = float(_s)

        # yield_bid
        _s = self.values_list[BondField.Yield_Bid.value]
        if _s.__contains__("N/A"): _s = _s = "0.0"
        self._yield_bid = float(_s)

        # ask_yield_worst
        self._ask_yield_worst = float(self.values_list[BondField.Ask_Yield_Worst.value])

        # ask_yield_maturity
        self._ask_yield_maturity = float(self.values_list[BondField.Ask_Yield_Maturity.value])

        # attributes
        self._attributes = self.values_list[BondField.Attributes.value]

        # sp_rating
        self._sp_rating = self.values_list[BondField.SP_Rating.value]
        if self._sp_rating in K.Ratings: self._sp_rating_value = K.Ratings[self._sp_rating]
        else: self._sp_rating_value = 0

        self._bid_value = self.clean_float(self.values_list[BondField.Bid.value])
        self.yearly_bid = self.clean_float(self.values_list[BondField.Yield_Bid.value])

        # bid_quantity
        _s = self.values_list[BondField.Quantity_Bid.value]
        if _s in ["N/A(N/A)", " 0(N/A)"]: _s = "0(0)"
        sp = _s.split('(')
        self._bid_quantity = self.clean_int(sp[0])

        # min_quantity_bid
        self._min_quantity_bid = self.clean_int(sp[1][:-1])

        # ask
        self._ask = self.clean_float(self.values_list[BondField.Ask.value])

        # ask_quantity
        _s = self.values_list[BondField.Quantity_Ask.value]
        sp = _s.split('(')
        self._ask_quantity = self.clean_int(sp[0])

        # min_quantity_ask
        self._min_quantity_ask = self.clean_int(sp[1][:-1])

        self._ask_yield_worst = self.clean_float(self.values_list[BondField.Ask_Yield_Worst.value])

        # ask_yield_maturity
        self._ask_yield_maturity = self.clean_float(self.values_list[BondField.Ask_Yield_Maturity.value])

        # attributes
        self._attributes = self.values_list[BondField.Attributes.value]

        # ranking attributes
        self._income_rank = 0
        self._profit_rank = 0
        self._composite_rank = 0

        self._payment_schedule = self.make_payment_schedule()
        self.calculate_profit()

    # region ------------------------  properties ---------------------------------#

    @property
    def is_callable(self) -> bool: return self._callable
    
    @property
    def next_call_date(self) -> datetime: return self._next_call_date
    
    @property
    def sp_rating_value(self) -> int: return self._sp_rating_value
    
    @property
    def bid(self) -> float: return self._bid
    
    @property
    def yield_bid(self) -> float: return self._yield_bid
    
    @property
    def ask_yield_worst(self) -> float: return self._ask_yield_worst
    
    @property
    def ask_yield_maturity(self) -> float: return self._ask_yield_maturity

    @property
    def ask_quantity(self) -> int: return self._ask_quantity

    @property
    def min_quantity_ask(self) -> int: return self._min_quantity_ask

    @property
    def available(self) -> int: return self._ask_quantity

    @property
    def quantity_bid(self) -> int: return self._bid_quantity

    @property
    def min_quantity_bid(self) -> int: return self._min_quantity_bid
    
    @property
    def attributes(self) -> str: return self._attributes

    @property
    def callable(self) -> bool: return self._callable

    # ranking properties
    @property
    def income_rank(self) -> int: return self._income_rank

    def set_income_rank(self, value: int): self._income_rank = value

    @property
    def profit_rank(self) -> int: return self._profit_rank

    def set_profit_rank(self, value: int): self._profit_rank = value

    @property
    def composite_rank(self) -> int: return self._composite_rank

    def set_composite_rank(self, value: int): self._composite_rank = value

    # endregion

    # region ------------------------  methods ---------------------------------#

    @staticmethod
    def clean_float(value: str) -> float:
        if value.__contains__("N/A"): return 0.0
        if value.__contains__("--"): return 0.0
        return float(value)

    def get_purchase_month_and_day(self) -> tuple[int, int]:
        return self._purchase_month, self._purchase_day_of_month

    def total_interest(self, number_bonds: int) -> float:    # multiply by number of shares to get $ interest amount
        total_percent = self._payment_schedule.sum()
        return total_percent/100.0 * float(number_bonds)

    def get_total_cost(self, number_of_shares: float) -> float:
        return self.ask / 100 * number_of_shares * 1000

# endregion

# region ------------------------  class  BondGroup ---------------------------------#


class BondGroup:
    
    headings_list = []       # list of strings for column headings - unused
    
    def __init__(self) -> None:
        super().__init__()
        self._bonds = []
        self.best_income = []
        self.best_profit = []
        self.best_composite = []
        self.excluded_bonds = []
        # self._profit = 0.0

    @property
    def bonds(self) -> [Bond]: return self._bonds

    def item(self, index: int) -> Bond:
        return self._bonds[index]
    
    def find_bond(self, cusip: str) -> Bond | None:  # sourcery skip: use-next
        for bond in self._bonds:
            if bond.cusip == cusip: return bond
        return None
        
    def length(self) -> int: return len(self._bonds)
    
    def add_bond(self, bond: Bond) -> None:
        self._bonds.append(bond)
    
    def set_headings(self, headings: list) -> None: self.headings_list = headings
    
    def get_heading(self, bond_field: BondField) -> str: return self.headings_list[bond_field.value]
    
    def has_headings(self) -> bool: return len(self.headings_list) > 0
    
    def sort_via_ask_ytm(self):
        self._bonds = sorted(self._bonds, key=lambda bond: bond.ask_yield_maturity, reverse=True)
    
    def sort_via_coupon(self):
        self._bonds = sorted(self._bonds, key=lambda bond: bond.coupon, reverse=True)
    
    def load_csv_file(self, file_name: str, max_year, exclusions: list) -> None:

        def is_excluded(description: str, cusip: str) -> bool:
            if not K.USE_EXCLUSIONS: return False
            for exclusion in exclusions:
                if len(exclusion) > 0 and exclusion in description:
                    self.excluded_bonds.append(f"{cusip}:{description}:{exclusion}")
                    if K.SHOW_EXCLUSIONS:
                        print(f"{cusip} {description[:30]} excluded by [{exclusion}]   ")
                    return True
            return False

        def protection_status_matches(bond_is_callable: bool) -> bool:
            return False if K.CALL_PROTECTED and bond_is_callable else True

        def report_results():
            # print(f"bonds to consider has {extracted_count} remaining from total of {source_bond_group.length()}")
            # print(f"   maturity too late = {too_late} unprotected = {len(unprotected_list)} excluded = {excluded}")
            # print(f"   bonds with no coupon = {no_coupon}")
            print(f"Loaded {self.length()} bonds")

        def read_bond_csv(file_path: str) -> list[list[str]]:
            """
                Reads a csv file and returns a list of bond
                property lists
                    :param file_path: location of .csv file
                    :return:    list of property lists
            """
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                theList = list(csv_reader)
                theList.pop(0)                                      # remove the header
                culled_list = []
                for row in theList:
                    try:
                        cusip = row[0]
                        # sometimes cusip is of form  ="ccccccccc"
                        if cusip.startswith("="): row[0] = cusip[2:-1]
                        culled_list.append(row)
                    except Exception:           # exception when we hit junk at end of .csf file
                        if not culled_list: traceback.format_exc()
                        break
                print(len(culled_list))
                return culled_list

        main_bonds = read_bond_csv(file_name)
        print(f"Loaded {len(main_bonds)} bonds from bond csv file")
        for row in main_bonds:
            try:
                newBond = Bond(row)
                if not is_excluded(newBond.description, newBond.cusip) and newBond.maturity_year <= max_year:
                    if protection_status_matches(newBond.callable):
                        self.add_bond(newBond)

            except Exception as e:
                traceback.format_exc()
                print(f"Exception reading bond {e} {row} ")
                # report_results()
                return

        report_results()

    def make_ranking_lists(self) -> None:
        self.rank_bonds()
        self.best_income: list[Bond] = sorted(self.bonds, key=lambda bond: bond.income_rank)
        self.best_profit: list[Bond] = sorted(self.bonds, key=lambda bond: bond.profit_rank)
        self.best_composite: list[Bond] = sorted(self.bonds, key=lambda bond: bond.composite_rank)

    @staticmethod
    def print_header(pdf, title):
        pdf.add_page()
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(200, 10, title, 0, 0, 'C')
        pdf.ln(10)
        pdf.set_font('Courier', '', 9)

    def print_bonds(self, pdf, include_callable: bool, title: str, max_lines: int) -> None:
        self.print_header(pdf, title)
        _ic = "next call date" if include_callable else ""
        pdf.cell(0, 5, f"  cusip        description                                 maturity       callable    ask yield  rating   {_ic}")
        pdf.ln()
        count = 0
        for qbond in self._bonds:
            count += 1
            if count > max_lines: break
            _m = qbond.maturity_date.strftime("%m/%d/%Y")
            _fc = qbond.next_call_date.strftime("%m/%d/%Y") if qbond.is_callable and include_callable else " "
            _c = "true" if qbond.is_callable else "false"
            _d = qbond.description[:40]
            pdf.cell(0, 5, f"{qbond.cusip}  {_d:<45}  {_m:<12}     {_c:5}       {qbond.ask_yield_maturity:<5}      {qbond.sp_rating:<5}     {_fc:<10}    ")
            pdf.ln()
        self.print_average_ask_yield(pdf, max_lines)

    def rank_bonds(self) -> None:
        ScoreList.rank_a_list(self, value=lambda be: be.yearly_income,
                              assign=lambda be, rank: be.set_income_rank(rank))

        ScoreList.rank_a_list(self, value=lambda be: be.profit,
                              assign=lambda be, rank: be.set_profit_rank(rank))

        for bex in self.bonds:
            bex.set_composite_rank(bex.income_rank + bex.profit_rank)

    def print_average_ask_yield(self, pdf, max_lines: int) -> None:
        count = 0
        ask_sum = 0.0
        for bond in self._bonds:
            count += 1
            if count > max_lines: break
            ask_sum += bond.ask_yield_maturity
            
        avg = ask_sum / (count - 1)
        avg_str = str(avg)
        pdf.cell(0, 5, f"                                                                  Average Ask Yield    {avg_str[:6]:<6}")
        pdf.ln()
        
    def __iter__(self): return BondIterator(self)
    
# endregion

# region ------------------------  class  BondIterator ---------------------------------#


class BondIterator:
    
    def __init__(self, bond_group: BondGroup):
        self._bonds = bond_group.bonds
        self._index = 0
    
    def __iter__(self):
        self._index = 0
        
    def __next__(self):
        if self._index >= len(self._bonds):
            raise StopIteration
        result = self._bonds[self._index]
        self._index += 1
        return result
# endregion

# region ------------------------  class  ScoreList ---------------------------------#


class ScoreList:

    def __init__(self) -> None:
        super().__init__()
        self._list_of_scores = {}

    @property
    def list_of_scores(self) -> dict: return self._list_of_scores

    def try_to_add(self, score: float):
        if score not in self._list_of_scores.keys():  self._list_of_scores[score] = 0

    def assign_ranks_to_scores(self):
        sorted_keys = sorted(self._list_of_scores.keys(), reverse=True)
        for theRank, key in enumerate(sorted_keys, start=1):
            self._list_of_scores[key] = theRank

    def score_to_rank(self, score: float):
        return self._list_of_scores[score]

    @classmethod
    def rank_a_list(cls, inlist: BondGroup, value=None, assign=None):
        score_list = ScoreList()
        for bond in inlist:
            score_list.try_to_add(value(bond))
        score_list.assign_ranks_to_scores()
        for bond in inlist:
            rank = score_list.score_to_rank(value(bond))
            assign(bond, rank)

# endregion
