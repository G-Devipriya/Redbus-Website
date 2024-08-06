import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from datetime import datetime, timedelta



# # Function to establish a database connection
# def database_connection(query):
    
#     engine = create_engine("mysql+pymysql://root:12345@localhost:3306/redbus_table")
#     with engine.connect() as conn:
#         df = pd.read_sql(query,conn)
#     return df

# Function to convert timedelta to datetime.time object
def convert_time_delta(timedelta):
    startTime = (datetime.min + timedelta).time().strftime("%H:%M")
    return startTime


# Function to connect to the database and fetch data
def database_connection(query):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='12345',
        database='redbus_table',
        port=3306
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

    # Convert the result into a pandas DataFrame
    data = pd.DataFrame(result, columns=column_names)
    return data

# Function to fetch unique values based on route name
def fetch_unique_values(route_name):
    query = f"SELECT DISTINCT departing_time, star_rating, price, seat_availability FROM bus_routes WHERE routename='{route_name}'"
    data = database_connection(query)
    return data

# Function to generate time intervals
def generate_time_intervals():
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("23:59", "%H:%M")
    interval = timedelta(minutes=30)
    times = []
    current_time = start_time
    while current_time <= end_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += interval
    return times


# Sidebar radio button for navigation
sidebar_radio = st.sidebar.radio(label="Main Menu", options=("Home","Search Buses"))

# Home page
if sidebar_radio == "Home":
    st.markdown("""**<h2>RedBus Site Information</h2>**""",True)
    Col1,Col2 = st.columns(2,gap="Large")
    Col1.image("E:/Guvi/VS_code/Red_Bus_Project/redbus_logo.jpeg", width=100)
    Col2.image("E:/Guvi/VS_code/Red_Bus_Project/google_play.jpeg", width=100)
    
    Col1.markdown("[RedBus Ticket Booking Site Link](https://www.redbus.in/)")
    Col2.markdown("[RedBus App Download Link](https://play.google.com/store/apps/details?id=in.redbus.android&hl=en_IN&pli=1)")
    st.video("https://youtu.be/kdSqTsAeNxo")

# Search Buses page  
elif sidebar_radio =="Search Buses":
    st.markdown("""<h3>Search Buses</h3>""",True)

    # Fetch distinct route names
    sql_query = "select DISTINCT routename from bus_routes"
    sql_data = database_connection(sql_query)
    

    # Extract unique route names
    busRoute_info = sql_data["routename"].unique()

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        bus_route = col1.selectbox("Select the Route", busRoute_info)

    # Fetch unique values based on selected route name
    if bus_route:
        unique_values = fetch_unique_values(bus_route)

        if unique_values is not None:

            rating_info = unique_values["star_rating"].unique()
            price_info = unique_values["price"].unique()
            seat_availability_info = unique_values["seat_availability"].unique()

            time_intervals = generate_time_intervals()

            with col1:
                price = col1.selectbox("Bus Fare Range(Start From)", price_info)
                
            with col2:
                departing_time_range_from = col2.selectbox("Departing Time Range From", time_intervals)
                star_rating = col2.selectbox("Star Rating", rating_info)

            with col3:
                departing_time_range_to = col3.selectbox("Departing Time Range To", time_intervals)
                seat_availability = col3.selectbox("Select Number of Seat Availablity", seat_availability_info)
                
            submit = st.button("Search")

            if submit:

                search_request_query = f"""
                    SELECT * FROM bus_routes
                    WHERE routename = "{bus_route}"
                    AND departing_time BETWEEN "{departing_time_range_from}" AND "{departing_time_range_to}"
                    AND star_rating >= {star_rating}
                    AND price >= {price}
                    AND seat_availability >= {seat_availability}
                    """

                # Fetch data using the generated query
                search_bus = database_connection(search_request_query)

                search_bus['departing_time'] = search_bus['departing_time'].apply(convert_time_delta)
                search_bus['reaching_time'] = search_bus['reaching_time'].apply(convert_time_delta)
                    
                
                # Check if DataFrame is empty
                if search_bus.empty:
                    st.warning("No results found.")  
                else:
                    st.success("Bus details are below")
                    st.dataframe(search_bus)
        else:
            st.error("No data found for the selected route")