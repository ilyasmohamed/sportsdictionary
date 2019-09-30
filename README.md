# Sports Dictionary
A crowd-sourced online sports dictionary written using the Django web framework

🏈 🏸 ⚾ 🏀 🎱 🎳 🥊 ♟️ 🤼‍♂️ 🏏 🚴‍♂️ 🎣 ⚽ ⛳ 🏒 🏇 ⛸ 🏁 🏉 🛹 🏂 🏊‍♂️ 🏓 🎾 🥏 🏐

## Setup
#### 1. Clone this repo
```Shell Session
git clone https://github.com/ilyasmohamed/sportsdictionary.git
```
#### 2. cd into the project folder
#### 3. Create a virtual environment, activate it and then install dependencies

  On macOS and Linux
```Shell Session
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
  On Windows
```Shell Session
py -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

#### 4. Initialize the database
```Shell Session
python manage.py migrate --settings=sportsdictionary.settings.dev
python manage.py makemigrations dictionary accounts --settings=sportsdictionary.settings.dev
python manage.py migrate --settings=sportsdictionary.settings.dev
python manage.py createcachetable --settings=sportsdictionary.settings.dev
```
#### 5. Seed the db
```Shell Session
python manage.py seeddb --settings=sportsdictionary.settings.dev
```
#### 6. Run the development server to verify everything is working
```Shell Session
python manage.py runserver --settings=sportsdictionary.settings.dev
```
#### 7. Login as the test user using the below credentials
Username: testuser\
Password: `wy3MW5`
