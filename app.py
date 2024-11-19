import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.drawing.image import Image
import matplotlib.pyplot as plt

# Initialize data (mock data for menu and inventory)
menu = {
    "Americano": 5.00,
    "Cappuccino": 6.00,
    "Latte": 6.50,
    "Caramel Macchiato": 7.00
}

default_inventory = {
    "coffee_beans": 1000,  # grams
    "milk": 500,           # ml
    "sugar": 200,          # grams
    "cups": 100            # count
}

# Initialize session state for order history, inventory, login status, loyalty points, and ratings
if "order_history" not in st.session_state:
    st.session_state["order_history"] = []
if "inventory" not in st.session_state:
    st.session_state["inventory"] = default_inventory.copy()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "is_customer" not in st.session_state:
    st.session_state["is_customer"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "loyalty_points" not in st.session_state:
    st.session_state["loyalty_points"] = {}
if "ratings" not in st.session_state:
    st.session_state["ratings"] = []

# Function to add loyalty points
def add_loyalty_points(customer_name, points):
    if customer_name in st.session_state["loyalty_points"]:
        st.session_state["loyalty_points"][customer_name] += points
    else:
        st.session_state["loyalty_points"][customer_name] = points

# Function to redeem loyalty points
def redeem_loyalty_points(customer_name, points_to_redeem):
    if customer_name in st.session_state["loyalty_points"]:
        if st.session_state["loyalty_points"][customer_name] >= points_to_redeem:
            st.session_state["loyalty_points"][customer_name] -= points_to_redeem
            st.success(f"{points_to_redeem} points redeemed successfully!")
        else:
            st.error("Not enough points to redeem.")
    else:
        st.error("Customer not found in loyalty program.")

# Function to save data to an Excel file
def save_data_to_excel():
    with pd.ExcelWriter("coffee_shop_data.xlsx", engine="openpyxl", mode="w") as writer:
        # Save order history
        if st.session_state["order_history"]:
            order_df = pd.DataFrame(st.session_state["order_history"])
            order_df.to_excel(writer, sheet_name="Order History", index=False)
        
        # Save inventory
        inventory_df = pd.DataFrame(st.session_state["inventory"].items(), columns=["Item", "Quantity"])
        inventory_df.to_excel(writer, sheet_name="Inventory", index=False)

        # Save revenue and sales breakdown
        total_sales = sum(order["price"] for order in st.session_state["order_history"])
        sales_summary = order_df["coffee_type"].value_counts()

        revenue_df = pd.DataFrame({
            "Metric": ["Total Revenue"],
            "Value": [total_sales]
        })
        revenue_df.to_excel(writer, sheet_name="Revenue Summary", index=False)

        sales_summary_df = pd.DataFrame(sales_summary).reset_index()
        sales_summary_df.columns = ["Coffee Type", "Count"]
        sales_summary_df.to_excel(writer, sheet_name="Sales Breakdown", index=False)

        # Save loyalty points
        loyalty_points_df = pd.DataFrame(st.session_state["loyalty_points"].items(), columns=["Customer", "Points"])
        loyalty_points_df.to_excel(writer, sheet_name="Loyalty Points", index=False)

        # Save ratings and feedback
        if st.session_state["ratings"]:
            ratings_df = pd.DataFrame(st.session_state["ratings"], columns=["Customer", "Rating", "Feedback"])
            ratings_df.to_excel(writer, sheet_name="Ratings and Feedback", index=False)
        st.title('Customer Rating')
        import pandas as pd
        data2 = pd.read_excel(ratings_df)

        fig, ax = plt.subplots()
        ax.bar(data2['Rating'], color='Lightgreen')
        st.pyplot(fig)

    # Load workbook to add charts
    wb = openpyxl.load_workbook("coffee_shop_data.xlsx")
    sheet = wb.create_sheet(title="Charts")

    # Generate and save chart as an image
    if not sales_summary.empty:
        plt.figure(figsize=(8, 6))
        sales_summary.plot(kind='bar', title="Sales Breakdown by Coffee Type")
        plt.xlabel("Coffee Type")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("sales_chart.png")

        # Insert image into Excel
        img = Image("sales_chart.png")
        sheet.add_image(img, "A1")

    # Save the workbook with the chart embedded
    wb.save("coffee_shop_data.xlsx")
    st.success("Data with revenue, loyalty points, ratings, feedback, and graph saved to 'coffee_shop_data.xlsx' successfully!")

# Role selection buttons
st.sidebar.write("Select your role:")
if st.sidebar.button("Customer"):
    st.session_state["is_customer"] = True
    st.session_state["is_admin"] = False
    st.session_state["logged_in"] = True
    st.session_state["user_role"] = "customer"
    st.sidebar.success("Customer Access Granted")

if st.sidebar.button("Admin"):
    st.session_state["is_admin"] = True
    st.session_state["is_customer"] = False

# Show admin login fields if "Admin" button was clicked
if st.session_state["is_admin"]:
    username = st.sidebar.text_input("Username", key="admin_username")
    password = st.sidebar.text_input("Password", type="password", key="admin_password")
    if st.sidebar.button("Login as Admin"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["user_role"] = "admin"
            st.sidebar.success("Admin Access Granted")
        else:
            st.sidebar.error("Invalid admin credentials.")
            st.session_state["is_admin"] = False  # Reset admin flag if login fails

# App title
st.title("Coffee Shop App")

# Customer Order Process
if st.session_state["logged_in"] and st.session_state["user_role"] == "customer":
    st.subheader("Place Your Order")

    customer_name = st.text_input("Enter Your Name")
    coffee_type = st.selectbox("Select Coffee Type", list(menu.keys()))
    coffee_size = st.radio("Choose Size", ("Small", "Medium", "Large"))
    add_ons = st.multiselect("Add-ons", ["Extra sugar", "Milk"])

    if st.button("Place Order"):
        order = {
            "customer_name": customer_name,
            "coffee_type": coffee_type,
            "size": coffee_size,
            "add_ons": add_ons,
            "price": menu[coffee_type],
            "order_time": datetime.now()
        }
        st.session_state["order_history"].append(order)
        st.success(f"Order placed! Your coffee will be ready shortly. Order: {coffee_type} ({coffee_size})")

        # Add loyalty points (e.g., 1 point per $1 spent)
        points_earned = int(order["price"])
        add_loyalty_points(customer_name, points_earned)
        st.info(f"{points_earned} loyalty points added. Total points: {st.session_state['loyalty_points'].get(customer_name, 0)}")

        # Update Inventory based on order (basic example)
        st.session_state["inventory"]["coffee_beans"] -= 10  # Adjust amount as per recipe
        st.session_state["inventory"]["cups"] -= 1

# Customer Feedback and Rating System
if st.session_state["logged_in"] and st.session_state["user_role"] == "customer":
    st.subheader("Feedback and Rating")
    feedback = st.text_area("Rate your experience with us!")
    rating = st.slider("Rate us (1 to 5 stars)", 1, 5, 3)
    if st.button("Submit Feedback"):
        st.session_state["ratings"].append((customer_name, rating, feedback))
        st.success("Thank you for your feedback and rating!")

# Inventory Management (Admin Only)
if st.session_state["logged_in"] and st.session_state["user_role"] == "admin":
    st.subheader("Inventory Management")

    # Display current inventory levels
    st.write("Inventory Levels")
    for item, qty in st.session_state["inventory"].items():
        st.write(f"{item.capitalize()}: {qty} units")

    # Low stock alert
    for item, qty in st.session_state["inventory"].items():
        if qty < 20:
            st.warning(f"Low stock alert: {item}")

    # Update inventory
    item_to_restock = st.selectbox("Item to Restock", list(st.session_state["inventory"].keys()))
    restock_amount = st.number_input("Restock Amount", min_value=1)
    if st.button("Restock Inventory"):
        st.session_state["inventory"][item_to_restock] += restock_amount
        st.success(f"{item_to_restock.capitalize()} restocked successfully.")

    # Button to save data to Excel
    if st.button("Save Data to Excel"):
        save_data_to_excel()

# Sales Reporting (Admin Only)
if st.session_state["logged_in"] and st.session_state["user_role"] == "admin":
    st.subheader("Sales Reporting")

    # Display total sales
    sales_df = pd.DataFrame(st.session_state["order_history"])
    st.write("Total Sales Data")
    st.dataframe(sales_df)

    # Sales Breakdown by Coffee Type
    if not sales_df.empty:
        sales_summary = sales_df["coffee_type"].value_counts()
        st.bar_chart(sales_summary)

        # Total Profit Calculation (mock example)
        total_sales = sum(order["price"] for order in st.session_state["order_history"])
        st.write(f"Total Revenue: ${total_sales}")

    # Display loyalty points summary
    st.subheader("Loyalty Points Summary")
    loyalty_points_df = pd.DataFrame(st.session_state["loyalty_points"].items(), columns=["Customer", "Points"])
    st.dataframe(loyalty_points_df)

    # Display ratings summary
    st.subheader("Ratings Summary")
    if st.session_state["ratings"]:
        ratings_df = pd.DataFrame(st.session_state["ratings"], columns=["Customer", "Rating", "Feedback"])
        st.dataframe(ratings_df)
        avg_rating = ratings_df["Rating"].mean()
        st.write(f"Average Rating: {avg_rating:.2f} / 5")