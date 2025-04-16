from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "L3ic3st3rCityFC!"  # Replace with a strong, random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite database
db = SQLAlchemy(app)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='class_item', lazy=True)

    def __repr__(self):
        return f"Class('{self.name}', '{self.date}', '{self.time}', '{self.location}', '{self.capacity}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    question1 = db.Column(db.String(10), nullable=False)
    question2 = db.Column(db.String(10), nullable=False)
    question3 = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

    def __repr__(self):
        return f"Booking('{self.user_name}', '{self.user_email}', '{self.class_id}')"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule')
def view_schedule():
    schedule = Class.query.all()  # Get all classes from the database
    return render_template('schedule.html', schedule=schedule)

@app.route('/book/<int:class_id>', methods=['GET'])
def book_class_form(class_id):
    class_item = Class.query.get_or_404(class_id)  # Get class by ID or return 404
    return render_template('book_class.html', class_item=class_item)

@app.route('/book', methods=['POST'])
def process_booking():
    class_id = int(request.form['class_id'])
    user_name = request.form['user_name']
    user_email = request.form['user_email']
    user_phone = request.form['user_phone']
    question1 = request.form['question1']
    question2 = request.form['question2']
    question3 = request.form['question3']

    class_item = Class.query.get_or_404(class_id)

    if len(class_item.bookings) < class_item.capacity:
        booking = Booking(
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            question1=question1,
            question2=question2,
            question3=question3,
            class_id=class_id
        )
        db.session.add(booking)
        db.session.commit()
        flash("Booking successful!", "success")
        return redirect(url_for('view_schedule'))
    else:
        flash("Class is full.", "danger")
        return redirect(url_for('book_class_form', class_id=class_id))

@app.route('/bookings', methods=['GET'])
def view_bookings():
    filter_class_name = request.args.get('filter_class_name', '').lower()
    filter_date = request.args.get('filter_date', '')

    filtered_schedule = Class.query.all()

    if filter_class_name:
        filtered_schedule = [
            class_item for class_item in filtered_schedule if filter_class_name in class_item.name.lower()
        ]
    if filter_date:
        filtered_schedule = [
            class_item for class_item in filtered_schedule if str(class_item.date) == filter_date
        ]

    return render_template('bookings.html', schedule=filtered_schedule)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create the database tables
    app.run(debug=True)