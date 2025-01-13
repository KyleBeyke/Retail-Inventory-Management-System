import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="inventory_adjustment_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class InventoryAdjustmentManagement:
    """
    A class to manage inventory adjustments across stores and warehouses.
    """

    def __init__(self, db_config):
        """
        Initialize the InventoryAdjustmentManagement class with database connection configuration.
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

    def adjust_inventory(self, location_type, location_id, product_id, adjustment_quantity, reason):
        """
        Adjust the inventory for a specific product at a store or warehouse.
        :param location_type: 'store' or 'warehouse'.
        :param location_id: ID of the store or warehouse.
        :param product_id: ID of the product.
        :param adjustment_quantity: Positive or negative quantity to adjust.
        :param reason: Reason for the adjustment (e.g., "damaged", "restocked").
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_location_type(location_type, ["store", "warehouse"])
        DataValidationManagement.validate_positive_integer(location_id, f"{location_type.capitalize()} ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        DataValidationManagement.validate_non_zero_integer(adjustment_quantity, "Adjustment Quantity")
        DataValidationManagement.validate_string(reason, "Reason")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                if location_type == "store":
                    table = "store_stock"
                elif location_type == "warehouse":
                    table = "warehouse_stock"

                # Adjust stock
                adjustment_query = sql.SQL("""
                    UPDATE {table}
                    SET quantity = quantity + %s
                    WHERE {location_column} = %s AND product_id = %s;
                """).format(
                    table=sql.Identifier(table),
                    location_column=sql.Identifier(f"{location_type}_id")
                )
                cursor.execute(adjustment_query, (adjustment_quantity, location_id, product_id))

                if cursor.rowcount == 0:
                    raise ValueError(f"Invalid {location_type} ID or product ID, or stock record does not exist.")

                # Log adjustment
                log_query = """
                    INSERT INTO inventory_adjustments (location_type, location_id, product_id, adjustment_quantity, reason)
                    VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(log_query, (location_type, location_id, product_id, adjustment_quantity, reason))
                conn.commit()
                logging.info(f"Adjusted inventory: {location_type.capitalize()} ID {location_id}, Product ID {product_id}, "
                             f"Quantity {adjustment_quantity}, Reason: {reason}.")
        except Error as e:
            logging.error(f"Error adjusting inventory for {location_type.capitalize()} ID {location_id}, Product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def get_adjustments(self, location_type=None, location_id=None, product_id=None):
        """
        Retrieve inventory adjustment records, optionally filtered by location or product.
        :param location_type: Filter by 'store' or 'warehouse' (optional).
        :param location_id: Filter by specific store or warehouse ID (optional).
        :param product_id: Filter by specific product ID (optional).
        :return: A list of dictionaries containing adjustment records.
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
                SELECT adjustment_id, location_type, location_id, product_id, adjustment_quantity, reason, adjustment_date
                FROM inventory_adjustments
                WHERE (%s IS NULL OR location_type = %s)
                  AND (%s IS NULL OR location_id = %s)
                  AND (%s IS NULL OR product_id = %s);
                """
                cursor.execute(query, (location_type, location_type, location_id, location_id, product_id, product_id))
                results = cursor.fetchall()
                adjustments = [
                    {
                        "adjustment_id": row[0],
                        "location_type": row[1],
                        "location_id": row[2],
                        "product_id": row[3],
                        "adjustment_quantity": row[4],
                        "reason": row[5],
                        "adjustment_date": row[6],
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(adjustments)} inventory adjustment records.")
                return adjustments
        except Error as e:
            logging.error(f"Error retrieving inventory adjustments: {e}")
            raise
        finally:
            conn.close()

    def delete_adjustment(self, adjustment_id):
        """
        Delete an inventory adjustment record.
        :param adjustment_id: ID of the adjustment to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(adjustment_id, "Adjustment ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM inventory_adjustments
                WHERE adjustment_id = %s;
                """
                cursor.execute(query, (adjustment_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No adjustment record found with ID {adjustment_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted inventory adjustment record with ID {adjustment_id}.")
        except Error as e:
            logging.error(f"Error deleting inventory adjustment record with ID {adjustment_id}: {e}")
            raise
        finally:
            conn.close()
