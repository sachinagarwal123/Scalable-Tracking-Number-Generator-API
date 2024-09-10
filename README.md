# Tracking Number Generator API

## Setup

1. Clone the repository.
2. Create a virtual environment:
    ```bash
    python -m venv env
    ```
3. Activate the virtual environment:
    ```bash
    source env/bin/activate  # On Windows use `.\env\Scripts\activate`
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Run migrations:
    ```bash
    python manage.py migrate
    ```
6. Run the server:
    ```bash
    python manage.py runserver
    ```

## Testing

Run the tests with:

```bash
python manage.py test
