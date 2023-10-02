from typing import *
import os, datetime, tkinter, tkinter.simpledialog, tkinter.filedialog
from enum import Enum
import financial_utilities.constants as K
# from financial_utilities import portfolio
from financial_utilities.bond import Bond, BondGroup
from financial_utilities.portfolio import Portfolio
from financial_utilities.pdf_document import PDFDocument


class F:
    """ Static methods for formatting numbers for display  """

    @classmethod
    def format_dollars(cls, num) -> str: return "${:,.2f}".format(num)

    @classmethod
    def format_float(cls, num) -> str: return "{:,.2f}".format(num)

    @classmethod
    def format_rank(cls, num: int) -> str: return str(num).center(4)


class InputSyntaxError(Exception):
    """Exception raised for errors in the input action's syntax.
        Attributes:
            message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Error in input action's syntax -> {self.message}"


class ActionType(Enum):
    AddBond = 1
    IncreaseBond = 2
    DeleteBond = 3
    DecreaseBond = 4
    PrintBriefAnalysis = 5
    PrintDetailedAnalysis = 6
    SaveBriefAnalysis = 7
    SaveDetailedAnalysis = 8
    QueryBond = 9
    OpenPortfolio = 10
    SavePortfolio = 11
    SavePortfolioAs = 12
    ClearPortfolio = 13
    NewPortfolio = 14
    SetTitle = 15

    Help = 98
    Quit = 99


class Action:
    def __init__(self, action_type: ActionType, cusip: str | None, quantity: int | None):
        super().__init__()
        self.action_type = action_type
        self.cusip = cusip
        self.quantity = quantity


class PortfolioBuilderEngine:

    cwd = os.getcwd()                                                   # get current working directory
    bonds_file_path = os.path.join(cwd, "bonds.csv")                    # keep bonds.csv in the working directory
    print(f"bonds_file_path: {bonds_file_path}")
    bond_history_file_path = os.path.join(cwd, "historical_bonds.csv")  # keep historical_bonds.csv in the working directory
    print(f"bond_history_file_path: {bond_history_file_path}")
    report_file_base = os.path.join(cwd, "bond_reports")        # base directory for per/date report folders
    print(f"report_file_base: {report_file_base}")
    today = datetime.datetime.now().strftime("%Y_%m_%d")
    report_file_directory = os.path.join(report_file_base, f"reports_{today}")
    print(f"report_file_directory: {report_file_directory}")
    if not os.path.exists(report_file_directory):
        os.makedirs(report_file_directory)
    instructions_file_path = os.path.join(cwd, 'instructions.txt')      # for display to user
    commands_file_path = os.path.join(cwd, 'commands.txt')
    exclusions_file_path = os.path.join(cwd, 'exclusions.txt')

    @staticmethod
    def load_exclusions() -> list[str]:
        exclusions = []
        with open("exclusions.txt", "r") as f:
            exclusions.extend(line.strip() for line in f)
        return exclusions

    def __init__(self):
        self.should_run = True
        self.exclusions = self.load_exclusions()
        self.source_bond_group = BondGroup()
        self.source_bond_group.load_csv_file(self.bonds_file_path, K.MAX_YEAR, self.exclusions)
        print(f"{len(self.source_bond_group.excluded_bonds)} bonds excluded")
        self.do_bond_rankings()
        self.portfolio: Portfolio = Portfolio()

    def bondIsInPortfolio(self, cusip) -> bool:
        return any(item.cusip == cusip for item in self.portfolio.portfolio_items)

    def bond_has_already_been_deleted(self, cusip) -> bool:
        return any(item.bond.cusip == cusip for item in self.portfolio.removed_bonds)

    def recommend_bond(self, theType: str, num: int) -> str | None:
        source_list: list[Bond] = []
        match theType:
            case "i": source_list = self.source_bond_group.best_income
            case "p": source_list = self.source_bond_group.best_profit
            case "c": source_list = self.source_bond_group.best_composite

        for bond in source_list:
            if self.bondIsInPortfolio(bond.cusip): continue
            if self.bond_has_already_been_deleted(bond.cusip): continue
            if bond.available < num: continue
            return bond.cusip
        return None

    # region  ----------------------------- Parsers -----------------------------------#

    def parse_add_bond_reference(self, bond_reference: str, num) -> str | None:
        # if it's a reference to a bond in the portfolio, return the cusip
        cusip = self.parse_existing_bond_reference(bond_reference)
        if cusip is not None: return cusip

        # might be a new bond, if it looks like a cusip, return it
        if len(bond_reference) == 9 and bond_reference.isalnum():
            return bond_reference

        # if its one of the special add operators, get a recommended bond
        if bond_reference.startswith(">"):          # is >i | >p | >c
            cusip = self.recommend_bond(bond_reference[1:], num)
            return cusip if cusip is not None else None

    def parse_existing_bond_reference(self, bond_reference: str) -> str | None:
        if bond_reference.isnumeric():      # is number of position in portfolio
            return self.portfolio.find_portfolio_item_by_position(int(bond_reference)).cusip
        elif bond_reference.isalpha():      # is text contained in bond description
            cusip = self.portfolio.find_portfolio_item_containing_text_in_description(bond_reference).cusip
            if cusip is not None: return cusip
        elif bond_reference.isalnum():      # could be a cusip
            item = self.portfolio.find_portfolio_item_by_cusip(bond_reference)
            if item is not None: return item.cusip  # found a bond in the portfolio
        else: return None

    def parse_add(self, addAction: str) -> Action | None:
        action = addAction[1:]                      # remove the leading '+'
        operands = action.split(":")
        # check for valid number of bonds
        if len(operands) == 2 and operands[1].isnumeric(): num = int(operands[1])
        else:
            print(f" Addition Error: {operands[1]} is not a number")
            return None

        # check for valid bond reference
        cusip = self.parse_add_bond_reference(operands[0], num)
        if cusip is None:
            print(f" Addition Error: {operands[0]} does not describe a bond")
            return None

        if self.bondIsInPortfolio(cusip):
            return Action(ActionType.IncreaseBond, cusip, num)      # increase the quantity of the bond
        else:
            return Action(ActionType.AddBond, cusip, num)           # add the bond to the portfolio

    def parse_delete(self, deleteAction: str) -> Action | None:
        action = deleteAction[1:]                   # remove the leading '-'
        operands = action.split(":")
        cusip = self.parse_existing_bond_reference(operands[0])
        if cusip is None:
            print(f" Deletion Error: {operands[0]} does not describe a bond in the portfolio")
            return None

        if len(operands) == 1:
            return Action(ActionType.DeleteBond, cusip, None)

        # grab the second operand : the number of bonds to delete
        if operands[1].isnumeric():
            num = int(operands[1])
            return Action(ActionType.DecreaseBond, cusip, num)
        else:
            print(f" Deletion Error: {operands[1]} is not a number")
            return None

    @staticmethod
    def parse_single_optional_operand(action: str, action_type: ActionType) -> Action | None:
        operands = action.split(":")
        arg2 = None if len(operands) == 1 else operands[1]
        return Action(action_type, arg2, None)

    def parse_actions(self, actions: str) -> list[Action]:
        actions = actions.removesuffix(";")
        action_list = []
        for action in actions.split(";"):
            if action.startswith("+"):
                action_list.append(self.parse_add(action))
            elif action.startswith("-"):
                action_list.append(self.parse_delete(action))
            elif action.startswith("new"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.NewPortfolio))
            elif action.startswith("title"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.SetTitle))
            elif action.startswith("quit"):
                action_list.append(Action(ActionType.Quit, None, None))
            elif action.startswith("db"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.PrintBriefAnalysis))
            elif action.startswith("dd"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.PrintDetailedAnalysis))
            elif action.startswith("sdb"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.SaveBriefAnalysis))
            elif action.startswith("sdd"):
                action_list.append(self.parse_single_optional_operand(action, ActionType.SaveDetailedAnalysis))
            elif action.startswith("Q"):
                action_list.append(Action(ActionType.QueryBond, action.split(":")[1], None))
            elif action.startswith("open"):
                action_list.append(Action(ActionType.OpenPortfolio, None, None))
            elif action.startswith("saveas"):
                action_list.append(Action(ActionType.SavePortfolioAs, None, None))
            elif action.startswith("save"):
                action_list.append(Action(ActionType.SavePortfolio, None, None))
            elif action.startswith("clear"):
                action_list.append(Action(ActionType.ClearPortfolio, None, None))
            elif action.startswith("help"):
                action_list.append(Action(ActionType.Help, None, None))
            else:
                raise InputSyntaxError(f"Unknown action: {action}")
                # self.show_error(actions, action)
        return action_list

    # endregion --------------------------------- Parsers -----------------------------------------#

    # region  ----------------------- Action Execution --------------------------------#

    def save_report(self, title=None, detail=True) -> None:
        theTitle = title if title is not None else self.portfolio.title
        output_file_path = tkinter.filedialog.asksaveasfilename(filetypes=[("PDF files", "*.pdf")])
        if len(output_file_path) > 0:
            if not output_file_path.endswith("pdf"): output_file_path += ".pdf"
            output_file_path = output_file_path.replace("/", "\\")
            doc = PDFDocument(output_file_path)
            # reporter = PortfolioReporter(lf.portfolio)
            self.portfolio.make_analysis_report(doc, theTitle, detail)
            doc.output_document()
            self.launch_report(output_file_path)

    def print_help(self) -> None:
        # read the instructions.txt file and print it to the console
        with open(self.instructions_file_path, "r") as instructions_file:
            print(instructions_file.read())

    @staticmethod
    def launch_report(report_file_path) -> None:
        # launch the pdf file for the report in the browser
        os.system(f"open {report_file_path}")

    def open_portfolio(self) -> None:
        # prompt user for file to load using file dialog
        # file name will end with .pflo
        # read the file and process the actions
        input_file_path = tkinter.filedialog.askopenfilename(filetypes=[("Serialized Portfolio", "*.pflo")])
        if len(input_file_path) == 0: return
        with open(input_file_path, "r") as input_file:
            actions = input_file.read()
            actions = actions.strip()
            print(f"open_portfolio: input => {actions}")
            self.process_actions(actions)

    def save_portfolio_as(self) -> None:
        # prompt user for file name to save using file dialog
        # file name will end with .txt
        # write the portfolio to the text file
        file_path = tkinter.filedialog.asksaveasfilename(filetypes=[("Portfolio files", "*.pflo")])
        if file_path is None: return
        self.portfolio.file_path = file_path
        self.save_portfolio()

    def save_portfolio(self) -> None:
        """
            write the serialized portfolio to the portfolio.file_path. If the file_path is None,
            prompt the user for a file name using file dialog
        """

        line = f"title:{self.portfolio.title};"
        for item in self.portfolio.portfolio_items:
            line += f"+{item.cusip}:{item.quantity};"

        if self.portfolio.file_path is None:
            output_file_path = tkinter.filedialog.asksaveasfilename(filetypes=[("Portfolio files", "*.pflo")])
            if len(output_file_path) == 0: return

            if not output_file_path.endswith("pflo"): output_file_path += ".pflo"
            self.portfolio.file_path = output_file_path

        with open(self.portfolio.file_path, "w") as output_file:
            output_file.write(line + "\n")

    def new_portfolio(self, title=None) -> None:
        self.portfolio = Portfolio()
        theTitle = title
        # if title is None:
        #     theTitle = tkinter.simpledialog.askstring("Title for New Portfolio", "Title:")
        #     if title is None: return
        self.portfolio.title = theTitle

    def print_report(self, detail=True, title=None) -> None:
        """
        Print the Portfolio Analysis Report
            :param detail: True to print the detailed analysis, False to print the brief analysis
            :param title: the title to use for the report
            creates a pdf file and launches it in the browser
            the file is a scratch file in the working directory and
            will be overwritten each time the option is run
         """
        # if there's no first argument, use the portfolio title
        theTitle = title if title is not None else self.portfolio.title
        file_path = os.path.join(self.cwd, "analysis.pdf")

        doc = PDFDocument(file_path)
        self.portfolio.make_analysis_report(doc, theTitle, detail)
        doc.output_document()
        self.launch_report(file_path)

    @staticmethod
    def show_error(actions, action):
        print(f"Error: {action} is not a valid action")
        print(f"In line {actions}")

    def query_bond(self, cusip: str, echo=False) -> Bond | None:
        for aBond in self.source_bond_group:
            if aBond.cusip == cusip:
                if echo: print(f"{aBond.description}   {aBond.coupon}  {aBond.maturity_date} ")
                return aBond
        print(f"Bond {cusip} not found")
        return None

    def add_bond(self, cusip: str, num: int) -> None:
        aBond = self.query_bond(cusip, echo=False)
        if aBond is None: return
        if not K.ANALYSING_EXISTING_PORTFOLIO and aBond.available < num:
            print(f"Error:  {aBond.cusip} {aBond.description} only {aBond.available} bonds available")
            return
        self.portfolio.add_bond(aBond, num)
        self.portfolio.portfolio_changed = True

    def increase_bond(self, cusip, num: int) -> None:
        theItem = self.portfolio.find_portfolio_item_by_cusip(cusip)
        if theItem is None: return
        theItem.quantity += num
        self.portfolio.portfolio_changed = True

    def decrease_bond(self, cusip: str, num: int) -> None:
        theItem = self.portfolio.find_portfolio_item_by_cusip(cusip)
        if theItem is None: return
        if theItem.quantity < num:
            print(f"Error: cannot decrease bond {cusip} by {num}")
            return
        theItem.quantity -= num
        self.portfolio.portfolio_changed = True

    def delete_bond(self, cusip: str) -> None:
        theItem = self.portfolio.find_portfolio_item_by_cusip(cusip)
        if theItem is None: return
        self.portfolio.remove_item(theItem)
        self.portfolio.portfolio_changed = True

    def execute_action_list(self, actions: list[Action]) -> None:
        for action in actions:
            # print(f"action: {action.action_type} action.cusip {action.cusip} ")
            if action.action_type == ActionType.AddBond: self.add_bond(action.cusip, action.quantity)
            elif action.action_type == ActionType.IncreaseBond: self.increase_bond(action.cusip, action.quantity)
            elif action.action_type == ActionType.DeleteBond: self.delete_bond(action.cusip)
            elif action.action_type == ActionType.DecreaseBond: self.decrease_bond(action.cusip, action.quantity)
            elif action.action_type == ActionType.Quit: quit(0)
            elif action.action_type == ActionType.PrintBriefAnalysis: self.print_report(detail=False, title=action.cusip)
            elif action.action_type == ActionType.PrintDetailedAnalysis: self.print_report(detail=True, title=action.cusip)
            elif action.action_type == ActionType.SaveBriefAnalysis: self.save_report(title=action.cusip, detail=False)
            elif action.action_type == ActionType.SaveDetailedAnalysis: self.save_report(title=action.cusip, detail=True)
            elif action.action_type == ActionType.QueryBond: self.query_bond(action.cusip, echo=True)
            elif action.action_type == ActionType.OpenPortfolio: self.open_portfolio()
            elif action.action_type == ActionType.NewPortfolio: self.new_portfolio(title=action.cusip)
            elif action.action_type == ActionType.SavePortfolio: self.save_portfolio()
            elif action.action_type == ActionType.SavePortfolioAs: self.save_portfolio_as()
            elif action.action_type == ActionType.ClearPortfolio: self.portfolio.clear_portfolio()
            elif action.action_type == ActionType.SetTitle: self.portfolio.title = action.cusip
            elif action.action_type == ActionType.Help: self.print_help()
            else:
                print(f"Error: {action.action_type} is not a valid action type")

    # endregion --------------------------------- Action Execution -----------------------------------------#

    def process_actions(self, actions: str) -> None:
        self.portfolio.portfolio_changed = False
        action_list = self.parse_actions(actions)
        self.execute_action_list(action_list)
        if self.portfolio.portfolio_changed:
            self.portfolio.print_bonds(Portfolio.abbreviated_bond_line)
            self.show_status()
            self.portfolio.portfolio_changed = False

    def show_status(self) -> None:
        print(
            f"\nYearly Income  {F.format_dollars(self.portfolio.yearly_income)}" +
            f"    Total interest  {F.format_dollars(self.portfolio.total_interest)}" +
            f"    Total invested {F.format_dollars(self.portfolio.total_invested)}"
        )

    # region ----------------  Ranking Implementation -----------------------#

    @staticmethod
    def print_heading_line(doc: PDFDocument) -> None:
        line = "cusip" + "        description"
        line += 30 * " "
        line += "   yearly_income"
        line += "     profit"
        line += "  available"
        line += "   income rank"
        line += "  profit rank"
        line += "     composite rank"
        doc.line(line)

    @staticmethod
    def print_report_heading(doc: PDFDocument, heading: str, font_size: int) -> None:
        doc.set_font('Courier', 'B', font_size)
        doc.pdf.cell(240, 10, heading, 0, 0, 'C')
        doc.ln()
        doc.reset_font()

    def print_bonds(self, selected_list: list, doc: PDFDocument, heading: str) -> None:
        doc.add_page()
        self.print_report_heading(doc, heading, 12)
        # print_assumptions(doc)
        self.print_heading_line(doc)

        count = 1
        for extract in selected_list:
            line = f"{extract.cusip}"
            line += f"   {extract.description[:40].ljust(45)}"
            line += f"   {F.format_dollars(extract.yearly_income)}"
            line += f"       {F.format_dollars(extract.profit)}"
            line += f"       {F.format_rank(extract.available)}"
            line += f"      {F.format_rank(extract.income_rank)}"
            line += f"        {F.format_rank(extract.profit_rank)}"
            line += f"             {F.format_rank(extract.composite_rank)}"
            doc.line(line)
            count += 1
            if count > K.NUMBER_RANKED_BONDS_TO_PRINT: break

    def make_portfolio_creation_file(self, composite: list, income: list, profit: list) -> None:
        lines = []
        self.make_portfolio(lines, "composite", composite)
        self.make_portfolio(lines, "income", income)
        self.make_portfolio(lines, "profit", profit)

        with open(self.commands_file_path, 'w') as f:
            f.write('\n'.join(lines))

    # endregion ----------------  Ranking Implementation -----------------------#

    # region ----------------- make maximized portfolios -------------------#
    def make_portfolio(self, lines: list, heading: str, selected_list: list) -> None:
        lines.append(heading + '\n')
        bond_index = 0
        line, bond_index = self.make_portfolio_line(selected_list, bond_index)
        line += f"save:Best_{heading.capitalize()}"
        lines.append(line + '\n')
        line, bond_index = self.make_portfolio_line(selected_list, bond_index+1)
        lines.append(line + '\n')

    def make_portfolio_line(self, theBondList: list, starting_bond_index: int) -> tuple[str, int]:
        line = ''
        invested = 0.0
        bond_index = starting_bond_index - 1
        while bond_index < len(theBondList):
            bond_index += 1
            bond = theBondList[bond_index]
            result, invested, line = self.try_to_add_bond_to_portfolio(bond, line, invested)
            match result:
                case "skipped":
                    continue

                case "added":
                    continue

                case "complete":
                    return line, bond_index

                case "over_budget":
                    return line, bond_index

    @staticmethod
    def try_to_add_bond_to_portfolio(bond: Bond, line: str, total_invested: float) -> Tuple[str, float, str]:
        # print(f"incoming total_invested: {total_invested}")
        # print(f"incoming line: {line}")
        quantity = min(bond.available, K.ORDER_QUANTITY)
        if quantity < K.PORTFOLIO_MIN_QUANTITY: return "skipped", total_invested, line

        line += f"+{bond.cusip}:{quantity};"
        total_invested += bond.ask * quantity * 10
        # print(f"this purchase={bond.ask * quantity * 10}")
        # print(f"new total_invested: {total_invested}")
        if total_invested > K.PORTFOLIO_TOTAL_COST:
            # spent more than the limit
            if total_invested - K.PORTFOLIO_TOTAL_COST > 20000.00:
                # print(f"$$$$$$$$$$$$$$line on return: {line}")
                return "over_budget", total_invested, line
            else:
                # print(f"$$$$$$$$$$$$$$line on return: {line}")
                return "complete", total_invested, line
        # haven't reached the target yet
        if K.PORTFOLIO_TOTAL_COST - total_invested < 20000.00: return "complete", total_invested, line
        return "added", total_invested, line

    def do_bond_rankings(self) -> None:
        today = datetime.datetime.now().strftime("%Y_%m_%d")
        output_file_path = os.path.join(self.report_file_directory, f"SelectedBonds_{today}.pdf")
        self.source_bond_group.make_ranking_lists()
        doc = PDFDocument(output_file_path)
        self.print_bonds(self.source_bond_group.best_composite, doc, "Bonds with Best Combined Rank")
        self.print_bonds(self.source_bond_group.best_income, doc, "Bonds with Best Yearly Income")
        self.print_bonds(self.source_bond_group.best_profit, doc, "Bonds with Best Profit")
        doc.output_document()
        os.system(f"open {output_file_path}")
        self.make_portfolio_creation_file(self.source_bond_group.best_composite, self.source_bond_group.best_income, self.source_bond_group.best_profit)

    # endregion ---------------------------------------------------------------------------#
