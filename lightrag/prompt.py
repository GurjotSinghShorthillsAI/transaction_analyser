GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["section", "category"]

PROMPTS["entity_extraction"] = """-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
Use {language} as output language.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
-Examples-
######################
{examples}

#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [section, category, subcategory]
Text:
During the annual compliance workshop, the Director introduced Section 305 for data privacy management. She explained that encryption standards, user access controls, and employee training programs all come under the scope of Section 305, ensuring that organizations handle personal data securely.
According to her, this section specifically addresses how companies should classify sensitive information, implement secure data handling protocols, and regularly train employees to avoid data breaches. Additionally, any legal disclosures or government-mandated audits are instead covered under Section 402, which ensures strict reporting to regulatory agencies.

Explanation:
1. Section: A “section” typically represents a broad legislative, policy-based, or thematic division. In the text, this corresponds to major rules or guidelines (e.g., Section 305, Section 402).

2. Category: A “category” is a subdivision of a section that groups related items. For instance, within Section 305 (data privacy management), “encryption standards” and “user access controls” can be considered categories because they are larger buckets of related practices.

3. Subcategory: A “subcategory” is an even more specific subdivision within a category. For example, if we elaborated on “user access controls,” we might have subcategories like “password rotation policies” or “two-factor authentication methods.”

Why certain items fall where:
1. Section 305 is a broad policy directive covering data privacy management.
2. Encryption standards and user access controls are key functional areas under data privacy, so they are labeled as categories.
3. If we had more detailed elements of these controls (e.g., “multi-factor authentication,” “encryption key rotation”), they would be subcategories.

################
Output:
("entity"{tuple_delimiter}"305"{tuple_delimiter}"section"{tuple_delimiter}"Section 305 focuses on data privacy management, outlining how organizations should handle personal data securely."){record_delimiter}
("entity"{tuple_delimiter}"402"{tuple_delimiter}"section"{tuple_delimiter}"Section 402 covers legal disclosures and government-mandated audits, ensuring strict reporting to regulatory agencies."){record_delimiter}
("entity"{tuple_delimiter}"encryption standards"{tuple_delimiter}"category"{tuple_delimiter}"Encryption standards are guidelines to protect data by converting it into a secure code."){record_delimiter}
("entity"{tuple_delimiter}"user access controls"{tuple_delimiter}"category"{tuple_delimiter}"User access controls define policies to restrict data access to authorized individuals only."){record_delimiter}
("entity"{tuple_delimiter}"employee training programs"{tuple_delimiter}"category"{tuple_delimiter}"Programs that educate staff on secure handling of sensitive data and ways to prevent data breaches."){record_delimiter}
("entity"{tuple_delimiter}"personal data"{tuple_delimiter}"subcategory"{tuple_delimiter}"Any information relating to an identified or identifiable individual, requiring secure handling."){record_delimiter}
("relationship"{tuple_delimiter}"encryption standards"{tuple_delimiter}"305"{tuple_delimiter}"falls under"{tuple_delimiter}"data privacy management"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"user access controls"{tuple_delimiter}"305"{tuple_delimiter}"falls under"{tuple_delimiter}"managing personal data securely"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"employee training programs"{tuple_delimiter}"305"{tuple_delimiter}"falls under"{tuple_delimiter}"ensuring staff awareness and data breach prevention"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"personal data"{tuple_delimiter}"encryption standards"{tuple_delimiter}"protected by"{tuple_delimiter}"data encryption practices"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"personal data"{tuple_delimiter}"user access controls"{tuple_delimiter}"restricted by"{tuple_delimiter}"access management policies"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"Section 305, data privacy, encryption, user access, employee training, personal data, Section 402, compliance, data breaches"){completion_delimiter}
#############################""",

    """Example 2:

Entity_types: [section, category, subcategory]
Text:
During a strategic development session, the Security Officer introduced Section 501 for risk management. She explained that risk assessment frameworks, compliance checklists, and threat intelligence modules all come under the scope of Section 501, ensuring that organizations handle potential vulnerabilities effectively.
According to her, this section specifically addresses how companies should identify, evaluate, and mitigate security threats. Additionally, any major system overhauls or architectural revamps are instead covered under Section 530, which ensures that overall infrastructure remains robust and scalable.

Explanation:
1. Section: Represents a broad legislative or policy-based directive. In this text, Section 501 sets the overarching guidelines for risk management and Section 530 addresses infrastructure-related upgrades or enhancements.

2. Category: A subdivision under a section that groups related areas. “Risk assessment frameworks,” “compliance checklists,” and “threat intelligence modules” are considered categories under Section 501 because each represents a major functional domain within risk management.

3. Subcategory: A further subdivision within a category. For example, within “threat intelligence modules,” subcomponents like “real-time threat feeds” or “automated vulnerability alerts” might be subcategories if we needed deeper granularity.

Why certain items fall where:
1. Section 501 covers broad policies around risk management.
2. Risk assessment frameworks, compliance checklists, and threat intelligence modules are overarching components (categories) within risk management.
3. If we detailed specific tools or automated alerts under threat intelligence modules, those would be subcategories.

################
Output:
("entity"{tuple_delimiter}"501"{tuple_delimiter}"section"{tuple_delimiter}"Section 501 focuses on risk management, guiding organizations to identify and mitigate potential vulnerabilities."){record_delimiter}
("entity"{tuple_delimiter}"530"{tuple_delimiter}"section"{tuple_delimiter}"Section 530 oversees major system upgrades or architectural revamps for robust infrastructure."){record_delimiter}
("entity"{tuple_delimiter}"risk assessment frameworks"{tuple_delimiter}"category"{tuple_delimiter}"Structured methods for identifying potential threats and evaluating their impact."){record_delimiter}
("entity"{tuple_delimiter}"compliance checklists"{tuple_delimiter}"category"{tuple_delimiter}"Lists of regulatory or internal policies to ensure adherence to legal and organizational standards."){record_delimiter}
("entity"{tuple_delimiter}"threat intelligence modules"{tuple_delimiter}"category"{tuple_delimiter}"Systems that gather and analyze information on emerging security threats."){record_delimiter}
("entity"{tuple_delimiter}"potential vulnerabilities"{tuple_delimiter}"subcategory"{tuple_delimiter}"Specific weaknesses or exposures that an organization must address to prevent breaches."){record_delimiter}

("relationship"{tuple_delimiter}"risk assessment frameworks"{tuple_delimiter}"501"{tuple_delimiter}"falls under"{tuple_delimiter}"overarching risk management strategy"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"compliance checklists"{tuple_delimiter}"501"{tuple_delimiter}"falls under"{tuple_delimiter}"ensuring legal and policy adherence"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"threat intelligence modules"{tuple_delimiter}"501"{tuple_delimiter}"falls under"{tuple_delimiter}"monitoring potential security risks"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"potential vulnerabilities"{tuple_delimiter}"threat intelligence modules"{tuple_delimiter}"identified by"{tuple_delimiter}"analysis of emerging threats"{tuple_delimiter}8){record_delimiter}

("content_keywords"{tuple_delimiter}"Section 501, risk management, threat intelligence, compliance, security threats, Section 530, infrastructure, vulnerabilities"){completion_delimiter}
#############################"""
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Target response length and format---

