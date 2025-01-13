import psycopg2
from psycopg2 import sql

def create_tables():
    """
    Create all necessary tables for the Retail Inventory Management System.
    """
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'manager', 'staff')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            product_sku VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id SERIAL PRIMARY KEY,
            supplier_name VARCHAR(255) NOT NULL,
            contact_info VARCHAR(255),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS supplier_products (
            supplier_id INT NOT NULL,
            product_id INT NOT NULL,
            PRIMARY KEY (supplier_id, product_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id SERIAL PRIMARY KEY,
            warehouse_name VARCHAR(255) NOT NULL,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS stores (
            store_id SERIAL PRIMARY KEY,
            store_name VARCHAR(255) NOT NULL,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS store_stock (
            store_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT DEFAULT 0 CHECK (quantity >= 0),
            minimum_stock_level INT DEFAULT 0 CHECK (minimum_stock_level >= 0),
            reorder_point INT DEFAULT 0 CHECK (reorder_point >= 0),
            PRIMARY KEY (store_id, product_id),
            FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS warehouse_stock (
            warehouse_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT DEFAULT 0 CHECK (quantity >= 0),
            PRIMARY KEY (warehouse_id, product_id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS purchase_orders (
            purchase_order_id SERIAL PRIMARY KEY,
            supplier_id INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'canceled')),
            total_amount NUMERIC(10, 2) DEFAULT 0 CHECK (total_amount >= 0),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id SERIAL PRIMARY KEY,
            user_id INT,
            action TEXT NOT NULL,
            ip_address VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id SERIAL PRIMARY KEY,
            user_id INT,
            message TEXT NOT NULL,
            notification_type VARCHAR(50) CHECK (notification_type IN ('info', 'warning', 'error')),
            read_status BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_orders (
            sales_order_id SERIAL PRIMARY KEY,
            customer_id INT,
            store_id INT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount NUMERIC(10, 2) DEFAULT 0 CHECK (total_amount >= 0),
            FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE
        );
        """
    ]

    # Connect to PostgreSQL and execute commands
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="inventory_db", user="inventory_user", password="inventory_pass", host="localhost", port=5432
        )
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        print("Tables created successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_tables()
