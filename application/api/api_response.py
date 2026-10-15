from flask import jsonify, Response

class ApiResponse:
    @staticmethod
    def _clean(data: dict) -> dict:

        cleaned_data = {}

        for key, value in data.items():
            if value is not None:
                cleaned_data[key] = value
        return cleaned_data

    @staticmethod
    def success(data=None, message="", code=200, meta=None):
        
        response = {
            "status": True,
            "message": message,
            "data": data,
            "meta": meta
        }

        return jsonify(ApiResponse._clean(response)), code

    @staticmethod
    def error(message="An error occurred", errors=None, code=400):
        
        response = {
            "status": False,
            "message": message,
            "errors": errors
        }

        return jsonify(ApiResponse._clean(response)), code
    
    
    @staticmethod
    def image(
        image_bytes,
        mimetype="image/png",
        filename=None,
        download=False,
        code=200
    ):
        headers = {}

        if filename:
            disposition = "attachment" if download else "inline"
            headers["Content-Disposition"] = (
                f'{disposition}; filename="{filename}"'
            )

        return Response(
            image_bytes,
            status=code,
            mimetype=mimetype,
            headers=headers
        )