from rest_framework import serializers
from .models import DocumentRequest, DocumentRequestHistory
from users.serializers import UserSerializer

class DocumentRequestHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentRequestHistory
        fields = '__all__'

class DocumentRequestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)
    student = UserSerializer(read_only=True)
    history = DocumentRequestHistorySerializer(many=True, read_only=True)

    class Meta:
        model = DocumentRequest
        fields = [
            'id', 'student', 'document_type', 'status', 'additional_info', 
            'created_at', 'updated_at', 'history', 'language', 'reception_type'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'history']

class DocumentRequestCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)

    class Meta:
        model = DocumentRequest
        fields = ['id', 'document_type', 'language', 'reception_type']

class DocumentRequestAdminUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = DocumentRequest
        fields = ['status', 'comment']

    def update(self, instance, validated_data):
        comment = validated_data.pop('comment', None)
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        instance = super().update(instance, validated_data)
        
        if old_status != new_status or comment:
            DocumentRequestHistory.objects.create(
                document_request=instance,
                changed_by=self.context['request'].user,
                old_status=old_status,
                new_status=new_status,
                comment=comment
            )
        return instance
