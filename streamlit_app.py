import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import datetime
import numpy as np


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

    conn.close()

@st.cache(allow_output_mutation=True)
def get_data(query):
    conn = sqlite3.connect('marketing_funnels.db')
    return pd.read_sql_query(query, conn)

def visualize_funnel(df):
    df['conversion_rate'] = df['realizations'].pct_change() + 1
    fig, ax = plt.subplots()
    bars = ax.bar(df['id'].astype(str) + ' ' + df['name'], df['realizations'], color='blue')
    for bar, rate in zip(bars, df['conversion_rate']):
        if np.isfinite(bar.get_height()) and np.isfinite(rate):
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(rate, 2), ha='center', va='bottom')
    plt.xlabel('Funnel Step (ID, Name)')
    plt.ylabel('Realizations')
    st.pyplot(fig)

def main():
    st.title("Marketing Funnels")
    menu = ["Home", "Add registration", "Add funnel step", "Visualize funnel"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Home":
        st.subheader("Home")
    elif choice == "Add registration":
        st.subheader("Add a new registration")
        df_funnel_steps = get_data("SELECT * FROM funnel_steps")
        funnel_step_id = st.selectbox("Funnel step ID", df_funnel_steps['id'])
        description = st.text_input("Description")
        realizations = st.number_input("Realizations", min_value=0, value=0, step=1)
        if st.button("Add"):
            conn = sqlite3.connect('marketing_funnels.db')
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO registrations (funnel_step_id, description, realizations, date)
            VALUES (?, ?, ?, ?)
            """, (funnel_step_id, description, realizations, datetime.datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            st.success("Registration added successfully!")
    elif choice == "Add funnel step":
        st.subheader("Add a new funnel step")
        name = st.text_input("Name")
        order_number = st.number_input("Order number", min_value=0, value=0, step=1)
        if st.button("Add"):
            conn = sqlite3.connect('marketing_funnels.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO funnel_steps (name, order_number) VALUES (?, ?)", (name, order_number))
            conn.commit()
            conn.close()
            st.success("Funnel step added successfully!")
    elif choice == "Visualize funnel":
        st.subheader("Funnel visualization")
        df = get_data("""
        SELECT
            funnel_steps.id,
            funnel_steps.name,
            SUM(registrations.realizations) AS realizations
        FROM funnel_steps
        LEFT JOIN registrations ON funnel_steps.id = registrations.funnel_step_id
        GROUP BY funnel_steps.id
        ORDER BY funnel_steps.order_number
        """)
        visualize_funnel(df)


if __name__ == "__main__":
    create_tables()
    main()
