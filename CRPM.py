import mysql.connector
from mysql.connector import errorcode
import streamlit as st
import pandas as pd

# Database Class
class Database:
    def __init__(self, db_name="crpm_system"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_database()
        self.create_tables()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Change to your MySQL username
                password="Qdpfp7xsm2@"  # Change to your MySQL password
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Invalid MySQL username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def create_database(self):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            self.conn.database = self.db_name
        except mysql.connector.Error as err:
            print(f"Failed creating database: {err}")
            exit(1)

    def create_tables(self):
        # Create Customers Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                CustomerID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) UNIQUE NOT NULL,
                PhoneNumber VARCHAR(15) UNIQUE NOT NULL,
                Gender VARCHAR(10),
                Age INT,
                Location VARCHAR(255),
                PaymentMethod VARCHAR(100),
                ReviewRating INT,
                PurchaseFrequency VARCHAR(50),
                Status INT DEFAULT 1
            )
        """)
        # Create Products Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                ProductID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Price DECIMAL(10, 2) NOT NULL,
                StockQuantity INT NOT NULL,
                Status INT DEFAULT 1
            )
        """)
        # Create Purchases Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Purchases (
                PurchaseID INT AUTO_INCREMENT PRIMARY KEY,
                CustomerID INT NOT NULL,
                ProductID INT NOT NULL,
                Quantity INT NOT NULL,
                TotalCost DECIMAL(10, 2) NOT NULL,
                Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
                FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
            )
        """)
        self.conn.commit()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


# Customer Class
class Customer:
    def __init__(self, db):
        self.db = db

    def add_customer(self, name, email, phone, gender, age, location, payment_method, review_rating, frequency):
        query = """
            INSERT INTO Customers (Name, Email, PhoneNumber, Gender, Age, Location, PaymentMethod, ReviewRating, PurchaseFrequency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (name, email, phone, gender, age, location, payment_method, review_rating, frequency))

    def view_customers(self):
        query = "SELECT * FROM Customers WHERE Status = 1"
        return self.db.fetch_all(query)

    def update_customer(self, customer_id, name=None, email=None, phone=None, gender=None, age=None, location=None, payment_method=None, review_rating=None, frequency=None):
        set_values = []
        params = []
        if name:
            set_values.append("Name = %s")
            params.append(name)
        if email:
            set_values.append("Email = %s")
            params.append(email)
        if phone:
            set_values.append("PhoneNumber = %s")
            params.append(phone)
        if gender:
            set_values.append("Gender = %s")
            params.append(gender)
        if age:
            set_values.append("Age = %s")
            params.append(age)
        if location:
            set_values.append("Location = %s")
            params.append(location)
        if payment_method:
            set_values.append("PaymentMethod = %s")
            params.append(payment_method)
        if review_rating:
            set_values.append("ReviewRating = %s")
            params.append(review_rating)
        if frequency:
            set_values.append("PurchaseFrequency = %s")
            params.append(frequency)

        query = f"UPDATE Customers SET {', '.join(set_values)} WHERE CustomerID = %s"
        params.append(customer_id)
        self.db.execute_query(query, tuple(params))

    def delete_customer(self, customer_id):
        query = "UPDATE Customers SET Status = 0 WHERE CustomerID = %s"
        self.db.execute_query(query, (customer_id,))

    def record_purchase(self, customer_id, product_id, quantity):
        product = self.db.fetch_one("SELECT Price, StockQuantity FROM Products WHERE ProductID = %s", (product_id,))
        if product:
            price, stock_quantity = product
            if stock_quantity >= quantity:
                total_cost = price * quantity
                self.db.execute_query("UPDATE Products SET StockQuantity = StockQuantity - %s WHERE ProductID = %s", (quantity, product_id))
                self.db.execute_query(
                    "INSERT INTO Purchases (CustomerID, ProductID, Quantity, TotalCost) VALUES (%s, %s, %s, %s)",
                    (customer_id, product_id, quantity, total_cost)
                )
                return True, total_cost
            else:
                return False, "Not enough stock available."
        else:
            return False, "Product not found."


# Product Class
class Product:
    def __init__(self, db):
        self.db = db

    def add_product(self, name, price, stock_quantity):
        query = "INSERT INTO Products (Name, Price, StockQuantity) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (name, price, stock_quantity))

    def view_products(self):
        query = "SELECT * FROM Products WHERE Status = 1"
        return self.db.fetch_all(query)

    def update_product(self, product_id, name=None, price=None, stock_quantity=None):
        set_values = []
        params = []
        if name:
            set_values.append("Name = %s")
            params.append(name)
        if price:
            set_values.append("Price = %s")
            params.append(price)
        if stock_quantity:
            set_values.append("StockQuantity = %s")
            params.append(stock_quantity)

        query = f"UPDATE Products SET {', '.join(set_values)} WHERE ProductID = %s"
        params.append(product_id)
        self.db.execute_query(query, tuple(params))

    def delete_product(self, product_id):
        query = "UPDATE Products SET Status = 0 WHERE ProductID = %s"
        self.db.execute_query(query, (product_id,))


