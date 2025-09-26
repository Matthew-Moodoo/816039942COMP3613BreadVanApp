from App.models import Driver, Resident, Route, Street, Stop
from App.database import db
from datetime import datetime, date, time
from sqlalchemy import and_

# Driver operations from UML diagram
def schedule_route(driver_userID, route_date, route_time, street_list=None):
    """
    Driver operation: schedule_route(route: Route, street: Street)
    Creates a new route for a driver with associated streets
    """
    try:
        # Create new route
        new_route = Route(driverID=driver_userID, driveDate=route_date, driveTime=route_time)
        db.session.add(new_route)
        db.session.flush()  # Get the route ID
        
        # Add streets to the route if provided
        if street_list:
            for street_info in street_list:
                if isinstance(street_info, dict):
                    street = Street(routeID=new_route.routeID, 
                                  streetName=street_info['name'], 
                                  streetLocation=street_info['location'])
                else:
                    # Assuming it's a tuple (name, location)
                    street = Street(routeID=new_route.routeID, 
                                  streetName=street_info[0], 
                                  streetLocation=street_info[1])
                db.session.add(street)
        
        db.session.commit()
        return new_route
    except Exception as e:
        db.session.rollback()
        return None

def view_stops(driver_userID, route_id=None):
    """
    Driver operation: view_stops(route: Route, routeStops: Stop[])
    Returns all stops for a driver's routes or specific route
    """
    try:
        if route_id:
            # Get stops for specific route
            route = db.session.get(Route, route_id)
            if route and route.driverID == driver_userID:
                stops = []
                for street in route.streets:
                    stops.extend(street.stops)
                return stops
        else:
            # Get all stops for all driver's routes
            driver = db.session.get(Driver, driver_userID)
            if driver:
                all_stops = []
                for route in driver.routes:
                    for street in route.streets:
                        all_stops.extend(street.stops)
                return all_stops
        return []
    except Exception as e:
        return []

def update_route(driver_userID, route_id, new_date=None, new_time=None, new_status=None):
    """
    Driver operation: update_route(route: Route, routeStops: Stop[])
    Updates route information and coordinates driver location
    """
    try:
        route = db.session.get(Route, route_id)
        if route and route.driverID == driver_userID:
            if new_date:
                route.driveDate = new_date
            if new_time:
                route.driveTime = new_time
            if new_status:
                route.status = new_status
            
            db.session.commit()
            return route
        return None
    except Exception as e:
        db.session.rollback()
        return None

# Resident operations from UML diagram
def view_driver(resident_userID, driver_userID=None):
    """
    Resident operation: view_driver(driver: Driver)
    Returns driver information that the resident can see
    """
    try:
        if driver_userID:
            driver = db.session.get(Driver, driver_userID)
            return driver
        else:
            # Return all drivers (public information)
            drivers = db.session.scalars(db.select(Driver)).all()
            return drivers
    except Exception as e:
        return None

def track_driver(resident_userID, driver_userID):
    """
    Resident operation: track_driver(driver: Driver)
    Returns current location and route information for a specific driver
    """
    try:
        driver = db.session.get(Driver, driver_userID)
        if driver:
            tracking_info = {
                'driver': driver,
                'currentLocation': {
                    'latitude': driver.currentLat,
                    'longitude': driver.currentLng
                },
                'currentRoute': driver.driverRoute,
                'activeRoutes': [route for route in driver.routes if route.status == 'active']
            }
            return tracking_info
        return None
    except Exception as e:
        return None

def request_stop(resident_userID, street_id, stop_time):
    """
    Resident operation: request_stop(newStop: Stop)
    Creates a new stop request for the resident
    """
    try:
        # Check if resident already has a stop on this street
        existing_stop = db.session.execute(
            db.select(Stop).filter(
                and_(Stop.residentID == resident_userID, Stop.streetID == street_id)
            )
        ).scalar_one_or_none()
        
        if existing_stop:
            return {'error': 'Stop already requested for this street'}
        
        new_stop = Stop(residentID=resident_userID, streetID=street_id, 
                       stopTime=stop_time, stopStatus='requested')
        db.session.add(new_stop)
        db.session.commit()
        return new_stop
    except Exception as e:
        db.session.rollback()
        return None

def cancel_stop(resident_userID, stop_id):
    """
    Resident operation: cancel_stop(toCancel: Stop)
    Cancels an existing stop request
    """
    try:
        stop = db.session.get(Stop, stop_id)
        if stop and stop.residentID == resident_userID:
            if stop.stopStatus in ['requested', 'confirmed']:
                stop.stopStatus = 'cancelled'
                db.session.commit()
                return stop
            else:
                return {'error': 'Stop cannot be cancelled (already completed or in progress)'}
        return None
    except Exception as e:
        db.session.rollback()
        return None

# Additional utility functions for route management
def get_routes_by_driver(driver_userID):
    """Get all routes for a specific driver"""
    try:
        driver = db.session.get(Driver, driver_userID)
        if driver:
            return driver.routes
        return []
    except Exception as e:
        return []

def get_stops_by_resident(resident_userID):
    """Get all stops requested by a specific resident"""
    try:
        resident = db.session.get(Resident, resident_userID)
        if resident:
            return resident.stops
        return []
    except Exception as e:
        return []

def get_streets_by_route(route_id):
    """Get all streets for a specific route"""
    try:
        route = db.session.get(Route, route_id)
        if route:
            return route.streets
        return []
    except Exception as e:
        return []

def add_street_to_route(route_id, street_name, street_location):
    """Add a street to an existing route"""
    try:
        route = db.session.get(Route, route_id)
        if route:
            street = Street(routeID=route_id, streetName=street_name, streetLocation=street_location)
            db.session.add(street)
            db.session.commit()
            return street
        return None
    except Exception as e:
        db.session.rollback()
        return None

def update_driver_location(driver_userID, new_lat, new_lng):
    """Update driver's current location"""
    try:
        driver = db.session.get(Driver, driver_userID)
        if driver:
            driver.currentLat = new_lat
            driver.currentLng = new_lng
            db.session.commit()
            return driver
        return None
    except Exception as e:
        db.session.rollback()
        return None

def get_active_routes():
    """Get all currently active routes"""
    try:
        active_routes = db.session.execute(
            db.select(Route).filter_by(status='active')
        ).scalars().all()
        return active_routes
    except Exception as e:
        return []