import json
import argparse
from fpdf import FPDF


def create_pdf(data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Assuming 'data' is a list of dictionaries
    for entry in data:
        # Extract relevant information from the entry and add to the PDF
        pdf.cell(200, 10, txt=f"Type: {entry.get('type')}", ln=True)
        pdf.cell(200, 10, txt=f"Other Key: {entry.get('other_key')}", ln=True)
        # Add more cells as needed for other key-value pairs

    pdf.output(output_path)


def main():
    parser = argparse.ArgumentParser(description="Process BBOT data and create a PDF report")
    parser.add_argument("-j", "--ndjson", type=str, help="Path to the output.ndjson", required=True, metavar="<PATH>")
    parser.add_argument("-o", "--output", type=str, help="Path where the report should be exported to", required=True, metavar="<PATH>")

    args = parser.parse_args()

    # Read NDJSON file
    with open(args.ndjson, "r") as file:
        lines = file.readlines()

    filtered_data = []
    for line in lines:
        try:
            entry = json.loads(line)
            filtered_data.append(entry)
        except json.JSONDecodeError:
            print("Error decoding JSON:", line)

    # Create PDF
    create_pdf(filtered_data, args.output)


if __name__ == "__main__":
    main()
