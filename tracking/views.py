from django.http import JsonResponse
from django.views import View
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
import hashlib
import time
from datetime import datetime, timezone
import logging
import traceback
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class NextTrackingNumberView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Extract and validate query parameters
            params = self.validate_params(request.GET)

            # Generate tracking number
            tracking_number = self.generate_tracking_number(params)

            # Prepare response
            created_at = datetime.now(timezone.utc).isoformat()
            response = {
                "tracking_number": tracking_number,
                "created_at": created_at
            }

            return JsonResponse(response)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

    def validate_params(self, query_params):
        params = {}
        required_params = [
            'origin_country_id', 'destination_country_id', 'weight',
            'created_at', 'customer_id', 'customer_name', 'customer_slug'
        ]

        for param in required_params:
            value = query_params.get(param)
            if not value:
                raise ValidationError(f"Missing required parameter: {param}")
            params[param] = value

        # Validate country codes
        country_code_validator = RegexValidator(r'^[A-Z]{2}$', 'Invalid country code')
        country_code_validator(params['origin_country_id'])
        country_code_validator(params['destination_country_id'])

        # Validate weight
        try:
            params['weight'] = float(params['weight'])
            if params['weight'] <= 0 or params['weight'] >= 1000:
                raise ValidationError("Weight must be between 0 and 1000 kg")
        except ValueError:
            raise ValidationError("Invalid weight format")

        # Validate created_at
        try:
            params['created_at'] = self.parse_datetime(params['created_at'])
        except ValueError as e:
            raise ValidationError(f"Invalid created_at format: {str(e)}")

        # Validate customer_id
        try:
            uuid.UUID(params['customer_id'])
        except ValueError:
            raise ValidationError("Invalid customer_id format")

        # Log the validated parameters
        logger.info(f"Validated parameters: {params}")

        return params

    def parse_datetime(self, dt_string):
        try:
            # First, try parsing with dateutil
            dt = date_parser.parse(dt_string)
            
            # Ensure the parsed datetime has a timezone
            if dt.tzinfo is None:
                raise ValueError("Timezone information is missing")
            
            return dt
        except Exception as e:
            logger.error(f"Error parsing datetime: {str(e)}")
            raise ValueError(f"Unable to parse datetime: {dt_string}")

    def generate_tracking_number(self, params):
        # Create a unique string based on input parameters and current timestamp
        unique_string = (
            f"{params['origin_country_id']}{params['destination_country_id']}"
            f"{params['weight']:.3f}{params['customer_id']}{time.time()}"
        )

        # Generate a SHA256 hash of the unique string
        hash_object = hashlib.sha256(unique_string.encode())
        hash_hex = hash_object.hexdigest()

        # Convert the hash to a base36 string and take the first 16 characters
        tracking_number = self.base36_encode(int(hash_hex, 16))[:16]

        # Ensure the tracking number matches the required pattern
        tracking_number = tracking_number.upper()

        logger.info(f"Generated tracking number: {tracking_number}")

        return tracking_number

    def base36_encode(self, number):
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        base36 = ''
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36
        return base36 or alphabet[0]