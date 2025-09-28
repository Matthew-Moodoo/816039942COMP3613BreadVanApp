import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from datetime import datetime, date, time

from App.database import db, get_migrate
from App.models import Driver, Resident, Route, Street, Stop
from App.main import create_app
from App.controllers import ( 
    create_user, get_all_users_json, get_all_users, initialize,
    create_driver, create_resident, get_all_drivers, get_all_residents,
    schedule_route, view_stops, update_route,
    view_driver, track_driver, request_stop, cancel_stop,
    get_routes_by_driver, get_stops_by_resident, add_street_to_route,
    update_driver_location, get_active_routes
)


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Driver Commands
'''

driver_cli = AppGroup('driver', help='Driver object commands')

@driver_cli.command("create", help="Creates a driver")
@click.argument("username")
@click.argument("password")
@click.option("--route", default=None, help="Driver route")
@click.option("--lat", default=None, type=float, help="Current latitude")
@click.option("--lng", default=None, type=float, help="Current longitude")
def create_driver_command(username, password, route, lat, lng):
    driver = create_driver(username, password, route, lng, lat)
    if driver:
        print(f'Driver {username} created with ID: {driver.userID}')
    else:
        print(f'Failed to create driver {username}')

@driver_cli.command("list", help="Lists all drivers")
def list_drivers_command():
    drivers = get_all_drivers()
    for driver in drivers:
        print(f'ID: {driver.userID}, Name: {driver.userName}, Route: {driver.driverRoute}')

@driver_cli.command("schedule", help="Schedule a route for a driver (date: YYYY-MM-DD, time: HH:MM)")
@click.argument("driver_id", type=int)
@click.argument("date_str")
@click.argument("time_str")
def schedule_route_command(driver_id, date_str, time_str):
    try:
        route_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        route_time = datetime.strptime(time_str, '%H:%M').time()
        route = schedule_route(driver_id, route_date, route_time)
        if route:
            print(f'Route scheduled for driver {driver_id}: Route ID {route.routeID}')
        else:
            print('Failed to schedule route')
    except ValueError as e:
        print(f'Invalid date/time format: {e}')

@driver_cli.command("view-stops", help="View stops for a driver")
@click.argument("driver_id", type=int)
@click.option("--route-id", default=None, type=int, help="Specific route ID")
def view_stops_command(driver_id, route_id):
    stops = view_stops(driver_id, route_id)
    if stops:
        for stop in stops:
            print(f'Stop ID: {stop.stopID}, Resident: {stop.residentID}, Time: {stop.stopTime}, Status: {stop.stopStatus}')
    else:
        print('No stops found')

@driver_cli.command("update-route", help="Update a route")
@click.argument("driver_id", type=int)
@click.argument("route_id", type=int)
@click.option("--status", help="New status")
@click.option("--date", help="New date (YYYY-MM-DD)")
@click.option("--time", help="New time (HH:MM)")
def update_route_command(driver_id, route_id, status, date, time):
    new_date = datetime.strptime(date, '%Y-%m-%d').date() if date else None
    new_time = datetime.strptime(time, '%H:%M').time() if time else None
    route = update_route(driver_id, route_id, new_date, new_time, status)
    if route:
        print(f'Route {route_id} updated successfully')
    else:
        print('Failed to update route')

@driver_cli.command("update-location", help="Update driver location")
@click.argument("driver_id", type=int)
@click.argument("lat", type=float)
@click.argument("lng", type=float)
def update_location_command(driver_id, lat, lng):
    driver = update_driver_location(driver_id, lat, lng)
    if driver:
        print(f'Location updated for driver {driver_id}: ({lat}, {lng})')
    else:
        print('Failed to update location')

app.cli.add_command(driver_cli)

'''
Resident Commands
'''

resident_cli = AppGroup('resident', help='Resident object commands')

@resident_cli.command("create", help="Creates a resident")
@click.argument("username")
@click.argument("password")
@click.argument("name")
@click.argument("address")
@click.argument("phone", type=int)
def create_resident_command(username, password, name, address, phone):
    resident = create_resident(username, password, name, address, phone)
    if resident:
        print(f'Resident {username} created with ID: {resident.userID}')
    else:
        print(f'Failed to create resident {username}')

@resident_cli.command("list", help="Lists all residents")
def list_residents_command():
    residents = get_all_residents()
    for resident in residents:
        print(f'ID: {resident.userID}, Name: {resident.userName}, Address: {resident.residentAddress}, Phone: {resident.residentPhone}')

@resident_cli.command("view-driver", help="View driver information")
@click.argument("resident_id", type=int)
@click.option("--driver-id", default=None, type=int, help="Specific driver ID")
def view_driver_command(resident_id, driver_id):
    drivers = view_driver(resident_id, driver_id)
    if isinstance(drivers, list):
        for driver in drivers:
            print(f'Driver ID: {driver.userID}, Username: {driver.userName}, Route: {driver.driverRoute}')
    elif drivers:
        print(f'Driver ID: {drivers.userID}, Username: {drivers.userName}, Route: {drivers.driverRoute}')
    else:
        print('No drivers found')

@resident_cli.command("track-driver", help="Track a specific driver")
@click.argument("resident_id", type=int)
@click.argument("driver_id", type=int)
def track_driver_command(resident_id, driver_id):
    tracking_info = track_driver(resident_id, driver_id)
    if tracking_info:
        driver = tracking_info['driver']
        location = tracking_info['currentLocation']
        print(f'Driver: {driver.userName}')
        print(f'Current Location: ({location["latitude"]}, {location["longitude"]})')
        print(f'Current Route: {tracking_info["currentRoute"]}')
        print(f'Active Routes: {len(tracking_info["activeRoutes"])}')
    else:
        print('Driver not found')

@resident_cli.command("request-stop", help="Request a stop (time format: HH:MM)")
@click.argument("resident_id", type=int)
@click.argument("street_id", type=int)
@click.argument("time_str")
def request_stop_command(resident_id, street_id, time_str):
    try:
        stop_time = datetime.strptime(time_str, '%H:%M').time()
        result = request_stop(resident_id, street_id, stop_time)
        if isinstance(result, dict) and 'error' in result:
            print(f'Error: {result["error"]}')
        elif result:
            print(f'Stop requested: Stop ID {result.stopID}')
        else:
            print('Failed to request stop')
    except ValueError as e:
        print(f'Invalid time format: {e}')

@resident_cli.command("cancel-stop", help="Cancel a stop")
@click.argument("resident_id", type=int)
@click.argument("stop_id", type=int)
def cancel_stop_command(resident_id, stop_id):
    result = cancel_stop(resident_id, stop_id)
    if isinstance(result, dict) and 'error' in result:
        print(f'Error: {result["error"]}')
    elif result:
        print(f'Stop {stop_id} cancelled successfully')
    else:
        print('Failed to cancel stop')

@resident_cli.command("my-stops", help="View all stops for a resident")
@click.argument("resident_id", type=int)
def my_stops_command(resident_id):
    stops = get_stops_by_resident(resident_id)
    if stops:
        for stop in stops:
            print(f'Stop ID: {stop.stopID}, Street: {stop.streetID}, Time: {stop.stopTime}, Status: {stop.stopStatus}')
    else:
        print('No stops found')

app.cli.add_command(resident_cli)

'''
Route Management Commands
'''

route_cli = AppGroup('route', help='Route management commands')

@route_cli.command("add-street", help="Add street to a route")
@click.argument("route_id", type=int)
@click.argument("street_name")
@click.argument("street_location")
def add_street_command(route_id, street_name, street_location):
    street = add_street_to_route(route_id, street_name, street_location)
    if street:
        print(f'Street added to route {route_id}: {street_name}')
    else:
        print('Failed to add street to route')

@route_cli.command("active", help="List all active routes")
def active_routes_command():
    routes = get_active_routes()
    if routes:
        for route in routes:
            print(f'Route ID: {route.routeID}, Driver: {route.driverID}, Date: {route.driveDate}, Status: {route.status}')
    else:
        print('No active routes found')

@route_cli.command("list-streets", help="List all streets")
def list_streets_command():
    from App.models.user import Street
    streets = Street.query.all()
    if streets:
        for street in streets:
            print(f'Street ID: {street.streetID}, Name: {street.streetName}, Location: {street.streetLocation}, Route: {street.routeID}')
    else:
        print('No streets found')

app.cli.add_command(route_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)