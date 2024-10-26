from django.test import TestCase
from .models import Wallet
from rest_framework.test import APIClient


class WalletAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.wallet_uuid = 'f2770897-7136-4018-b0b9-04608ea39c56'
        self.wallet = Wallet.objects.create(uuid=self.wallet_uuid, balance=1000)

    def test_get_wallet_balance(self):
        response = self.client.get(f'/api/v1/wallets/{self.wallet_uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['balance'], 1000)

    def test_deposit_funds(self):
        response = self.client.post(f'/api/v1/wallets/{self.wallet_uuid}/operation', 
                                   {'operationType': 'DEPOSIT', 'amount': 500}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['balance'], 1500)

    def test_withdraw_funds(self):
        response = self.client.post(f'/api/v1/wallets/{self.wallet_uuid}/operation', 
                                   {'operationType': 'WITHDRAW', 'amount': 200}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['balance'], 800)

    def test_withdraw_insufficient_funds(self):
        response = self.client.post(f'/api/v1/wallets/{self.wallet_uuid}/operation', 
                                   {'operationType': 'WITHDRAW', 'amount': 1500}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_wallet_not_found(self):
        response = self.client.get('/api/v1/wallets/invalid_uuid')
        self.assertEqual(response.status_code, 404)
