# Retail Inventory Management System

A Python-based inventory management prototype for small and medium-sized retailers. The project contains modules for products, suppliers, stores, warehouses, purchase orders, reporting, auditing, notifications, and PyQt-based management windows.

This repository is best treated as an application prototype and module library. It includes database schema setup helpers and individual management components, but it does not currently package a single production installer.

## Features

- Product, category, supplier, purchase order, store, and warehouse management modules.
- Store and warehouse stock tracking.
- Audit log, reporting, notification, backup, and maintenance helpers.
- PyQt window components for interactive management screens.
- PostgreSQL schema creation in `create_tables.py`.
- Integration-oriented modules for data import/export and ecommerce synchronization.

## Requirements

- Python 3.9+
- PostgreSQL
- Python dependencies listed in `requirements.txt`

## Setup

```bash
git clone https://github.com/KyleBeyke/Retail-Inventory-Management-System.git
cd Retail-Inventory-Management-System
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database

Create a PostgreSQL database/user for local development, then update the connection values in the modules you plan to run. The current repository uses example local values in several demo blocks.

Initialize the core tables:

```bash
python create_tables.py
```

## Run A GUI Demo

```bash
python guimanagement.py
```

Other window modules can be imported and registered through `NavigationManager` as the application shell is developed.

## Validate The Repository

```bash
scripts/validate.sh
```

The validation script compiles the Python files and checks that local/generated files such as `.history/`, `.DS_Store`, logs, and virtual environments are not tracked.

## Local Files

Do not commit:

- `.venv/` or `venv/`
- `.history/`
- `.DS_Store`
- logs
- local database dumps
- local configuration files with real credentials

## License

This project is licensed under the terms in [LICENSE.txt](LICENSE.txt).
