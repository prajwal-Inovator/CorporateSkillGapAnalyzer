# app.py - Main entry point for Corporate Skill Gap Analyzer

import os
from flask import Flask, render_template, flash, redirect, url_for, session
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from db import db

# Load environment variables from .env file
load_dotenv()

# Initialize extensions (will be configured after app creation)
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Application factory pattern - creates and configures the Flask app"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        sqlite_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corporate_skill_gap.db')
        database_url = f"sqlite:///{sqlite_db_path}"
        app.logger.warning('DATABASE_URL is not set; using fallback SQLite database at %s', sqlite_db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload folder for CSV files
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # redirect to login page if not authenticated
    login_manager.login_message_category = 'warning'

    # Allow trailing slash variants for routes to reduce accidental 404s
    app.url_map.strict_slashes = False

    # Auto-create tables when using the local SQLite fallback database
    if database_url.startswith('sqlite:'):
        with app.app_context():
            db.create_all()
    
    # Import models (must be after db initialization to avoid circular imports)
    from models.user import User
    from models.employee import Employee
    from models.department import Department
    from models.skill import Skill
    from models.job_role import JobRole
    from models.employee_skill import EmployeeSkill
    from models.role_required_skill import RoleRequiredSkill
    from models.training_resource import TrainingResource
    from models.gap_analysis import GapAnalysis
    from utils.csv_handler import process_all_dataset_files
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints (routes)
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.employee_routes import employee_bp
    from routes.analytics_routes import analytics_bp
    from routes.recommendation_routes import recommendation_bp
    from routes.upload_routes import upload_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(recommendation_bp, url_prefix='/recommendation')
    app.register_blueprint(upload_bp, url_prefix='/upload')

    with app.app_context():
        try:
            db.create_all()

            if not User.query.filter_by(role='admin').first():
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
                admin = User(email=admin_email, role='admin')
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                app.logger.warning('Created default admin user: %s', admin_email)

            if Department.query.count() == 0:
                departments = [
                    Department(name='Engineering', description='Engineering and development'),
                    Department(name='Human Resources', description='HR and people operations'),
                    Department(name='Sales', description='Sales and customer success'),
                ]
                db.session.add_all(departments)
                db.session.commit()
                app.logger.warning('Created default departments')

            if JobRole.query.count() == 0:
                engineering = Department.query.filter_by(name='Engineering').first()
                hr = Department.query.filter_by(name='Human Resources').first()
                sales = Department.query.filter_by(name='Sales').first()
                job_roles = [
                    JobRole(title='Software Engineer', department_id=engineering.id if engineering else None, description='Software development role'),
                    JobRole(title='HR Manager', department_id=hr.id if hr else None, description='HR management role'),
                    JobRole(title='Sales Representative', department_id=sales.id if sales else None, description='Sales representative role'),
                ]
                db.session.add_all(job_roles)
                db.session.commit()
                app.logger.warning('Created default job roles')

            if Employee.query.count() == 0 or Skill.query.count() == 0 or JobRole.query.count() == 0 or EmployeeSkill.query.count() == 0 or RoleRequiredSkill.query.count() == 0:
                dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets')
                import_result = process_all_dataset_files(dataset_dir)
                if isinstance(import_result, dict) and import_result.get('error'):
                    app.logger.warning('Dataset auto-import failed: %s', import_result['error'])
                else:
                    app.logger.warning('Imported repository datasets on startup: %s', import_result)
        except Exception as e:
            app.logger.warning('Unable to create database tables or seed startup data: %s', e)
    
    @app.route('/login')
    def login_redirect():
        return redirect(url_for('auth.login'))

    @app.route('/register')
    def register_redirect():
        return redirect(url_for('auth.register'))

    @app.route('/logout')
    def logout_redirect():
        return redirect(url_for('auth.logout'))

    # Homepage route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        flash('An internal error occurred. Please try again later.', 'danger')
        return render_template('500.html'), 500
    
    # Context processor to inject current year and user into all templates
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return dict(current_year=datetime.now().year, current_user=current_user)
    
    return app

# Create the app instance for production (used by WSGI servers)
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)