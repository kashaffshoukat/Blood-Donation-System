# Blood Donation System

A comprehensive web-based Blood Bank Management System built with Django that connects blood donors with patients in need, streamlining the blood donation and request process.

## Project Overview

The Blood Donation System is a web application designed to efficiently manage blood donation activities, inventory, and requests. It provides a platform for donors to register and donate blood, patients to request blood, and administrators to manage the entire blood bank system. The system aims to bridge the gap between blood donors and recipients, ensuring timely access to blood for those in need while maintaining accurate records of donations and inventory.

## Features

- **Multi-User System**: Separate interfaces for administrators, donors, and patients with role-specific dashboards
- **Blood Inventory Management**: Track blood stock by blood group with real-time updates
- **Donation Management**: Process and approve blood donations with health screening
- **Request Management**: Handle blood requests from patients with priority settings
- **User Authentication**: Secure login for different user roles with password protection
- **Profile Management**: Users can manage their profiles and view their donation/request history
- **Search Functionality**: Find donors by blood group and location
- **Responsive Design**: Mobile-friendly interface for access on various devices
- **Automated Stock Updates**: Blood inventory automatically updates after approved donations and requests
- **Admin Dashboard**: Comprehensive statistics and management tools for administrators

## Technology Stack

- **Backend**: Django 3.0+ (Python web framework)
- **Database**: SQLite (default), easily configurable for PostgreSQL or MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 4
- **Authentication**: Django's built-in authentication system with custom user roles
- **Form Processing**: Django Forms with widget-tweaks for enhanced UI
- **Deployment**: Vercel-ready configuration with whitenoise for static files
- **Version Control**: Git
- **Development Tools**: Virtual environment for dependency isolation

## System Architecture

The system is built using Django's MVT (Model-View-Template) architecture and consists of three main applications:

1. **blood**: Core application that manages blood stock and requests
   - Handles blood inventory tracking
   - Processes blood requests from patients
   - Provides admin dashboard and management interfaces
   - Controls authentication and session management

2. **donor**: Manages donor registration, profiles, and donation activities
   - Handles donor registration and authentication
   - Manages donor profiles and personal information
   - Processes blood donation requests
   - Tracks donation history and eligibility

3. **patient**: Handles patient registration, profiles, and blood requests
   - Manages patient registration and authentication
   - Maintains patient medical information
   - Processes blood request submissions
   - Tracks request history and status updates

### Technical Architecture

The application follows a layered architecture:

- **Presentation Layer**: HTML templates with Bootstrap styling
- **Application Layer**: Django views and forms handling business logic
- **Data Access Layer**: Django models and ORM for database operations
- **Database Layer**: SQLite database (configurable for other databases)

### Data Flow

1. User authentication and role assignment
2. Role-based access to specific modules
3. CRUD operations on profiles, donations, and requests
4. Automated inventory management based on approved actions
5. Notification system for status updates

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Blood-Donation-System.git
   cd Blood-Donation-System
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## User Roles and Functionality

### Administrator
- Manage blood inventory
- Approve/reject blood donations
- Approve/reject blood requests
- View and manage donors and patients
- Access to admin dashboard with statistics

### Donor
- Register as a blood donor
- Update profile information
- Request to donate blood
- View donation history
- Request blood (if needed)

### Patient
- Register as a patient
- Update profile information
- Request blood
- View request history

## Database Models and Schema

### Blood App
- **Stock**:
  - `bloodgroup` (CharField): Blood group identifier (A+, A-, B+, B-, AB+, AB-, O+, O-)
  - `unit` (PositiveIntegerField): Available units of blood for this blood group
  - Purpose: Manages blood inventory by blood group, tracking available units

- **BloodRequest**:
  - `request_by_patient` (ForeignKey): Reference to Patient model
  - `request_by_donor` (ForeignKey): Reference to Donor model (optional)
  - `patient_name` (CharField): Name of the patient requiring blood
  - `patient_age` (PositiveIntegerField): Age of the patient
  - `reason` (CharField): Medical reason for blood request
  - `bloodgroup` (CharField): Required blood group
  - `unit` (PositiveIntegerField): Number of units requested
  - `status` (CharField): Current status (Pending, Approved, Rejected)
  - `date` (DateField): Date of request
  - Purpose: Tracks blood requests from patients or donors, including approval status

### Donor App
- **Donor**:
  - `user` (OneToOneField): Link to Django User model for authentication
  - `profile_pic` (ImageField): Profile picture of donor
  - `bloodgroup` (CharField): Donor's blood group
  - `address` (CharField): Donor's address
  - `mobile` (CharField): Contact number
  - Purpose: Stores donor information with authentication capabilities

- **BloodDonate**:
  - `donor` (ForeignKey): Reference to Donor model
  - `disease` (CharField): Any diseases to note
  - `age` (PositiveIntegerField): Age of donor at time of donation
  - `bloodgroup` (CharField): Blood group of donation
  - `unit` (PositiveIntegerField): Units of blood donated
  - `status` (CharField): Status of donation (Pending, Approved, Rejected)
  - `date` (DateField): Date of donation
  - Purpose: Records blood donation details, health information, and approval status

### Patient App
- **Patient**:
  - `user` (OneToOneField): Link to Django User model for authentication
  - `profile_pic` (ImageField): Profile picture of patient
  - `age` (PositiveIntegerField): Patient's age
  - `bloodgroup` (CharField): Patient's blood group
  - `disease` (CharField): Patient's medical condition
  - `doctorname` (CharField): Attending physician's name
  - `address` (CharField): Patient's address
  - `mobile` (CharField): Contact number
  - Purpose: Stores patient information with medical details and authentication

