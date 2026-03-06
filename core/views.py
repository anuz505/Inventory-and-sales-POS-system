from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
            cache.set("healthcheck", "ok", 1)
        except Exception:
            return Response({"status": "error"}, status=500)

        return Response({"status": "ok"})
