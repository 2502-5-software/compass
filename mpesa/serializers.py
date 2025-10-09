from .models import MpesaRequest, MpesaResponse
from rest_framework import serializers

class MpesaRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaRequest
        fields = ['id', 'amount', 'phone_number', 'account_reference', 'transaction_desc', 'timestamp']
        read_only_fields = ['id', 'timestamp']  
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['amount'] = str(instance.amount) 
        return rep
    
class MpesaResponseSerializer(serializers.ModelSerializer):
    request = MpesaRequestSerializer(read_only=True)
    
    class Meta:
        model = MpesaResponse
        fields = ['id', 'request', 'response_code', 'response_description', 'merchant_request_id', 'checkout_request_id', 'customer_message', 'timestamp']
        read_only_fields = ['id', 'timestamp']  
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
    
class MpesaDetailSerializer(serializers.ModelSerializer):
    responses = MpesaResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = MpesaRequest
        fields = ['id', 'amount', 'phone_number', 'account_reference', 'transaction_desc', 'timestamp', 'responses']
        read_only_fields = ['id', 'timestamp', 'responses']  
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['amount'] = str(instance.amount) 
        return rep