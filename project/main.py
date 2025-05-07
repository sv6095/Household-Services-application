from datetime import datetime
from importlib.resources import Package
import os
from flask import Flask, flash, render_template, session, request, redirect, url_for, send_file
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy import func, and_
from datetime import datetime
from applications.database import db
from applications.config import Config
from applications.model import *  
from sqlalchemy import Column, Integer, String, Float, DateTime

def create_app():
    app = Flask(__name__, template_folder='templates')  
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():

        db.create_all()

        roles = ['admin', 'customer', 'professional']

        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_role = Role.query.filter_by(name='admin').first()  
            admin = User(username='admin',
                         email='admin@ds.study.iitm.ac.in',
                         password='admin',  
                         roles=[admin_role])  
            db.session.add(admin)

        db.session.commit()

    return app

app = create_app() 
services = [
    {'id': 1, 'name': 'AC Service'},
    {'id': 2, 'name': 'Fridge Service'},
    {'id': 3, 'name': 'Cleaning Service'},
    {'id': 4, 'name': 'Washing Machine Service'},
    {'id': 5, 'name': 'TV Repair'},
    {'id': 6, 'name': 'Plumbing Service'},
    {'id': 7, 'name': 'Electrical Service'},
    {'id': 8, 'name': 'Pest Control'},
    {'id': 9, 'name': 'Carpentry'},
    {'id': 10, 'name': 'Painting Service'},
]

packages = {
        1: [
        {'name': 'Basic AC Cleaning', 'price': 499, 'description': 'Includes cleaning of filters and basic maintenance.'},
        {'name': 'Full AC Service', 'price': 999, 'description': 'Complete AC service with deep cleaning.'}
        ],
        2: [
        {'name': 'Fridge Cooling Check', 'price': 299, 'description': 'Check and repair cooling issues.'},
        {'name': 'Full Fridge Service', 'price': 799, 'description': 'Complete maintenance and cleaning.'}
        ],
        3: [
        {'name': 'Home Cleaning Basic', 'price': 399, 'description': 'Basic cleaning for 1BHK apartment.'},
        {'name': 'Deep Cleaning', 'price': 1299, 'description': 'Deep cleaning for entire home.'}
        ],
        4: [
        {'name': 'Basic Washing Machine Check', 'price': 349, 'description': 'Check and repair minor issues.'},
        {'name': 'Full Washing Machine Repair', 'price': 749, 'description': 'Complete service for washing machine repair.'}
        ],
        5: [
        {'name': 'Basic TV Check', 'price': 199, 'description': 'Check display and sound issues.'},
        {'name': 'Full TV Service', 'price': 599, 'description': 'Complete TV repair and service.'}
        ],
        6: [
        {'name': 'Basic Plumbing Service', 'price': 249, 'description': 'Fixing leaks and basic plumbing tasks.'},
        {'name': 'Full Plumbing Service', 'price': 649, 'description': 'Complete plumbing service for major repairs.'}
        ],
        7: [
        {'name': 'Electrical Check', 'price': 199, 'description': 'Check for electrical issues in your home.'},
        {'name': 'Full Electrical Service', 'price': 799, 'description': 'Complete electrical repair and installation services.'}
        ],
        8: [
        {'name': 'Basic Pest Control', 'price': 499, 'description': 'Pest control for small infestations.'},
        {'name': 'Full Pest Control', 'price': 1499, 'description': 'Complete pest control for your home.'}
        ],
        9: [
        {'name': 'Basic Carpentry Service', 'price': 399, 'description': 'Small repairs and adjustments.'},
        {'name': 'Complete Carpentry Service', 'price': 899, 'description': 'Furniture assembly and major repairs.'}
        ],
        10: [
        {'name': 'Basic Painting Service', 'price': 599, 'description': 'Painting for a single room.'},
        {'name': 'Full Home Painting', 'price': 3999, 'description': 'Complete painting service for your home.'}
        ]
    }