{response_type}

---Data tables---

{context_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown."""

PROMPTS["keywords_extraction"] = """
---Role---
You are a helpful assistant tasked with identifying both high-level and low-level keywords in user queries.

---Goal---
High-level keywords refer to terms that directly describe visible elements or overarching themes of a transaction. Low-level keywords delve deeper, relating closely to the transaction’s specifics or associated processes, often in terms of potential tax implications as per the TDS sections.

provided_sections: ["194C", "194JA", "194JB", "194Q", "194A", "194IA", "194IB", "194H", "No TDS"]

---Instructions---
- Extract keywords from the transaction query provided.
- Output the keywords in JSON format with two keys:
  - "high_level_keywords": For general themes or visible aspects.
  - "low_level_keywords": For specific, detailed aspects.
- Ensure the language of the output matches that of the query and avoid using unicode characters.

######################
-Examples-
######################
{examples}

#############################
-Real Data-
######################
Query: {query}
######################
Output:
"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:
Query: "This transaction pertains to charges for bill printing and postage related to GBPA - 88356."
################
Output:
{
  "high_level_keywords": ["Bill Printing", "Postage Charges", "Delivery Services"],
  "low_level_keywords": ["Payment to Contractor", "Work Contract", "Carriage of Goods"]
}
Reasoning for high_level_keywords & low_level_keywords: 'Bill Printing' is a direct activity related to the transaction, categorizable under a 'work contract' from Section 194C, suggesting a contractual obligation for service delivery. 'Postage Charges' connect to 'Carriage of Goods,' aligning with logistical aspects that can be essential under Section 194C for contractual transport services.
#############################""",
    """Example 2:
Query: "Payment made for software licensing fees to TechSoft Solutions."
################
Output:
{
  "high_level_keywords": ["Software Licensing", "TechSoft Solutions", "Technology Expenses"],
  "low_level_keywords": ["Royalty Payments", "Intellectual Property", "Software Use"]
}
Reasoning for high_level_keywords & low_level_keywords: 'Software Licensing' directly reflects the nature of the transaction, relating it to 'Royalty Payments' under Sections 194J and 194JA which often involve fees for the right to use intellectual property. 'TechSoft Solutions' provides context to the provider, emphasizing the transaction's focus on technology-based services. 'Technology Expenses' categorize the financial aspect under general business expenditures while 'Intellectual Property' and 'Software Use' delve into the specifics of what the licensing covers, pertinent to understanding the underlying tax implications.
#############################"""
]

PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to questions about documents provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Target response length and format---

{response_type}

---Documents---

{content_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate the following two points and provide a similarity score between 0 and 1 directly:
1. Whether these two questions are semantically similar
2. Whether the answer to Question 2 can be used to answer Question 1
Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a professional assistant responsible for answering questions based on knowledge graph and textual information. Please respond in the same language as the user's question.

---Goal---

Generate a concise response that summarizes relevant points from the provided information. If you don't know the answer, just say so. Do not make anything up or include information where the supporting evidence is not provided.

When handling information with timestamps:
1. Each piece of information (both relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content/relationship and the timestamp
3. Don't automatically prefer the most recent information - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Data Sources---

1. Knowledge Graph Data:
{kg_context}

2. Vector Data:
{vector_context}

---Response Requirements---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Aim to keep content around 3 paragraphs for conciseness
- Each paragraph should be under a relevant section heading
- Each section should focus on one main point or aspect of the answer
- Use clear and descriptive section titles that reflect the content
- List up to 5 most important reference sources at the end under "References", clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (VD)
  Format: [KG/VD] Source content

Add sections and commentary to the response as appropriate for the length and format. If the provided information is insufficient to answer the question, clearly state that you don't know or cannot provide an answer in the same language as the user's question."""
