'''
from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for flash messages

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "KDdas@321",
    "database": "mydb",   # this is the DATABASE name
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    print("Received from form:", name, email)  # debug

    if not name or not email:
        flash("Both name and email are required.")
        return redirect(url_for("index"))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        print("DB connected")  # debug
        cursor = conn.cursor()

        # Make sure this table exists in DB "mydb"
        # CREATE TABLE mydb_t (
        #   id INT AUTO_INCREMENT PRIMARY KEY,
        #   name VARCHAR(255),
        #   email VARCHAR(255)
        # );

        insert_query = "INSERT INTO mydb_t (name, email) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, email))
        conn.commit()
        print("Inserted row ID:", cursor.lastrowid)  # debug
        flash("Data inserted successfully!")
    except Error as e:
        print("Error while inserting into MySQL:", e)
        flash(f"Error saving data: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for("index"))

'''
'''if __name__ == "__main__":
    app.run(debug=True)'''
'''
'''
'''DATA INSERTED SUCCESSFULLY IN DATABASE'''
'''

@app.route("/showdb", methods=["GET"])
def showdb():
    # Get the email from query string (e.g. /showdb?email=abc@example.com)
    email = request.args.get("email", "").strip()
    results = []

    if email:  # only search if something was entered
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # search by email (partial match)
            query = "SELECT id, name, email FROM mydb_t WHERE email LIKE %s"
            cursor.execute(query, (f"%{email}%",))
            results = cursor.fetchall()
        except Error as e:
            print("Error while reading from MySQL:", e)
            flash(f"Error reading data: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

    # results is a list of tuples: (id, name, email)
    return render_template("showdb.html", results=results, search_email=email)

'''
'''////////////////////////////////'''


'''

@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit(record_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            # Save the edited data
            name = request.form.get("name")
            email = request.form.get("email")

            if not name or not email:
                flash("Name and email are required.")
                return redirect(url_for("edit", record_id=record_id))

            update_query = "UPDATE mydb_t SET name = %s, email = %s WHERE id = %s"
            cursor.execute(update_query, (name, email, record_id))
            conn.commit()

            flash("Record updated successfully!")
            # redirect back to the search page, searching by this email
            return redirect(url_for("showdb", email=email))

        else:
            # GET: load current data to show in form
            select_query = "SELECT id, name, email FROM mydb_t WHERE id = %s"
            cursor.execute(select_query, (record_id,))
            record = cursor.fetchone()

            if not record:
                flash("Record not found.")
                return redirect(url_for("showdb"))

            return render_template("edit.html", record=record)

    except Error as e:
        print("Error while reading/updating MySQL:", e)
        flash(f"Error: {e}")
        return redirect(url_for("showdb"))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()




@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    # this keeps the current search filter after delete
    search_email = request.form.get("search_email", "")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM mydb_t WHERE id = %s"
        cursor.execute(delete_query, (record_id,))
        conn.commit()

        if cursor.rowcount > 0:
            flash("Record deleted successfully.")
        else:
            flash("Record not found or already deleted.")

    except Error as e:
        print("Error while deleting from MySQL:", e)
        flash(f"Error deleting record: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    # redirect back to showdb, preserving the email filter if present
    if search_email:
        return redirect(url_for("showdb", email=search_email))
    else:
        return redirect(url_for("showdb"))
    


if __name__ == "__main__":
    app.run(debug=True)

'''


