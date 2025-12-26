# app.py
from flask import Flask, render_template, request, redirect, session, url_for, g
import mysql.connector
import logging
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

try:
    from config import Config
except ImportError:
    raise RuntimeError("FATAL: config.py not found. Please create config.py with Config class.")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.secret_key = Config.SECRET_KEY

# -------------------------
# Database connection
# -------------------------
def get_db():
    if 'db' not in g:
        try:
            if not Config.DB_PASSWORD:
                raise RuntimeError("DB_PASSWORD not configured in config.py or environment.")
            g.db = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False
            )
            logger.debug("Database connection established.")
        except mysql.connector.Error as err:
            logger.exception("Database connection failed.")
            raise RuntimeError(f"Database connection failed: {err}")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None and getattr(db, "is_connected", lambda: True)():
        try:
            db.close()
            logger.debug("Database connection closed.")
        except Exception:
            pass

# -------------------------
# Helpers
# -------------------------
def is_admin_or_employee():
    return session.get('role') in ['admin', 'employee']

def _add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# -------------------------
# Routes: index/login/logout/register
# -------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '').lower()

        if role not in ['admin', 'employee', 'member']:
            return "Invalid role specified.", 400

        table = role.capitalize()  # Admin, Employee, Member
        db = get_db()
        try:
            # Use dictionary cursor for select to keep key access consistent
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table} WHERE username=%s", (username,))
            user = cursor.fetchone()
            cursor.close()

            if not user:
                return "Login Failed: Invalid username or password.", 401

            stored = user.get('password', '')

            # If the stored password looks like a werkzeug hash (starts with algo:)
            if stored.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
                if check_password_hash(stored, password):
                    session['username'] = user['username']
                    session['role'] = role
                    return redirect(url_for(f'{role}_dashboard'))
                else:
                    return "Login Failed: Invalid username or password.", 401
            else:
                # Plaintext stored (not recommended). Compare directly.
                if stored == password:
                    session['username'] = user['username']
                    session['role'] = role
                    return redirect(url_for(f'{role}_dashboard'))
                else:
                    return "Login Failed: Invalid username or password.", 401
        except Exception as e:
            logger.exception("Login Error")
            return f"Login Error: {str(e)}", 500

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        raw_password = request.form.get('password', '')

        if not (username and email and raw_password):
            return "All fields are required.", 400

        hashed_password = generate_password_hash(raw_password)
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Member (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed_password))
            db.commit()
            cursor.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            db.rollback()
            logger.exception("Registration Error")
            return f"Registration failed: {str(e)}", 500

    return render_template('register.html')

# -------------------------
# Dashboard helpers & routes
# -------------------------
def _get_dashboard_stats(role, username=None):
    stats = {'books_count': 0, 'reservations_count': 0, 'fines_count': 0, 'members_count': 0}
    db = get_db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS count FROM Book")
        stats['books_count'] = cursor.fetchone()['count'] or 0

        if role == 'admin':
            cursor.execute("SELECT COUNT(*) AS count FROM Member")
            stats['members_count'] = cursor.fetchone()['count'] or 0
            cursor.execute("SELECT COUNT(*) AS count FROM Reservation")
            stats['reservations_count'] = cursor.fetchone()['count'] or 0
            cursor.execute("SELECT COUNT(*) AS count FROM Fine")
            stats['fines_count'] = cursor.fetchone()['count'] or 0
        elif role == 'employee':
            cursor.execute("SELECT COUNT(*) AS count FROM Reservation")
            stats['reservations_count'] = cursor.fetchone()['count'] or 0
            cursor.execute("SELECT COUNT(*) AS count FROM Fine")
            stats['fines_count'] = cursor.fetchone()['count'] or 0
        elif role == 'member' and username:
            cursor.execute("SELECT id FROM Member WHERE username=%s", (username,))
            member = cursor.fetchone()
            if member:
                member_id = member['id']
                cursor.execute("SELECT COUNT(*) AS count FROM Reservation WHERE member_id=%s", (member_id,))
                stats['reservations_count'] = cursor.fetchone()['count'] or 0
                cursor.execute("SELECT COUNT(*) AS count FROM Fine WHERE member_id=%s", (member_id,))
                stats['fines_count'] = cursor.fetchone()['count'] or 0

        cursor.close()
    except Exception:
        logger.exception("Error building dashboard stats")
    return stats

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    stats = _get_dashboard_stats('admin')
    response = app.make_response(render_template('admin_dashboard.html', **stats))
    return _add_no_cache_headers(response)

