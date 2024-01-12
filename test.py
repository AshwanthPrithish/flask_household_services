from flask_project import app, db
from flask_project.models import Student, Librarian, Book, BookIssue, Genre
from datetime import datetime
# Create all tables in the database
with app.app_context():
    db.create_all()

    # Librarian adding three new books to the database
    librarian = Librarian(username='librarian1', email='librarian1@example.com', admin_id=124, password='password123')
    db.session.add(librarian)
    db.session.commit()

    genre1 = Genre(name='Genre 1', id=12)
    genre2 = Genre(name='Genre 2', id=14)
    genre3 = Genre(name='Genre 3', id=15)

    db.session.add_all([genre1, genre2, genre3])
    db.session.commit()

    book1 = Book(title='Book 1', author='Author 1', content='Content 1', rating=5, librarian_admin=librarian, genre=genre1.name, genre_id=genre1.id)
    book2 = Book(title='Book 2', author='Author 2', content='Content 2', rating=4, librarian_admin=librarian, genre=genre2.name, genre_id=genre2.id)
    book3 = Book(title='Book 3', author='Author 3', content='Content 3', rating=3, librarian_admin=librarian, genre=genre3.name, genre_id=genre3.id)
    book4 = Book(title='Book 4', author='Author 4', content='Content 4', rating=2, librarian_admin=librarian, genre=genre1.name, genre_id=genre1.id)

    db.session.add_all([book1, book2, book3, book4])
    db.session.commit()

    print("\nLibrarian, Books, and Genres in the Database:")
    print("Librarian:", Librarian.query.all())
    print("Books:", Book.query.all())
    print("Genres:", Genre.query.all())

    # Student being issued one book by a librarian
    student = Student(username='student1', email='student@example.com', password='password123')
    db.session.add(student)
    db.session.commit()

    librarian = Librarian.query.first()
    book_to_issue = Book.query.filter_by(title='Book 1').first()

    book_issue = BookIssue(issue_date=datetime.utcnow(), student=student, book=book_to_issue, librarian=librarian)

    db.session.add(book_issue)
    db.session.commit()

    print("\nIssued Books Information:")
    print("Issued Books:", BookIssue.query.all())
    print("Issued Book Details:")
    for issued_book in BookIssue.query.all():
        print(issued_book)
        print("Student:", issued_book.student)
        print("Book:", issued_book.book)
        print("Librarian:", issued_book.librarian)
        print()

    print("\nBooks and their associated genres:")
    all_books = Book.query.all()
    for book in all_books:
        print(f"Book: {book.title}, Genre: {book.genre}, Genre ID: {book.genre_id}")


    # Print books in a specific genre
    print("\nBooks in Genre 1:")
    books_in_genre1 = Genre.query.filter_by(name='Genre 1').first().books
    print(books_in_genre1)