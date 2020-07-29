from .. import db


class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(
        db.String(200),
        default="",
        nullable=False
    )

    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def get_json(self):
        return {
            'name': self.name,
            'date': self.created_on.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
