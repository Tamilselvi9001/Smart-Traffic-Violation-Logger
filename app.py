from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Officer, Violation
from datetime import datetime, date
import qrcode
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trafficlog-secret-2024-xk9z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

os.makedirs('static/qrcodes', exist_ok=True)

VIOLATION_TYPES = [
    'No Helmet', 'Overspeeding', 'Signal Jumping', 'Wrong Parking',
    'No Seatbelt', 'Triple Riding', 'Drunk Driving', 'No License',
    'Using Mobile While Driving', 'No Insurance'
]

@login_manager.user_loader
def load_user(user_id):
    return Officer.query.get(int(user_id))

def generate_qr(violation_id):
    url = f"http://localhost:5000/status/{violation_id}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0f1e", back_color="white")
    path = f"static/qrcodes/challan_{violation_id}.png"
    img.save(path)
    return path

@app.route('/')
def index():
    total = Violation.query.count()
    unpaid = Violation.query.filter_by(status='Unpaid').count()
    paid = Violation.query.filter_by(status='Paid').count()
    return render_template('index.html', total=total, unpaid=unpaid, paid=paid)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        officer = Officer.query.filter_by(username=username).first()
        if officer and check_password_hash(officer.password, password):
            login_user(officer)
            flash(f'Welcome back, {officer.name}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total = Violation.query.count()
    unpaid_count = Violation.query.filter_by(status='Unpaid').count()
    paid_count = Violation.query.filter_by(status='Paid').count()
    total_fine = db.session.query(db.func.sum(Violation.fine_amount)).scalar() or 0
    collected = db.session.query(db.func.sum(Violation.fine_amount)).filter_by(status='Paid').scalar() or 0
    recent = Violation.query.order_by(Violation.created_at.desc()).limit(10).all()
    return render_template('dashboard.html',
        total=total, unpaid_count=unpaid_count,
        paid_count=paid_count, total_fine=total_fine,
        collected=collected, recent=recent)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_violation():
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        violation_type = request.form.get('violation_type', '').strip()
        location = request.form.get('location', '').strip()
        date_str = request.form.get('date', '')
        fine_amount = request.form.get('fine_amount', '0')

        if not all([vehicle_number, violation_type, location, date_str, fine_amount]):
            flash('All fields are required.', 'danger')
            return render_template('add_violation.html', violation_types=VIOLATION_TYPES)

        try:
            vdate = datetime.strptime(date_str, '%Y-%m-%d').date()
            fine = float(fine_amount)
        except ValueError:
            flash('Invalid date or fine amount.', 'danger')
            return render_template('add_violation.html', violation_types=VIOLATION_TYPES)

        v = Violation(
            vehicle_number=vehicle_number,
            violation_type=violation_type,
            location=location,
            date=vdate,
            fine_amount=fine,
            status='Unpaid',
            officer_id=current_user.id
        )
        db.session.add(v)
        db.session.commit()

        qr_path = generate_qr(v.id)
        v.qr_code_path = qr_path
        db.session.commit()

        flash(f'Violation logged successfully! Challan #{v.id} created.', 'success')
        return redirect(url_for('challan', violation_id=v.id))

    return render_template('add_violation.html', violation_types=VIOLATION_TYPES,
                           today=date.today().strftime('%Y-%m-%d'))

@app.route('/history')
@login_required
def history():
    query = Violation.query
    search = request.args.get('search', '').strip().upper()
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    if search:
        query = query.filter(Violation.vehicle_number.contains(search))
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(violation_type=type_filter)
    if date_from:
        try:
            query = query.filter(Violation.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Violation.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    violations = query.order_by(Violation.created_at.desc()).all()
    return render_template('history.html', violations=violations,
                           violation_types=VIOLATION_TYPES,
                           search=search, status_filter=status_filter,
                           type_filter=type_filter,
                           date_from=date_from, date_to=date_to)

@app.route('/challan/<int:violation_id>')
@login_required
def challan(violation_id):
    v = Violation.query.get_or_404(violation_id)
    return render_template('challan.html', v=v)

@app.route('/mark-paid/<int:violation_id>', methods=['POST'])
@login_required
def mark_paid(violation_id):
    v = Violation.query.get_or_404(violation_id)
    v.status = 'Paid'
    db.session.commit()
    flash(f'Challan #{v.id} marked as Paid.', 'success')
    return redirect(request.referrer or url_for('history'))

@app.route('/status/<int:violation_id>')
def status(violation_id):
    v = Violation.query.get_or_404(violation_id)
    return render_template('status.html', v=v)

@app.route('/api/stats')
@login_required
def api_stats():
    return jsonify({
        'total': Violation.query.count(),
        'unpaid': Violation.query.filter_by(status='Unpaid').count(),
        'paid': Violation.query.filter_by(status='Paid').count(),
        'collected': db.session.query(db.func.sum(Violation.fine_amount)).filter_by(status='Paid').scalar() or 0
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Officer.query.filter_by(username='admin').first():
            admin = Officer(
                username='admin',
                password=generate_password_hash('admin123'),
                name='Admin Officer'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default officer created: admin / admin123")
    app.run(debug=True)
