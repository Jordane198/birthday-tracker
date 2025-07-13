from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, date
app = Flask("Birthday Tracker")
DATA_FILE = 'Birthday.json'


def load_birthdays():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)
    
def save_birthdays(birthdays):
    with open(DATA_FILE, 'w')as f:
        json.dump(birthdays, f,indent=4)

def calculate_age(birthday_str):
    birthdate = datetime.strptime(birthday_str, '%Y-%m-%d').date()
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

@app.context_processor
def inject_utilities():
    return dict(calculate_age=calculate_age)

@app.route('/')
def index():
    birthdays = load_birthdays()
    today= datetime.today()

    def days_until(birthday_str):
        # Parse the birthday
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days
    birthdays.sort(key=lambda b: days_until(b["birthday"]))
    return render_template('index.html', birthdays=birthdays)

@app.route('/edit/<int:birthday_id>', methods=['GET', 'POST'])
def edit(birthday_id):
    birthdays = load_birthdays()
    birthday = next((b for b in birthdays if b['id'] == birthday_id), None)

    if not birthday:
        return "Birthday not found!", 404

    if request.method == 'POST':
        birthday['name'] = request.form['name']
        birthday['birthday'] = request.form['birthday']
        birthday['notes'] = request.form.get('notes', '')
        save_birthdays(birthdays)
        return redirect(url_for('index'))

    return render_template('edit.html', birthday=birthday)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        birthdays = load_birthdays()
        new_id = max([b["id"] for b in birthdays], default=0) + 1
        name = request.form['name']
        birthday = request.form['birthday']
        notes = request.form.get('notes', '')
        birthdays.append({
            "id": new_id,
            "name": name,
            "birthday": birthday,
            "notes": notes
        })
        save_birthdays(birthdays)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:birthday_id>')
def delete(birthday_id):
    birthdays = load_birthdays()
    birthdays = [b for b in birthdays if b['id'] != birthday_id]
    save_birthdays(birthdays)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)