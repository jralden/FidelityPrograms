from typing import *
import sys, os, datetime, csv, tkinter, tkinter.simpledialog
from enum import Enum


import financial_utilities.constants as K
from  financial_utilities.portfolio import Portfolio, PortfolioItem
from  financial_utilities.pdf_document import PDFDocument
from  financial_utilities.format import Format as F

cwd = os.getcwd()
data_file_path = os.path.join(cwd, "data")
K.SHOW_AVAILABILITY = False


def clean_int(int_string: str) -> int:
    return int(int_string.replace(",", ""))

def clean_float(float_string: str) -> float:
    return float(float_string.replace(",", ""))

def launch_report(report_file_path) -> None:
    # launch the pdf file for the report in the browser
    os.system(f"start {report_file_path}")

def save_report(portfolio: Portfolio, title=None, detail=True) -> None:
    theTitle = title if title is not None else portfolio.title
    output_file_path = os.path.join(data_file_path, f"{theTitle}.pdf")
    doc = PDFDocument(output_file_path)
    portfolio.make_analysis_report(doc, theTitle, detail)
    doc.output_document()
    launch_report(output_file_path)

def load_csv_file(file_path: str) -> list[list[str]]:
    """
       Reads a csv file and returns a list of bond
       property lists that can be added to a portfolio
           :param file_path: location of .csv file
           :return:    list of property lists
    """
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        theList = list(csv_reader)
        theList.pop(0)  # remove the index row
        theList.pop(0)  # remove the header
        csv_file.close()
    return theList

def process_account(account_name: str)-> Portfolio:
    file_path = os.path.join(data_file_path, f"{account_name}.csv")
    portfolio = Portfolio()
    portfolio.title = account_name
    items = load_csv_file(file_path)
    item: List[str]
    for item in items:
        quantity = int(clean_int(item[6]) / 1000)
        purchase_date = item[7]
        portfolio_item = PortfolioItem.portfolio_item_from_csv(item, quantity, purchase_date)
        portfolio.add_item(portfolio_item)

    save_report(portfolio, title=portfolio.title, detail=True)
    return portfolio

def main() -> None:
    K.IS_TAXABLE = False
    process_account("marys_IRA")
    process_account("johns_IRA")
    K.IS_TAXABLE = True
    process_account("joint_account")


if __name__ == '__main__':
    main()
