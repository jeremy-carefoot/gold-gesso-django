# Build files script for deployment on Vercel
sudo apt install python3 python3-pip # Ubuntu/Debian
pip install -r requirements.txt
python manage.py migrate
