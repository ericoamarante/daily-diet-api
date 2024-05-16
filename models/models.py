from database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default="User")
    recipes = db.relationship("Recipe", backref="user", lazy=True)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default="User")
    in_diet = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def toDict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            datetime=self.datetime,
            in_diet=self.in_diet,
            user_id=self.user_id,
        )
