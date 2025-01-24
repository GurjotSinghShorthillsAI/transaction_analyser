import pandas as pd
import os

class TransactionLogger:
    def __init__(self, file_name="final-results-gpt4o.xlsx"):
        self.file_name = file_name
        self.data = []  # Use a list to store rows of data
        self.headers = [
            "Transaction No", "Transaction summary", "High-Level Keywords", "Low-Level Keywords", 
            "Entities Retrieved", "Relations Retrieved", "Chunks Retrieved", "Final Prompt", 
            "Mode", "Retrieved Section", "Original Answer"
        ]

        # Check if the file exists and load data
        if os.path.exists(self.file_name):
            self.existing_data = pd.read_excel(self.file_name)
        else:
            # Initialize an empty DataFrame with headers
            self.existing_data = pd.DataFrame(columns=self.headers)

    # def update_transaction(self, transaction_no, **kwargs):
    #     """
    #     Add a new row to the data.
    #     """
    #     row = {"Transaction No": transaction_no}
    #     row.update(kwargs)
    #     self.data.append(row)
    def update_transaction(self, transaction_no, mode, **kwargs):
        """
        Update or add a new row to the data based on the composite key of Transaction No and Mode.
        """
        row = {"Transaction No": transaction_no, "Mode": mode}
        row.update(kwargs)
        # Debugging output
        print("Row to be updated/added:", row)
        # Check if the row already exists
        matching_rows = [(index, r) for index, r in enumerate(self.data)
                         if r["Transaction No"] == transaction_no and r["Mode"] == mode]
        
        if matching_rows:
            # Update the existing row
            index, existing_row = matching_rows[0]  # Assuming only one match should be found
            existing_row.update(row)
            self.data[index] = existing_row
            print(f"Updated row for Transaction No = {transaction_no} and Mode = {mode}.")
        else:
            # Add new row
            self.data.append(row)
            print(f"Added new row for Transaction No = {transaction_no} and Mode = {mode}.")

    def save_to_excel(self):
        """
        Save all logged transactions to an Excel file, appending to existing data.
        """
        # Convert current data to a DataFrame
        new_df = pd.DataFrame(self.data, columns=self.headers)

        # Append to existing data
        updated_df = pd.concat([self.existing_data, new_df], ignore_index=True)

        # Save the updated data to the Excel file
        updated_df.to_excel(self.file_name, index=False)

        # Clear the in-memory data after saving
        self.data.clear()




# Create a shared logger instance
mylogger = TransactionLogger()
