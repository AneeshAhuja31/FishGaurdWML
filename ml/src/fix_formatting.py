import csv

def fix_csv_format(file_path):
    """Removes extra quotation marks from rows in a CSV file."""
    # Read the existing rows from the CSV file
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        rows = []
        for row in reader:
            # Remove any unintended quotes around the content
            fixed_row = [cell.strip('"') for cell in row]
            rows.append(fixed_row)

    # Write back the corrected rows to the same file
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)

# Specify the path to your CSV file
csv_file_path = r"C:\Users\HP\OneDrive\Desktop\FISHGUARD\ml\data\processed\train_urls.csv"

# Fix the formatting of the CSV file
fix_csv_format(csv_file_path)

print(f"The formatting issues in {csv_file_path} have been fixed!")
