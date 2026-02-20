from database import db

class TagModel(db.Model):
    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)


    store = db.relationship("StoreModel", back_populates="tag")
    item_tag = db.relationship("ItemTag", back_populates="tag")

    @property
    def items(self):
        return [item.item for item in self.item_tag]