from datetime import datetime
from flask_project import db, app
from flask_project.models import Customer, Service_Request, Service_Professional

def db_setup_rbac():
  with app.app_context():
    l = Customer.query.all()
    if not l:
      db.session.add(Customer(id=10001,username='dummy', password='dummy', email='dummy@gmail.com',contact='1234565432'))
      db.session.commit()

  with app.app_context():
    s = Service_Professional.query.all()
    if not s:
      db.session.add(Service_Professional(id=1001,username='dummy', password='dummy', email='dummy@gmail.com',description='im good', experience="5 years"))
      db.session.commit()
  
# def automatic_revoke():
#   with app.app_context():
#     bi = BookIssue.query.all()
#     for i in bi:
#       if i.return_date < datetime.now():
#           db.session.delete(i)
#           db.session.commit()


if __name__ == "__main__":
  db_setup_rbac()
  # automatic_revoke()

  app.run(host='0.0.0.0', debug=True, port=5001)
