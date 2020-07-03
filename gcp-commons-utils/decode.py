import base64

import binascii
import json

class DecodeUtil:

    def decode_input_to_dict(input_request):
        """Decode input request to dict python."""
        if isinstance(input_request, dict):
            return input_request

        if isinstance(input_request, str):
            input_request = input_request.encode()

        try:
            input_request = base64.decodebytes(input_request)
        except (TypeError, binascii.Error):
            pass

        try:
            input_request = json.loads(input_request)
        except Exception:
            raise Exception(f"Invalid JSON object. {input_request} ...")
        return input_request
