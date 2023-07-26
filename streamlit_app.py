import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import streamlit as st

# Database functions
def create_tables():
    conn = sqlite3.connect('marketing_funnels.db')
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
    conn.close()

@st.cache(allow_output_mutation=True)
def get_data(query):
    conn = sqlite3.connect('marketing_funnels.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit app
def main():
    create_tables()

    st.title("Marketing Funnels")

    st.sidebar.title("Menu")
    menu = ["Home", "Add funnel step", "Add registration", "Add hypothesis", "View funnel", "View funnel by week"]
    choice = st.sidebar.selectbox("Choose an option", menu)

    if choice == "Home":
        st.write("Welcome to the Marketing Funnels app.")

    elif choice == "Add funnel step":
        st.subheader("Add a new funnel step")
        name = st.text_input("Enter the name of the funnel step")
        order_number = st.number_input("Enter the order number of the funnel step", value=1, step=1)
        if st.button("Add Funnel Step"):
            conn = sqlite3.connect('marketing_funnels.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO funnel_steps (name, order_number) VALUES (?, ?)", (name, order_number))
            conn.commit()
            conn.close()
            st.success("Funnel step added successfully.")

    elif choice == "Add registration":
        st.subheader("Add a new registration")
        # Fetch funnel steps
        df_funnel_steps = get_data("SELECT * FROM funnel_steps")
        funnel_step_id = st.selectbox("Select funnel step", df_funnel_steps['id'])
        description = st.text_input("Enter a description for the registration")
        realizations = st.number_input("Enter the number of realizations", value=1, step=1)
        if st.button("Add Registration"):
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect('marketing_funnels.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO registrations (funnel_step_id, description, realizations, date) VALUES (?, ?, ?, ?)", (funnel_step_id, description, realizations, date))
            conn.commit()
            conn.close()
            st.success("Registration added successfully.")

    elif choice == "Add hypothesis":
        st.subheader("Add a new hypothesis")
        name = st.text_input("Enter the name of the hypothesis")
        description = st.text_input("Enter a description for the hypothesis")
        if st.button("Add Hypothesis"):
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect('marketing_funnels.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO hypotheses (name, description, date) VALUES (?, ?, ?)", (name, description, date))
            conn.commit()
            conn.close()
            st.success("Hypothesis added successfully.")

    elif choice == "View funnel":
        st.subheader("View funnel")
        start_date = st.date_input("Enter the start date")
        end_date = st.date_input("Enter the end date")
        if st.button("View Funnel"):
            df = get_data(f"""
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
            st.dataframe(df)

    elif choice == "View funnel by week":
        st.subheader("View funnel by week")
        start_date = st.date_input("Enter the start date")
        end_date = st.date_input("Enter the end date")
        if st.button("View Funnel by Week"):
            df = get_data(f"""
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
            st.dataframe(df)

if __name__ == "__main__":
    main()
