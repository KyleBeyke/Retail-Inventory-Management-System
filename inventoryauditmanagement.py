import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="inventory_audit_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class InventoryAuditManagement:
    """
    A class to manage inventory audits to reconcile physical stock with system records.
    """

    def __init__(self, db_config):
        """
        Initialize the InventoryAuditManagement class with database connection configuration.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        """
        self.db_config = db_config

    def _connect(self):
        """
        Establish a connection to the PostgreSQL database.
        :return: A psycopg2 connection object.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def initiate_audit(self, location_type, location_id, product_id, physical_count):
        """
        Reconcile the physical count of a product at a specific store or warehouse.
        :param location_type: 'store' or 'warehouse'.
        :param location_id: ID of the store or warehouse.
        :param product_id: ID of the product being audited.
        :param physical_count: Physical count of the product.
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_location_type(location_type, ["store", "warehouse"])
        DataValidationManagement.validate_positive_integer(location_id, f"{location_type.capitalize()} ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        DataValidationManagement.validate_non_negative_integer(physical_count, "Physical Count")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Determine stock table
                if location_type == "store":
                    table = "store_stock"
                elif location_type == "warehouse":
                    table = "warehouse_stock"

                # Get current stock
                query = sql.SQL("""
                    SELECT quantity
                    FROM {table}
                    WHERE {location_column} = %s AND product_id = %s;
                """).format(
                    table=sql.Identifier(table),
                    location_column=sql.Identifier(f"{location_type}_id")
                )
                cursor.execute(query, (location_id, product_id))
                result = cursor.fetchone()

                if not result:
                    raise ValueError(f"No stock record found for {location_type} ID {location_id}, Product ID {product_id}.")

                recorded_quantity = result[0]

                # Calculate discrepancy
                discrepancy = physical_count - recorded_quantity

                # Log audit record
                log_query = """
                    INSERT INTO inventory_audits (location_type, location_id, product_id, recorded_quantity, physical_count, discrepancy)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(log_query, (location_type, location_id, product_id, recorded_quantity, physical_count, discrepancy))

                # Update stock levels if there is a discrepancy
                if discrepancy != 0:
                    update_query = sql.SQL("""
                        UPDATE {table}
                        SET quantity = %s
                        WHERE {location_column} = %s AND product_id = %s;
                    """).format(
                        table=sql.Identifier(table),
                        location_column=sql.Identifier(f"{location_type}_id")
                    )
                    cursor.execute(update_query, (physical_count, location_id, product_id))

                conn.commit()
                logging.info(f"Audit completed for {location_type.capitalize()} ID {location_id}, Product ID {product_id}. "
                             f"Discrepancy: {discrepancy}.")
        except Error as e:
            logging.error(f"Error initiating audit for {location_type.capitalize()} ID {location_id}, Product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def get_audit_records(self, location_type=None, location_id=None, product_id=None):
        """
        Retrieve inventory audit records, optionally filtered by location or product.
        :param location_type: Filter by 'store' or 'warehouse' (optional).
        :param location_id: Filter by specific store or warehouse ID (optional).
        :param product_id: Filter by specific product ID (optional).
        :return: A list of dictionaries containing audit records.
        """
        # Validate inputs
        if location_type:
            DataValidationManagement.validate_location_type(location_type, ["store", "warehouse"])
        if location_id:
            DataValidationManagement.validate_positive_integer(location_id, f"{location_type.capitalize()} ID")
        if product_id:
            DataValidationManagement.validate_positive_integer(product_id, "Product ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT audit_id, location_type, location_id, product_id, recorded_quantity, physical_count, discrepancy, audit_date
                FROM inventory_audits
                WHERE (%s IS NULL OR location_type = %s)
                  AND (%s IS NULL OR location_id = %s)
                  AND (%s IS NULL OR product_id = %s);
                """
                cursor.execute(query, (location_type, location_type, location_id, location_id, product_id, product_id))
                results = cursor.fetchall()
                audits = [
                    {
                        "audit_id": row[0],
                        "location_type": row[1],
                        "location_id": row[2],
                        "product_id": row[3],
                        "recorded_quantity": row[4],
                        "physical_count": row[5],
                        "discrepancy": row[6],
                        "audit_date": row[7],
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(audits)} inventory audit records.")
                return audits
        except Error as e:
            logging.error(f"Error retrieving inventory audit records: {e}")
            raise
        finally:
            conn.close()

    def delete_audit_record(self, audit_id):
        """
        Delete an inventory audit record.
        :param audit_id: ID of the audit record to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(audit_id, "Audit ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM inventory_audits
                WHERE audit_id = %s;
                """
                cursor.execute(query, (audit_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No audit record found with ID {audit_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted inventory audit record with ID {audit_id}.")
        except Error as e:
            logging.error(f"Error deleting inventory audit record with ID {audit_id}: {e}")
            raise
        finally:
            conn.close()
