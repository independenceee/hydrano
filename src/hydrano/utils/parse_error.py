import json

from requests.exceptions import RequestException


def parse_error(error: Exception) -> str:
    """
    Description: Parse an HTTP error from a requests exception into a JSON string.
    Args: error: The exception to parse.
    Returns: A JSON string representing the error details.
    """
    if not isinstance(error, RequestException):
        return json.dumps(str(error))
    if hasattr(error, 'response') and error.response is not None:
        return json.dumps({
            'data': error.response.text,  
            'headers': dict(error.response.headers),  
            'status': error.response.status_code
        })
    if hasattr(error, 'request') and error.request is not None: 
        return json.dumps({
            'method': error.request.method,
            'url': error.request.url,
            'headers': dict(error.request.headers)
        })
    return json.dumps({
        'code': getattr(error, 'errno', None),  
        'message': str(error)
    })