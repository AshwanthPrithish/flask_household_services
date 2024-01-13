from flask_project import db, app
from flask_project.models import Student, Librarian

def db_setup_rbac():
  with app.app_context():
    l = Librarian.query.all()
    if not l:
      db.session.add(Librarian(id=10001,username='dummy', password='dummy', email='dummy@gmail.com', admin_id=12345))
      db.session.commit()

  with app.app_context():
    s = Student.query.all()
    if not s:
      db.session.add(Student(id=1001,username='dummy', password='dummy', email='dummy@gmail.com'))
      db.session.commit()

if __name__ == "__main__":
  db_setup_rbac()

  app.run(host='0.0.0.0', debug=True)
