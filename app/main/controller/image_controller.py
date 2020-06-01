from ..util.dto import ImageDTO
from ..service.image_service import get_image
from flask_restplus import Resource

api = ImageDTO.api

@api.route('/get_image/<image_name>')
class ImageServer(Resource):
    @api.doc('Retrieve an image based on passed in image filename')
    @api.response(200, 'Image retrieved')
    def get(self, image_name):
        """Get image from passed in image filename"""
        return get_image(image_name)