from rest_framework import serializers 

class RawLLMSerializer(serializers.Serializer):
    proposal_text = serializers.CharField(required=False, allow_blank=True)
    changeset = serializers.DictField(required=True)
    metadata = serializers.DictField(required=False)

# serializer cho từng phần tử trong "changes"
class ChangeSerializer(serializers.Serializer):
    action = serializers.CharField()
    service = serializers.CharField()
    config = serializers.DictField(required=False)

class ChangeSetSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    intent = serializers.CharField(required=True)
    timestamp = serializers.CharField(required=True)
    request_context = serializers.DictField(required=True)
    changes = ChangeSerializer(many=True, required=True)  # 👈 sửa lại đây
    impacted_services = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    metadata = serializers.DictField(required=True)
