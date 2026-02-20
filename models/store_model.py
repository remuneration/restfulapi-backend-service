from database import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    store_id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(80), unique=True, nullable=False)


    item = db.relationship("ItemModel", back_populates="store", cascade="all, delete")
    tag = db.relationship("TagModel", back_populates="store")
