import os
# from typing import *
from financial_utilities.pdf_document import PDFDocument
# from portfolio import Portfolio, PortfolioItem
import numpy as np
import datetime
import financial_utilities.constants as K

_bond_line = [
        ["cusip", 12, lambda item: item.cusip],
        ["description", 26, lambda item: item.description],
        ["interest/yr", 12, lambda item: "${:,.2f}".format(item.yearly_income * item.quantity)],
        ["avail", 9, lambda item: item.available],
        ["maturity", 12, lambda item: item.maturity],
        ["coupon", 7, lambda item: item.coupon],
        ["num", 4, lambda item: item.quantity],
        ["tot cost", 12, lambda item: "${:,.2f}".format(item.total_cost)],
        ["price", 10, lambda item: str(item.ask)],
        ["lop", 14, lambda item: "${:,.2f}".format(item.lop)],
        ["rating", 6, lambda item: item.rating],
        # ["ask YTM", 8, lambda item: str(item.ask_ytm)]
    ]


def launch_report(report_file_path) -> None:
    """ launch the pdf file for the report in the browser"""
    os.system(f"start {report_file_path}")


def format_dollars(num) -> str:
    return "${:,.2f}".format(num)


def format_float(num) -> str:
    return "{:,.2f}".format(num)


def print_bond_detail_summary(doc: PDFDocument, item) -> None:
    # bond summary line when printing yearly income by bond
    quantity = item.quantity
    line = f" profit* = {format_dollars(item.profit * quantity)}"
    line += f"  interest = {format_dollars(item.total_interest(1000) * quantity)}"
    line += f"  return = {format_dollars(item.total_return_pretax * quantity)}"
    line += f"  return* = {format_dollars(item.total_return_posttax * quantity)}"
    line += f"  income/yr = {format_dollars(item.yearly_income * quantity)}"
    doc.line(line)
    line = "      * = after tax,       profit = (principal_return + total_interest* + tax_savings) - cost"

    doc.line(line)

def print_income_matrix(doc: PDFDocument, income_matrix: np.ndarray) -> None:

    def printTheHeading() -> None:
        pline = 'year      '
        for aMonth in range(1, 13):
            m = str(aMonth)
            pline += m.ljust(9)
        pline += "total".ljust(10)
        doc.line(pline)

    def hasIncome(theYear) -> bool:
        return any(income_matrix[theYear, theMonth] != 0.0 for theMonth in range(1, 13))

    # print the income by month for each year
    printTheHeading()
    total_for_all_years = 0.0
    for year in range(0, K.YEARS + 1):
        line = ""
        if hasIncome(year):
            # print the year line
            yearly_total = 0.0
            calendar_year = str(year + 2022)
            line += calendar_year.ljust(5)
            for month in range(1, 13):
                coupons = f"{income_matrix[year, month]:9.2f}"
                yearly_total += income_matrix[year, month]
                line += coupons
            # print the yearly total
            total_for_all_years += yearly_total
            yt = "${:,.2f}".format(yearly_total)
            line += f"    {yt}"
            doc.line(line)
    tfay = "${:,.2f}".format(total_for_all_years)
    tfay = ' ' * 111 + tfay
    doc.line(f"total {tfay}")

def analysis_income_by_bond(doc: PDFDocument, portfolio) -> None:
    doc.add_page()
    analysis_heading(doc, "Yearly Income By Bond", 12)
    for item in portfolio.portfolio_items:
        coupon_matrix = item.coupon_matrix
        analysis_heading(doc, f"{item.description}", 12)
        print_bond_detail_summary(doc, item)
        print_income_matrix(doc, coupon_matrix)

def print_bond_heading(doc: PDFDocument) -> None:
    line = ""
    line_length = 0
    for field in _bond_line:
        title = field[0]
        if title == "avail" and not K.SHOW_AVAILABILITY: continue
        length = field[1]
        line_length += length
        line += title.ljust(length)
    doc.line(line)
    doc.line(line_length * "-")

