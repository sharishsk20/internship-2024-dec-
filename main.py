from dotenv import load_dotenv
import streamlit as st
import os
import pyodbc  # For MSSQL connection
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define database configurations for both databases
db_configs = {
    "Database1": {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": os.getenv("MSSQL_SERVER_DB1"),
        "database": os.getenv("MSSQL_DATABASE_DB1"),
        "username": os.getenv("MSSQL_USERNAME_DB1"),
        "password": os.getenv("MSSQL_PASSWORD_DB1"),
    },
    # "Database2": {
    #     "driver": "ODBC Driver 17 for SQL Server",
    #     "server": os.getenv("MSSQL_SERVER_DB2"),
    #     "database": os.getenv("MSSQL_DATABASE_DB2"),
    #     "username": os.getenv("MSSQL_USERNAME_DB2"),
    #     "password": os.getenv("MSSQL_PASSWORD_DB2"),
    # },
}

# Function to retrieve data from the MSSQL database
def read_sql_query(sql, db_config):
    try:
        conn = pyodbc.connect(
            f"DRIVER={db_config['driver']};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']}"
        )
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows, [desc[0] for desc in cur.description]  # Fetch column names
    except Exception as e:
        return f"Error while executing query: {str(e)}", None

# Function to load Google Gemini Model and provide queries as responses
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        sql_query = response.text.strip()  # Clean leading/trailing whitespace
        sql_query = sql_query.replace("```", "").replace("'''", "")  # Remove formatting quotes
        
        # Clean up the generated SQL query by removing any unwanted 'sql' keyword
        sql_query = sql_query.replace("sql", "").strip()
        
        return sql_query
    except Exception as e:
        return f"Error while using Google Gemini: {str(e)}"

