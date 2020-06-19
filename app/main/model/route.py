from .. import db


class Route(db.Model):
    """Route model for representing custom routes"""
    __tablename__ = "route"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Route '{}':'{}'>".format(self.origin, self.target)