def analysis_heading(doc: PDFDocument, heading: str, font_size: int) -> None:
    doc.set_font('Courier', 'B', font_size)
    doc.pdf.cell(240, 10, heading, 0, 0, 'C')
    doc.ln()
    doc.reset_font()


class PortfolioReporter:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.cwd = os.getcwd()

    # def print_report(self, detail=True, title=None) -> None:
    #     """ Print the Portfolio Analysis Report
    #      :param detail: True to print the detailed analysis, False to print the brief analysis
    #      :param title: the title to use for the report
    #         creates a pdf file and launches it in the browser
    #         the file is a scratch file in the working directory and
    #         will be overwritten each time the option is run
    #      """
    #     # if there's no first argument, use the portfolio title
    #     theTitle = title if title is not None else self.portfolio.title
    #     file_path = os.path.join(self.cwd, "analysis.pdf")
    #
    #     doc = PDFDocument(file_path)
    #     self.make_analysis_report(pdf_document=doc, title=theTitle, detail=detail)
    #     doc.output_document()
    #     launch_report(file_path)

    def make_analysis_report(self, pdf_document=None, title=None, detail=False) -> None:
        pdf_document.add_page()
        analysis_heading(pdf_document, "Bond Portfolio Analysis", 14)
        if title is not None:
            today = datetime.datetime.now().strftime("%Y_%m_%d")
            analysis_heading(pdf_document, f"{title} Portfolio on {today}", 12)
        self.analysis_summary_lines(pdf_document)
        self.analysis_portfolio_contents(pdf_document)
        self.analysis_yearly_income_table(pdf_document)
        if detail:
            analysis_income_by_bond(pdf_document, self.portfolio)

    def analysis_summary_lines(self, doc: PDFDocument) -> None:
        print_line = f"                Yearly Income  {format_dollars(self.portfolio.yearly_income)}"
        print_line += f"  Total Cost  {format_dollars(self.portfolio.total_invested)}"
        print_line += f"  Total Interest {format_dollars(self.portfolio.total_interest)}"
        print_line += f"  total_LOP  {format_dollars(self.portfolio.total_LOP)}"
        doc.line(print_line)
        if K.IS_TAXABLE:
            print_line = f"                Yearly Income*  {format_dollars(self.portfolio.yearly_income * (1.0 - K.TAX_RATE))}"
            print_line += f"   Profit*  {format_dollars(self.portfolio.total_profit)}"
        else:
            print_line = f"                Profit  {format_dollars(self.portfolio.total_profit)}"
        print_line += f"   Par value  {format_dollars(self.portfolio.total_par_value)}"
        doc.line(print_line)
        doc.ln()

    def analysis_portfolio_contents(self, doc: PDFDocument) -> None:
        # bond detail section when printing the portfolio. Quantity not applied. each
        # metric is calculated per 1000 bonds

        print_bond_heading(doc)
        item: PortfolioItem
        for item in self.portfolio.portfolio_items:
            line = ""
            for field in _bond_line:
                if field[0] == "avail" and not K.SHOW_AVAILABILITY: continue
                length = field[1]
                data = str(field[2](item))  # execute lambda function
                data = data[:length - 1]  # truncate to length - 1
                line += data.ljust(length)  # print it left justified
            doc.line(line)
            if K.SHOW_PER_1000_DETAIL:
                line = "   per 1000 =>"
                line += f" profit* = {format_dollars(item.profit)}"
                line += f"  interest = {format_dollars(item.total_interest(1000))}"
                line += f"  return = {format_dollars(item.total_return_pretax)}"
                line += f"  return* = {format_dollars(item.total_return_posttax)}"
                line += f"  income/yr = {format_dollars(item.yearly_income)}"
                doc.line(line)

    def analysis_yearly_income_table(self, doc: PDFDocument) -> None:
        sum_of_coupons = self.portfolio.get_combined_income_matrix()
        doc.ln()
        analysis_heading(doc, "Yearly Income", 12)
        print_income_matrix(doc, sum_of_coupons)
