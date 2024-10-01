# Import sqlalchemy and marshmallow
from init import db, ma

# Import func method for database methods (timestamp)
from sqlalchemy import func

# Table for Like Model
class Like(db.Model):
    # Name of table
    __tablename__ = "likes"

    # Attributes of table
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Keys
    # Note: created attribute with timestamp has been added to assist "View Liked Routines" route to allow user to retrieve the like routines from most recently liked to oldest.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), nullable=False)
    created = db.Column(db.DateTime, server_default=func.current_timestamp(), nullable=False)

    # Define relationships with routine and user table 
    routine = db.relationship("Routine", back_populates="likes")
    user = db.relationship("User", back_populates="likes")

class LikeSchema(ma.Schema):
    # Confirms which fields will be visible
    class Meta:
        fields = ("id", "user", "routine")

# to hand a single like object
like_schema = LikeSchema()
# to hand a list of like objects
likes_schema = LikeSchema(many=True)