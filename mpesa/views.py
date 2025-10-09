from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import MpesaRequest, MpesaResponse
from .serializers import MpesaRequestSerializer, MpesaResponseSerializer, MpesaDetailSerializer
from django.conf import settings
import requests
from rest_framework.decorators import api_view
from datetime import datetime
import base64

@api_view(['POST'])
def stk_push(request):
    serializer = MpesaRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        mpesa_request = serializer.save()
        print("MpesaRequest saved:", mpesa_request)
        
        try:
            response_data = initiate_stk_push(mpesa_request)
            print("STK Push response data:", response_data)
            
        except Exception as e:
            print("Error initiating STK Push:", str(e))
            return Response({"error": "Failed to initiate STK Push"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        mpesa_response = MpesaResponse(
            request=mpesa_request,
            response_code=response_data.get('ResponseCode', ''),
            response_description=response_data.get('ResponseDescription', ''),
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            customer_message=response_data.get('CustomerMessage', '')
        )
        
        response_serializer = MpesaResponseSerializer(mpesa_response)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print("Error saving MpesaRequest:", str(e))
        return Response({"error": "Failed to process request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

def initiate_stk_push(mpesa_request):
    try:
        access_token = get_access_token()
    
    except Exception as e:
        raise Exception("Failed to get access token: " + str(e))
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": generate_password(timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(mpesa_request.amount),
        "PartyA": mpesa_request.phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": mpesa_request.phone_number,
        "CallBackURL": "https://yourdomain.com/api/mpesa/callback/",
        "AccountReference": mpesa_request.account_reference,
        "TransactionDesc": mpesa_request.transaction_desc
    }   
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"STK Push request failed: {getattr(e.response, 'text',  str(e))}")

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        access_token = response.json().get('access_token')
        if not access_token:
            raise Exception("No access token in response")
        return access_token
    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", str(e))
        raise Exception(f"Failed to get access token: {getattr(e.response, 'text', str(e))}")
    
def generate_password(timestamp):
    try:
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        data_to_encode = shortcode + passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8')
    except Exception as e:
        print("Error generating password:", str(e))
        raise Exception("Failed to generate password")