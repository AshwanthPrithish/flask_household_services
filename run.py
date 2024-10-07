from datetime import datetime
from flask_project import db, app
from flask_project.models import Customer, Service, Service_Request, Service_Professional

def db_setup_rbac():
    with app.app_context():
        # Check for existing customers and create a dummy customer if none exist
        customer_list = Customer.query.all()
        if not customer_list:
            dummy_customer = Customer(
                id=10001,
                username='dummy_customer',
                password='dummy_password',
                address="123 Dummy Street, Nowhere",
                email='dummy_customer@gmail.com',
                contact='1234565432'
            )
            db.session.add(dummy_customer)
            db.session.commit()

        # Check for existing services and create dummy household services if none exist
        service_list = Service.query.all()
        if not service_list:
            # Create three dummy services
            services = [
                Service(name='House Cleaning', price='50', description='Professional house cleaning service'),
                Service(name='Plumbing', price='75', description='Expert plumbing services for all your needs'),
                Service(name='Electrical Work', price='100', description='Certified electrical services for your home'),
            ]
            db.session.bulk_save_objects(services)  # Bulk add services
            db.session.commit()

        # Now check for existing service professionals and create a dummy if none exist
        service_professional_list = Service_Professional.query.all()
        if not service_professional_list:
            # Get the IDs of the services to associate with the service professional
            service_ids = [service.id for service in Service.query.all()]

            # Create a dummy service professional for each service
            for service_id in service_ids:
                dummy_service_professional = Service_Professional(
                    id=1001 + service_id,  # Ensure unique IDs
                    username=f'dummy_professional_{service_id}',
                    password='dummy_password',
                    email=f'dummy_professional_{service_id}@gmail.com',
                    description='Experienced household service provider',
                    experience="5 years",
                    service_id=service_id  # Associate with the service
                )
                db.session.add(dummy_service_professional)
            db.session.commit()

if __name__ == "__main__":
    db_setup_rbac()
    app.run(host='0.0.0.0', debug=True, port=5001)
