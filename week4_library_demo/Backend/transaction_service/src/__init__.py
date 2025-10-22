from flask import Flask
from .config import Config
from .database import db
from .controllers.transaction_controller import transaction_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    
    app.register_blueprint(transaction_bp)

    @app.route('/health')
    def health_check():
        return "Transaction Service OK"

    return app
