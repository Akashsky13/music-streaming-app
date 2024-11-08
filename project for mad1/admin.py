from flask import Blueprint, render_template, request, redirect, url_for, flash

admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates')

# Predefined admin credentials (for a real application, these should be stored securely, e.g., in environment variables)
ADMIN_EMAIL = "admin@iitm.ac.in"
ADMIN_PASSWORD = "pass"

@admin.route("/admin", methods=['GET', 'POST'])
def admin_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check against predefined admin credentials
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return redirect(url_for('adminpage.adminpage'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('admin.html', error='Invalid credentials')

    return render_template('admin.html')
