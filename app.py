from flask import Flask, render_template, request, url_for, redirect, jsonify
import csv

app = Flask(__name__)

CSV_FILE = 'inventory.csv'

def read_inventory():
    inventory = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            inventory.append(row)
    return inventory

def write_inventory(inventory):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(inventory)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    inventory_data = read_inventory()
    alert = ''
    for i in inventory_data:
        if (int(i[1])) <= 2:
            alert =  f'Only {i[1]} {i[2]} of {i[0]} remaining. Restock it immediately'
    return render_template('inventory.html', inventory=inventory_data, alert = alert)

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    data = request.json
    item_name = data.get('name')
    new_quantity = data.get('quantity')

    inventory = read_inventory()
    for row in inventory:
        if row[0] == item_name:
            row[1] = new_quantity
            break

    write_inventory(inventory)
    return jsonify({"data": read_inventory()})

events_store = {
    '2024-08-03': [
        {
            'type': 'Dentist',
            'datetime': '2024-08-03T08:30'
        },
        {
            'type': 'Therapy',
            'datetime': '2024-08-03T14:00'
        }
    ],
    '2024-08-04': [
        {
            'type': 'Physiotherapist',
            'datetime': '2024-08-04T10:00'
        }
    ]
}

@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    event_type = data.get('type')
    datetime = data.get('datetime')
    date = datetime.split('T')[0]
    # Store the event
    if date not in events_store:
        events_store[date] = []
    
    events_store[date].append({
        'type': event_type,
        'datetime': datetime
    })

    return jsonify({'status': 'success', 'message': 'Appointment booked'})

@app.route('/events/<date>', methods=['GET'])
def get_events(date):
    events = events_store.get(date, [])
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True)
