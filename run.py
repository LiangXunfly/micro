from app import app, db
from flask_script import Manager, Shell
from app.models import User, Post, Follow, Comment
from flask_migrate import Migrate, MigrateCommand


manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    users = User.query.all()
    return dict(db=db, app=app, User=User, Post=Post, Follow=Follow, Comment=Comment,
                lx=users[0], fzd=users[1], zh=users[2])
# manager.add_command('shell', make_context=make_shell_context())
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()