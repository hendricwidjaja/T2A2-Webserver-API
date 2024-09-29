from init import db, ma
from sqlalchemy import func


class Like(db.Model):
    # name of table
    __tablename__ = "likes"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), nullable=False)
    created = db.Column(db.DateTime, server_default=func.current_timestamp(), nullable=False)

    routine = db.relationship("Routine", back_populates="likes")
    user = db.relationship("User", back_populates="likes")


class LikeSchema(ma.Schema):
    class Meta:
        fields = ("id", "user", "routine", "created")

# to handle a single user object
like_schema = LikeSchema()
# to hand a list of user objects
likes_schema = LikeSchema(many=True)