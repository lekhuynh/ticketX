import hashlib
import hmac
import urllib.parse
from datetime import datetime

class VNPay:
    def __init__(self, tmn_code, hash_secret, payment_url, return_url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.return_url = return_url
        self.request_data = {}

    def get_payment_url(self, order_id: str, amount: int, order_desc: str, ipaddr: str) -> str:
        self.request_data['vnp_Version'] = '2.1.0'
        self.request_data['vnp_Command'] = 'pay'
        self.request_data['vnp_TmnCode'] = self.tmn_code
        self.request_data['vnp_Amount'] = str(amount * 100)
        self.request_data['vnp_CurrCode'] = 'VND'
        self.request_data['vnp_TxnRef'] = order_id
        self.request_data['vnp_OrderInfo'] = order_desc
        self.request_data['vnp_OrderType'] = 'other'
        self.request_data['vnp_Locale'] = 'vn'
        self.request_data['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        self.request_data['vnp_IpAddr'] = ipaddr
        self.request_data['vnp_ReturnUrl'] = self.return_url

        inputData = sorted(self.request_data.items())
        queryString = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self._hmac_sha512(self.hash_secret, queryString)
        return self.payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, response_data: dict) -> bool:
        vnp_SecureHash = response_data.get('vnp_SecureHash')
        if not vnp_SecureHash:
            return False

        # Build signature from response data
        inputData = []
        for key, val in response_data.items():
            if key.startswith('vnp_') and key not in ['vnp_SecureHashType', 'vnp_SecureHash']:
                inputData.append((key, str(val)))

        inputData.sort()
        queryString = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self._hmac_sha512(self.hash_secret, queryString)
        return hashValue.upper() == vnp_SecureHash.upper()

    def _hmac_sha512(self, key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
