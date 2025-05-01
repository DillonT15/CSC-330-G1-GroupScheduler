from app import create_app, db
from app.models import User, StudyGroup, Thread, Post, Message, ViolationType
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@southernct.edu',
            password=generate_password_hash('adminpassword'),
            name='Admin User',
            major='Computer Science',
            is_admin=True,
            is_verified=True
        )
        
        # Create test user
        student = User(
            username='student',
            email='student@southernct.edu',
            password=generate_password_hash('password'),
            name='Test Student',
            major='Computer Science',
            is_verified=True
        )
        
        # Add to session and commit
        db.session.add_all([admin, student])
        db.session.commit()
        
        # Create a study group
        group = StudyGroup(
            title='CSC 330 Study Group',
            subject='Computer Science',
            course='CSC 330',
            description='A study group for CSC 330 students',
            tags='programming, flask, python',
            time='Mondays 5-7 PM',
            op_id=student.id
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Add the user to their study group
        group.add_member(student)
        db.session.commit()
        
        # Create violation types
        violation_types = [
            ViolationType(violation_code=1, violation_description='Inappropriate Content'),
            ViolationType(violation_code=2, violation_description='Harassment'),
            ViolationType(violation_code=3, violation_description='Spam'),
            ViolationType(violation_code=4, violation_description='Off-topic Content')
        ]
        
        db.session.add_all(violation_types)
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()