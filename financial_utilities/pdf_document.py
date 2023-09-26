from fpdf import FPDF


class PDFDocument:

    def __init__(self, report_file_path) -> None:
        super().__init__()
        self._report_file_path = report_file_path
        self._pdf: FPDF = FPDF(orientation="L", format="Letter")
        # self._pdf.add_page()
        self._pdf.set_font('Courier', '', 9)
        self._pdf.set_text_color(20, 20, 20)

    @property
    def pdf(self): return self._pdf

    def set_font(self, tf, b, h): self.pdf.set_font(tf, b, h)

    def reset_color(self):
        self._pdf.set_text_color(20, 20, 20)

    def reset_font(self):
        self._pdf.set_font('Courier', '', 9)

    def set_red(self):
        self._pdf.set_text_color(255, 0, 0)
        self._pdf.set_font('Courier', 'BI', 9)

    def set_normal(self):
        self.reset_color()
        self.reset_font()

    def add_page(self):
        self._pdf.add_page()

    def ln(self): self._pdf.ln()

    def cell(self, width: int, height: int, text: str):
        self._pdf.cell(width, height, text)

    def line(self, text):
        self._pdf.cell(0, 5, text)
        self._pdf.ln()

    def output_document(self):
        self._pdf.output(self._report_file_path, 'F')
