from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from forms import LoginForm, RegistrationForm
import json
from api import create_meeting, send_email
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SpaceIt'
JSON_FILE = 'data.json'


# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not logged in

def add_mins(dtstr, mins):
    dt = datetime.strptime(dtstr, "%Y-%m-%dT%H:%M")
    new_dt = dt + timedelta(minutes=mins)
    new_datetime_str = new_dt.strftime("%Y-%m-%dT%H:%M")
    return new_datetime_str


def get_diff(tstr1, tstr2):
    dt1 = datetime.strptime(tstr1, "%Y-%m-%dT%H:%M")
    dt2 = datetime.strptime(tstr2, "%Y-%m-%dT%H:%M")
    diff = dt2 - dt1
    return diff.total_seconds() / 60

def dtstr_to_date(dtstr):
    return dtstr.split('T')[0]
    
def load_data():
    with open(JSON_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    data = load_data()
    if user_id in data:
        return User(user_id)
    return None

@app.before_request
def load_user_data():
    if current_user.is_authenticated:
        global user_data
        data = load_data()
        user_data = data.get(current_user.id, {})
    else:
        user_data = {}

def read_inventory():
    inventory_list = []
    inventory = user_data.get("inventory", {})
    for item, details in inventory.items():
        inventory_list.append([item] + details)
    return inventory_list

def write_inventory(inventory_list):
    data = load_data()
    user_inventory = {item[0]: [item[1], item[2]] for item in inventory_list}
    data[current_user.id]["inventory"] = user_inventory
    save_data(data)

from werkzeug.security import generate_password_hash, check_password_hash

def check_password(user, passw):
    data = load_data()
    user_data = data.get(user)
    if user_data and check_password_hash(user_data["password"], passw):
        return True
    return False

def register_user(user, email, password):
    data = load_data()
    if user in data:
        return False
    
    hashed_password = generate_password_hash(password)
    
    data[user] = {
        "password": hashed_password,
        "email": email,
        "inventory": {},
        "events": {}
    }
    
    save_data(data)
    return True


def get_email(user):
    data = load_data()
    user_data = data.get(user)
    if user_data:
        return user_data.get("email")
    return None

def get_events(user, date):
    data = load_data()
    user_data = data.get(user)
    if user_data:
        return user_data["events"].get(date, [])
    return []

def add_event(user, date, dt, event_type):
    data = load_data()
    user_data = data.get(user)
    if not user_data:
        return False
    
    if date not in user_data["events"]:
        user_data["events"][date] = []

    meetlink = ''
    meetlink = create_meeting(event_type, dt + ':00', add_mins(dt, 30)+ ':00')


    
    user_data["events"][date].append({
        "type": event_type,
        "datetime": dt,
        "meetlink" : meetlink
    })
    
    save_data(data)

    send_email(user_data['email'], 'Appoinment confirmed', f"Dear User, \n Your appoinment has been confirmed. Kindly join the given meet link at the time of the appoinment. \nAppoinment Type: {event_type}\n Appoinment Date : {dt.split('T')[0]} \n Appoinment Time : {dt.split('T')[1]} \n Appoinment Link : {meetlink}")

    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/inventory')
@login_required
def inventory():
    inventory_data = read_inventory()
    alert = ''
    for i in inventory_data:
        if int(i[1]) <= 2:
            alert = f'Only {i[1]} {i[2]} of {i[0]} remaining. Restock it immediately'
    return render_template('inventory.html', inventory=inventory_data, alert=alert)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess = ''
    if form.validate_on_submit():
        if check_password(form.username.data, form.password.data):
            user = User(form.username.data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            mess = 'Wrong Password/Username'
    return render_template('login.html', form=form, mess=mess)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    mess = ''
    if form.validate_on_submit():
        if register_user(form.username.data, form.email.data, form.password.data):
            user = User(form.username.data)
            login_user(user)
            return redirect(url_for('home'))
        else:
            mess = 'User already exists, please choose a different username'
    return render_template('register.html', form=form, mess=mess)


@app.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    data = request.json
    event_type = data.get('type')
    dt = data.get('datetime')
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    diff = get_diff(current_time, dt)
    if 0 < diff < 5:
        return jsonify({'status': 'error', 'message': 'Appointments must be booked at least 5 minutes in advance'}), 400
    elif diff < 0:
        return jsonify({'status': 'error', 'message': 'Sorry, We are still working on time travel, please try again later :)'}), 400

    appts = get_events(current_user.id , dtstr_to_date(dt))
    for appt in appts:
        if -30 < get_diff(dt, appt['datetime'] ) < 30:
            return jsonify({'status': 'error', 'message': 'A gap of 30 minutes must be there between two appointments'}), 400

    if not event_type or not dt:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    date = dt.split('T')[0]

    success = add_event(current_user.id, date, dt, event_type)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Appointment booked'})
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

@app.route('/events/<date>', methods=['GET'])
@login_required
def events_api(date):
    events = get_events(current_user.id, date)
    
    if events is not None:
        return jsonify(events)
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404


@app.route('/update_inventory', methods=['POST'])
@login_required
def update_inventory_api():
    data = request.json
    item_name = data.get('name')
    new_quantity = int(data.get('quantity'))
    unit = data.get('unit')

    if not item_name or new_quantity is None or not unit:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    inventory = read_inventory()

    item_updated = False
    for row in inventory:
        if row[0] == item_name:
            row[1] = new_quantity
            row[2] = unit
            item_updated = True
            break

    if not item_updated:
        inventory.append([item_name, new_quantity,unit])


    write_inventory(inventory)

    return jsonify({'status': 'success', 'message': 'Inventory updated', 'data': inventory})


@app.route('/delete_inventory', methods=['POST'])
@login_required
def delete_inventory_api():
    data = request.json
    item_name = data.get('name')

    if not item_name:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    inventory = read_inventory()

    item_deleted = False
    updated_inventory = []
    for row in inventory:
        if row[0] == item_name:
            item_deleted = True
        else:
            updated_inventory.append(row)

    if not item_deleted:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


    write_inventory(updated_inventory)

    return jsonify({'status': 'success', 'message': 'Item deleted', 'data': updated_inventory})



if __name__ == "__main__":
    app.run(debug=True)
