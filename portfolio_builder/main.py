# This is the main program for the portfolio builder.
from portfolio_builder.portfolio_builder_engine import PortfolioBuilderEngine as PBE
from portfolio_builder.portfolio_builder_engine import InputSyntaxError
import json



def capture_actions() -> str:
    while True:
        print("\nenter action: ", end="")
        action = input()
        if len(action) > 0: return action

def item_tostr(item) -> str:
    return str(item)


if __name__ == '__main__':

    """
       Portfolio Json Format
        {
            "title": "Inome Portfolio 10/21/2023",
            "items": [
                {"cusip": "22550L2M2", "description": "CREDIT SUISSE AG NEWYORK MTN", ...},
                {"cusip": "338915AM3", "description": "BANK AMERICA CORP BOND", ...}
             ]
        }
    """

    """
    item1 = {"cusip": "22550L2M2", "description": "CREDIT SUISSE AG NEWYORK MTN"}
    item2 = {"cusip": "338915AM3", "description": "BANK AMERICA CORP BOND"}
    portfolio = {"title": "Inome Portfolio 10/21/2023", "items": [item1, item2]}
    print(json.dumps(portfolio, indent=4))

    quit(0)
    """



    # create the portfolio builder engine
    engine = PBE()
    # process input program lines until quit is entered
    should_run = True
    while should_run:
        actions = capture_actions()
        try:
            engine.process_actions(actions)
        except InputSyntaxError as se:
            print(se)
            continue
        engine.show_status()

