# Build files script for deployment on Vercel
python3.12 -m pip install -r requirements.txt
python3.12 manage.py migrate

# static files
python3.12 manage.py collectstatic --noinput 
