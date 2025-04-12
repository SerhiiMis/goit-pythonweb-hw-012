.. Contacts API documentation master file, created by
   sphinx-quickstart on Sat Apr 12 08:43:16 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Contacts API Documentation
==========================

Overview
--------
This documentation provides details on the Contacts API, which is a secure, asynchronous REST API for managing personal contacts. The API supports the following functionalities:
  
- **User Authentication:** Secure JWT-based login and registration.
- **Email Verification:** Users verify their email to activate their accounts.
- **Contact Management:** Create, update, delete, search, and list contacts.
- **Avatar Upload:** Upload user avatars using Cloudinary.
- **Rate Limiting:** Protect sensitive endpoints such as the user profile endpoint.
- **Caching:** (Upcoming feature) Using Redis for caching user data.
- **Password Reset:** (Upcoming feature) Secure mechanism for resetting passwords.
- **Role-based Access:** (Upcoming feature) Separate admin and user roles.

Features
--------
- **JWT Authentication:** Secure login and issuance of tokens.
- **CRUD Operations:** Create, retrieve, update, and delete contacts.
- **Email Verification:** Activate user accounts through email confirmation.
- **Avatar Upload:** Users can upload and update their avatars via Cloudinary integration.
- **Rate Limiting:** Limits the number of requests to sensitive endpoints.

Installation & Setup
--------------------
For complete instructions on installation, please refer to the **Getting Started** section in the project README.

API Endpoints
-------------
The API includes several endpoints grouped by functionality:
  
- **Authentication:** `/auth/signup`, `/auth/login`, `/auth/verify-email`
- **User Profile:** `/users/me`, `/users/avatar`
- **Contacts:** `/contacts/` (CRUD operations), `/contacts/search/`, `/contacts/upcoming-birthdays/`

Additional Documentation
------------------------
For detailed API references, please consult the module documentation generated via autodoc. This includes descriptions of functions, parameters, and responses.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


