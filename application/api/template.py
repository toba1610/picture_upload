from flask import Blueprint, request, current_app
from typing import TYPE_CHECKING, cast

from application.api.api_response import ApiResponse

connection = Blueprint('XXXXXXXXXXX', __name__)
connection.url_prefix = '/XXXXXXXXXXX'

@connection.route('/')
def index():
    
    return ApiResponse.success(message="automatic")
