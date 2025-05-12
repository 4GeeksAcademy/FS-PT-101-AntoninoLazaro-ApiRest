from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # ahora en plural para coherencia
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    profile: Mapped['Profile'] = relationship(back_populates='user', uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "age": self.age,
            "profile": self.profile.serialize() if self.profile else None
            # do not serialize the password, it's a security breach
        }

class Profile(db.Model):
    __tablename__ = 'profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    bio: Mapped[str] = mapped_column(String(120))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='profile')

    def serialize(self):
        return {
            'user_id':self.user_id,
            "bio": self.bio,
            "title" : self.title
        }