@app.route('/')
def home():
    # Retrieve username and roles from the session, defaulting to None if not found
    username = session.get('username')  # Get username from the session
    roles = session.get('roles', [])    # Get roles from the session, default to an empty list if not found

    return render_template('index.html', username=username, roles=roles)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('login_page'))

        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  
            session['user_id'] = user.id
            session['username'] = user.username

            roles = [role.name.lower() for role in user.roles]
            session['roles'] = roles  

            if 'admin' in roles:
                return redirect(url_for('admin_dashboard'))
            elif 'customer' in roles:
                customer = Customer.query.filter_by(user_id=user.id).first()
                session['customer_id'] = customer.id if customer else None
                return redirect(url_for('customer_dashboard'))
            elif 'professional' in roles:
                professional = Professional.query.filter_by(user_id=user.id).first()
                session['professional_id'] = professional.id if professional else None
                return redirect(url_for('professional_dashboard'))
            else:
                flash('User does not have a valid role', 'danger')
                return redirect(url_for('login_page'))
        
        flash('Invalid username or password', 'danger')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('customer_id', None)
    session.pop('professional_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'customer':
            return redirect(url_for('custreg'))  
        elif role == 'professional':
            return redirect(url_for('profreg'))  

@app.route('/custreg', methods=['GET', 'POST'])
def custreg():
    if request.method == 'GET':
        return render_template('custreg.html')
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        pincode = request.form['pincode']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('login_page'))

        # Creating a new user entry
        new_user = User(
            username=username,
            email=email,
            password=password  # Assuming you're not hashing the password
        )
        db.session.add(new_user)
        db.session.commit()

        # Assigning the 'customer' role to the new user
        customer_role = Role.query.filter_by(name='customer').first()  # Fetch the 'customer' role
        if customer_role:
            user_role = UserRole(user_id=new_user.id, role_id=customer_role.id)
            db.session.add(user_role)
            db.session.commit()
        else:
            flash('Role "customer" does not exist. Please contact support.', 'error')
            return redirect(url_for('login_page'))

        # Creating a new customer entry
        new_customer = Customer(
            name=name,
            username=username,
            password=password,  
            email=email,
            address=address,
            pincode=pincode,
            user_id=new_user.id
        )
        db.session.add(new_customer)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login_page'))

@app.route('/profreg', methods=['GET', 'POST'])
def profreg():
    if request.method == 'GET':
        return render_template('profreg.html') 
    
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['re-password']
        service = request.form['service']
        work_experience = request.form['work_experience']

        if password != re_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('profreg'))
        
        if 'id_proof' not in request.files:
            flash('No ID proof file uploaded.', 'error')
            return redirect(url_for('profreg'))
        
        file = request.files['id_proof']
        
        if file and file.filename.endswith('.pdf'):
            upload_folder = r"C:\Users\shant\Downloads\ibw\ibw\project\uploads" # Update this path
            # Ensure the upload folder exists
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, file.filename)

            file.save(file_path)

            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                if existing_user.username == username:
                    flash('Username already exists. Please choose another.', 'error')
                elif existing_user.email == email:
                    flash('Email already exists. Please use another email.', 'error')
                return redirect(url_for('profreg'))

            new_user = User(
                username=username,
                email=email,
                password=password 
            )
            db.session.add(new_user)
            db.session.commit()

            professional_role = Role.query.filter_by(name='professional').first()
            if professional_role:
                user_role = UserRole(user_id=new_user.id, role_id=professional_role.id)
                db.session.add(user_role)
                db.session.commit()
            else:
                flash('Role "professional" does not exist. Please contact support.', 'error')
                return redirect(url_for('profreg'))

            # Create a new professional entry
            new_professional = Professional(
                name=name,
                username=username,
                email=email,
                password=password,  
                service=service,
                work_experience=work_experience,
                id_proof=file_path,
                user_id=new_user.id  # Associate professional with the user
            )
            db.session.add(new_professional)
            db.session.commit()

            flash('Professional registration successful! You can now log in.', 'success')
            return redirect(url_for('login_page'))

        flash('Only PDF files are accepted for ID proof.', 'error')
        return redirect(url_for('profreg'))


