from App.models import Driver, Resident
from App.database import db

# Driver functions
def create_driver(userName, password, driverRoute=None, currentLng=None, currentLat=None):
    new_driver = Driver(userName=userName, password=password, driverRoute=driverRoute, 
                       currentLng=currentLng, currentLat=currentLat)
    db.session.add(new_driver)
    db.session.commit()
    return new_driver

def get_driver_by_username(userName):
    result = db.session.execute(db.select(Driver).filter_by(userName=userName))
    return result.scalar_one_or_none()

def get_driver(userID):
    return db.session.get(Driver, userID)

def get_all_drivers():
    return db.session.scalars(db.select(Driver)).all()

def get_all_drivers_json():
    drivers = get_all_drivers()
    if not drivers:
        return []
    return [driver.get_json() for driver in drivers]

def update_driver(userID, userName=None, driverRoute=None, currentLng=None, currentLat=None):
    driver = get_driver(userID)
    if driver:
        if userName:
            driver.userName = userName
        if driverRoute:
            driver.driverRoute = driverRoute
        if currentLng is not None:
            driver.currentLng = currentLng
        if currentLat is not None:
            driver.currentLat = currentLat
        db.session.commit()
        return True
    return None

# Resident functions
def create_resident(userName, password, residentName, residentAddress, residentPhone):
    new_resident = Resident(userName=userName, password=password, residentName=residentName,
                           residentAddress=residentAddress, residentPhone=residentPhone)
    db.session.add(new_resident)
    db.session.commit()
    return new_resident

def get_resident_by_username(userName):
    result = db.session.execute(db.select(Resident).filter_by(userName=userName))
    return result.scalar_one_or_none()

def get_resident(userID):
    return db.session.get(Resident, userID)

def get_all_residents():
    return db.session.scalars(db.select(Resident)).all()

def get_all_residents_json():
    residents = get_all_residents()
    if not residents:
        return []
    return [resident.get_json() for resident in residents]

def update_resident(userID, userName=None, residentName=None, residentAddress=None, residentPhone=None):
    resident = get_resident(userID)
    if resident:
        if userName:
            resident.userName = userName
        if residentName:
            resident.residentName = residentName
        if residentAddress:
            resident.residentAddress = residentAddress
        if residentPhone:
            resident.residentPhone = residentPhone
        db.session.commit()
        return True
    return None

# Legacy functions for backward compatibility
def create_user(username, password):
    # Default to creating a driver for backward compatibility
    return create_driver(username, password)

def get_user_by_username(username):
    # Try to find driver first, then resident
    driver = get_driver_by_username(username)
    if driver:
        return driver
    return get_resident_by_username(username)

def get_user(id):
    # Try to find driver first, then resident
    driver = get_driver(id)
    if driver:
        return driver
    return get_resident(id)

def get_all_users():
    # Return all drivers and residents
    drivers = get_all_drivers()
    residents = get_all_residents()
    return drivers + residents

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    return [user.get_json() for user in users]

def update_user(id, username):
    # Try updating as driver first, then resident
    if update_driver(id, userName=username):
        return True
    return update_resident(id, userName=username)
