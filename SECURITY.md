# Security Notes

This project should not include real credentials, production database details, customer data, or local runtime output.

Do not commit:

- `.env` files or local config files
- database passwords or service credentials
- exported reports containing real customer, supplier, or inventory data
- logs
- local database dumps
- virtual environments

If a secret or sensitive business dataset is accidentally published, rotate the affected credential and remove the sensitive data from git history before making the repository public.
