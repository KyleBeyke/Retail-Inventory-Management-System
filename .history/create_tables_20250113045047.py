import psycopg2
from psycopg2 import sql

def create_tables():
    commands = [
        # Users Table
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role_id INTEGER REFERENCES roles(role_id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Roles Table
        """
        CREATE TABLE IF NOT EXISTS roles (
            role_id SERIAL PRIMARY KEY,
            role_name VARCHAR(50) UNIQUE NOT NULL
        );
        """,
        # Products Table
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            sku VARCHAR(50) UNIQUE NOT NULL,
            category_id INTEGER REFERENCES categories(category_id),
            price NUMERIC(10, 2) CHECK (price >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Categories Table
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) UNIQUE NOT NULL,
            department_id INTEGER REFERENCES departments(department_id)
        );
        """,
        # Departments Table
        """
        CREATE TABLE IF NOT EXISTS departments (
            department_id SERIAL PRIMARY KEY,
            department_name VARCHAR(100) UNIQUE NOT NULL
        );
        """,
        # Warehouses Table
        """
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id SERIAL PRIMARY KEY,
            warehouse_name VARCHAR(100) UNIQUE NOT NULL,
            location VARCHAR(255)
        );
        """,
        # Stores Table
        """
        CREATE TABLE IF NOT EXISTS stores (
            store_id SERIAL PRIMARY KEY,
            store_name VARCHAR(100) UNIQUE NOT NULL,
            location VARCHAR(255)
        );
        """,
        # Inventory Table
        """
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id),
            warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
            quantity INTEGER CHECK (quantity >= 0),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (product_id, warehouse_id)
        );
        """,
        # Store Stock Table
        """
        CREATE TABLE IF NOT EXISTS store_stock (
            stock_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id),
            store_id INTEGER REFERENCES stores(store_id),
            quantity INTEGER CHECK (quantity >= 0),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (product_id, store_id)
        );
        """,
        # Suppliers Table
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id SERIAL PRIMARY KEY,
            supplier_name VARCHAR(100) UNIQUE NOT NULL,
            contact_info VARCHAR(255),
            address VARCHAR(255)
        );
        """,
        # Supplier Products Table (Many-to-Many Relationship)
        """
        CREATE TABLE IF NOT EXISTS supplier_products (
            supplier_id INTEGER REFERENCES suppliers(supplier_id),
            product_id INTEGER REFERENCES products(product_id),
            PRIMARY KEY (supplier_id, product_id)
        );
        """,
        # Purchase Orders Table
        """
        CREATE TABLE IF NOT EXISTS purchase_orders (
            order_id SERIAL PRIMARY KEY,
            supplier_id INTEGER REFERENCES suppliers(supplier_id),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) NOT NULL
        );
        """,
        # Purchase Order Items Table
        """
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES purchase_orders(order_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER CHECK (quantity > 0),
            unit_price NUMERIC(10, 2) CHECK (unit_price >= 0)
        );
        """,
        # Sales Table
        """
        CREATE TABLE IF NOT EXISTS sales (
            sale_id SERIAL PRIMARY KEY,
            store_id INTEGER REFERENCES stores(store_id),
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount NUMERIC(10, 2) CHECK (total_amount >= 0)
        );
        """,
        # Sales Items Table
        """
        CREATE TABLE IF NOT EXISTS sales_items (
            sale_item_id SERIAL PRIMARY KEY,
            sale_id INTEGER REFERENCES sales(sale_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER CHECK (quantity > 0),
            unit_price NUMERIC(10, 2) CHECK (unit_price >= 0)
        );
        """,
        # Audit Logs Table
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            action VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Notifications Table
        """
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Synchronization Logs Table
        """
        CREATE TABLE IF NOT EXISTS sync_logs (
            sync_id SERIAL PRIMARY KEY,
            sync_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Reports Table (Optional)
        """
        CREATE TABLE IF NOT EXISTS reports (
            report_id SERIAL PRIMARY KEY,
            report_name VARCHAR(100) NOT NULL,
            report_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="inventory_db",
            user="inventory_user",
            password="inventory_pass",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        # Execute each command to create tables
        for command in commands:
            cur.execute(command)
        # Commit the changes
        conn.commit()
        # Close communication with the database
        cur.close()
        conn.close()
        print("Tables created successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn is not None:
            conn.rollback()
            cur.close()
            conn.close()

if __name__ == "__main__":
    create_tables()
