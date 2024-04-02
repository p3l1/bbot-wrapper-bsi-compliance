import json
import argparse
import logging
import os
import subprocess
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Union

import jinja2
import pypandoc

LATEX_JINJA_ENV = jinja2.Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath('.'))
)


class BSIComplianceReport:

    def __init__(self, template_path: Path, output_path: Path, data: List[Dict], is_debug: bool,
                 disable_scan_id_checking: bool = False, use_pdflatex: bool = True):

        self.log_level = logging.INFO
        if is_debug:
            self.log_level = logging.DEBUG

        self.logger = self._setup_logger(self.log_level)

        self.disable_scan_id_checking = disable_scan_id_checking
        self.use_pdflatex = use_pdflatex
        self.template_path = template_path
        self.output_path = output_path
        self.data = data

        if not self._validate_data():
            self.logger.error(f"The given output.ndjson contains data from more than one bbot scan.")

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

    def _validate_data(self) -> bool:
        """
        Check if the input only contains events from one unique SCAN event. Can be disabled via CLI flag.
        :returns: True, if only one SCAN event is found, otherwise False.
        """

        if self.disable_scan_id_checking:
            # Check is disabled
            self.logger.warning("BBOT scan id checking is disabled. Report may contain results from multiple scans.")
            return True

        scan = ""
        for event in self.data:
            if not scan:
                scan = event.get("scan")
                continue

            if scan != event.get("scan"):
                return False

        return True

    def _template_data(self) -> Union[bool, Path]:

        report_template = LATEX_JINJA_ENV.get_template(str(Path("templates/report.tex.j2")))

        self.scan_id = {e.get("scan") for e in self.data if self.disable_scan_id_checking}
        if not self.scan_id:
            self.scan_id = {e.get("scan") for e in self.data}
        else:
            self.logger.warning("Detected multiple bbot scan ids. Report is based on data from multiple scans!")

        self.timestamp = self.data[0].get("timestamp")
        self.timestamp = datetime.fromtimestamp(float(self.timestamp), UTC)

        # Format datetime object to German date format
        german_date_format = "%d.%m.%Y"
        self.timestamp = self.timestamp.strftime(german_date_format)

        self.tls_compliance_events = [e.get("data") for e in self.data if "bsi_compliance_tls" == e.get("module")]
        self.ssh_compliance_events = [e.get("data") for e in self.data if "bsi_compliance_ssh" == e.get("module")]
        self.ipsec_compliance_events = [e.get("data") for e in self.data if "bsi_compliance_ipsec" == e.get("module")]

        # Example BEGIN
        header = ['Num', 'Date', 'Ticker']
        data = [[1, 2, 3], [4, 'STR', 'Test'], [5, 6, 'Ticker2']]
        # Example END

        renderer_template = report_template.render(scan_ids=self.scan_id,
                                                   timestamp=self.timestamp,
                                                   tls_compliance_events=self.tls_compliance_events,
                                                   ssh_compliance_events=self.ssh_compliance_events,
                                                   ipsec_compliance_events=self.ipsec_compliance_events,
                                                   dict_map=data,
                                                   header=header)

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

        if self.use_pdflatex:
            command = ["pdflatex", f"-output-directory={self.output_path.parent.absolute()}", str(templated_latex_path.absolute())]
            subprocess.run(command)
            return self.output_path

        try:
            # Convert LaTeX file to PDF
            pypandoc.convert_file(templated_latex_path, 'latex', outputfile=self.output_path)

            # Delete templated LaTeX file again
            if self.log_level > logging.DEBUG:
                os.unlink(templated_latex_path)

            return self.output_path

        except RuntimeError as e:
            self.logger.error("Error while converting file from LaTeX to PDF")
            self.logger.exception(e)
        except OSError as e:
            self.logger.error("Pandoc binary not found!")
            self.logger.exception(e)

        return False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process BBOT output.ndjson and create PDF report based on LaTeX "
                                                 "Jinja2 template")
    parser.add_argument("-j", "--ndjson", type=str, help="Path to the output.ndjson",
                        metavar="<PATH>", default=Path("../scans/bsi_compliance/output.ndjson"))
    parser.add_argument("-o", "--output", type=str, help="Path where the report should be exported to",
                        metavar="<PATH>", default=Path("output/report.pdf"))
    parser.add_argument("-t", "--template", type=str, help="Path to the report.tex.j2",
                        metavar="<PATH>", default=Path("templates/report.tex.j2"))
    parser.add_argument("-d", "--debug", help="Enable debug logging, disable deletion of templated "
                                              "LaTeX file", action='store_true')
    parser.add_argument("--disable-scan-id-checking", help="Prevents generation "
                        "of reports based on multiple bbot scans. Default: True",
                        action='store_true')
    parser.add_argument("-p", "--use-pdflatex", help="Create PDF using pdflatex instead of pypandoc ",
                        action='store_true')

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

    report = BSIComplianceReport(args_template_path,
                                 args_output_path,
                                 report_data,
                                 args.debug,
                                 args.disable_scan_id_checking,
                                 args.use_pdflatex)
