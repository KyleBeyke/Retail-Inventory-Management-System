import psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    "dbname": "inventory_db",
    "user": "inventory_user",
    "password": "inventory_pass",
    "host": "localhost",
    "port": 5432
}

def create_tables():
    """
    Create all necessary tables for the Inventory Management System.
    Includes constraints, indexes, and relationships for normalization.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # SQL commands for table creation
        tables = [
            # Users Table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Products Table
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                sku VARCHAR(50) NOT NULL UNIQUE,
                price NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Suppliers Table
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id SERIAL PRIMARY KEY,
                supplier_name VARCHAR(100) NOT NULL,
                contact_info VARCHAR(255),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Supplier-Product Relationship Table
            """
            CREATE TABLE IF NOT EXISTS supplier_products (
                supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                PRIMARY KEY (supplier_id, product_id)
            );
            """,

            # Warehouses Table
            """
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Stores Table
            """
            CREATE TABLE IF NOT EXISTS stores (
                store_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Inventory Table (Warehouse Stock)
            """
            CREATE TABLE IF NOT EXISTS warehouse_stock (
                warehouse_id INT REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity >= 0),
                PRIMARY KEY (warehouse_id, product_id)
            );
            """,

            # Store Stock Table
            """
            CREATE TABLE IF NOT EXISTS store_stock (
                store_id INT REFERENCES stores(store_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity >= 0),
                PRIMARY KEY (store_id, product_id)
            );
            """,

            # Purchase Orders Table
            """
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_id SERIAL PRIMARY KEY,
                supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) NOT NULL CHECK (status IN ('Pending', 'Completed', 'Cancelled')),
                total_cost NUMERIC(12, 2) NOT NULL
            );
            """,

            # Purchase Order Details Table
            """
            CREATE TABLE IF NOT EXISTS purchase_order_details (
                po_id INT REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity > 0),
                cost_per_unit NUMERIC(10, 2) NOT NULL,
                PRIMARY KEY (po_id, product_id)
            );
            """,

            # Sales Table
            """
            CREATE TABLE IF NOT EXISTS sales (
                sale_id SERIAL PRIMARY KEY,
                store_id INT REFERENCES stores(store_id) ON DELETE SET NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount NUMERIC(12, 2) NOT NULL
            );
            """,

            # Sale Details Table
            """
            CREATE TABLE IF NOT EXISTS sale_details (
                sale_id INT REFERENCES sales(sale_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity > 0),
                price_per_unit NUMERIC(10, 2) NOT NULL,
                PRIMARY KEY (sale_id, product_id)
            );
            """,

            # Audit Log Table
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        # Execute each table creation command
        for table in tables:
            cursor.execute(table)

        conn.commit()
        print("All tables created successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating tables: {error}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_tables()
