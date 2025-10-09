from django.db import models
from django.utils import timezone

class MpesaRequest(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15, help_text="Format: CountryCodeNumber, e.g., 2547XXXXXXXX")
    account_reference = models.CharField(max_length=100)
    transaction_desc = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    def is_recent(self):
        
        return self.timestamp >= timezone.now() - timezone.timedelta(days=1)
    is_recent.boolean = True
    is_recent.short_description = 'Requested recently?'
    
    def get_latest_response(self):
        return self.responses.order_by('-timestamp').first()
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Mpesa Request'
        verbose_name_plural = 'Mpesa Requests'

class MpesaResponse(models.Model):
    request = models.ForeignKey(MpesaRequest, related_name='responses', on_delete=models.CASCADE)
    response_code = models.CharField(max_length=10)
    response_description = models.TextField()
    merchant_request_id = models.CharField(max_length=50)
    checkout_request_id = models.CharField(max_length=50)
    customer_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.request.phone_number} - code {self.response_code or 'pending'}"
    
    def is_successful(self):
        return self.response_code == '0'  # Assuming '0' indicates success
    is_successful.boolean = True
    is_successful.short_description = 'Successful?' 
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Mpesa Response'
        verbose_name_plural = 'Mpesa Responses'