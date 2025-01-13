import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="create_tables.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_tables(db_config):
    """
    Create tables for the Retail Inventory Management System.
    :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
    """
    tables = {
        "suppliers": """
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id SERIAL PRIMARY KEY,
                supplier_name VARCHAR(255) NOT NULL,
                contact_info TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "products": """
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL,
                sku VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL,
                category_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE SET NULL
            );
        """,
        "categories": """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                category_name VARCHAR(255) NOT NULL,
                parent_category_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_parent_category FOREIGN KEY (parent_category_id) REFERENCES categories (category_id) ON DELETE SET NULL
            );
        """,
        "warehouses": """
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id SERIAL PRIMARY KEY,
                warehouse_name VARCHAR(255) NOT NULL,
                location TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "store_stock": """
            CREATE TABLE IF NOT EXISTS store_stock (
                stock_id SERIAL PRIMARY KEY,
                store_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT DEFAULT 0,
                CONSTRAINT fk_store FOREIGN KEY (store_id) REFERENCES stores (store_id) ON DELETE CASCADE,
                CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
            );
        """,
        "stores": """
            CREATE TABLE IF NOT EXISTS stores (
                store_id SERIAL PRIMARY KEY,
                store_name VARCHAR(255) NOT NULL,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "supplier_products": """
            CREATE TABLE IF NOT EXISTS supplier_products (
                supplier_product_id SERIAL PRIMARY KEY,
                supplier_id INT NOT NULL,
                product_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE CASCADE,
                CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
            );
        """,
        "purchase_orders": """
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_id SERIAL PRIMARY KEY,
                supplier_id INT NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount NUMERIC(12, 2),
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE SET NULL
            );
        """,
        "audit_logs": """
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id SERIAL PRIMARY KEY,
                user_id INT,
                action VARCHAR(255) NOT NULL,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            );
        """
    }

    try:
        # Establish the database connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Create each table
        for table_name, table_query in tables.items():
            logging.info(f"Creating table: {table_name}")
            cursor.execute(table_query)
            logging.info(f"Table {table_name} created successfully.")

        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("All tables created successfully.")
    except Error as e:
        logging.error(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    create_tables(db_config)
