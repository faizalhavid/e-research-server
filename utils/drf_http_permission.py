from rest_framework import viewsets, status
from rest_framework.response import Response

from utils.exceptions import failure_response

class ReadOnlyModelViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        return failure_response("Method not allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return failure_response("Method not allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return failure_response("Method not allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return failure_response("Method not allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)