# Build files script for deployment on Vercel

# Setup Python venv
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
python3.12 -m pip install -r requirements.txt

# Perform migrations
python3.12 manage.py migrate

# static files
python3.12 manage.py collectstatic --noinput 
