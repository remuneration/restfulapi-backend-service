from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from models import TagModel, StoreModel, ItemModel, ItemTag
from schemas import TagSchema, TagUpdateSchema, TagAndItemSchema

from database import db


blp = Blueprint("tags", __name__, description="Operations with tags")

@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):

    @jwt_required()
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required(fresh=True)
    @blp.response(202, description="Deleting a specific Tag if not items assigned to it")
    @blp.alt_response(404, description="Tag not found")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag was deleted"}
        abort(400, message="Could not delete tag. Tag is connected to items. Disconnect the tag first")

@blp.route("/tag")
class TagList(MethodView):

    @jwt_required()
    @blp.response(200, TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()
        return tags

@blp.route("/store/<int:store_id>/tag")
class TagInStoreList(MethodView):

    @jwt_required()
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        specific_store = StoreModel.query.get_or_404(store_id)

        return specific_store.tag

    @jwt_required(fresh=True)
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.tag_name == tag_data["tag_name"]).first():
            abort(400, message="Tag is already exists with the same store")

        tag = TagModel(**tag_data, store_id= store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            return abort(500, message="An error occurred while inserting a tag")

        return tag

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class TagsToItem(MethodView):

    @jwt_required(fresh=True)
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(400,
                  message="Item and Tag have different store ids, make sure you are connecting with same store_id")

        check_link = ItemTag.query.filter_by(tag_id=tag_id,item_id=item_id).first()
        if check_link:
            abort(400, message="Link is already exist")

        create_link = ItemTag(tag_id=tag_id,item_id=item_id)

        try:
            db.session.add(create_link)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while connecting tag to item")

        return tag

    @jwt_required(fresh=True)
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        delete_link = ItemTag.query.filter_by(tag_id=tag_id,item_id=item_id).first()

        try:
            db.session.delete(delete_link)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while removing tag from item")

        return {"message":"Item removed from tag"}








