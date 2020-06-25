import os
import json
from ..model.route import Route


def get_routes():
    response_object = {}
    routes_list = Route.query.filter_by(active=True).all()
    if not routes_list:
        path = os.path.abspath(os.path.dirname(__file__))
        json_path = path + '/resources/routes_service/default_routes.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                routes = json.load(f)
                response_object["status"] = "success"
                response_object["message"] = "Successfully retrieved routes."
                response_object["routes"] = routes
        else:
            response_object = {
                "status": "failure",
                "message": "Failed to retrieve application routes."
            }
    else:
        response_object["status"] = "success"
        response_object["message"] = "Successfully retrieved routes."
        response_object["routes"] = {}
        for r in routes_list:
            response_object["routes"][r.origin] = [r.target]
    return response_object