# Define Your Prompt
prompt = [
      """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name a007_oee_monitoring_oeedata and has the following columns -  ,[date]
      ,[oee]
      ,[availability]
      ,[performance]
      ,[quality]
      ,[avl_time]
      ,[pdt]
      ,[updt]
      ,[pq_plan]
      ,[pq_perf_plan]
      ,[pq_actual]
      ,[pq_ok_p]
      ,[tot_le]
      ,[fm_le_it]
      ,[sm_le_it]
      ,[tm_le_it]
      ,[fm_le_what_i_id]
      ,[fm_le_where_i_id]
      ,[production_line_i_id]
      ,[shift_id]
      ,[sm_le_what_i_id]
      ,[sm_le_where_i_id]
      ,[tm_le_what_i_id]
      ,[tm_le_where_i_id] \n
\nFor example,\nExample 1 - What is the availability on 15 october 2024 shift a in spr4 bb, 
    the SQL command will be something like this: SELECT [availability]
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] = '2024-10-15'
  AND [shift_id] = '11'
  AND [production_line_i_id] = 600000;
\nExample 2 - What is the availability on 15 october 2024 shift B in SPR4 3PGA1, 
    the SQL command will be something like this: SELECT [availability]
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] = '2024-10-15'
  AND [shift_id] = '12'
  AND [production_line_i_id] = 600100;, icode	name
600000	SPR4 BB
600100	SPR4 3PGA1 
600200	SPR4 3PGA2
600300	IFS1 BB
600400	IFS1 3PGA 
600500	NFS1 BB
600600	NFS1 3PGA
600700	3.0 BB
600800	3.0 3PGA map all these names to production_line_i_id 
also map shift_id null to combined shift, 11 to shift a, 12 to shift b and 13 to shift c
\nExample 3 -  What is the availability from 15 oct 2024 to 20 0ct 2024 shift B in SPR4 3PGA1 then the sql command will be like
SELECT [availability]
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-10-15' AND '2024-10-20'
  AND [shift_id] = 12
  AND [production_line_i_id] = 600100;

\nExample 4 - what is the average performance in october shift a spr4 3pga1 , 
    the SQL command will be something like this:SELECT AVG([availability]) AS AverageAvailability
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-10-15' AND '2024-10-20'
  AND [shift_id] = 12
  AND [production_line_i_id] = 600100;
  \nExample 5 - What is the average availability from 15 oct 2024 to 20 0ct 2024 in SPR4 3PGA1 THEN THE SQL query will be like
  SELECT AVG([availability]) AS AverageAvailability
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-10-15' AND '2024-10-20'
  AND [production_line_i_id] = 600100
  AND [shift_id] IS NULL; 
  if shift id is not specified take null values
\nExample5 - what is the average performance of prodectoin line spr4 3pga1 on july shift b
  SELECT AVG([performance]) AS AveragePerformance
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-07-01' AND '2024-07-31'
  AND [shift_id] = '12'
  AND [production_line_i_id] = 600100;
\nExample 6 -what is the average oee for spr4 3pga1 on july shift b
  the sql command will be like SELECT AVG([oee]) AS AverageOEE
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-07-01' AND '2024-07-31'
  AND [shift_id] = '12'
  AND [production_line_i_id] = 600100;
\n Example 7 - what is the average oee for spr4 3pga1 on july 
  then sql command should be SELECT AVG([oee]) AS AverageOEE
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-07-01' AND '2024-07-31'
  AND [production_line_i_id] = 600100;
  AND [shift_id] IS NULL
\nExample 8 - what and WHEN is the MAXIMUM oee from oct 2024  IFS1 BB 
  the sql command should be be SELECT TOP 1 [date], [oee]
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-10-01' AND '2024-10-31'
  AND [production_line_i_id] = 600300
ORDER BY [oee] DESC;
\nExample 9 - which line has highest OEE in october? the SQL command will be
SELECT TOP 1 [production_line_i_id], MAX([oee]) AS MaxOEE
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] BETWEEN '2024-10-01' AND '2024-10-31'
GROUP BY [production_line_i_id]
ORDER BY MaxOEE DESC;
and print the required mapped icode name like if it is 600600 then NFS1 3PGA
\nExample 10 - which line has highest OEE in october
the sql command will be SELECT TOP 1 m.[name], o.[production_line_i_id], MAX(o.[oee]) AS MaxOEE
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] o
JOIN [a000_xylem_master].[dbo].[a000_xylem_master_icodes] m
ON o.[production_line_i_id] = m.[icode]
WHERE o.[date] BETWEEN '2024-10-01' AND '2024-10-31'
GROUP BY m.[name], o.[production_line_i_id]
ORDER BY MaxOEE DESC;
    oee =  'OEE'  
    availability =  'Availability'  
    performance =  'Performance'  
    quality =  'Quality'  
    avl_time =  'Available Time in seconds'  
    pdt =  'Planned Down Time in seconds'  
    updt =  'Unplanned Down Time in seconds'  
    pq_plan =  Production Quantity Plan'  
    pq_perf_plan =  Production Quantity Performance Plan'  
    pq_actual =  Production Quantity Actual'  
    pq_ok_p =  Production Quantity Ok parts'  
    tot_le =  Total Loss Events'  
    fm_le_where_i =  First Major Loss Event 's where id' 
    fm_le_what_i =  First Major Loss Event 's what id' , 
    fm_le_it =  'First Major Loss Event 's Idle time in seconds'
    sm_le_where_i =  Second Major Loss Event 's where id'
    sm_le_what_i =  Second Major Loss Event 's what id'
    sm_le_it =  'Second Major Loss Event 's Idle time in seconds'
    tm_le_where_i =  Third Major Loss Event 's where id' 
    tm_le_what_i =  Third Major Loss Event 's what id'
    tm_le_it =  'Third Major Loss Event 's Idle time in seconds'
\nExample 11 - What was the total number of loss events on 23 sep?
the sql command will be SELECT SUM([tot_le]) AS TotalLossEvents
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] = '2024-09-23';
\nExample 12 - what was the issue on sep 23 second major?
then sql command will be
SELECT
    oe.[date],
    ic.name AS IssueDescription,
    oe.[sm_le_it]/60 AS SecondMajorLossEventTime__in_mins
FROM
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] oe
JOIN
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic
    ON oe.[sm_le_what_i_id] = ic.icode
WHERE
    oe.[date] = '2024-09-23'
    AND oe.[sm_le_what_i_id] = 10064;
\nExample 13 - what was pq actual parts on 23 sep shift b with date and shift?
then sql command will be
SELECT 
    oe.[date],
    oe.[pq_actual] AS PQActualParts,
    'Shift B' AS ShiftName
FROM 
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] oe
JOIN 
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic
    ON oe.[shift_id] = ic.[icode]
WHERE 
    oe.[date] = '2024-09-23'
    AND oe.[shift_id] = 12;
\nExample 14 - what was pq actual parts on 23 sep with date and shift combined?
then sql command will be
SELECT 
    [date],
    [pq_actual] AS PQActualParts,
    'Combined Shift' AS ShiftName
FROM 
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE 
    [date] = '2024-09-23'
    AND [shift_id] IS NULL;


\nExample 14 - what was total loss on 23 sep with date and shift with production line?
then sql command will be
SELECT 
    oe.[date],
    oe.[tot_le] AS TotalLossEvents,
    CASE 
        WHEN oe.[shift_id] = 11 THEN 'Shift A'
        WHEN oe.[shift_id] = 12 THEN 'Shift B'
        WHEN oe.[shift_id] = 13 THEN 'Shift C'
        ELSE 'Combined Shift'
    END AS ShiftName,
    ic.[name] AS ProductionLineName
FROM 
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] oe
JOIN 
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic
    ON oe.[production_line_i_id] = ic.[icode]
WHERE 
    oe.[date] = '2024-09-23';


\nExample 15 - what was the major issue on 24 oct?
then sql command will be SELECT
    oe.[date],
    ic.name AS IssueDescription,
    oe.[fm_le_it]/60 AS FirstMajorLossEventTime__in_mins
FROM
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] oe
JOIN
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic
    ON oe.[fm_le_what_i_id] = ic.icode
WHERE
    oe.[date] = '2024-10-24';
\n Example 16 - what was the issue on sep 23 third major with shift with prod line?
then sql command will be 

SELECT
    oe.[date],
    ic.name AS IssueDescription,
    oe.[tm_le_it]/60 AS ThirdMajorLossEventTime__in_mins,
    CASE 
        WHEN oe.[shift_id] = 11 THEN 'Shift A'
        WHEN oe.[shift_id] = 12 THEN 'Shift B'
        WHEN oe.[shift_id] = 13 THEN 'Shift C'
        ELSE 'Combined Shift'
    END AS ShiftName,
    ic1.name AS ProductionLineName
FROM
    [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata] oe
JOIN
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic
    ON oe.[tm_le_what_i_id] = ic.icode
JOIN
    [a000_xylem_master].[dbo].[a000_xylem_master_icodes] ic1
    ON oe.[production_line_i_id] = ic1.icode
WHERE
    oe.[date] = '2024-09-23';

\n Example 17-plant availability on 20-sep-2024

then sql command should be

SELECT AVG([availability]) AS Average_Availability
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] = '2024-09-20';

\n Example 18-plant oee on 20-sep-2024

then sql command should be

SELECT AVG([oee]) AS Average_OEE
FROM [a007_oee_monitoring].[dbo].[a007_oee_monitoring_oeedata]
WHERE [date] = '2024-09-20';
    


\nthis is another table SELECT [id]
      ,[password]
      ,[last_login]
      ,[is_superuser]
      ,[username]
      ,[first_name]
      ,[last_name]
      ,[email]
      ,[is_staff]
      ,[date_joined]
      ,[dob]
      ,[is_active]
      ,[dept_i_id]
      ,[designation_i_id]
      ,[gender_i_id]
      ,[plant_location_i_id]
      ,[responded_by_id]
  FROM [a000_xylem_master].[dbo].[a000_xylem_master_userprofile]
\nExample 11 - how many users are there?
then sql command will be SELECT COUNT(*) AS TotalUsers
FROM [a000_xylem_master].[dbo].[a000_xylem_master_userprofile];
\nExample 12 - how many users are in plant engineering?
the sql command will be SELECT COUNT(*) AS TotalUsers
FROM [a000_xylem_master].[dbo].[a000_xylem_master_userprofile]
WHERE [dept_i_id] = (
    SELECT [icode]
    FROM [a000_xylem_master].[dbo].[a000_xylem_master_icodes]
    WHERE [name] = 'Plant Engineering'
\nExample 
);




Please and Please ensure the SQL code does not have ``` or SQL prefixes.
Please and Please ensure the SQL code does not have ``` or SQL prefixes.
Please and Please ensure the SQL code does not have ``` or SQL prefixes.
    """
]

