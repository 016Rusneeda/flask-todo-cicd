import os
from flask import Flask, jsonify
from app.models import db
from app.routes import api
from app.config import config

# ✅ ป้องกันไม่ให้ crash ถ้ายังไม่มี flask_cors
try:
    from flask_cors import CORS
except ImportError:
    CORS = None


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ✅ เปิดใช้งาน CORS ถ้ามีโมดูล flask_cors
    if CORS:
        CORS(app, resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://localhost:5000",
                    "https://*.github.io",
                    "https://016Rusneeda.github.io"
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type"],
                "supports_credentials": False
            }
        })
    else:
        print("⚠️ Warning: Flask-Cors not installed. CORS disabled.")

    # ✅ Database setup
    db.init_app(app)
    app.register_blueprint(api, url_prefix='/api')

    # ✅ Routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Flask Todo API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'todos': '/api/todos'
            }
        })

    # ✅ Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    with app.app_context():
        db.create_all()

    return app