### Database Relationships
- Users can be either Donors or Patients (one-to-one relationship with Django User)
- Donors can make multiple blood donations (one-to-many relationship)
- Patients can make multiple blood requests (one-to-many relationship)
- Blood inventory is updated based on approved donations and requests

## Workflow and Business Logic

1. **Blood Donation Process**:
   - Donor logs in and submits a donation request through the donation form
   - System records donation details including health information and blood group
   - Admin reviews the donation request on the admin dashboard
   - Admin approves/rejects the donation based on eligibility criteria
   - Upon approval, blood stock is automatically updated with the new units
   - Donor can view their donation history and status updates

2. **Blood Request Process**:
   - Patient logs in and submits a blood request with medical details
   - System records request details including required blood group and units
   - Admin reviews the blood request on the admin dashboard
   - Admin checks blood availability and approves/rejects the request
   - Upon approval, blood stock is automatically reduced by the requested units
   - Patient can view their request history and status updates

3. **Inventory Management Process**:
   - System maintains real-time blood inventory by blood group
   - Inventory automatically updates after approved donations (increase) and requests (decrease)
   - Admin can view current stock levels on the dashboard
   - System prevents approval of requests when insufficient stock is available
   - Admin can manually adjust inventory if needed

## API Documentation

The system provides several internal APIs for handling data operations:

### Authentication APIs
- **Login**: `/login/` - Handles user authentication
- **Logout**: `/logout/` - Handles user logout
- **After Login**: `/afterlogin/` - Routes users based on their role

### Admin APIs
- **Admin Dashboard**: `/admin-dashboard/` - Main admin interface
- **Admin Blood View**: `/admin-blood/` - Blood inventory management
- **Admin Blood Request**: `/admin-request/` - Handle blood requests
- **Admin Donation**: `/admin-donation/` - Manage blood donations
- **Admin Donor**: `/admin-donor/` - Manage donor accounts
- **Admin Patient**: `/admin-patient/` - Manage patient accounts

### Donor APIs
- **Donor Registration**: `/donor/donorsignup/` - Register new donors
- **Donor Dashboard**: `/donor/donor-dashboard/` - Donor main interface
- **Donate Blood**: `/donor/donate-blood/` - Submit donation requests
- **Donation History**: `/donor/donation-history/` - View past donations
- **Profile Management**: `/donor/profile/` - Update donor profile

### Patient APIs
- **Patient Registration**: `/patient/patientsignup/` - Register new patients
- **Patient Dashboard**: `/patient/patient-dashboard/` - Patient main interface
- **Make Request**: `/patient/make-request/` - Submit blood requests
- **Request History**: `/patient/my-request/` - View past requests
- **Profile Management**: `/patient/profile/` - Update patient profile

## Troubleshooting Guide

### Common Installation Issues

1. **Database Migration Errors**
   - **Problem**: `django.db.utils.OperationalError: no such table`
   - **Solution**: Run `python manage.py migrate` to create all required tables

2. **Static Files Not Loading**
   - **Problem**: CSS/JS files not loading in the browser
   - **Solution**: Ensure `DEBUG=True` in development or run `python manage.py collectstatic` for production

3. **User Authentication Issues**
   - **Problem**: Unable to login after registration
   - **Solution**: Verify user is assigned to the correct group (DONOR or PATIENT)

4. **Email Configuration Errors**
   - **Problem**: Email sending fails
   - **Solution**: Update EMAIL_* settings in settings.py with valid credentials

### Runtime Troubleshooting

1. **Blood Stock Issues**
   - **Problem**: Blood stock not updating after donation/request
   - **Solution**: Verify the donation/request status is set to "Approved"

2. **Permission Errors**
   - **Problem**: "Permission Denied" when accessing certain pages
   - **Solution**: Ensure user is logged in and has the correct role assignment

3. **Form Submission Errors**
   - **Problem**: Form validation errors
   - **Solution**: Check form field requirements and error messages

## Security Features

- **Django's Authentication System**: Secure user authentication and session management
- **CSRF Protection**: Cross-Site Request Forgery protection on all forms
- **Password Hashing**: Secure password storage using Django's password hashers
- **User Role-based Access Control**: Different permissions for admin, donor, and patient
- **Form Validation**: Input validation to prevent malicious data entry
- **Session Security**: Secure cookie handling and session expiration
- **SQL Injection Protection**: Django ORM prevents SQL injection attacks

## Deployment

The application is configured for deployment on Vercel with the included vercel.json file. The system uses whitenoise middleware for serving static files in production.

### Deployment Steps

1. Create a Vercel account and install Vercel CLI
2. Configure environment variables in Vercel dashboard
3. Run `vercel --prod` from the project directory
4. Access your deployed application at the provided URL

## Future Enhancements

- **Email Notifications**: Automated email alerts for request status updates
- **Mobile Application**: Native mobile apps for Android and iOS
- **Blood Donation Camp Management**: Organize and manage donation camps
- **Geographic-based Donor Search**: Find donors by proximity
- **Hospital Integration**: API integration with hospital management systems
- **Advanced Analytics**: Reporting and predictive analytics for blood demand
- **Multi-language Support**: Internationalization for broader accessibility
- **SMS Notifications**: Text message alerts for urgent blood needs

## Contributors

- [Your Name] - Initial work and development

## Acknowledgments

- Django documentation and community
- Bootstrap for responsive UI components
- Open-source community for inspiration and tools
