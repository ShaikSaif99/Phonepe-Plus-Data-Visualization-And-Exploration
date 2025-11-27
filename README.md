# Phonepe-Pulse-Data-Visualization-and-Exploration
A data engineering + visualization project that extracts PhonePe Pulse JSON data, processes it into CSV → MySQL, and visualizes it using Streamlit + Plotly.

This project demonstrates ETL pipeline, database design, and interactive dashboards with choropleth maps, bar charts, line charts, and pie charts.

🚀 Features

✅ Extracted JSON data → CSV → MySQL
✅ Created normalized SQL schema (Transactions, Users, Insurance)
✅ Handled missing values (NULL → 0, Unknown)
✅ Interactive Streamlit dashboard with:
Dropdowns (Year, Quarter, Category, State, Top 10 filters)
Plotly visualizations (Choropleth, Pie, Bar, Line)
Drill-down from Country → State → District → Pincode
✅ Caching with st.cache_data & st.cache_resource for performance
✅ Dashboard ready for deployment on Streamlit Cloud

📂 Project Workflow

Data Extraction
Cloned PhonePe Pulse data repo
Converted JSON → CSV
Database Ingestion

Designed SQL schema with tables:

aggregated_transactions,
aggregated_users,
aggregated_insurance_country,
map_transactions,
map_users,
map_insurance,
top_transactions,
top_users,
top_insurance

Inserted CSV data into MySQL
Dashboard Development
Built with Streamlit
Plotly for interactive charts
Sidebar filters for Year, Quarter, State, Category
Top 10 states/districts/pincodes
Streamlit Cloud 

🗄️ Database Schema

<img width="1915" height="175" alt="phonepe_pulse_schema_full" src="https://github.com/user-attachments/assets/c73cd0c9-aa4c-4c75-a207-70887101828f" />


Home/Main Page
Choropleth Transaction Map
Top 10 States/Districts/Pincodes
Graphical Visualization

🛠️ Tech Stack

Python: pandas, json, mysql-connector-python, plotly, streamlit
Database: MySQL
Visualization: Streamlit + Plotly
Version Control: GitHub
