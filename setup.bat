@echo off
echo Installing required packages...
pip install python-dotenv Django==5.0.6 requests Pillow scikit-learn pandas numpy psycopg2-binary django-crispy-forms crispy-bootstrap5

echo Creating .env file...
if not exist .env (
    echo SECRET_KEY=django-insecure-your-secret-key-here> .env
    echo TMDB_API_KEY=your-tmdb-api-key-here>> .env
    echo DEBUG=True>> .env
    echo .env file created.
)

echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Setup complete!
echo To run the server: python manage.py runserver
pause