'''
from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # change in real app

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "KDdas@321",   # change in real app
    "database": "mydb",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ------------------ HOME PAGE ------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ------------------ INSERT NAME + EMAIL + FILES (ONE BUTTON) ------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    files = request.files.getlist("files[]")  # all file inputs

    print("Received from form:", name, email, "Files:", [f.filename for f in files])

    if not name or not email:
        flash("Both name and email are required.")
        return redirect(url_for("index"))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Table mydb_t:
        # CREATE TABLE mydb_t (
        #   id INT AUTO_INCREMENT PRIMARY KEY,
        #   name VARCHAR(255),
        #   email VARCHAR(255)
        # );
        insert_person = "INSERT INTO mydb_t (name, email) VALUES (%s, %s)"
        cursor.execute(insert_person, (name, email))

        # Table uploaded_files:
        # CREATE TABLE uploaded_files (
        #   id INT AUTO_INCREMENT PRIMARY KEY,
        #   filename VARCHAR(255),
        #   file_data LONGBLOB,
        #   uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        # );

        insert_file = "INSERT INTO uploaded_files (filename, file_data) VALUES (%s, %s)"

        for f in files:
            if f and f.filename:
                file_bytes = f.read()
                cursor.execute(insert_file, (f.filename, file_bytes))

        conn.commit()
        flash("Data and file(s) saved successfully!")

    except Error as e:
        print("Error while inserting into MySQL:", e)
        if conn:
            conn.rollback()
        flash(f"Error saving data: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for("index"))


# ------------------ SHOW / SEARCH NAME + EMAIL ------------------
@app.route("/showdb", methods=["GET"])
def showdb():
    email = request.args.get("email", "").strip()
    results = []

    if email:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT id, name, email FROM mydb_t WHERE email LIKE %s"
            cursor.execute(query, (f"%{email}%",))
            results = cursor.fetchall()
        except Error as e:
            print("Error while reading from MySQL:", e)
            flash(f"Error reading data: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

    return render_template("showdb.html", results=results, search_email=email)


# ------------------ EDIT RECORD ------------------
@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit(record_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")

            if not name or not email:
                flash("Name and email are required.")
                return redirect(url_for("edit", record_id=record_id))

            update_query = "UPDATE mydb_t SET name = %s, email = %s WHERE id = %s"
            cursor.execute(update_query, (name, email, record_id))
            conn.commit()
            flash("Record updated successfully!")
            return redirect(url_for("showdb", email=email))

        else:
            select_query = "SELECT id, name, email FROM mydb_t WHERE id = %s"
            cursor.execute(select_query, (record_id,))
            record = cursor.fetchone()
            if not record:
                flash("Record not found.")
                return redirect(url_for("showdb"))
            return render_template("edit.html", record=record)

    except Error as e:
        print("Error while reading/updating MySQL:", e)
        flash(f"Error: {e}")
        return redirect(url_for("showdb"))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ------------------ DELETE RECORD ------------------
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    search_email = request.form.get("search_email", "")
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        delete_query = "DELETE FROM mydb_t WHERE id = %s"
        cursor.execute(delete_query, (record_id,))
        conn.commit()
        if cursor.rowcount > 0:
            flash("Record deleted successfully.")
        else:
            flash("Record not found or already deleted.")
    except Error as e:
        print("Error while deleting from MySQL:", e)
        flash(f"Error deleting record: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    if search_email:
        return redirect(url_for("showdb", email=search_email))
    else:
        return redirect(url_for("showdb"))


if __name__ == "__main__":
    app.run(debug=True)

    '''


from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    send_file,
)
import mysql.connector
from mysql.connector import Error
import io

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # change in real app

