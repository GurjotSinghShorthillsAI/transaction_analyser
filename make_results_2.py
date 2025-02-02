import pandas as pd
import re

# Load the Excel file
df = pd.read_excel('final-results-gpt4o.xlsx')

# Select only the necessary columns
df = df[['Transaction No', 'Mode', 'Retrieved Section', 'Original Answer']]

# List of all valid sections
sections = ["194C", "194JA", "194JB", "194Q", "194A", "194IA", "194IB", "194H", "NO TDS"]

def remove_all_punctuation_and_spaces(text: str) -> str:
    """
    Removes all punctuation and whitespace characters from the text.
    Returns the cleaned string in uppercase.
    """
    # Convert to uppercase
    text = text.upper()
    # Replace any sequence of non-alphanumeric characters with nothing
    text = re.sub(r'[^A-Z0-9]+', '', text)
    return text

def extract_sections(section_str):
    """
    Extract recognized TDS sections from the given string.
    - Handles non-string inputs by returning an empty list.
    - Special handling for 'NO TDS' since removing spaces/punctuation turns it into 'NOTDS'.
    """
    if not isinstance(section_str, str):
        return []
    
    # Normalized string with all punctuation/spaces removed, uppercase
    cleaned_str = remove_all_punctuation_and_spaces(section_str)
    
    found_sections = []
    
    for sec in sections:
        if sec == "NO TDS":
            # Check if "NOTDS" is in the cleaned string
            if "NOTDS" in cleaned_str:
                found_sections.append(sec)
        else:
            # Remove punctuation/spaces from the section itself just in case
            clean_sec = remove_all_punctuation_and_spaces(sec)
            if clean_sec in cleaned_str:
                found_sections.append(sec)
    
    return found_sections

def match_sections(retrieved, original):
    """
    1. Extract both retrieved sections and original sections.
    2. If the original answer includes 'doubt' or 
       'can't find any section' (in any punctuation form), return True.
    3. Otherwise, check if at least one retrieved section appears
       in the original section list.
    """
    retrieved_sections = extract_sections(retrieved)
    original_sections = extract_sections(original)
    
    # We'll use the cleaned original string to detect "doubt" or "cant find any section"
    cleaned_original = remove_all_punctuation_and_spaces(original) if isinstance(original, str) else ""
    
    # If the original has "DOUBT" or "CANTFINDANYSECTION", match is True
    if "DOUBT" in cleaned_original or "CANTFINDANYSECTION" in cleaned_original:
        return retrieved_sections, original_sections, True
    
    # Otherwise, check if any retrieved section is also in the original section list
    is_match = any(section in original_sections for section in retrieved_sections)
    
    return retrieved_sections, original_sections, is_match

# Apply the matching function and create three columns in the DataFrame
df[['Retrieved Sections List', 'Original Sections List', 'Match']] = df.apply(
    lambda x: pd.Series(match_sections(x['Retrieved Section'], x['Original Answer'])), axis=1
)

# Function to calculate precision, recall, and accuracy
def calculate_metrics(data):
    TP = sum(data['Match'])   # True positives are all matches
    FP = len(data) - TP       # False positives are the non-matches
    FN = 0  # Assuming no false negatives based on the stated logic
    precision = (TP / (TP + FP) if (TP + FP) > 0 else 0) * 100
    recall = (TP / (TP + FN) if (TP + FN) > 0 else 0) * 100  # Recall is 100% if FN is 0
    accuracy = (TP / len(data) if len(data) > 0 else 0) * 100
    return precision, recall, accuracy

# Calculate metrics for each mode across all transactions
results = []
for mode in df['Mode'].unique():
    mode_data = df[df['Mode'] == mode]
    precision, recall, accuracy = calculate_metrics(mode_data)
    results.append({
        'Mode': mode,
        'Precision': precision,
        'Recall': recall,
        'Accuracy': accuracy
    })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Optionally save results and detailed section analysis back to Excel
with pd.ExcelWriter('accuracy-metrics-gpt-4o.xlsx') as writer:
    df.to_excel(writer, sheet_name='Detailed Section Analysis', index=False)
    results_df.to_excel(writer, sheet_name='Summary Results', index=False)

# Display the results summary
print(results_df)
