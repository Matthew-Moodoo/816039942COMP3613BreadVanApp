from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime, date, time

class User(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, userName, password):
        self.userName = userName
        self.set_password(password)

    def get_json(self):
        return{
            'userID': self.userID,
            'userName': self.userName,
            'user_type': self.user_type
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    # Legacy properties for backward compatibility
    @property
    def id(self):
        return self.userID
    
    @property
    def username(self):
        return self.userName


class Driver(User):
    __tablename__ = 'drivers'
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), primary_key=True)
    driverRoute = db.Column(db.String(100), nullable=True)
    currentLng = db.Column(db.Float, nullable=True)
    currentLat = db.Column(db.Float, nullable=True)
    
    # Relationships
    routes = db.relationship('Route', backref='driver', lazy=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'driver'
    }

    def __init__(self, userName, password, driverRoute=None, currentLng=None, currentLat=None):
        super().__init__(userName, password)
        self.driverRoute = driverRoute
        self.currentLng = currentLng
        self.currentLat = currentLat

    def get_json(self):
        json_data = super().get_json()
        json_data.update({
            'driverRoute': self.driverRoute,
            'currentLng': self.currentLng,
            'currentLat': self.currentLat
        })
        return json_data


class Resident(User):
    __tablename__ = 'residents'
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), primary_key=True)
    residentName = db.Column(db.String(100), nullable=False)
    residentAddress = db.Column(db.String(200), nullable=False)
    residentPhone = db.Column(db.BigInteger, nullable=False)
    
    # Relationships
    stops = db.relationship('Stop', backref='resident', lazy=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'resident'
    }

    def __init__(self, userName, password, residentName, residentAddress, residentPhone):
        super().__init__(userName, password)
        self.residentName = residentName
        self.residentAddress = residentAddress
        self.residentPhone = residentPhone

    def get_json(self):
        json_data = super().get_json()
        json_data.update({
            'residentName': self.residentName,
            'residentAddress': self.residentAddress,
            'residentPhone': self.residentPhone
        })
        return json_data


class Route(db.Model):
    __tablename__ = 'routes'
    routeID = db.Column(db.Integer, primary_key=True)
    driverID = db.Column(db.Integer, db.ForeignKey('drivers.userID'), nullable=False)
    driveDate = db.Column(db.Date, nullable=False)
    driveTime = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='scheduled')
    
    # Relationships
    streets = db.relationship('Street', backref='route', lazy=True)

    def __init__(self, driverID, driveDate, driveTime, status='scheduled'):
        self.driverID = driverID
        self.driveDate = driveDate
        self.driveTime = driveTime
        self.status = status

    def get_json(self):
        return {
            'routeID': self.routeID,
            'driverID': self.driverID,
            'driveDate': self.driveDate.isoformat() if self.driveDate else None,
            'driveTime': self.driveTime.isoformat() if self.driveTime else None,
            'status': self.status
        }


class Street(db.Model):
    __tablename__ = 'streets'
    streetID = db.Column(db.Integer, primary_key=True)
    routeID = db.Column(db.Integer, db.ForeignKey('routes.routeID'), nullable=False)
    streetName = db.Column(db.String(100), nullable=False)
    streetLocation = db.Column(db.String(200), nullable=False)
    
    # Relationships
    stops = db.relationship('Stop', backref='street', lazy=True)

    def __init__(self, routeID, streetName, streetLocation):
        self.routeID = routeID
        self.streetName = streetName
        self.streetLocation = streetLocation

    def get_json(self):
        return {
            'streetID': self.streetID,
            'routeID': self.routeID,
            'streetName': self.streetName,
            'streetLocation': self.streetLocation
        }


class Stop(db.Model):
    __tablename__ = 'stops'
    stopID = db.Column(db.Integer, primary_key=True)
    residentID = db.Column(db.Integer, db.ForeignKey('residents.userID'), nullable=False)
    streetID = db.Column(db.Integer, db.ForeignKey('streets.streetID'), nullable=False)
    stopTime = db.Column(db.Time, nullable=False)
    stopStatus = db.Column(db.String(50), nullable=False, default='requested')

    def __init__(self, residentID, streetID, stopTime, stopStatus='requested'):
        self.residentID = residentID
        self.streetID = streetID
        self.stopTime = stopTime
        self.stopStatus = stopStatus

    def get_json(self):
        return {
            'stopID': self.stopID,
            'residentID': self.residentID,
            'streetID': self.streetID,
            'stopTime': self.stopTime.isoformat() if self.stopTime else None,
            'stopStatus': self.stopStatus
        }

