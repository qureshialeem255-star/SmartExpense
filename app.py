import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, login_manager, Category

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance directory exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes import (
        auth_bp,
        dashboard_bp,
        transactions_bp,
        budgets_bp,
        reports_bp,
        insights_bp,
        savings_bp,
        categories_bp
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(categories_bp)

    # Global Jinja helpers
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            val = float(value)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.context_processor
    def inject_global_data():
        return {
            'app_name': 'Smart Expense AI',
            'current_year': 2026
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Auto-create tables & seed default categories
    with app.app_context():
        db.create_all()
        Category.seed_default_categories(db.session)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

