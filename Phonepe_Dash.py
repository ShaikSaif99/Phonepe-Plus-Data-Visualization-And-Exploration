import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import mysql.connector
import json

st.image(r"C:\Users\rahul\Data Science\PhonePe_Logo.png", width=200)
st.title( "Phonepe Pulse Data Visualization and Exploration")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main Page", "Graphical Visualization"])

if page == "Main Page":
    # -------------------------
    # Database connection
    # -------------------------
    @st.cache_resource #Cache the return value of this function across reruns
    def get_connection():
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='phonepe_pulse'
        )

    conn = get_connection()
    # -------------------------
    # Cache GeoJSON (load once)
    # -------------------------
    @st.cache_data #cache data/outputs (don’t want to re-fetch/recompute).
    def load_geojson():
        with open("GeoJSON.json", "r") as f:
            return json.load(f)

    india_states = load_geojson()

    # Data to explore
    df = pd.DataFrame({ 
        "category": ["Transactions","Users","Insurance"]
    })
    st.sidebar.title("Dashboards Filter")
    option = st.sidebar.selectbox("Select category", df["category"])


    if option == "Insurance":
        year_range = (2020, 2021, 2022, 2023, 2024)
    else:
        year_range = (2018, 2019, 2020, 2021, 2022, 2023, 2024)

    # Add a slider to the sidebar:
    year = st.sidebar.selectbox(
        'Select Year',
        year_range
    )
    if option == "Insurance" and year == 2020:
        select_quarter = (2,3,4)
    else:
        select_quarter = (1,2,3,4)
    
    quarter = st.sidebar.selectbox(
        'Select Quarter',
        select_quarter
    )
    
    #main Dashboard
    st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
    if option == "Transactions":
        st.title("💳 Transactions")
    elif option =="Users":
        st.title("👥 Users")
    elif option == "Insurance":
        st.title("🛡️ Insurance")
        
    @st.cache_data(ttl=200)
    def retrieve_data_from_mysql_db(option,quarter,year):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='phonepe_pulse'
        )
        cursor = conn.cursor()
        query = {
            "Transactions": [
                """SELECT 
            sum(transaction_count) as All_Phonepe_transcations,
            CONCAT("₹", FORMAT(sum(transaction_amount) / 10000000,0),'Cr') as Total_payment_value,
            CONCAT("₹", ROUND(SUM(transaction_amount) / SUM(transaction_count),0)) AS avg_transaction_value
            FROM aggregated_transactions
            where quarter = %s AND year = %s AND location = 'india'
            """,
            """SELECT 
            category, transaction_count as No_of_transcation
            FROM aggregated_transactions
            where quarter = %s AND year = %s AND location = 'india'""",
             # top 10 State
            """SELECT 
            state_dis_pin_name as Top_10_state,
            CONCAT("₹", FORMAT(transaction_count / 10000000,2), " Cr") as Transcation_count_No_users
            FROM top_transactions
            WHERE quarter = %s AND year = %s AND location = 'india' AND state_dis_pin = 'state'
            ORDER BY transaction_count DESC""",
            # top 10 districts
            """SELECT 
            state_dis_pin_name as Top_10_district,
            CONCAT("₹", FORMAT(transaction_count / 10000000,2), " Cr") as Transcation_count_No_users
            FROM top_transactions
            WHERE quarter = %s AND year = %s AND location = 'india' AND state_dis_pin = 'district'
            ORDER BY transaction_count DESC""",
            # top 10 postal code
            """SELECT 
            state_dis_pin_name as Top_10_postal_codes,
            CONCAT("₹", FORMAT(transaction_count / 10000000,2), " Cr") as Transcation_count_No_users
            FROM top_transactions
            WHERE quarter = %s AND year = %s AND location = 'india' AND state_dis_pin = 'pincode'
            ORDER BY transaction_count DESC""",
            ],
            "Users": [
                """SELECT registered_users as Registered_phonepe_user, 
                app_opens AS Phonepe_app_open
                FROM aggregated_users
                WHERE quarter = %s AND year = %s AND location = 'india' 
                LIMIT 1""",
                #top 10 state
                """SELECT state_dis_pin_name as Top_10_state, 
                CONCAT("₹", FORMAT(registeredUsers / 10000000,2), " Cr") as Transcation_count_No_users
                FROM top_users
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'state'AND location = 'india'
                order by registeredUsers desc""",
                # top 10 districts
                """SELECT  state_dis_pin_name as Top_10_district, 
                CONCAT("₹", FORMAT(registeredUsers / 100000,2), " lakh") as Transcation_count_No_users 
                FROM top_users
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'district' AND location = 'india'
                order by registeredUsers desc""",
                # top 10 postal codes
                """SELECT state_dis_pin_name as Top_10_postal_codes,
                CONCAT("₹", FORMAT(registeredUsers / 100000,2), " lakh") as Transcation_count_No_users
                FROM top_users 
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'pincode' AND location = 'india'
                order by registeredUsers desc"""
            ],
            "Insurance": [
                """SELECT transaction_count as Insurance_Policies_Purchased_Nos,
                CONCAT("₹", FORMAT(transaction_amount / 10000000,0), " Cr") as Total_premium_value,
                CONCAT("₹", ROUND(transaction_amount / transaction_count,0)) AS "Average premium value"
                FROM aggregated_insurance
                where quarter = %s AND year = %s AND location = 'india'""",
                #top 10 state
                """SELECT state_dis_pin_name as Top_10_state,
                CONCAT("₹", FORMAT(transaction_count / 1000,2), " k") as Transcation_count_No_users
                FROM top_insurance
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'state' AND location = 'india'
                order by transaction_count desc""",
                #top 10 district
                """SELECT state_dis_pin_name as Top_10_district,
                CONCAT("₹", FORMAT(transaction_count / 1000,2), " k") as Transcation_count_No_users
                FROM top_insurance 
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'district' AND location = 'india'
                order by transaction_count desc""",
                #top 10 postal codes
                """SELECT state_dis_pin_name as Top_10_postal_codes,
                CONCAT("₹", FORMAT(transaction_count / 1000,2), " k") as Transcation_count_No_users
                FROM top_insurance 
                WHERE quarter = %s AND year = %s AND state_dis_pin = 'pincode' AND location = 'india'
                order by transaction_count desc"""
            ]
        }
        results = []
        # Loop through all queries for selected option
        if option in query:
            for q in query[option]:
                cursor.execute(q, (quarter, year))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                results.append(df)
    
        cursor.close()
        conn.close()
        return results
    
    dataframes = retrieve_data_from_mysql_db(option, quarter, year)

    if option == "Transactions":
        summary_df = dataframes[0]
        category_df = dataframes[1]
        top_states_df = dataframes[2]
        top_districts_df = dataframes[3]
        top_pins_df = dataframes[4]

    else:
        summary_df = dataframes[0]
        top_states_df = dataframes[1]
        top_districts_df = dataframes[2]
        top_pins_df = dataframes[3]


    if option == "Transactions":
        col1, col2, col3, col4  = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:30px; margin-bottom:0;'>{summary_df["All_Phonepe_transcations"].values[0]:,}</h2>
                    <p style="font-size:14px; color:white; margin-top:2px 0 0 0;line-height:1;">All PhonePe transactions<br>(UPI + Cards + Wallets)</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:30px; margin-bottom:0;'>{summary_df["Total_payment_value"].values[0]}</h2>
                    <p style="font-size:16px; color:white; margin-top:0;">Total Payment Value</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="text-align:right;">
                    <h2 style='color:#00C4B4; font-size:30px; margin-bottom:0;'>{summary_df["avg_transaction_value"].values[0]}</h2>
                    <p style="font-size:16px; color:white; margin-top:0;">Avg. Transaction Value</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("Category Breakdown")
        for i, row in category_df.iterrows():
            st.markdown(
                f"""
                    <div style="display:flex; justify-content:space-between; 
                        background-color:#1E1E1E; padding:10px 20px; 
                        margin-bottom:10px; border-radius:10px;">
                        <p style="color:white; font-size:16px; margin:0;">{row['category']}</p>
                        <p style="color:#00C4B4; font-size:18px; margin:0;">{row['No_of_transcation']}</p>
                </div>
            """,
            unsafe_allow_html=True
            )
            
    elif option == 'Users':
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:40px; margin-bottom:0;'>{summary_df["Registered_phonepe_user"].values[0]:,}</h2>
                    <p style="font-size:14px; color:white; margin-top:0;">Registered PhonePe users</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:40px; margin-bottom:0;'>{summary_df["Phonepe_app_open"].values[0]}</h2>
                    <p style="font-size:14px; color:white; margin-top:0;">PhonePe app opens</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    elif option == "Insurance":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:40px; margin-bottom:0;'>{summary_df["Insurance_Policies_Purchased_Nos"].values[0]:,}</h2>
                    <p style="font-size:14px; color:white; margin-top:0;">All India Insurance Policies Purchased (Nos.)</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:40px; margin-bottom:0;'>{summary_df["Total_premium_value"].values[0]}</h2>
                    <p style="font-size:14px; color:white; margin-top:0;">Total_premium_value</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <h2 style='color:#00C4B4; font-size:40px; margin-bottom:0;'>{summary_df["Average premium value"].values[0]}</h2>
                    <p style="font-size:14px; color:white; margin-top:0;">Average premium value</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    
    left, middle, right = st.columns(3)
    if left.button("Top 10 State"):
        for i, row in top_states_df.iterrows():
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; 
                    background-color:#1E1E1E; padding:5px 10px; 
                    margin-bottom:5px; border-radius:5px;">
                    <p style="color:white; font-size:16px; margin:0;">{row['Top_10_state']}</p>
                    <p style="color:#00C4B4; font-size:16px; margin:0;">{row['Transcation_count_No_users']}</p>
                </div>
            """,
            unsafe_allow_html=True
        )
    if middle.button("Top 10 District"):
        for i, row in top_districts_df.iterrows():
            st.markdown(
                f"""
                    <div style="display:flex; justify-content:space-between; 
                        background-color:#1E1E1E; padding:5px 10px; 
                        margin-bottom:5px; border-radius:5px;">
                        <p style="color:white; font-size:16px; margin:0;">{row['Top_10_district']}</p>
                        <p style="color:#00C4B4; font-size:16px; margin:0;">{row['Transcation_count_No_users']}</p>
                    </div>
                """,
                unsafe_allow_html=True
            )
            
        
    if right.button("Top 10 Postal Codes"):
        for i, row in top_pins_df.iterrows():
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; 
                    background-color:#1E1E1E; padding:5px 10px; 
                    margin-bottom:5px; border-radius:5px;">
                    <p style="color:white; font-size:16px; margin:0;">{row['Top_10_postal_codes']}</p>
                    <p style="color:#00C4B4; font-size:16px; margin:0;">{row['Transcation_count_No_users']}</p>
                </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # Query data
    # -------------------------
    @st.cache_data(ttl=200)
    def Map_query (option,quarter,year):
        if option == "Transactions":
            return """
            SELECT 
            location AS state,
            SUM(transaction_count) AS ALL_transaction,
            CONCAT("₹", FORMAT(SUM(transaction_amount) / 10000000,0), " Cr") as All_payment_value, -- formatted for hover
            ROUND(SUM(transaction_amount) / SUM(transaction_count),0) AS avg_transaction_value
            FROM map_transactions
            WHERE quarter = %s AND year = %s AND country_state_level = 'state'
            GROUP BY location
            """
        elif option == "Users":
            return """
            SELECT 
            location AS state,
            SUM(registeredUsers) AS Registered_Users,
            SUM(app_opens) as App_opens
            FROM map_users
            WHERE quarter = %s AND year = %s AND country_state_level = 'state'
            GROUP BY location
            """
        elif option == "Insurance":
            return """
            SELECT 
            location AS state,
            SUM(transaction_count) AS "Insurance Policies (Nos.)",
            CONCAT("₹", FORMAT(SUM(transaction_amount) / 100000,0), " Lakh") as Total_premium_value,
            CONCAT("₹",ROUND(SUM(transaction_amount) / SUM(transaction_count),1)) as Avg_premium_value
            FROM map_insurance_country
            WHERE quarter = %s AND year = %s AND country_state_level = 'state'
            GROUP BY location
            """
        
    query = Map_query(option, quarter, year)
    df = pd.read_sql(query, conn, params=(quarter, year))

    # -------------------------
    # State Name Mapping
    # -------------------------
    state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island',
        'andhra-pradesh': 'Andhra Pradesh',
        'arunachal-pradesh': 'Arunanchal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chandigarh': 'Chandigarh',
        'chhattisgarh': 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadara & Nagar Havelli',
        'delhi': 'NCT of Delhi',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal-pradesh': 'Himachal Pradesh',
        'jammu-&-kashmir': 'Jammu & Kashmir',
        'jharkhand': 'Jharkhand',
        'karnataka': 'Karnataka',
        'kerala': 'Kerala',
        'lakshadweep': 'Lakshadweep',
        'madhya-pradesh': 'Madhya Pradesh',
        'maharashtra': 'Maharashtra',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'odisha': 'Odisha',
        'puducherry': 'Puducherry',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil-nadu': 'Tamil Nadu',
        'telangana': 'Telangana',
        'tripura': 'Tripura',
        'uttar-pradesh': 'Uttar Pradesh',
        'uttarakhand': 'Uttarakhand',
        'west-bengal': 'West Bengal'
    }

    # Apply mapping
    df['state'] = df['state'].map(state_name_map)

    # -------------------------
    # Choropleth map
    # -------------------------
    if option == "Transactions":
        hover_cols = ["All_payment_value", "avg_transaction_value"]
        color_col = "ALL_transaction"

    elif option == "Users":
        hover_cols = ["Registered_Users", "App_opens"]
        color_col = "Registered_Users"

    elif option == "Insurance":
        hover_cols = ["Total_premium_value", "Avg_premium_value"]
        color_col = "Insurance Policies (Nos.)"

    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey="properties.st_nm",
        locations="state",
        color=color_col,
        hover_data=hover_cols
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=700, width=900)

    st.plotly_chart(fig, key="india_choropleth")


    
elif page == "Graphical Visualization":
    st.title("📊Chart and Graph for Visualization")
    
    @st.cache_resource #Cache the return value of this function across reruns
    def get_connection():
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='phonepe_pulse'
        )

    conn = get_connection()
    
    # Data to explore
    df = pd.DataFrame({ 
        "category": ["Transactions","Users","Insurance"]
    })
    st.sidebar.title("Charts Filter")
    option = st.sidebar.selectbox("Select category", df["category"])


    if option == "Insurance":
        year_range = (2020, 2021, 2022, 2023, 2024)
    else:
        year_range = (2018, 2019, 2020, 2021, 2022, 2023, 2024)


    # Add a slider to the sidebar:
    year = st.sidebar.selectbox(
        'Select Year',
        year_range
    )

    if option == "Insurance" and year == 2020:
        select_quarter = (2,3,4)
    else:
        select_quarter = (1,2,3,4)
    
    quarter = st.sidebar.selectbox(
        'Select Quarter',
        select_quarter
    )
        
    state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island',
        'andhra-pradesh': 'Andhra Pradesh',
        'arunachal-pradesh': 'Arunanchal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chandigarh': 'Chandigarh',
        'chhattisgarh': 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadara & Nagar Havelli',
        'delhi': 'NCT of Delhi',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal-pradesh': 'Himachal Pradesh',
        'jammu-&-kashmir': 'Jammu & Kashmir',
        'jharkhand': 'Jharkhand',
        'karnataka': 'Karnataka',
        'kerala': 'Kerala',
        'lakshadweep': 'Lakshadweep',
        'madhya-pradesh': 'Madhya Pradesh',
        'maharashtra': 'Maharashtra',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'odisha': 'Odisha',
        'puducherry': 'Puducherry',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil-nadu': 'Tamil Nadu',
        'telangana': 'Telangana',
        'tripura': 'Tripura',
        'uttar-pradesh': 'Uttar Pradesh',
        'uttarakhand': 'Uttarakhand',
        'west-bengal': 'West Bengal'
    }
    
    state_list = list(state_name_map.keys())
    state = st.sidebar.selectbox(
        'select the state to visualize',
        state_list
    )
        
    query = """
    SELECT 
    location,
    brand AS BRAND,
    brand_count AS BRAND_COUNT
    FROM aggregated_users
    WHERE quarter = %s AND year = %s AND country_state_level = 'state'AND location = %s"""
    
    if year in range(2018,2022):
        brand_year = year
        df = pd.read_sql(query, conn, params=(quarter, brand_year, state))
        fig = px.pie(df, 
                     names="BRAND", 
                     values="BRAND_COUNT", 
                     title=f"Brand Share in {df['location'].iloc[0].title()}")
        st.plotly_chart(fig)

    else:
        st.write("Brand Data Available From 2018 to 2021")
                
    
    def bar_chart(option,quarter,year,location):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='phonepe_pulse'
        )
        cursor = conn.cursor()
        query = {
            "Transactions": [
                #Bar Chart 
                """SELECT 
                district as District,
                CONCAT(FORMAT(transaction_count / 100000,2), " lakh") as Transcation_count
                FROM map_transactions
                WHERE quarter = %s AND year = %s AND location = %s
                """,
                #Line Chart (Trend Over Time)
                """SELECT 
                year,
                quarter,
                CONCAT("₹", FORMAT(SUM(transaction_amount) / 100000000,2), " Cr") AS total_amount
                FROM aggregated_transactions
                WHERE country_state_level = 'state'
                GROUP BY year, quarter
                ORDER BY year, quarter""" 
            ],
            "Users": [
                #pie chart for brand share over the year
                """SELECT 
                state_dis_pin_name AS District,
                CONCAT(FORMAT((registeredUsers) / 1000,2), " k") AS Resistered_users
                FROM top_users
                where quarter = %s AND year = %s AND location = %s AND country_state_level = "state" AND state_dis_pin = "district"
                """,
                #here location is state_name
                
                #Line Chart (Trend Over Time of resigter users
                """SELECT 
                year,
                quarter,
                CONCAT(FORMAT(SUM(registeredUsers) / 1000,2), " k") AS Resistered_users
                FROM map_users
                WHERE country_state_level = 'state'
                GROUP BY year, quarter
                ORDER BY year, quarter
                """
            ],
            "Insurance": [
                #Bar Chart
                """SELECT 
                district as District,
                CONCAT(FORMAT(transaction_count / 1000,2), " k") as Insurance_count
                FROM map_insurance_country
                WHERE quarter = %s AND year = %s AND location = %s
                """,
                #here location is state_name
                #Line Chart (Trend Over Time)
                """SELECT 
                year,
                quarter,
                CONCAT("₹", FORMAT(sum(transaction_amount) / 1000,2), " k") AS Insurance_amount
                FROM aggregated_insurance
                WHERE country_state_level = 'state'
                GROUP BY year, quarter
                ORDER BY year, quarter""" 
            ]
        }
        results = []
        # Loop through all queries for selected option
        if option in query:
            for q in query[option]:
                if "location = %s" in q:
                    cursor.execute(q, (quarter, year, location))

                else:
                    cursor.execute(q)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                results.append(df)
    
        cursor.close()
        conn.close()
        return results

    state_list = list(state_name_map.keys())
    chart_dataframe = bar_chart(option, quarter, year, state)
    
    bar_df = chart_dataframe[0]
    line_df = chart_dataframe[1]

    if option == "Transactions":
        fig_bar = px.bar(
            bar_df,
            x="District",
            y="Transcation_count",
            title=f"Transaction Count by District"
        )
        st.plotly_chart(fig_bar)

        fig_line = px.line(
            line_df,
            x="quarter",   # or combine year+quarter into a single column
            y="total_amount",
            color="year",  # separate lines for each year
            markers=True,
            title="Transaction Amount Trend Over Time"
        )
        st.plotly_chart(fig_line)
    
    elif option == "Users":
        fig_bar = px.bar(
            bar_df,
            x="District",
            y="Resistered_users",
            title=f"Resistered_users Count by District"
        )
        st.plotly_chart(fig_bar)

        fig_line = px.line(
            line_df,
            x="quarter",   # or combine year+quarter into a single column
            y="Resistered_users",
            color="year",  # separate lines for each year
            markers=True,
            title="Resistered Users Trend Over Time"
        )
        st.plotly_chart(fig_line)

    elif option == "Insurance":
        fig_bar = px.bar(
            bar_df,
            x="District",
            y="Insurance_count",
            title=f"Resistered_users Count by District"
        )
        st.plotly_chart(fig_bar)

        fig_line = px.line(
            line_df,
            x="quarter",   # or combine year+quarter into a single column
            y="Insurance_amount",
            color="year",  # separate lines for each year
            markers=True,
            title="Insurance Amount Users Trend Over Time"
        )
        st.plotly_chart(fig_line)
        
