import psycopg2
import logging

# Configure logging
logging.basicConfig(
    filename="datasynchronization.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataSynchronizationManagement:
    """
    A class to handle data synchronization between database tables or external systems.
    """

    def __init__(self, db_connection):
        """
        Initialize the DataSynchronizationManagement class.
        :param db_connection: A psycopg2 connection object to the database.
        """
        self.db_connection = db_connection

    def synchronize_tables(self, source_table, target_table, key_column, columns_to_sync):
        """
        Synchronize data from a source table to a target table based on a key column.
        :param source_table: The source table name.
        :param target_table: The target table name.
        :param key_column: The column used to match rows between tables.
        :param columns_to_sync: A list of columns to synchronize.
        :return: None.
        """
        try:
            logging.info(f"Starting synchronization from {source_table} to {target_table}...")
            with self.db_connection.cursor() as cursor:
                for column in columns_to_sync:
                    query = f"""
                    UPDATE {target_table} AS t
                    SET {column} = s.{column}
                    FROM {source_table} AS s
                    WHERE t.{key_column} = s.{key_column};
                    """
                    cursor.execute(query)
                self.db_connection.commit()
            logging.info(f"Synchronization completed between {source_table} and {target_table}.")
        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
            raise

    def synchronize_external_system(self, external_data, table_name, key_column):
        """
        Synchronize data from an external system into a database table.
        :param external_data: A list of dictionaries representing external data.
        :param table_name: The target database table name.
        :param key_column: The column used to match rows in the database.
        :return: None.
        """
        try:
            logging.info(f"Starting synchronization with external system into {table_name}...")
            with self.db_connection.cursor() as cursor:
                for record in external_data:
                    set_clause = ", ".join([f"{key} = %s" for key in record.keys()])
                    values = list(record.values())
                    values.append(record[key_column])
                    query = f"""
                    INSERT INTO {table_name} ({", ".join(record.keys())})
                    VALUES ({", ".join(["%s"] * len(record))})
                    ON CONFLICT ({key_column})
                    DO UPDATE SET {set_clause};
                    """
                    cursor.execute(query, values)
                self.db_connection.commit()
            logging.info(f"Synchronization with external system completed for {table_name}.")
        except Exception as e:
            logging.error(f"Error during external system synchronization: {e}")
            raise
