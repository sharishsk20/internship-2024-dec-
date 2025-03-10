## Gemini SQL Query Generator

This application allows users to convert natural language questions into SQL queries using Google's Generative AI and execute the generated queries on an MSSQL database. It features a user-friendly interface built with Streamlit, complete with query execution results and chat history.
/
---

### Features
- *Natural Language to SQL Conversion*: Generate SQL queries from user-input questions.
- *MSSQL Database Integration*: Execute queries directly on your configured database.
- *Chat History*: Maintain a record of previously asked questions, generated SQL queries, and results.
- *Enhanced Query Visualization*: Display query results in an interactive and readable table format.
- *Customizable Styles*: Easily modify header and row colors for better visibility.

---

### Requirements
- Python 3.9 or above.
- Required Python libraries:
  - dotenv
  - streamlit
  - os
  - pyodbc
  - google.generativeai
- MSSQL database with ODBC Driver 17 installed.

---

### Setup Instructions
1. *Clone the Repository*  
   Download or clone the project files.

2. *Install Dependencies* 
   

3. *Environment Variables*  
   Create a .env file in the root directory with the following entries:
   GOOGLE_API_KEY=your_google_api_key
   MSSQL_SERVER=your_server_name
   MSSQL_DATABASE=your_database_name
   MSSQL_USERNAME=your_username
   MSSQL_PASSWORD=your_password
to get your api key go to https://aistudio.google.com/app/apikey

4. *Run the Application*  
   Use the command below to start the Streamlit app:
   streamlit run app.py
4.1. *To Train*
	When entering the prompt for training or using the application, the system processes the input to either fine-tune a model or generate results based on the predefined functionality. The prompt should be clear, concise, and well-structured to yield accurate outputs. For instance, in an AI-driven SQL generator, entering a question like "What is the average availability from 15 Oct 2024 to 20 Oct 2024 in SPR4 3PGA1?" would guide the model to interpret the context, generate the corresponding SQL query, and retrieve the desired data. A well-defined prompt ensures the system comprehends user intent, aligns with the dataset schema, and minimizes errors in output generation. 

5. *Access the Application*  
   Open the local URL (e.g., http://localhost:8501) in your browser.

### Usage
1. Enter a natural language question in the input field (e.g., "What is the average availability from 15 Oct 2024 to 20 Oct 2024 in SPR4 3PGA1?").
2. Click on the *Ask* button to generate the corresponding SQL query and view the results.
3. The generated SQL query and its results will be displayed, along with chat history for reference.
4. Query results are presented in a table with improved visibility for headers.

### Customization
- *Query History*: Modify the logic in chat dictionary to retain chat history across sessions.
- *Styling*: Update the HTML and CSS styles in the table code for further customization.
- *Prompts*: Edit the prompt variable to include more specific SQL generation rules or examples.

---

For issues or suggestions, feel free to reach out!

Sharish.S.K-8608166920-sharishsk20@gmail.com
Sree Santh.K.B-6383276700- sreesanthkb01@gmail.com
Prem KS-7845734656-kspremnkl@gmail.com