# Streamlit UI
db = Database()
customer_manager = Customer(db)
product_manager = Product(db)

st.title("Customer Relationship and Product Management System")

menu = st.sidebar.radio("Navigation", ["Customer Management", "Product Management", "Customer Purchases", "Analytics and Reports"])

if menu == "Customer Management":
    st.header("Customer Management")
    option = st.radio("Choose an option", ["Add Customer", "View Customers", "Update Customer", "Delete Customer"])

    if option == "Add Customer":
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        gender = st.radio("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=1)
        location = st.text_input("Location")
        payment_method = st.radio("Payment Method", ["Cash", "GPay", "PhonePay", "Apple Pay", "Debit Card", "Credit Card", "Bank Transfer"])
        review_rating = st.slider("Review Rating (0-5)", 0, 5)
        frequency = st.radio("Purchase Frequency", ["Fortnightly", "Weekly", "Monthly", "Annually"])
        if st.button("Add Customer"):
            customer_manager.add_customer(name, email, phone, gender, age, location, payment_method, review_rating, frequency)
            st.success("Customer added successfully")

    elif option == "View Customers":
        customers = customer_manager.view_customers()
        st.write(customers)

    elif option == "Update Customer":
        customer_id = st.number_input("Customer ID", min_value=1)
        if customer_id:
            customer = customer_manager.db.fetch_one("SELECT * FROM Customers WHERE CustomerID = %s", (customer_id,))
            if customer:
                name = st.text_input("Name", value=customer[1])
                email = st.text_input("Email", value=customer[2])
                phone = st.text_input("Phone Number", value=customer[3])
                gender = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(customer[4]))
                age = st.number_input("Age", min_value=1, value=customer[5])
                location = st.text_input("Location", value=customer[6])
                payment_method = st.radio("Payment Method", ["Cash", "GPay", "PhonePay", "Apple Pay", "Debit Card", "Credit Card", "Bank Transfer"], index=["Cash", "GPay", "PhonePay", "Apple Pay", "Debit Card", "Credit Card", "Bank Transfer"].index(customer[7]))
                review_rating = st.slider("Review Rating (0-5)", 0, 5, value=customer[8])
                frequency = st.radio("Purchase Frequency", ["Fortnightly", "Weekly", "Monthly", "Annually"], index=["Fortnightly", "Weekly", "Monthly", "Annually"].index(customer[9]))
                if st.button("Update Customer"):
                    customer_manager.update_customer(customer_id, name, email, phone, gender, age, location, payment_method, review_rating, frequency)
                    st.success("Customer updated successfully")
            else:
                st.warning("Customer not found")

    elif option == "Delete Customer":
        customer_id = st.number_input("Customer ID to delete", min_value=1)
        if st.button("Delete Customer"):
            customer_manager.delete_customer(customer_id)
            st.success("Customer deleted successfully")

elif menu == "Product Management":
    st.header("Product Management")
    option = st.radio("Choose an option", ["Add Product", "View Products", "Update Product", "Delete Product"])

    if option == "Add Product":
        name = st.text_input("Name")
        price = st.number_input("Price", min_value=0.0)
        stock_quantity = st.number_input("Stock Quantity", min_value=1)
        if st.button("Add Product"):
            product_manager.add_product(name, price, stock_quantity)
            st.success("Product added successfully")

    elif option == "View Products":
        products = product_manager.view_products()
        st.write(products)

    elif option == "Update Product":
        product_id = st.number_input("Product ID", min_value=1)
        if product_id:
            product = product_manager.db.fetch_one("SELECT * FROM Products WHERE ProductID = %s", (product_id,))
            if product:
                name = st.text_input("Name", value=product[1])
                price = st.number_input("Price", min_value=0.0, value=product[2])
                stock_quantity = st.number_input("Stock Quantity", min_value=0, value=product[3])
                if st.button("Update Product"):
                    product_manager.update_product(product_id, name, price, stock_quantity)
                    st.success("Product updated successfully")
            else:
                st.warning("Product not found")

    elif option == "Delete Product":
        product_id = st.number_input("Product ID to delete", min_value=1)
        if st.button("Delete Product"):
            product_manager.delete_product(product_id)
            st.success("Product deleted successfully")

