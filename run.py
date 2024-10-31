from flask_project import db, bcrypt, create_app
from flask_project.models import Admin, Customer, Service, Service_Request, Service_Professional

app = create_app()
def db_setup_rbac():
    with app.app_context():
        if not Admin.query.first():
            # Create an admin user
            hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
            admin_user = Admin(id=-1, username='admin', email='admin@test.com', password=hashed_password) # type: ignore
            db.session.add(admin_user)
            db.session.commit()

    with app.app_context():
        # Check for existing customers and create a dummy customer if none exist
        customer_list = Customer.query.all()
        if not customer_list:
            dummy_customer = Customer(
                id=1001, # type: ignore
                username='dummy_customer', # type: ignore
                password='dummy_password', # type: ignore
                address="123 Dummy Street, Nowhere", # type: ignore
                email='dummy_customer@gmail.com', # type: ignore
                contact='1234565432' # type: ignore
            )
            db.session.add(dummy_customer)
            db.session.commit()

        # Check for existing services and create dummy household services if none exist
        service_list = Service.query.all()
        if not service_list:
            # Create three dummy services
            services = [
                Service(name='Cleaning', price='50', description='cleaning service'), # type: ignore
                 Service(name='Washing', price='50', description='washing service'), # type: ignore
            ]
            db.session.bulk_save_objects(services)  # Bulk add services
            db.session.commit()

        # Now check for existing service professionals and create a dummy if none exist
        service_professional_list = Service_Professional.query.all()
        if not service_professional_list:
            # Get the IDs of the services to associate with the service professional
            service_ids = [Service.query.first_or_404().id]

            # Create a dummy service professional for each service
            x = 0
            for service_id in service_ids:
                dummy_service_professional = Service_Professional(
                    id=10001,  # Ensure unique IDs # type: ignore
                    username=f'dummy_professional_{x}', # type: ignore
                    password='dummy_password', # type: ignore
                    email=f'dummy_professional_{x}@gmail.com', # type: ignore
                    description='Experienced household service provider', # type: ignore
                    experience="5 years", # type: ignore
                    service_id=service_id  # Associate with the service # type: ignore
                )
                x += 1
                db.session.add(dummy_service_professional)
            db.session.commit()

if __name__ == "__main__":
    db_setup_rbac()
    app.run(host='0.0.0.0', debug=True, port=5001)
