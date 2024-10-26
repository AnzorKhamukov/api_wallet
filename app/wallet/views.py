from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet, Operation
from .serializers import WalletSerializer, OperationSerializer
from django.db import transaction


class WalletView(APIView):

    def get(self, request, wallet_uuid):
        try:
            wallet = Wallet.objects.get(uuid=wallet_uuid)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def post(self, request, wallet_uuid):
        serializer = OperationSerializer(data=request.data)
        if serializer.is_valid():
            operation_type = serializer.validated_data['operation_type']
            amount = serializer.validated_data['amount']
            try:
                wallet = Wallet.objects.select_for_update().get(uuid=wallet_uuid)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
            if operation_type == 'WITHDRAW' and wallet.balance < amount:
                return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
            if operation_type == 'DEPOSIT':
                wallet.balance += amount
            elif operation_type == 'WITHDRAW':
                wallet.balance -= amount
            wallet.save()
            operation = Operation.objects.create(wallet=wallet,operation_type=operation_type, amount=amount)
            return Response({'message': 'Operation successful', 'balance': wallet.balance}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
