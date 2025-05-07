from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Role Model (Many-to-Many with User)
# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Defining back_populates to link with User
    users = db.relationship('User', secondary='user_roles', back_populates='roles')

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Many-to-Many relationship with Role (back_populates defined here as well)
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')

# UserRole Model (Many-to-Many link table between User and Role)
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)


# Professional Model (One-to-One with User)
class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)  # Type of service provided
    work_experience = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    id_proof = db.Column(db.String(200), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

    # One-to-One with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationship with Assignments (Professional can have many assignments)
    assignments = db.relationship("Assignment", backref="professional")

# Customer Model (One-to-One with User)
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    # One-to-One with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationship with Service Requests (Customer can have many requests)
    service_requests = db.relationship("ServiceRequest", backref="customer")

# ServiceRequest Model (Customer creates service requests)
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False)  # Type of service requested
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='Pending')  # Status of the request (e.g., Pending, Assigned, Completed)
    request_date = db.Column(db.DateTime, nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    # Foreign key linking to the Customer who made the request
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    professional = db.relationship('Professional', backref='service_requests')
    price = db.Column(db.Float, nullable=False)  # Price of the service

# Assignment Model 
class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))
    assignment_date = db.Column(db.DateTime, nullable=False)
    completion_status = db.Column(db.String(50), default='Not Assigned')
    feedback = db.Column(db.String(500), nullable=True)

