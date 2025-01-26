import os
import logging
import asyncio
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from openai import AzureOpenAI
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from langchain.prompts import PromptTemplate
from transaction_logger import mylogger

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")


class TransactionApp:
    """
    This class encapsulates the entire transaction processing application in an OOP manner.
    It includes:
      - Token counters
      - LLM model functionality
      - Embedding functionality
      - Main processing flow
    """

    def __init__(self):
        """
        Initialize the application with counters for input and output tokens.
        """
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    async def llm_model_func(
        self,
        prompt,
        system_prompt=None,
        history_messages=[],
        keyword_extraction=False,
        **kwargs
    ) -> str:
        """
        Asynchronous function to call the AzureOpenAI chat completion endpoint. 
        It builds the messages list from system and user prompts, logs token usage, 
        and updates the global (class-level) counters.
        """
        # Create a client for AzureOpenAI
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        # Build the messages list for the conversation
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})

        # Call the LLM
        chat_completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            top_p=kwargs.get("top_p", 1),
            n=kwargs.get("n", 1),
        )

        # Retrieve token usage info from the response
        usage = chat_completion.usage  
        input_tokens = usage.prompt_tokens      # Tokens in the input
        output_tokens = usage.completion_tokens # Tokens in the output
        total_tokens = usage.total_tokens       # Total tokens (input + output)

        # Update class counters
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Log token usage
        logging.info(f"Input Tokens: {input_tokens}, Output Tokens: {output_tokens}, Total Tokens: {total_tokens}")

        return chat_completion.choices[0].message.content

    async def embedding_func(self, texts: list[str]) -> np.ndarray:
        """
        Asynchronous function to generate text embeddings using SentenceTransformer.
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings

    def run(self):
        """
        The main entry point for the transaction processing:
          1. Reads and processes text chunks from a file.
          2. Configures LightRAG for knowledge retrieval.
          3. Reads Excel data, extracts relevant columns, and processes each transaction.
          4. Uses both LLM for summarization and LightRAG for TDS section classification.
          5. Logs the results and token usage.
        """
        # Read file contents
        file_path = "final_docs.txt"
        with open(file_path, 'r') as file:
            text = file.read()

        # Split text into chunks
        chunks = text.split('///')
        chunks = [chunk.strip() for chunk in chunks]

        # Step 2: Configure LightRAG
        WORKING_DIR = "./final_database"
        if not os.path.exists(WORKING_DIR):
            os.mkdir(WORKING_DIR)

        # Initialize LightRAG with the LLM model function and embedding function
        # Note: We wrap the instance methods in lambdas or call them directly in asyncio
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=self.llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=384,
                max_token_size=8192,
                func=self.embedding_func,
            )
        )

        # Insert the custom chunks into LightRAG
        rag.insert_custom_chunks(text, chunks)

        print("########################## Tokens used to create knowledge graph: #####################################")
        print("Total Input Tokens:", self.total_input_tokens)
        print("Total Output Tokens:", self.total_output_tokens)

        # Reset counters before queries
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Read Excel data
        data = pd.read_excel("sample_wht_100_data.xlsx")
        columns_to_extract = [
            'Sr No', 
            'PO Line Item Description', 
            'Line Description', 
            'Expense GL Description', 
            'Invoice Description',
            'Section as required in TDS Return'     
        ]
        filtered_data = data[columns_to_extract]

        # Convert each row into a transaction dictionary
        transactions_list = []
        for _, row in filtered_data.iterrows():
            def clean_cell_value(val):
                """
                Clean each cell by removing unwanted characters and handling missing values.
                """
                if pd.isna(val):
                    return ""
                if isinstance(val, str):
                    val = val.replace('\xa0', ' ').strip()
                    return val if val else ""
                return str(val)

            po_desc = clean_cell_value(row["PO Line Item Description"])
            line_desc = clean_cell_value(row["Line Description"])
            gl_desc = clean_cell_value(row["Expense GL Description"])
            invoice_desc = clean_cell_value(row["Invoice Description"])
            section = clean_cell_value(row['Section as required in TDS Return'])

            transaction = {
                "po_desc": po_desc,
                "line_desc": line_desc,
                "gl_desc": gl_desc,
                "invoice_desc": invoice_desc,
                "section": section
            }
            transactions_list.append(transaction)

        # Process each transaction
        hybrid_results = []
        for i, transaction in enumerate(transactions_list):
            # Create a prompt template for transaction interpretation
            prompt = PromptTemplate(
                input_variables=["po_desc", "line_desc", "gl_desc", "invoice_desc"],
                template="""
                You are provided with details of a transaction including descriptions from various fields. Using the descriptions given below, generate a concise yet comprehensive summary that captures all essential aspects of the transaction.

                Transaction Details: {{
                    "po_desc": "{po_desc}",
                    "line_desc": "{line_desc}",
                    "gl_desc": "{gl_desc}",
                    "invoice_desc": "{invoice_desc}"
                }}

                Please provide a summary that integrates information from all the above fields to offer a complete understanding of the transaction in one or two sentences.
                """
            )

            # Format the prompt with the transaction fields
            formatted_prompt = prompt.format(
                po_desc=transaction["po_desc"],
                line_desc=transaction["line_desc"],
                gl_desc=transaction["gl_desc"],
                invoice_desc=transaction["invoice_desc"],
            )

            # Summarize the transaction
            summary = asyncio.run(
                self.llm_model_func(
                    prompt=formatted_prompt,
                    system_prompt=None,
                    history_messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant responsible for interpreting transactions."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                "Can you help me interpret this transaction comprehensively using all the details provided?"
                            )
                        },
                    ],
                    temperature=0.1
                )
            )

            # Prepare the question prompt for TDS section classification
            question = PromptTemplate(
                input_variables=["ll_keywords", "hl_keywords", "summary"],
                template="""
                You are provided with a transaction summary and a set of keywords extracted from that transaction summary.
                Your task is to identify the most relevant TDS (Tax Deducted at Source) section(s) from this list:
                ["194C", "194JA", "194JB", "194Q", "194A", "194IA", "194IB", "194H", "No TDS"] based on the guidelines below.

                Guidelines:
                1. Analyze the provided transaction summary and keywords (low-level and high-level) to determine the most applicable TDS section.
                2. Distinctly classify transactions that involve procurement of services as falling under 194C when the service involves labor or work execution, like construction, repairs, advertising services, and broadcasting.
                3. Classify transactions that involve straightforward goods purchases under 194Q, especially when these are large-scale transactions that purely involve buying goods without an associated service component.
                4. For transactions involving payments for professional or technical services and royalties, consider:
                - 194JA for specific technical services and film-related royalties,
                - 194JB for professional services, non-compete fees, and other royalties.
                5. When there is ambiguity or reasonable doubt between two sections, particularly between 194C and 194Q, explicitly return both sections.
                - Format: Section 1: [primary section], Section 2: [secondary section if applicable]
                6. If considering "No TDS" but not completely certain, list "No TDS" and pair it with the next most applicable section.
                - Format: Section 1: No TDS, Section 2: [second most applicable section]
                7. Avoid defaulting to "No TDS" unless it is clear from the transaction details that no TDS deduction is applicable.

                #### Keywords:
                Low-level keywords: {ll_keywords}
                High-level keywords: {hl_keywords}

                ### Transaction summary:
                Transaction summary: {summary}

                ### Required Output Format:
                Section 1: [Your answer here]
                Section 2: [Optional; include only if applicable based on ambiguity]

                ### Strictly adhere to this output format. Do not include any additional information. Only provide the section numbers as mentioned in the example.
                For example: 
                Section 1: 194C
                Section 2: 194Q
                """
            )

            # Query LightRAG in 'hybrid' mode with separate keyword extraction
            hybrid_response = rag.query_with_separate_keyword_extraction(
                query=summary,
                prompt=question,
                param=QueryParam(mode="hybrid", top_k=5, transaction_no=i+1)
            )

            # Collect the results
            hybrid_results.append(f"Transaction no: {i+1} Section: {hybrid_response}")

            # Update the logger with the retrieved and original section
            mylogger.update_transaction(i+1, "hybrid", **{
                "Retrieved Section": hybrid_response,
                "Original Answer": transaction["section"], 
                "Transaction summary": summary
            })
        
        # Save all transaction logs to Excel
        mylogger.save_to_excel()    
        
        print("########################## Tokens used for 100 queries: #####################################")
        print("Total Input Tokens:", self.total_input_tokens)
        print("Total Output Tokens:", self.total_output_tokens)


def main():
    """
    Main function that creates an instance of TransactionApp and runs the application.
    """
    app = TransactionApp()
    app.run()


if __name__ == "__main__":
    # Entry point: Run the main function
    main()