# ------------- DATABASE CONFIG -------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "KDdas@321",  # change in real app
    "database": "mydb",       # your database name
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ------------------ HOME PAGE ------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ------------------ INSERT NAME + EMAIL + FILES ------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    files = request.files.getlist("files[]")

    if not name or not email:
        flash("Both name and email are required.")
        return redirect(url_for("index"))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_person = "INSERT INTO mydb_t (name, email) VALUES (%s, %s)"
        cursor.execute(insert_person, (name, email))
        person_id = cursor.lastrowid

        insert_file = """
            INSERT INTO uploaded_files (person_id, filename, file_data)
            VALUES (%s, %s, %s)
        """
        for f in files:
            if f and f.filename:
                file_bytes = f.read()
                cursor.execute(insert_file, (person_id, f.filename, file_bytes))

        conn.commit()
        flash("Data and file(s) saved successfully!")
    except Error as e:
        print("Error while inserting into MySQL:", e)
        if conn:
            conn.rollback()
        flash(f"Error saving data: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for("index"))


# ------------------ SHOW / SEARCH NAME + EMAIL + FILES ------------------
@app.route("/showdb", methods=["GET"])
def showdb():
    search_email = request.args.get("email", "").strip()
    results = []            # list of (id, name, email)
    files_by_person = {}    # {person_id: [(file_id, filename), ...]}

    if search_email:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query_people = """
                SELECT id, name, email
                FROM mydb_t
                WHERE email LIKE %s
                ORDER BY id
            """
            cursor.execute(query_people, (f"%{search_email}%",))
            results = cursor.fetchall()

            if results:
                person_ids = [row[0] for row in results]
                placeholders = ",".join(["%s"] * len(person_ids))
                query_files = f"""
                    SELECT id, person_id, filename
                    FROM uploaded_files
                    WHERE person_id IN ({placeholders})
                    ORDER BY id
                """
                cursor.execute(query_files, person_ids)
                file_rows = cursor.fetchall()

                for file_id, person_id, filename in file_rows:
                    files_by_person.setdefault(person_id, []).append((file_id, filename))

        except Error as e:
            print("Error while reading from MySQL:", e)
            flash(f"Error reading data: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

    return render_template(
        "showdb.html",
        results=results,
        search_email=search_email,
        files_by_person=files_by_person,
    )


# ------------------ DOWNLOAD FILE ------------------
@app.route("/file/<int:file_id>")
def download_file(file_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename, file_data FROM uploaded_files WHERE id = %s",
            (file_id,),
        )
        row = cursor.fetchone()
        if not row:
            flash("File not found.")
            return redirect(url_for("showdb"))

        filename, file_data = row

        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=filename,
        )
    except Error as e:
        print("Error while reading file from MySQL:", e)
        flash(f"Error reading file: {e}")
        return redirect(url_for("showdb"))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ------------------ EDIT RECORD + FILES ------------------
@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit(record_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            files = request.files.getlist("files[]")

            if not name or not email:
                flash("Name and email are required.")
                return redirect(url_for("edit", record_id=record_id))

            update_query = "UPDATE mydb_t SET name = %s, email = %s WHERE id = %s"
            cursor.execute(update_query, (name, email, record_id))

            new_files = [f for f in files if f and f.filename]
            if new_files:
                delete_files_query = "DELETE FROM uploaded_files WHERE person_id = %s"
                cursor.execute(delete_files_query, (record_id,))

                insert_file = """
                    INSERT INTO uploaded_files (person_id, filename, file_data)
                    VALUES (%s, %s, %s)
                """
                for f in new_files:
                    file_bytes = f.read()
                    cursor.execute(insert_file, (record_id, f.filename, file_bytes))

            conn.commit()
            flash("Record (and files, if changed) updated successfully!")
            return redirect(url_for("showdb", email=email))

        else:
            # GET: load record and its files
            select_person = "SELECT id, name, email FROM mydb_t WHERE id = %s"
            cursor.execute(select_person, (record_id,))
            record = cursor.fetchone()  # (id, name, email)

            if not record:
                flash("Record not found.")
                return redirect(url_for("showdb"))

            select_files = """
                SELECT id, filename
                FROM uploaded_files
                WHERE person_id = %s
                ORDER BY id
            """
            cursor.execute(select_files, (record_id,))
            files = cursor.fetchall()  # list of (id, filename)

            # CRITICAL: we pass record (not person)
            return render_template("edit.html", record=record, files=files)

    except Error as e:
        print("Error while reading/updating MySQL:", e)
        flash(f"Error: {e}")
        return redirect(url_for("showdb"))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


# ------------------ DELETE RECORD ------------------
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    search_email = request.form.get("search_email", "")
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM mydb_t WHERE id = %s"
        cursor.execute(delete_query, (record_id,))
        conn.commit()

        if cursor.rowcount > 0:
            flash("Record deleted successfully.")
        else:
            flash("Record not found or already deleted.")
    except Error as e:
        print("Error while deleting from MySQL:", e)
        flash(f"Error deleting record: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

    if search_email:
        return redirect(url_for("showdb", email=search_email))
    else:
        return redirect(url_for("showdb"))


if __name__ == "__main__":
    app.run(debug=True)