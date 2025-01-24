import pandas as pd

# Load the Excel file
df = pd.read_excel('final-results-gpt4o.xlsx')

# Select only the necessary columns
df = df[['Transaction No', 'Mode', 'Retrieved Section', 'Original Answer']]

# Normalize the data by removing spaces and converting to uppercase for consistent comparison
df['Retrieved Section'] = df['Retrieved Section'].str.replace(' ', '').str.upper()
df['Original Answer'] = df['Original Answer'].str.replace(' ', '').str.upper()

# Function to split sections and check for matches
def match_sections(retrieved, original):
    # Splitting the retrieved section to correctly identify sections even without spaces
    parts = retrieved.split('SECTION2:')
    # Extract "Section 1" correctly by finding where it starts and ends
    section_1 = parts[0].split('SECTION1:')[1][:4] if 'SECTION1:' in parts[0] else ''
    section_2 = parts[1][:4] if len(parts) > 1 else ''  # Extracting the first four characters of Section 2 if it exists
    
    # Check if either section matches the original
    return original in [section_1, section_2]

# Apply the matching function to create a new column 'Match'
df['Match'] = df.apply(lambda x: match_sections(x['Retrieved Section'], x['Original Answer']), axis=1)

# Function to calculate precision, recall, and accuracy
def calculate_metrics(data):
    TP = sum(data['Match'])  # True positives are all matches
    FP = len(data) - TP       # False positives are the non-matches
    FN = 0  # Assuming no false negatives as explained previously.
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

# Display the results
print(results_df)
# Optionally save back to Excel
results_df.to_excel('accuracy-metrics-gpt-4o.xlsx', index=False)
