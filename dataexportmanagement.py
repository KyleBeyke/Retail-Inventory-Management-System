import csv
import pandas as pd
import os
from datetime import datetime

class DataExportManagement:
    """
    A class to handle exporting data from the system to various file formats,
    such as CSV, Excel, and PDF.
    """

    def __init__(self, export_dir="exports"):
        """
        Initialize the DataExportManagement class.

        :param export_dir: Directory where exported files will be saved.
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def export_to_csv(self, data, file_name):
        """
        Export data to a CSV file.

        :param data: A list of dictionaries or a list of tuples containing the data to export.
        :param file_name: Name of the CSV file to save.
        :return: Full path of the exported CSV file.
        """
        try:
            file_path = os.path.join(self.export_dir, f"{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            keys = data[0].keys() if isinstance(data[0], dict) else None

            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                if keys:
                    writer.writerow(keys)  # Write header row
                    for row in data:
                        writer.writerow(row.values())
                else:
                    for row in data:
                        writer.writerow(row)  # Write rows for tuple data

            return file_path
        except Exception as e:
            raise Exception(f"Error exporting to CSV: {e}")

    def export_to_excel(self, data, file_name):
        """
        Export data to an Excel file.

        :param data: A list of dictionaries or a pandas DataFrame containing the data to export.
        :param file_name: Name of the Excel file to save.
        :return: Full path of the exported Excel file.
        """
        try:
            file_path = os.path.join(self.export_dir, f"{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

            if isinstance(data, pd.DataFrame):
                data.to_excel(file_path, index=False)
            elif isinstance(data, list) and data:
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
            else:
                raise ValueError("Invalid data format. Expected a DataFrame or a list of dictionaries.")

            return file_path
        except Exception as e:
            raise Exception(f"Error exporting to Excel: {e}")

    def export_to_pdf(self, data, file_name):
        """
        Export data to a PDF file.

        :param data: A pandas DataFrame containing the data to export.
        :param file_name: Name of the PDF file to save.
        :return: Full path of the exported PDF file.
        """
        try:
            from fpdf import FPDF

            if not isinstance(data, pd.DataFrame):
                raise ValueError("Invalid data format. Expected a pandas DataFrame.")

            file_path = os.path.join(self.export_dir, f"{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add table header
            for col in data.columns:
                pdf.cell(40, 10, col, border=1)
            pdf.ln()

            # Add table rows
            for _, row in data.iterrows():
                for cell in row:
                    pdf.cell(40, 10, str(cell), border=1)
                pdf.ln()

            pdf.output(file_path)
            return file_path
        except Exception as e:
            raise Exception(f"Error exporting to PDF: {e}")

    def log_export_action(self, file_path):
        """
        Log export action details.

        :param file_path: Path of the exported file.
        """
        print(f"Data exported to: {file_path}")

# Example Usage
if __name__ == "__main__":
    data_export = DataExportManagement()

    # Example data
    example_data = [
        {"Product": "Shirt", "Price": 20, "Stock": 50},
        {"Product": "Jeans", "Price": 40, "Stock": 30},
    ]

    # Export to CSV
    csv_path = data_export.export_to_csv(example_data, "inventory_report")
    data_export.log_export_action(csv_path)

    # Export to Excel
    excel_path = data_export.export_to_excel(example_data, "inventory_report")
    data_export.log_export_action(excel_path)

    # Export to PDF
    df = pd.DataFrame(example_data)
    pdf_path = data_export.export_to_pdf(df, "inventory_report")
    data_export.log_export_action(pdf_path)