@app.route('/admin/dashboard')
def admin_dashboard():
    professionals = Professional.query.all()
    assigned_requests = []
    username = session.get('username')
    roles = session.get('roles', [])


    return render_template(
        'adboard.html', 
        professionals=professionals, 
        assigned_requests=assigned_requests, 
        services=services, 
        packages=packages,
        username=username,
        roles=roles
    )

@app.route('/admin/view_id_proof/<int:professional_id>')
def view_id_proof(professional_id):
    # Check if user is admin
    roles = session.get('roles', [])
    if 'admin' not in roles:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))

    professional = Professional.query.get_or_404(professional_id)
    if professional.id_proof and os.path.exists(professional.id_proof):
        return send_file(
            professional.id_proof,
            mimetype='application/pdf',
            as_attachment=False,  # Show in browser instead of download
            download_name=f'id_proof_{professional.username}.pdf'
        )
    else:
        flash('ID proof not found', 'error')
        return redirect(url_for('admin_dashboard'))


# Manage Professional Route
@app.route('/admin/manage_professional/<int:professional_id>', methods=['POST'])
def manage_professional(professional_id):
    action = request.form.get('action')  # Get the action from the form submission
    professional = Professional.query.get(professional_id)

    if not professional:
        flash('Professional not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if action == 'approve':
        professional.is_approved = True  # Assuming you have an 'is_approved' attribute in the Professional model
        db.session.commit()
        flash('Professional approved successfully.', 'success')

    elif action == 'reject':
        db.session.delete(professional)  # Or you can update a status attribute instead
        db.session.commit()
        flash('Professional rejected successfully.', 'success')

    else:
        flash('Invalid action specified.', 'danger')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/manage_service_packages', methods=['GET', 'POST'])
def manage_service_packages():
    if request.method == 'POST':
        service_id = int(request.form.get('service_id'))
        package_name = request.form.get('package_name')
        price = float(request.form.get('price'))
        description = request.form.get('description')

        # Add or modify the package
        if service_id not in packages:
            packages[service_id] = []  # If service_id doesn't exist, initialize it as an empty list

        new_package = {
            'name': package_name,
            'price': price,
            'description': description
        }

        # Append the new package to the corresponding service_id in the packages dictionary
        packages[service_id].append(new_package)

        flash('Service package added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Render the admin dashboard with services and packages
    return render_template('adboard.html', services=services, packages=packages)


# Update Service Request Route (modify status, description)
@app.route('/admin/update_service_request/<int:request_id>', methods=['POST'])
def update_service_request(request_id):
    service_request = None  # Fetch service request from the database by ID
    
    if not service_request:
        flash('Service request not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    service_request.status = request.form.get('status')
    service_request.description = request.form.get('description')

    # Save the changes to the database
    flash('Service request updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_package_price', methods=['POST'])
def update_package_price():
    service_id = int(request.form.get('service_id'))
    package_name = request.form.get('package_name')
    new_price = float(request.form.get('new_price'))

    # Search for the package in the packages dictionary
    if service_id in packages:
        for package in packages[service_id]:
            if package['name'] == package_name:
                package['price'] = new_price  # Update the price of the package
                flash(f"Package price updated to {new_price} successfully.", 'success')
                return redirect(url_for('admin_dashboard'))

    flash('Package not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/customer/dashboard')
def customer_dashboard():
    return render_template('cdboard.html', services=services)

@app.route('/service/<int:service_id>', methods=['GET', 'POST'])
def service_details(service_id):
    # Fetch service by ID
    service = next((s for s in services if s['id'] == service_id), None)
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services'))
    
    service_packages = packages.get(service_id, [])

    if request.method == 'POST':
        # Check if customer is logged in
        customer_id = session.get('customer_id')
        if not customer_id:
            flash('You need to be logged in to book a service.', 'danger')
            return redirect(url_for('login'))

        # Get customer details
        customer = Customer.query.get(customer_id)
        if not customer:
            flash('Customer profile not found.', 'error')
            return redirect(url_for('customer_dashboard'))

        # Capture the form data
        package_name = request.form.get('package_name')
        package_price = float(request.form.get('package_price'))  # Ensure price is captured
        description = request.form.get('description')

        # Find available and approved professionals for this service
        available_professionals = Professional.query.filter(
            and_(
                Professional.is_approved == True,
                Professional.service == service['name']
            )
        ).all()

        if available_professionals:
            try:
                # Create a new service request
                new_service_request = ServiceRequest(
                    service_type=service['name'],
                    description=description,
                    status='Pending',
                    request_date=datetime.utcnow(),
                    customer_id=customer_id,
                    price=package_price  # Set the price
                )
                db.session.add(new_service_request)
                db.session.flush()  # This gets us the ID without committing

                # Create assignments for available professionals
                for professional in available_professionals:
                    new_assignment = Assignment(
                        professional_id=professional.id,
                        service_request_id=new_service_request.id,
                        assignment_date=datetime.utcnow(),
                        completion_status='Pending'  # Set initial status
                    )
                    db.session.add(new_assignment)

                # Commit all changes
                db.session.commit()
                
                flash('Your service request has been successfully created and sent to available professionals.', 'success')
                return redirect(url_for('customer_dashboard'))

            except Exception as e:
                db.session.rollback()
                flash('An error occurred while processing your request. Please try again.', 'error')
                return redirect(url_for('service_details', service_id=service_id))
        else:
            flash('No professionals are currently available for this service. Please try again later.', 'warning')
            return redirect(url_for('service_details', service_id=service_id))

    return render_template('service_details.html', 
                         service=service, 
                         packages=service_packages)

@app.route('/professional/dashboard')
def professional_dashboard():
    # Get the logged-in professional's ID from the session
    professional_id = session.get('professional_id')

    if professional_id is None:
        flash('You need to be logged in to access the dashboard.', 'danger')
        return redirect(url_for('login_page'))

    # Fetch the professional's details
    professional = Professional.query.get(professional_id)

    if professional is None:    
        flash('Professional not found.', 'danger')
        return redirect(url_for('login_page'))

    # Fetch assigned service requests with 'Pending' status, for the same service type
    assigned_rows = (
        ServiceRequest.query
        .filter(ServiceRequest.professional_id.is_(None), ServiceRequest.status == 'Pending')
        .filter(ServiceRequest.service_type == professional.service)  
        .join(Customer)
        .add_columns(
            ServiceRequest.id.label('request_id'),
            ServiceRequest.request_date,
            ServiceRequest.price,
            ServiceRequest.description,
            Customer.name.label('customer_name')
        ).all()
    )

    # Convert query results to list of dicts
    assigned_requests = []
    for row in assigned_rows:
        # Access values using getattr to handle both Row and NamedTuple results
        assigned_requests.append({
            'id': getattr(row, 'request_id'),
            'request_date': getattr(row, 'request_date'),
            'price': getattr(row, 'price'),
            'description': getattr(row, 'description'),
            'customer_name': getattr(row, 'customer_name')
        })

    # Fetch service history (accepted, rejected, completed)
    service_history = ServiceRequest.query.filter(ServiceRequest.professional_id == professional.id).filter(ServiceRequest.status != 'Pending').all()

    return render_template('pdboard.html', 
                           professional=professional, 
                           assigned_requests=assigned_requests, 
                           service_history=service_history,
                           services=services, 
                           packages=packages
                           )  # Pass price to the template


@app.route('/accept_or_reject_request/<int:request_id>', methods=['POST'])
def accept_or_reject_request(request_id):
    action = request.form.get('action')
    professional_id = session.get('professional_id')

    # Check if the professional is logged in
    if professional_id is None:
        flash('You need to be logged in to accept or reject requests.', 'danger')
        return redirect(url_for('professional_dashboard'))

    # Find the service request
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        flash('Service request not found.', 'danger')
        return redirect(url_for('professional_dashboard'))

    if action == 'accept':
        # Mark the service request as accepted
        service_request.status = 'Accepted'
        service_request.professional_id = professional_id  # Assign the professional to the request
        db.session.commit()

        # Notify the customer (optional: you can implement a notification system)
        flash('You have accepted the service request.', 'success')

        # Cancel other pending requests of the same service type
        other_pending_requests = ServiceRequest.query.filter_by(service_type=service_request.service_type, status='Pending').all()

        for other_request in other_pending_requests:
            if other_request.id != service_request.id:
                other_request.status = 'Cancelled'  # Cancel other pending requests
                db.session.commit()
                
    elif action == 'reject':
        # Mark the service request as rejected
        service_request.status = 'Rejected'
        db.session.commit()

        flash('You have rejected the service request.', 'warning')

    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('professional_dashboard'))


@app.route('/professional/close_request/<int:request_id>', methods=['POST'])
def close_request(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        flash('Service request not found.', 'danger')
        return redirect(url_for('professional_dashboard'))

    # Update the status to 'Completed'
    service_request.status = 'Completed'
    db.session.commit()
    flash('Service request closed successfully.', 'success')

    return redirect(url_for('professional_dashboard'))

@app.route('/summary')
def summary():
    # Count service requests by status
    try:
        status_counts = db.session.query(
            ServiceRequest.status, 
            func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.status).all()

        # Prepare data for charts
        statuses = [status for status, count in status_counts]
        counts = [count for status, count in status_counts]

        # Create Pie Chart for Service Request Statuses
        plt.figure(figsize=(10, 6))
        plt.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=90)
        plt.title('Service Request Statuses')
        
        # Save pie chart to a buffer
        pie_buffer = io.BytesIO()
        plt.savefig(pie_buffer, format='png')
        pie_buffer.seek(0)
        pie_chart = base64.b64encode(pie_buffer.getvalue()).decode('utf-8')
        plt.close()

        # Create Bar Chart for Service Requests Over Time
        # Get monthly service request counts
        monthly_requests = db.session.query(
            func.strftime('%Y-%m', ServiceRequest.request_date).label('month'),
            func.count(ServiceRequest.id).label('request_count')
        ).group_by('month').order_by('month').all()

        plt.figure(figsize=(12, 6))
        months = [month for month, count in monthly_requests]
        request_counts = [count for month, count in monthly_requests]

        plt.bar(months, request_counts)
        plt.title('Monthly Service Requests')
        plt.xlabel('Month')
        plt.ylabel('Number of Requests')
        plt.xticks(rotation=45)
        
        # Save bar chart to a buffer
        bar_buffer = io.BytesIO()
        plt.savefig(bar_buffer, format='png', bbox_inches='tight')
        bar_buffer.seek(0)
        bar_chart = base64.b64encode(bar_buffer.getvalue()).decode('utf-8')
        plt.close()

        # Additional Statistics
        total_requests = ServiceRequest.query.count()
        closed_requests = ServiceRequest.query.filter_by(status='Completed').count()
        pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
        assigned_requests = ServiceRequest.query.filter_by(status='Assigned').count()

        return render_template('summary.html', 
                               pie_chart=pie_chart, 
                               bar_chart=bar_chart,
                               total_requests=total_requests,
                               closed_requests=closed_requests,
                               pending_requests=pending_requests,
                               assigned_requests=assigned_requests)
    
    except Exception as e:
        # Fallback in case of any chart generation errors
        print(f"Error in summary route: {e}")
        return render_template('summary.html', 
                               error="Unable to generate charts")

if __name__ == '__main__':
    app.run(debug=True)
