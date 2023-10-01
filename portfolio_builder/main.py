import sys

# sys.path.append("D:/Development/FidelityPrograms/financial_utilities")
from financial_utilities.portfolio_builder_engine import PortfolioBuilderEngine as PBE
from financial_utilities.portfolio_builder_engine import InputSyntaxError


def capture_actions() -> str:
    while True:
        print("\nenter action: ", end="")
        action = input()
        if len(action) > 0: return action


if __name__ == '__main__':

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

