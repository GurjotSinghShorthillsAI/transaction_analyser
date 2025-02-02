import pandas as pd
import re

# 1. List of all valid sections you want to detect:
SECTIONS = ["194C", "194JA", "194JB", "194Q", "194A", "194IA", "194IB", "194H", "NO TDS"]

def remove_all_punctuation_and_spaces(text: str) -> str:

    text = text.upper()
    # Replace any sequence of non-alphanumeric characters (punctuation, spaces, etc.) with nothing
    text = re.sub(r'[^A-Z0-9]+', '', text)
    return text

def extract_sections(section_str):

    if not isinstance(section_str, str):
        return []
    
    # Normalized string with all punctuation/spaces removed, uppercase
    cleaned_str = remove_all_punctuation_and_spaces(section_str)
    
    found_sections = []
    for sec in SECTIONS:
        if sec == "NO TDS":
            if "NOTDS" in cleaned_str:
                found_sections.append(sec)
        else:
            # Remove punctuation/spaces from the section name itself, just in case
            clean_sec = remove_all_punctuation_and_spaces(sec)
            if clean_sec in cleaned_str:
                found_sections.append(sec)
    
    return found_sections

def main():

    # Suppose you have an Excel file named 'my_transactions.xlsx'
    # with columns: "Transaction No", "Original Answer", etc.
    
    # 1. Read your data
    df_file = pd.read_excel("sample_100_transactions.xlsx")
    
    # 2. Create the "Original Sections List" column
    df_file["Original Sections List"] = df_file["Original Answer"].apply(extract_sections)
    
    # 3. (Optionally) write the results to a new Excel or CSV
    df_file.to_excel("original_sections_list_output.xlsx", index=False)
    
    print("=== Data from Excel file (with extracted sections) ===")
    print(df_file)


if __name__ == "__main__":
    main()
