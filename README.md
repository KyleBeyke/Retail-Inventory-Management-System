The **BeykeTechnik Retail Inventory Management System** is a Python-based inventory management and point-of-sale (POS) solution designed for small to medium-sized retailers. It supports both local operation and integration with third-party POS systems such as WooCommerce. The system is tailored to streamline inventory control, product categorization, supplier management, and sales tracking, while remaining scalable to accommodate future business growth.

---

## Features

- **Inventory Management**
  - Track stock levels, departments, categories, and subcategories.
  - Monitor stock across multiple stores and warehouses.
  - Support for detailed product attributes such as size, color, and custom tags.

- **Supplier and Purchase Order Management**
  - Maintain supplier contact details and manage supplier-product relationships.
  - Create and track purchase orders, linking them to stock updates.

- **Point of Sale (POS)**
  - Integrate with third-party POS systems (e.g., Square or WooCommerce).
  - Custom local POS option for in-store sales, including receipt printing and barcode scanning.

- **Reporting and Insights**
  - Generate detailed sales and inventory reports.
  - Track sales trends and monitor inventory performance.

- **User-Friendly GUI**
  - Built using PyQt for an intuitive and responsive interface.
  - Robust error handling and logging for ease of use and reliability.

- **Scalability**
  - Designed to support multi-store and multi-warehouse operations.
  - Ready for future integration with WooCommerce and other e-commerce platforms.

---

## Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: Python 3.9 or later
- **Database**: PostgreSQL
- **Libraries**:
  - psycopg2
  - PyQt5
  - logging
  - other dependencies listed in `requirements.txt`

---

## Installation

1. **Clone the Repository**:
git clone <repository_url> cd BeykeTechnik-Inventory-System

2. **Set Up the Database**:
- Install PostgreSQL and create a new database for the system.
- Use the provided `setup_database.py` script to initialize the database schema:
  ```
  python setup_database.py
  ```

3. **Install Dependencies**:
Install required Python packages using `pip`:
pip install -r requirements.txt


4. **Configure the Application**:
Update the configuration file (`config.ini`) with your database credentials and other system settings.

5. **Run the Application**:
Launch the main application:
python main.py

---

## Usage

- **Adding Products**:
Use the GUI to add products with details such as SKU, size, color, and pricing.

- **Managing Suppliers**:
Link products to suppliers and create purchase orders directly in the system.

- **Tracking Inventory**:
Monitor stock levels in real time and generate alerts for low inventory.

- **Sales and Reporting**:
Process sales transactions through the POS system and generate detailed reports for analysis.

---

## Support

For questions, bug reports, or feature requests, please contact the developer:

**Kyle Beyke**  
Email: [kyle.beyke@gmail.com](mailto:kyle.beyke@gmail.com)  
Location: Tennessee, USA  

---

## License

This project is licensed under the **BeykeTechnik Retail Inventory Management System License**.  
See the `LICENSE` file for full details.

---

## Future Enhancements

- Multi-currency handling for international transactions.
- Enhanced WooCommerce integration for seamless online and offline synchronization.
- Mobile app support for on-the-go inventory management.

---

Thank you for choosing the BeykeTechnik Retail Inventory Management System!
