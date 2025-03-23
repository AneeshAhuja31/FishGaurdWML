import csv
import random

def shuffle_csv(file_path):
    """Shuffles all rows in a CSV file and writes them back in random order."""
    # Read all rows from the CSV file
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        reader = list(csv.reader(csv_file))
    
    # Shuffle the rows
    random.shuffle(reader)
    
    # Write the shuffled rows back to the same file
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(reader)

# Path to your CSV file
csv_file_path = r'C:\Users\HP\OneDrive\Desktop\FISHGUARD\ml\data\processed\train_urls.csv'

# Shuffle the rows in the CSV file
shuffle_csv(csv_file_path)

print(f"The rows in {csv_file_path} have been shuffled successfully!")
