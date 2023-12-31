import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import streamlit as st
import os
import shutil

# Database functions
def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS funnel_steps (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        order_number INTEGER NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY,
        funnel_step_id INTEGER NOT NULL,
        description TEXT,
        realizations INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(funnel_step_id) REFERENCES funnel_steps(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hypotheses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL
    );
    """)

    conn.commit()

def get_data(conn, query):
    return pd.read_sql_query(query, conn)

# Streamlit app
def main():
    st.title("Marketing Funnels")

    st.sidebar.title("Menu")
    menu = ["Home", "Upload DB", "Download DB", "Create new DB", "Add funnel step", "Add registration", "Add hypothesis", "View funnel", "View funnel by week"]
    choice = st.sidebar.selectbox("Choose an option", menu)

    if choice == "Home":
        st.write("Welcome to the Marketing Funnels app.")

    elif choice == "Upload DB":
        uploaded_file = st.file_uploader("Choose a database file", type="db")
        if uploaded_file is not None:
            # Delete existing DB
            if os.path.exists("marketing_funnels.db"):
                os.remove("marketing_funnels.db")
            with open("marketing_funnels.db", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Database uploaded successfully.")

    elif choice == "Create new DB":
        db_name = st.text_input("Enter new DB name")
        if st.button("Create DB"):
            # Delete existing DB
            if os.path.exists("marketing_funnels.db"):
                os.remove("marketing_funnels.db")
            conn = sqlite3.connect('marketing_funnels.db')
            conn.close()
            st.success(f"Database {db_name}.db created successfully.")


    elif choice == "Download DB":
        if st.button("Download DB"):
            st.download_button(
                "Download DB",
                data=open("marketing_funnels.db", "rb"),
                file_name="marketing_funnels.db",
                mime="application/octet-stream",
            )

    else:
        conn = sqlite3.connect('marketing_funnels.db')
        create_tables(conn)

        if choice == "Add funnel step":
            st.subheader("Add a new funnel step")
            name = st.text_input("Enter the name of the funnel step")
            order_number = st.number_input("Enter the order number of the funnel step", value=1, step=1)
            if st.button("Add Funnel Step"):
                cur = conn.cursor()
                cur.execute("INSERT INTO funnel_steps (name, order_number) VALUES (?, ?)", (name, order_number))
                conn.commit()
                st.success("Funnel step added successfully.")

        elif choice == "Add registration":
            st.subheader("Add a new registration")
            # Fetch funnel steps
            df_funnel_steps = get_data(conn, "SELECT * FROM funnel_steps")
            funnel_step_id = st.selectbox("Select funnel step", df_funnel_steps['id'])
            description = st.text_input("Enter a description for the registration")
            realizations = st.number_input("Enter the number of realizations", value=1, step=1)
            if st.button("Add Registration"):
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                cur = conn.cursor()
                cur.execute("INSERT INTO registrations (funnel_step_id, description, realizations, date) VALUES (?, ?, ?, ?)", (funnel_step_id, description, realizations, date))
                conn.commit()
                st.success("Registration added successfully.")

        elif choice == "Add hypothesis":
            st.subheader("Add a new hypothesis")
            name = st.text_input("Enter the name of the hypothesis")
            description = st.text_input("Enter a description for the hypothesis")
            if st.button("Add Hypothesis"):
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                cur = conn.cursor()
                cur.execute("INSERT INTO hypotheses (name, description, date) VALUES (?, ?, ?)", (name, description, date))
                conn.commit()
                st.success("Hypothesis added successfully.")

        elif choice == "View funnel":
            st.subheader("View funnel")
            start_date = st.date_input("Enter the start date")
            end_date = st.date_input("Enter the end date")
            if st.button("View Funnel"):
                df = get_data(conn, f"""
                SELECT
                    funnel_steps.id,
                    funnel_steps.name,
                    SUM(registrations.realizations) AS realizations
                FROM funnel_steps
                LEFT JOIN registrations ON funnel_steps.id = registrations.funnel_step_id
                WHERE date(registrations.date) BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY funnel_steps.id
                ORDER BY funnel_steps.order_number
                """)
                # Compute conversion rates
                df['conversion_rate'] = df['realizations'].pct_change() + 1
                st.dataframe(df)


        elif choice == "View funnel by week":
            st.subheader("View funnel by week")
            start_date = st.date_input("Enter the start date")
            end_date = st.date_input("Enter the end date")
            if st.button("View Funnel by Week"):
                df = get_data(conn, f"""
                SELECT
                    date,
                    funnel_steps.name,
                    funnel_steps.order_number,
                    SUM(registrations.realizations) AS realizations
                FROM funnel_steps
                LEFT JOIN registrations ON funnel_steps.id = registrations.funnel_step_id
                WHERE date(registrations.date) BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, funnel_steps.name
                ORDER BY date, funnel_steps.order_number
                """)
                # Add year, month, week columns
                df['date'] = pd.to_datetime(df['date'])
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                df['week_of_month'] = df['date'].apply(lambda x: (x.day - 1) // 7 + 1)
                
                # Compute conversion rates
                df = df.sort_values(by=['year', 'month', 'week_of_month', 'order_number'])
                df['conversion_rate'] = df['realizations'] / df.groupby(['year', 'month', 'week_of_month'])['realizations'].shift(1)
                
                # Get hypotheses for each week
                df_hypotheses = get_data(conn, f"""
                SELECT
                    date,
                    name,
                    description
                FROM hypotheses
                WHERE date(date) BETWEEN '{start_date}' AND '{end_date}'
                """)
                df_hypotheses['date'] = pd.to_datetime(df_hypotheses['date'])
                df_hypotheses['year'] = df_hypotheses['date'].dt.year
                df_hypotheses['month'] = df_hypotheses['date'].dt.month
                df_hypotheses['week_of_month'] = df_hypotheses['date'].apply(lambda x: (x.day - 1) // 7 + 1)
                df_hypotheses.drop('date', axis=1, inplace=True)
        
                # Merge with hypotheses data
                # First, group by year, month, and week_of_month and concatenate the hypotheses
                df_hypotheses_grouped = df_hypotheses.groupby(['year', 'month', 'week_of_month']).agg({
                    'name': lambda x: ', '.join(x),
                    'description': lambda x: ', '.join(x)
                }).reset_index()
                
                # Then merge with the main DataFrame
                df = df.merge(df_hypotheses_grouped, on=['year', 'month', 'week_of_month'], how='left')

                
                # Order by year, month, week of the month, and order number
                df = df.sort_values(by=['year', 'month', 'week_of_month', 'order_number'])
        
                st.dataframe(df)



if __name__ == "__main__":
    main()
