from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    response=exception_handler(exc,context)
    if response is not None:
        detail=response.data.get('detail') if hasattr(response.data,'get') else None
        response.data={'error': {'code': exc.__class__.__name__.upper(), 'message': detail or response.data}}
    return response