# Initialize Streamlit App
st.set_page_config(page_title="Gemini SQL Query Generator", layout="wide")
st.header("My3 Chatbot")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User Input
question = st.text_input("", key="input")
submit = st.button("Ask")


if submit:
    if question:
        try:
            # Step 1: Generate SQL query using Gemini
            generated_sql = get_gemini_response(question, prompt)
            st.subheader("Generated SQL Query:")
            st.code(generated_sql)

            # Step 2: Execute the generated SQL query on both databases and combine the results
            combined_result = []
            columns = None

            # for db_name, db_config in db_configs.items():
            result, db_columns = read_sql_query(generated_sql, db_configs["Database1"])
            if result:
                if not columns:  # Set the columns from the first result
                    columns = db_columns
                # Ensure no duplicates are added to combined_result
                combined_result.extend(result)  # Add results only once
            # print(db_configs.items())

            # Append the question and combined results to chat history
            st.session_state.chat_history.insert(0, {
                "question": question,
                "sql": generated_sql,
                "result": combined_result,
                "columns": columns,
            })

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Add a JavaScript event listener for the Enter key press
st.markdown("""
<script>
document.getElementById('input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission behavior
        document.querySelector('button[aria-label="Ask"]').click(); // Trigger the button click event
    }
});
</script>
""", unsafe_allow_html=True)

# Display Chat History
st.subheader("Chat History")
qd_len = len(st.session_state.chat_history)
for i, chat in enumerate(st.session_state.chat_history):
    st.markdown(f"**Q{qd_len-i}:** {chat['question']}")
    st.code(chat['sql'], language='sql')

    if isinstance(chat["result"], str):  # Error message
        st.error(chat["result"])
    else:
        # Display combined results from both databases as a table
        rows_html = ""
        for row in chat["result"]:
            rows_html += f"<tr><td>{'</td><td>'.join(map(str, row))}</td></tr>"
        table_html = f"""
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead style="background-color: #00274d; color: white;">
                    <tr>
                        {''.join(f'<th style="border: 1px solid #ddd; padding: 8px;">{col}</th>' for col in chat["columns"]) }
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        """
        st.markdown(table_html, unsafe_allow_html=True)
