from flask import Flask
from flask import render_template,request,url_for,redirect
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
    return render_template('inventory.html', inventory = inventory_data)

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

    return redirect(url_for('inventory'))






if __name__ == "__main__":
    app.run(debug=True)