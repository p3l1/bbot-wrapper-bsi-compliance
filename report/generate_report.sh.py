import json
import argparse
import logging
import os
from pathlib import Path
from typing import Dict, List, Union

import jinja2
import pypandoc
from fpdf import FPDF

LATEX_JINJA_ENV = jinja2.Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath('.'))
)


class BSIComplianceReport:

    def __init__(self, template_path: Path, output_path: Path, data: List):

        self.logger = self._setup_logger()
        self.template_path = template_path
        self.output_path = output_path
        self.data = data

        templated_latex_path = self._template_data()
        if not templated_latex_path:
            self.logger.error(f"Error while templating Jinja2 LaTeX template at {template_path.absolute()}")
            exit(1)

        self._render_pdf(templated_latex_path)

    def _setup_logger(self, log_level=logging.INFO) -> logging.Logger:
        # Create a logger
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(log_level)

        # Create a stream handler (console) and set the log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Set the formatter for the handlers
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(console_handler)

        return logger

    def _template_data(self) -> Union[bool, Path]:

        # TODO: Read input data and assign it to variables for readablity

        header = ['Num', 'Date', 'Ticker']
        data = [[1, 2, 3], [4, 'STR', 'Test'], [5, 6, 'Ticker']]

        template = LATEX_JINJA_ENV.get_template('templates/report.tex.j2')
        renderer_template = template.render(dict_map=data, header=header)

        # Write rendered LaTeX to file
        latex_report_path = Path("output/report.tex").absolute()
        try:
            with open(latex_report_path, 'w') as latex_report:
                latex_report.write(renderer_template)
            return latex_report_path
        except OSError as e:
            self.logger.error("Error while writing file to disk!")
            self.logger.exception(e)
            return False

    def _render_pdf(self, templated_latex_path: Path) -> Union[bool, Path]:
        # Convert LaTeX file to PDF
        try:
            pypandoc.convert_file(templated_latex_path, 'latex', outputfile=self.output_path)

            # Delete templated LaTeX file again
            os.unlink(templated_latex_path)
            return self.output_path
        except RuntimeError as e:
            self.logger.error("Error while converting file from LaTeX to PDF")
            self.logger.exception(e)
            return False
        except OSError as e:
            self.logger.error("Pandoc binary not found!")
            self.logger.exception(e)
        return False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process BBOT data and create a PDF report")
    parser.add_argument("-j", "--ndjson", type=str, help="Path to the output.ndjson",
                        metavar="<PATH>", default=Path("../scans/bsi_compliance/output.ndjson"))
    parser.add_argument("-o", "--output", type=str, help="Path where the report should be exported to",
                        metavar="<PATH>", default=Path("output/report.pdf"))
    parser.add_argument("-t", "--template", type=str, help="Path to the report.tex.j2",
                        metavar="<PATH>", default=Path("templates/report.tex.j2"))

    args = parser.parse_args()

    # Read NDJSON file
    with open(args.ndjson, "r") as file:
        lines = file.readlines()

    report_data = []
    for line in lines:
        try:
            entry = json.loads(line)
            report_data.append(entry)
        except json.JSONDecodeError:
            print("Error decoding JSON:", line)

    args_template_path = Path(args.template).resolve()
    args_output_path = Path(args.output).resolve()

    report = BSIComplianceReport(args_template_path, args_output_path, report_data)