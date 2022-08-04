

class Format:

    @classmethod
    def format_dollars(cls, num) -> str: return "${:,.2f}".format(num)

    @classmethod
    def format_float(cls, num) -> str: return "{:,.2f}".format(num)

    @classmethod
    def format_rank(cls, num: int) -> str: return str(num).center(4)
