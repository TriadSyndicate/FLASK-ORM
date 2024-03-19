from flask import jsonify
from functions import convert_object_ids_to_string
from models.body import Body


class BodyController:
    def __init__(self):
        self.body = Body()
    
    def get_all_bodies(self):
        try:
            bodies = self.body.get_all_bodies()
            serialized_bodies = [convert_object_ids_to_string(body)
                                 for body in bodies
                                ]
            return jsonify({"bodies": serialized_bodies}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500