@app.route('/employee/dashboard')
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))
    stats = _get_dashboard_stats('employee')
    response = app.make_response(render_template('employee_dashboard.html', **stats))
    return _add_no_cache_headers(response)

@app.route('/member/dashboard')
def member_dashboard():
    if session.get('role') != 'member':
        return redirect(url_for('login'))
    stats = _get_dashboard_stats('member', session.get('username'))
    response = app.make_response(render_template('member_dashboard.html', **stats))
    return _add_no_cache_headers(response)

# -------------------------
# Book management
# -------------------------
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if not is_admin_or_employee():
        return redirect(url_for('login'))

    db = get_db()
    # Use dictionary cursor for read operations
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM Author")
    authors = cursor.fetchall()
    cursor.execute("SELECT id, name FROM Publisher")
    publishers = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        quantity = request.form.get('quantity', '').strip()
        # Safely get author_id / publisher_id
        author_id = request.form.get('author_id')  # might be '' or None
        new_author_name = request.form.get('new_author_name', '').strip()
        publisher_id = request.form.get('publisher_id')
        new_publisher_name = request.form.get('new_publisher_name', '').strip()

        if not title or not quantity:
            return render_template('add_book.html', authors=authors, publishers=publishers,
                                   error="Title and quantity are required.")

        try:
            q_int = int(quantity)
        except ValueError:
            return render_template('add_book.html', authors=authors, publishers=publishers,
                                   error="Quantity must be an integer.")

        try:
            cursor = db.cursor()
            # Insert new author if provided
            if new_author_name:
                cursor.execute("INSERT INTO Author (name) VALUES (%s)", (new_author_name,))
                db.commit()
                author_id = cursor.lastrowid
            else:
                # allow author_id empty -> set None
                author_id = int(author_id) if author_id else None

            # Insert new publisher if provided
            if new_publisher_name:
                cursor.execute("INSERT INTO Publisher (name) VALUES (%s)", (new_publisher_name,))
                db.commit()
                publisher_id = cursor.lastrowid
            else:
                publisher_id = int(publisher_id) if publisher_id else None

            cursor.execute("INSERT INTO Book (title, author_id, publisher_id, quantity) VALUES (%s, %s, %s, %s)",
                           (title, author_id, publisher_id, q_int))
            db.commit()
            cursor.close()
            return redirect(url_for('manage_books'))
        except Exception as e:
            db.rollback()
            logger.exception("Error inserting book")
            return render_template('add_book.html', authors=authors, publishers=publishers, error=str(e))

    return render_template('add_book.html', authors=authors, publishers=publishers)

@app.route('/manage-books')
def manage_books():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT Book.id, Book.title, Author.name AS author, Publisher.name AS publisher, Book.quantity 
                      FROM Book
                      LEFT JOIN Author ON Book.author_id = Author.id 
                      LEFT JOIN Publisher ON Book.publisher_id = Publisher.id""")
    books = cursor.fetchall()
    cursor.close()
    return render_template('manage_books.html', books=books)

@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM Author")
    authors = cursor.fetchall()
    cursor.execute("SELECT id, name FROM Publisher")
    publishers = cursor.fetchall()
    cursor.execute("SELECT * FROM Book WHERE id=%s", (book_id,))
    book = cursor.fetchone()
    cursor.close()

    if not book:
        return "Book not found!", 404

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author_id = request.form.get('author_id')
        publisher_id = request.form.get('publisher_id')
        quantity = request.form.get('quantity', '').strip()

        try:
            q_int = int(quantity)
        except ValueError:
            return "Quantity must be an integer.", 400

        try:
            cursor = db.cursor()
            author_id = int(author_id) if author_id else None
            publisher_id = int(publisher_id) if publisher_id else None

            cursor.execute("UPDATE Book SET title=%s, author_id=%s, publisher_id=%s, quantity=%s WHERE id=%s",
                           (title, author_id, publisher_id, q_int, book_id))
            db.commit()
            cursor.close()
            return redirect(url_for('manage_books'))
        except Exception as e:
            db.rollback()
            logger.exception("Error updating book")
            return f"Update Error: {str(e)}", 500

    return render_template('edit_book.html', book=book, authors=authors, publishers=publishers)

@app.route('/delete-book/<int:book_id>')
def delete_book(book_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Book WHERE id=%s", (book_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('manage_books'))

# -------------------------
# Issue & return books
# -------------------------
@app.route('/admin/issue-book', methods=['GET', 'POST'])
@app.route('/employee/issue-book', methods=['GET', 'POST'])
def issue_book():
    if not is_admin_or_employee():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, title FROM Book WHERE quantity > 0")
    books = cursor.fetchall()
    cursor.execute("SELECT id, username FROM Member")
    members = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        issue_date = request.form.get('issue_date')
        return_date = request.form.get('return_date')

        if not (book_id and member_id and issue_date and return_date):
            return "All fields are required.", 400

        try:
            cursor = db.cursor()
            cursor.execute("UPDATE Book SET quantity = quantity - 1 WHERE id=%s AND quantity > 0", (book_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return "Book issue failed: Out of stock.", 400

            cursor.execute("""
                INSERT INTO Issued_Books (book_id, member_id, issue_date, return_date)
                VALUES (%s, %s, %s, %s)
            """, (book_id, member_id, issue_date, return_date))
            db.commit()
            cursor.close()
            return redirect(url_for('view_issued_books'))
        except Exception as e:
            db.rollback()
            logger.exception("Error issuing book")
            return f"Error issuing book: {str(e)}", 500

    return render_template('issue_book.html', books=books, members=members)

@app.route('/admin/issued-books')
@app.route('/employee/issued-books')
def view_issued_books():
    if not is_admin_or_employee():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ib.id, b.title AS book_title, m.username AS member_name,
               ib.issue_date, ib.return_date, ib.returned, ib.book_id
        FROM Issued_Books ib
        JOIN Book b ON ib.book_id = b.id
        JOIN Member m ON ib.member_id = m.id
        ORDER BY ib.issue_date DESC
    """)
    issued_books = cursor.fetchall()
    cursor.close()
    return render_template('issued_books.html', issued_books=issued_books)

