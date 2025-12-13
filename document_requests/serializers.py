from rest_framework import serializers
from .models import DocumentRequest, DocumentRequestHistory, PresenceRequestApproval
from users.serializers import UserSerializer
from users.models import User

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
            'id', 'student', 'document_type', 'status', 'additional_info', 'academic_year', 
            'created_at', 'updated_at', 'history', 'language', 'reception_type'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'history']

class DocumentRequestCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id', read_only=True)

    class Meta:
        model = DocumentRequest
        fields = ['id', 'document_type', 'language', 'reception_type', 'academic_year']

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

class DocumentRequestedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = ['pdf_requested_file']
        read_only_fields = ['public_id', 'student', 'document_type', 'status', 'language', 'reception_type', 'additional_info', 'pdf_file', 'created_at', 'updated_at']


class PresenceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating presence certificate requests with teacher selection"""
    teachers = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2,
        max_length=2,
        write_only=True,
        help_text="List of exactly 2 teacher UUIDs to approve this request"
    )
    id = serializers.UUIDField(source='public_id', read_only=True)

    class Meta:
        model = DocumentRequest
        fields = ['id', 'language', 'reception_type', 'academic_year', 'teachers']

    def validate_teachers(self, value):
        """Validate that exactly 2 teachers are selected and they exist"""
        if len(value) != 2:
            raise serializers.ValidationError("Exactly 2 teachers must be selected.")

        teachers = User.objects.filter(
            public_id__in=value,
            role=User.Role.TEACHER,
            is_active=True
        )

        if teachers.count() != 2:
            raise serializers.ValidationError("Selected users must be active teachers.")

        return teachers

    def create(self, validated_data):
        teachers = validated_data.pop('teachers')
        validated_data['document_type'] = DocumentRequest.DocumentType.CERTIFICATE_PRESENCE
        validated_data['status'] = DocumentRequest.Status.NEW

        document_request = super().create(validated_data)

        # Create approval records for each teacher
        for teacher in teachers:
            PresenceRequestApproval.objects.create(
                document_request=document_request,
                teacher=teacher
            )

        return document_request


class PresenceRequestApprovalSerializer(serializers.ModelSerializer):
    """Serializer for presence request approvals"""
    teacher = UserSerializer(read_only=True)
    document_request = DocumentRequestSerializer(read_only=True)

    class Meta:
        model = PresenceRequestApproval
        fields = ['id', 'document_request', 'teacher', 'status', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'document_request', 'teacher', 'created_at', 'updated_at']


class PresenceRequestApprovalUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating approval status"""
    class Meta:
        model = PresenceRequestApproval
        fields = ['status', 'comment']

    def validate_status(self, value):
        """Ensure status can only be set to APPROVED or REJECTED"""
        if value not in [PresenceRequestApproval.ApprovalStatus.APPROVED, PresenceRequestApproval.ApprovalStatus.REJECTED]:
            raise serializers.ValidationError("Status must be either APPROVED or REJECTED.")
        return value

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status')

        # Update the approval
        instance = super().update(instance, validated_data)

        # Check if we need to update the document request status
        document_request = instance.document_request

        if new_status == PresenceRequestApproval.ApprovalStatus.REJECTED and old_status != new_status:
            # If rejected, automatically reject the entire request
            document_request.status = DocumentRequest.Status.REJECTED
            document_request.save()

            # Create history record
            DocumentRequestHistory.objects.create(
                document_request=document_request,
                changed_by=self.context['request'].user,
                old_status=document_request.status,
                new_status=DocumentRequest.Status.REJECTED,
                comment=f"Rejeté par {instance.teacher.get_full_name() or instance.teacher.email}: {validated_data.get('comment', '')}"
            )

        elif new_status == PresenceRequestApproval.ApprovalStatus.APPROVED and old_status != new_status:
            # If approved, check if all teachers have approved
            if document_request.is_ready_for_processing():
                document_request.status = DocumentRequest.Status.IN_PROGRESS
                document_request.save()

                # Create history record
                DocumentRequestHistory.objects.create(
                    document_request=document_request,
                    changed_by=self.context['request'].user,
                    old_status=DocumentRequest.Status.NEW,
                    new_status=DocumentRequest.Status.IN_PROGRESS,
                    comment="Approuvé par tous les enseignants - prêt pour traitement administratif"
                )

        return instance