elif menu == "Customer Purchases":
    st.header("Customer Purchases")
    
    # Record a New Purchase
    st.subheader("Record a New Purchase")
    customer_id = st.number_input("Customer ID", min_value=1, key="purchase_customer_id")
    product_id = st.number_input("Product ID", min_value=1, key="purchase_product_id")
    quantity = st.number_input("Quantity", min_value=1, key="purchase_quantity")
    
    if st.button("Record Purchase"):
        success, message = customer_manager.record_purchase(customer_id, product_id, quantity)
        if success:
            st.success(f"Purchase recorded successfully! Total cost: {message:.2f}")
        else:
            st.error(f"Error: {message}")

    # View Purchase History
    st.subheader("View Purchase History")
    purchase_history = customer_manager.db.fetch_all("""
        SELECT p.PurchaseID, c.Name, pr.Name AS ProductName, p.Quantity, p.TotalCost, p.Timestamp
        FROM Purchases p
        JOIN Customers c ON p.CustomerID = c.CustomerID
        JOIN Products pr ON p.ProductID = pr.ProductID
        ORDER BY p.Timestamp DESC
    """)
    
    if purchase_history:
        purchase_df = pd.DataFrame(purchase_history, columns=["PurchaseID", "CustomerName", "ProductName", "Quantity", "TotalCost", "Timestamp"])
        st.dataframe(purchase_df)
    else:
        st.warning("No purchase history found.")


elif menu == "Analytics and Reports":
    st.header("Analytics and Reports")

    # Generate Sales Reports
    st.subheader("Sales Report")
    
    try:
        # Total revenue generated
        total_revenue = customer_manager.db.fetch_one("""
            SELECT SUM(p.TotalCost) FROM Purchases p
        """)[0]
        
        # Total number of products sold
        total_products_sold = customer_manager.db.fetch_one("""
            SELECT SUM(p.Quantity) FROM Purchases p
        """)[0]
        
        # Update stock information (assuming you have stock information in the Products table)
        stock_updates = customer_manager.db.fetch_all("""
            SELECT pr.ProductID, pr.Name, pr.StockQuantity, SUM(p.Quantity) AS SoldQuantity
            FROM Products pr
            LEFT JOIN Purchases p ON pr.ProductID = p.ProductID
            GROUP BY pr.ProductID, pr.Name, pr.StockQuantity
        """)
        
        stock_df = pd.DataFrame(stock_updates, columns=["ProductID", "ProductName", "StockQuantity", "SoldQuantity"])
        stock_df['UpdatedStock'] = stock_df['StockQuantity'] - stock_df['SoldQuantity']
        
        st.write(f"Total Revenue Generated: ${total_revenue:.2f}")
        st.write(f"Total Products Sold: {total_products_sold}")
        st.write("Stock Updates:")
        st.dataframe(stock_df)
        
    except Exception as e:
        st.error(f"Error generating sales report: {e}")

    # Display Top Customers
    st.subheader("Top Customers")
    
    try:
        # Rank customers based on total spending
        top_customers = customer_manager.db.fetch_all("""
            SELECT c.Name, SUM(p.TotalCost) AS TotalSpent, COUNT(p.PurchaseID) AS Purchases
            FROM Customers c
            JOIN Purchases p ON c.CustomerID = p.CustomerID
            GROUP BY c.CustomerID
            ORDER BY TotalSpent DESC
            LIMIT 10
        """)
        
        top_customers_df = pd.DataFrame(top_customers, columns=["CustomerName", "TotalSpent", "Purchases"])
        st.dataframe(top_customers_df)
    
    except Exception as e:
        st.error(f"Error fetching top customers: {e}")
    
    # Visualize Product Performance
    st.subheader("Product Performance")
    
    try:
        # Best-selling products
        best_selling_products = customer_manager.db.fetch_all("""
            SELECT pr.Name, SUM(p.Quantity) AS TotalQuantitySold
            FROM Products pr
            JOIN Purchases p ON pr.ProductID = p.ProductID
            GROUP BY pr.ProductID
            ORDER BY TotalQuantitySold DESC
            LIMIT 10
        """)
        
        best_selling_df = pd.DataFrame(best_selling_products, columns=["ProductName", "TotalQuantitySold"])
        st.write("Top 10 Best-Selling Products:")
        st.dataframe(best_selling_df)
        
        # Least-selling products
        least_selling_products = customer_manager.db.fetch_all("""
            SELECT pr.Name, SUM(p.Quantity) AS TotalQuantitySold
            FROM Products pr
            LEFT JOIN Purchases p ON pr.ProductID = p.ProductID
            GROUP BY pr.ProductID
            ORDER BY TotalQuantitySold ASC
            LIMIT 10
        """)
        
        least_selling_df = pd.DataFrame(least_selling_products, columns=["ProductName", "TotalQuantitySold"])
        st.write("Top 10 Least-Selling Products:")
        st.dataframe(least_selling_df)
    
    except Exception as e:
        st.error(f"Error fetching product performance data: {e}")
