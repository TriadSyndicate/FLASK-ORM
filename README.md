# Backend-Flask-API-ORM
PyMongo, Flask backend with ORM allocation

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/LightHouseSports/Backend-Flask-API-ORM.git
    ```

2. **Setup Virtual Environment:**

    ```bash
    python -m venv lightHouseV
    source lightHouseV/bin/activate  # For Unix-based systems
    .\lightHouseV\Scripts\activate   # For Windows
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables:**

    Create a `.env` file in the project root and add the following:

    ```plaintext
    DB_USERNAME=your_db_username
    DB_PASSWORD=your_db_password
    DB_URI=your_db_uri
    ```

## Usage

Run the application using the following command:

```bash
python app.py
