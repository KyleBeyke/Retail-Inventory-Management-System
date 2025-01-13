import psycopg2
from psycopg2 import sql

def create_tables_and_views():
    """
    Connects to the PostgreSQL database and creates tables and views for the inventory management system.
    """
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="inventory_db",
            user="inventory_user",
            password="inventory_pass",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # SQL to create tables
        create_tables_sql = [
            # Suppliers table
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                contact_email VARCHAR(255),
                contact_phone VARCHAR(50),
                address TEXT
            );
            """,

            # Categories table
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
            """,

            # Products table
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                sku VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
                supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE SET NULL
            );
            """,

            # Warehouses table
            """
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location TEXT
            );
            """,

            # Stores table
            """
            CREATE TABLE IF NOT EXISTS stores (
                store_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location TEXT
            );
            """,

            # Stock table (for warehouses)
            """
            CREATE TABLE IF NOT EXISTS warehouse_stock (
                stock_id SERIAL PRIMARY KEY,
                warehouse_id INT REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity >= 0)
            );
            """,

            # Store stock table (for stores)
            """
            CREATE TABLE IF NOT EXISTS store_stock (
                stock_id SERIAL PRIMARY KEY,
                store_id INT REFERENCES stores(store_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity >= 0)
            );
            """,

            # Purchase orders table
            """
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_id SERIAL PRIMARY KEY,
                supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'Pending'
            );
            """,

            # Purchase order items table
            """
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                poi_id SERIAL PRIMARY KEY,
                po_id INT REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
                product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INT NOT NULL CHECK (quantity > 0)
            );
            """
        ]

        # Execute table creation SQL
        for table_sql in create_tables_sql:
            cursor.execute(table_sql)

        # SQL to create a view for total inventory per product
        create_view_sql = """
        CREATE OR REPLACE VIEW total_inventory AS
        SELECT
            p.product_id,
            p.name AS product_name,
            COALESCE(SUM(ws.quantity), 0) AS total_warehouse_stock,
            COALESCE(SUM(ss.quantity), 0) AS total_store_stock,
            (COALESCE(SUM(ws.quantity), 0) + COALESCE(SUM(ss.quantity), 0)) AS total_stock
        FROM products p
        LEFT JOIN warehouse_stock ws ON p.product_id = ws.product_id
        LEFT JOIN store_stock ss ON p.product_id = ss.product_id
        GROUP BY p.product_id, p.name;
        """

        # Execute view creation SQL
        cursor.execute(create_view_sql)

        # Commit changes
        conn.commit()
        print("Tables and views created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables_and_views()
