# django-boiler-plate
django-boiler-plate is a Django project template designed to help you get started quickly with a modern and scalable web application. This template includes a REST API setup with Django REST framework, authentication using Django Simple JWT, API documentation with Swagger, an enhanced Django admin interface with Jazzmin, and example unit tests for the account app.

## Features
1. REST API: Built with Django REST framework to provide robust and scalable API endpoints.
2. Auth Token: Secure authentication using Django Simple JWT.
3. Django Admin: Enhanced and customizable admin interface using Jazzmin.
4. Unit Testing: Example unit tests for the account app to ensure code quality and reliability.
5. Faker data user factory_boy



## Installation
Follow these steps to set up the project on your local machine:




### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- virtualenv (optional but recommended)

### Steps
1. Clone the Repository
```base
git clone https://github.com/yourusername/django-boiler-plate.git
cd django-boiler-plate
```
2. Create and Activate Virtual Environment (optional)
```base
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```
3. Install Dependencies
```base
pip install -r requirements.txt
```
4. Configure Environment Variables
```base
cp .env.example .env
```
Edit the .env file to configure your database and other settings.

5. copy core/default_local_settings.py to core/local_settings.py, then set up your database

6. Apply Migrations
```bash
python manage.py createsuperuser
```
7. Create a Superuser
```bash
python manage.py createsuperuser
```

8. Run the Development Server
```bash
python manage.py runserver
```

## Usage
### Accessing the Admin Interface
Visit `http://127.0.0.1:8000/admin` and log in with the superuser credentials you created.

### API Endpoints
The API is accessible at `http://127.0.0.1:8000/api/`. Detailed API documentation is available at `http://127.0.0.1:8000`.

### Running Unit Tests
To run the provided unit tests, use the following command:
```bash
python manage.py test
```
This will execute the example unit tests located in the `account` app and any other tests you add to your project.


## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas or improvements.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
