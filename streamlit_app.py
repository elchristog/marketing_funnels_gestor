import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np

# Create a connection to the database
conn = sqlite3.connect('marketing_funnels.db', check_same_thread=False)

@st.cache(allow_output_mutation=True)
def get_conn():
    return sqlite3.connect('marketing_funnels.db')

@st.cache(hash_funcs={sqlite3.Cursor: id})
def get_cursor(conn):
    return conn.cursor()

def create_tables():
    cur = get_cursor(conn)
    # Create the table for the funnel steps
    cur.execute("""
    CREATE TABLE IF NOT EXISTS funnel_steps (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        order_number INTEGER NOT NULL UNIQUE
    );
    """)

    # Modify the table for the registrations to include a description, realizations, and a date
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

    # Create the table for the hypotheses
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hypotheses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL
    );
    """)

def add_funnel_step(name, order_number):
    cur = get_cursor(conn)
    cur.execute("INSERT INTO funnel_steps (name, order_number) VALUES (?, ?)", (name, order_number))
    conn.commit()

def delete_funnel_step(id):
    cur = get_cursor(conn)
    cur.execute("DELETE FROM funnel_steps WHERE id = ?", (id,))
    conn.commit()

# Modify the add_registration function to include a description, realizations, and a date
def add_registration(funnel_step_id, description, realizations):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    cur = get_cursor(conn)
    cur.execute("""
    INSERT INTO registrations (funnel_step_id, description, realizations, date)
    VALUES (?, ?, ?, ?)
    """, (funnel_step_id, description, realizations, date))
    conn.commit()

def add_hypothesis(name, description):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    cur = get_cursor(conn)
    cur.execute("""
    INSERT INTO hypotheses (name, description, date)
    VALUES (?, ?, ?)
    """, (name, description, date))
    conn.commit()

def visualize_funnel(start_date=None, end_date=None):
    cur = get_cursor(conn)
    # Create the base of the SQL query
    sql_query = """
    SELECT
        funnel_steps.id,
        funnel_steps.name,
        SUM(registrations.realizations) AS realizations
    FROM funnel_steps
    LEFT JOIN registrations ON funnel_steps.id = registrations.funnel_step_id
    """
    # Add a WHERE clause to filter by date if start_date and end_date are provided
    if start_date and end_date:
        sql_query += f" WHERE date(registrations.date) BETWEEN '{start_date}' AND '{end_date}'"

    sql_query += """
    GROUP BY funnel_steps.id
    ORDER BY funnel_steps.order_number
    """

    df = pd.read_sql_query(sql_query, conn)

    df['conversion_rate'] = df['realizations'].pct_change() + 1

    plt.figure(figsize=(10, 6))

    bars = plt.bar(df['id'].astype(str) + ' ' + df['name'], df['realizations'], color='blue')

    for bar, rate in zip(bars, df['conversion_rate']):
        if np.isfinite(bar.get_height()) and np.isfinite(rate):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(rate, 2), ha='center', va='bottom')

    plt.xlabel('Funnel Step (ID, Name)')
    plt.ylabel('Realizations')
    st.pyplot(plt)

def main():
    st.title("Marketing Funnels")

    menu = ["Home", "Add funnel step", "Delete funnel step", "Add registration", 
            "View funnel", "Add hypothesis", "View funnel by week", 
            "Preview table"]
    choice = st.sidebar.selectbox("Choose an option", menu)

    if choice == "Add funnel step":
        st.subheader("Add Funnel Step")
        name = st.text_input("Enter the name of the funnel step")
        order_number = st.number_input("Enter the order number of the funnel step", value=1, step=1)
        if st.button("Add Funnel Step"):
            add_funnel_step(name, order_number)
            st.success("Added funnel step successfully!")

    elif choice == "View funnel":
        st.subheader("View Funnel")
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        if st.button("Show Funnel"):
            visualize_funnel(start_date, end_date)

    # Similar blocks for other choices...

if __name__ == "__main__":
    conn = get_conn()
    create_tables()
    main()
