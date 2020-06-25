from ..util.dto import ImageDTO
from ..service.image_service import get_image
from flask_restplus import Resource

api = ImageDTO.api


@api.route('/get_image/<image_class>/<image_id>.<image_type>')
class ImageServer(Resource):
    @api.doc('Retrieve an image based on passed in image filename')
    @api.response(200, 'Image retrieved')
    def get(self, image_class, image_id, image_type):
        """Get image from passed in image filename"""
        return get_image(image_class, image_id, image_type)
