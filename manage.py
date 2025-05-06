import os
from flask_migrate import Migrate, init, migrate, upgrade
from app import create_app, db

app = create_app()
migrate_obj = Migrate(app, db)

def initialize_migrations():
    with app.app_context():
        if not os.path.exists('migrations'):
            init()
        migrate(message='Initial tables')
        upgrade()

if __name__ == '__main__':
    initialize_migrations()
    app.run()