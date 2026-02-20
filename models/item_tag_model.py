from database import db

class ItemTag(db.Model):
    __tablename__ = "item_tag"

    secondary_id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.tag_id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"))

    tag = db.relationship("TagModel", back_populates="item_tag")
    item = db.relationship("ItemModel", back_populates="item_tag")



