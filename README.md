# Marketing Funnels with Streamlit
This project provides a Streamlit application for marketing funnel analysis. It enables creating, uploading, and downloading SQLite databases to track marketing funnels, registrations, and hypotheses. The application presents the marketing funnel data in a weekly view, showing conversion rates and any hypotheses created during the week.

Try: https://marketingfunnelsgestor-y5o3fozhgo.streamlit.app/

## Project Structure
The project comprises a single Python script, which contains both the Streamlit application and SQLite database interactions. The code is organized into several parts:

## Database functions: This section defines the functions create_tables and get_data used for database interactions. The create_tables function initializes the database with the necessary tables: funnel_steps, registrations, and hypotheses. The get_data function executes SQL queries and returns the results as pandas DataFrames.

## Streamlit application: This section defines the user interface and interactions of the application. The main function main creates the Streamlit interface, which includes menus for different actions (e.g., creating a new database, adding funnel steps, viewing funnel data, etc.), file uploaders, and data presentation widgets.

## How to Use
The application provides a sidebar menu with several options:

- Home: Displays a welcome message.
- Upload DB: Allows users to upload an existing SQLite database file. Any existing database is removed and replaced by the uploaded one.
- Download DB: Allows users to download the current database as an SQLite file.
- Create new DB: Allows users to create a new, empty database. Any existing database is removed.
- Add funnel step: Allows users to add a new funnel step to the database.
- Add registration: Allows users to add a new registration to the database.
- Add hypothesis: Allows users to add a new hypothesis to the database.
- View funnel: Allows users to view the funnel data for a specific date range. The data includes conversion rates for each step in the funnel.
- View funnel by week: Allows users to view weekly funnel data, including conversion rates and any hypotheses created during the week. The data is presented in a - table, with one row per week.
- 
## Implementation Details
The application uses SQLite for data storage, pandas for data manipulation, and Streamlit for the user interface.

The funnel data includes the number of realizations (e.g., conversions) at each step in the funnel. Conversion rates are calculated by dividing the realizations at a given step by the realizations at the previous step.

When viewing funnel data by week, any hypotheses created during the week are included in the data. If multiple hypotheses are created in the same week, their names and descriptions are concatenated into a single string.

## Requirements
The application requires Python 3.6 or later and the following Python libraries:

streamlit
pandas
sqlite3
matplotlib
datetime
os
shutil

## Running the Application
To run the application, navigate to the project directory in the terminal and run the command streamlit run app.py, where app.py is the name of the Python script. The application will open in a new browser window
