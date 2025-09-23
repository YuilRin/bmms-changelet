from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import yaml

# import serializers
from .serializers import RawLLMSerializer, ChangeSetSerializer

# import core logic từ src/bmms_changelet
from bmms_changelet.normalize_input import normalize
from bmms_changelet.validator import validate_changeset, load_catalogue, load_schema
from bmms_changelet.convert_to_helm import convert, load_mapping

# preload schema & catalogue
CATALOGUE = load_catalogue()
SCHEMA = load_schema()
MAPPING = load_mapping()


# ----------------------------
# Normalize endpoint
# ----------------------------
@swagger_auto_schema(
    method="post",
    request_body=RawLLMSerializer,
    responses={200: ChangeSetSerializer},
    operation_description="Nhận output từ LLM, chuẩn hóa thành ChangeSet hợp lệ."
)
@api_view(["POST"])
def normalize_view(request):
    serializer = RawLLMSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    normalized = normalize(serializer.validated_data)
    return Response(normalized)


# ----------------------------
# Validate endpoint
# ----------------------------
@swagger_auto_schema(
    method="post",
    request_body=ChangeSetSerializer,
    responses={200: openapi.Response("Validation result")},
    operation_description="Kiểm tra ChangeSet dựa trên schema, catalogue, và policy."
)
@api_view(["POST"])
def validate_view(request):
    serializer = ChangeSetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = validate_changeset(serializer.validated_data, CATALOGUE, SCHEMA)
    return Response(result)


# ----------------------------
# Convert endpoint
# ----------------------------
@swagger_auto_schema(
    method="post",
    request_body=ChangeSetSerializer,
    responses={200: openapi.Response("Helm values YAML + JSON")},
    operation_description="Chuyển ChangeSet thành Helm values (YAML & JSON)."
)
@api_view(["POST"])
def convert_view(request):
    serializer = ChangeSetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    values = convert(serializer.validated_data, MAPPING)

    return Response({
        "values_yaml": yaml.safe_dump(values, sort_keys=False, allow_unicode=True),
        "values_json": values
    })
