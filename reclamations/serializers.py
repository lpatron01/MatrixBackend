from rest_framework import serializers
from .models import Reclamation, ReclamationHistory
from users.serializers import UserSerializer

class ReclamationHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ReclamationHistory
        fields = '__all__'

class ReclamationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)
    student = UserSerializer(read_only=True)
    history = ReclamationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Reclamation
        fields = [
            'id', 'student', 'category', 'status', 'description', 
            'file', 'is_anonymous', 'created_at', 'updated_at', 'history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'history']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # If anonymous, hide student info
        if instance.is_anonymous:
            data['student'] = None 
        return data

class ReclamationCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)

    class Meta:
        model = Reclamation
        fields = ['id', 'category', 'description', 'file', 'is_anonymous']

class ReclamationAdminUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False, allow_blank=True)
    response = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Reclamation
        fields = ['status', 'category', 'comment', 'response']

    def update(self, instance, validated_data):
        # Accept both 'comment' and 'response' fields
        comment = validated_data.pop('comment', None) or validated_data.pop('response', None)
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        instance = super().update(instance, validated_data)
        
        # Create history if there is a change or comment
        if old_status != new_status or comment:
            ReclamationHistory.objects.create(
                reclamation=instance,
                changed_by=self.context['request'].user,
                old_status=old_status,
                new_status=new_status,
                comment=comment
            )
        return instance
