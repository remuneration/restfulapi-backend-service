from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import current_app
from rq.job import Job
from rq.exceptions import NoSuchJobError

from database import db

from tasks import complex_calculations


from models import StoreModel
from schemas import StoreSchema, StoreUpdateSchema, Calculation

blp = Blueprint("stores",__name__, description="Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):

    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required(fresh=True)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"message":"Store deleted"}

    @jwt_required(fresh=True)
    @blp.arguments(StoreUpdateSchema)
    @blp.response(201, StoreSchema)
    def put(self, store_data, store_id):
        store = StoreModel.query.get(store_id)
        if store:
            store.store_name = store_data["store_name"]
        else:
            store = StoreModel(store_id= store_id, **store_data)

        db.session.add(store)
        db.session.commit()

        return store

@blp.route("/store")
class StoreList(MethodView):

    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(500, message="A store with a current name already exist")
        except SQLAlchemyError:
            abort(500, message="An error occurred during creating the store")
        return store, 201

@blp.route("/calculation")
class Calculation(MethodView):
    @jwt_required()
    @blp.arguments(Calculation)
    def post(self, cal_data):
        job = current_app.heavy_queue.enqueue(complex_calculations,**cal_data)
        return {"job_id":job.id}

@blp.route("/calculation/<job_id>")
class CheckingCalculation(MethodView):
    @jwt_required()
    def get(self, job_id):

        try:
            job = Job.fetch(job_id, connection=current_app.redis_connection)
        except NoSuchJobError:
            return {"error":"Job not found"}, 404

        return {
            "status": job.get_status(),
            "result": job.return_value()
        }