@app.route('/admin/return-book/<int:issue_id>')
@app.route('/employee/return-book/<int:issue_id>')
def return_book(issue_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))

    db = get_db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT book_id FROM Issued_Books WHERE id=%s AND returned=FALSE", (issue_id,))
        rec = cursor.fetchone()
        cursor.close()

        if not rec:
            return "Book already returned or not found.", 404

        book_id = rec['book_id']
        cursor = db.cursor()
        cursor.execute("UPDATE Issued_Books SET returned=TRUE WHERE id=%s", (issue_id,))
        cursor.execute("UPDATE Book SET quantity = quantity + 1 WHERE id=%s", (book_id,))
        db.commit()
        cursor.close()
        return redirect(url_for('view_issued_books'))
    except Exception as e:
        db.rollback()
        logger.exception("Error returning book")
        return f"Error returning book: {str(e)}", 500

# -------------------------
# Member management
# -------------------------
@app.route('/admin/add-member', methods=['GET', 'POST'])
def add_member():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        raw_password = request.form.get('password', '')

        if not (username and email and raw_password):
            return "All fields required.", 400

        hashed = generate_password_hash(raw_password)
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Member (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed))
            db.commit()
            cursor.close()
            return redirect(url_for('view_members'))
        except Exception as e:
            db.rollback()
            logger.exception("Error adding member")
            return f"Error adding member: {str(e)}", 500

    return render_template('add_member.html')

@app.route('/admin/view-members')
def view_members():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM Member")
        members = cursor.fetchall()
        cursor.close()
        return render_template('view_members.html', members=members)
    except Exception as e:
        logger.exception("Error fetching members")
        return render_template('view_members.html', members=[], error=str(e))

