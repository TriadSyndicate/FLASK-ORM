# models.body

from mongoengine import *

from functions import convert_object_ids_to_string


class Body(Document):
    name = StringField(required=True)
    competitions = ListField(ReferenceField('Competition', dbref=False), default=[])
    meta = {
    'collection': 'bodies',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.competition import Competition
    
    # get all bodies    
    @classmethod
    def get_all_bodies(cls):
        try:
            bodies = cls.objects()  # Retrieve all documents from the collection
            serialized_bodies = [convert_object_ids_to_string(body.to_mongo()) for body in bodies]
            return serialized_bodies  # Return serialized bodies as a list of dictionaries
        except Exception as e:
            return {"error": f"Failed to retrieve bodies: {str(e)}"}
