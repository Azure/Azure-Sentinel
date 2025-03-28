import os
import glob
import yaml
from collections import Counter

def extract_ids(data):
    """
    Recursively traverse the data structure to collect all values for the key 'id'.
    """
    ids = []
    if isinstance(data, dict):
        for key, value in data.items():
            # print(key)
            if key == 'id':
                ids.append(value)

            else:
                ids.extend(extract_ids(value))
                
    elif isinstance(data, list):
        for item in data:
            ids.extend(extract_ids(item))
    return ids

def main(folder_path):
    # Find all YAML files in the folder (including .yaml and .yml)
    yaml_files = glob.glob(os.path.join(folder_path, '*.yaml'))
    yaml_files.extend(glob.glob(os.path.join(folder_path, '*.yml')))

    all_ids = []
    for filepath in yaml_files:
        try:
            with open(filepath, 'r') as file:
                content = yaml.safe_load(file)
                if content is not None:
                    ids = extract_ids(content)
                    all_ids.extend(ids)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # Count occurrences of each id
    id_counts = Counter(all_ids)

    # Filter out ids that appear more than once
    duplicates = {id_value: count for id_value, count in id_counts.items() if count > 1}

    if duplicates:
        print("Duplicate IDs found:")
        for id_value, count in duplicates.items():
            print(f"ID '{id_value}' appears {count} times.")
    else:
        print("No duplicate IDs found.")

if __name__ == '__main__':
    # Replace 'your_folder_path' with the path to the folder containing YAML files.
    folder_path = './'
    main(folder_path)