@app.route('/admin/delete-member/<int:member_id>')
def delete_member(member_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Member WHERE id=%s", (member_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('view_members'))

# -------------------------
# Authors & Publishers
# -------------------------
@app.route('/admin/authors')
def view_authors():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM Author")
    authors = cursor.fetchall()
    cursor.close()
    return render_template('authors.html', authors=authors)

@app.route('/admin/add-author', methods=['GET', 'POST'])
def add_author():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Author (name) VALUES (%s)", (name,))
        db.commit()
        cursor.close()
        return redirect(url_for('view_authors'))
    return render_template('add_author.html')

@app.route('/admin/publishers')
def view_publishers():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM Publisher")
    publishers = cursor.fetchall()
    cursor.close()
    return render_template('publishers.html', publishers=publishers)

@app.route('/admin/add-publisher', methods=['GET', 'POST'])
def add_publisher():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Publisher (name) VALUES (%s)", (name,))
        db.commit()
        cursor.close()
        return redirect(url_for('view_publishers'))
    return render_template('add_publisher.html')

# -------------------------
# Reservations / Vendors / Fines
# -------------------------
@app.route('/view-reservations')
def view_reservations():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, b.title AS book_title, m.username AS member_username, r.reservation_date
        FROM Reservation AS r
        JOIN Book AS b ON r.book_id = b.id
        JOIN Member AS m ON r.member_id = m.id
    """)
    reservations = cursor.fetchall()
    cursor.close()
    return render_template('view_reservations.html', reservations=reservations)

@app.route('/admin/vendors')
def manage_vendors():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, contact FROM Vendor")
    vendors = cursor.fetchall()
    cursor.close()
    return render_template('manage_vendors.html', vendors=vendors)

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Vendor (name, contact) VALUES (%s, %s)", (name, contact))
        db.commit()
        cursor.close()
        return redirect(url_for('manage_vendors'))
    return render_template('add_vendor.html')

@app.route('/admin/vendor/delete/<int:vendor_id>')
def delete_vendor_by_id(vendor_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Vendor WHERE id=%s", (vendor_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('manage_vendors'))

@app.route('/admin/fines')
def manage_fines():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT Fine.id, Member.username, Fine.amount, Fine.reason, Fine.date_assessed
        FROM Fine
        JOIN Member ON Fine.member_id = Member.id
    """)
    fines = cursor.fetchall()
    cursor.close()
    return render_template('manage_fines.html', fines=fines)

@app.route('/admin/fine/add', methods=['GET', 'POST'])
def add_fine():
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM Member")
    members = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        amount = request.form.get('amount')
        reason = request.form.get('reason', '').strip()
        date_assessed = request.form.get('date_assessed')

        cursor = db.cursor()
        cursor.execute("INSERT INTO Fine (member_id, amount, reason, date_assessed) VALUES (%s, %s, %s, %s)",
                       (member_id, amount, reason, date_assessed))
        db.commit()
        cursor.close()
        return redirect(url_for('manage_fines'))

    return render_template('add_fine.html', members=members)

@app.route('/admin/fine/delete/<int:fine_id>')
def delete_fine(fine_id):
    if not is_admin_or_employee():
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Fine WHERE id=%s", (fine_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('manage_fines'))

# -------------------------
# Member-specific pages
# -------------------------
@app.route('/member/view-books')
def view_books():
    if session.get('role') != 'member':
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT Book.id, Book.title, Author.name AS author, Publisher.name AS publisher, Book.quantity 
        FROM Book
        LEFT JOIN Author ON Book.author_id = Author.id
        LEFT JOIN Publisher ON Book.publisher_id = Publisher.id
        ORDER BY Book.title
    """)
    books = cursor.fetchall()
    cursor.close()
    return render_template('view_books.html', books=books)

@app.route('/member/reserve-book', methods=['GET', 'POST'])
def reserve_book():
    if session.get('role') != 'member':
        return redirect(url_for('login'))
    db = get_db()
    username = session.get('username')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM Member WHERE username=%s", (username,))
    member = cursor.fetchone()
    member_id = member['id'] if member else None
    cursor.close()

    if not member_id:
        return "Could not find member information for reservation.", 404

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        try:
            cursor = db.cursor()
            cursor.execute("UPDATE Book SET quantity = quantity - 1 WHERE id=%s AND quantity > 0", (book_id,))
            if cursor.rowcount == 0:
                db.rollback()
                return "Reservation failed: Book is out of stock or does not exist.", 400
            cursor.execute("INSERT INTO Reservation (book_id, member_id, reservation_date) VALUES (%s, %s, CURDATE())",
                           (book_id, member_id))
            db.commit()
            cursor.close()
            return "Book reserved successfully!"
        except Exception as e:
            db.rollback()
            logger.exception("Reservation failed")
            return f"Reservation failed: {str(e)}", 500

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT Book.id, Book.title, Author.name AS author, Book.quantity 
        FROM Book 
        LEFT JOIN Author ON Book.author_id = Author.id 
        WHERE Book.quantity > 0
    """)
    books = cursor.fetchall()
    cursor.close()
    return render_template('reserve_book.html', books=books)

@app.route('/member/my-fines')
def my_fines():
    if session.get('role') != 'member':
        return redirect(url_for('login'))
    db = get_db()
    username = session.get('username')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM Member WHERE username=%s", (username,))
    member = cursor.fetchone()
    if member:
        cursor.execute("SELECT * FROM Fine WHERE member_id=%s ORDER BY date_assessed DESC", (member['id'],))
        fines = cursor.fetchall()
        cursor.close()
        return render_template('my_fines.html', fines=fines)
    cursor.close()
    return "Could not find member information.", 404

# -------------------------
# Run
# -------------------------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
