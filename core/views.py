from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_otp
from .models import User

# Create your views here.
class LoginView(APIView):
    http_method_names = ['post']
    def  post(self, request):
        phone = request.data.get('phone', '')
        try:
            user = User.objects.get(phone=phone)
            is_new = False
        except User.DoesNotExist:
             # Create a new user
            user = User(phone=phone, username=phone)
            user.save()
            is_new = True

        otp = generate_otp()
        user.otp = otp
        user.save()

        response_data = {
            'is_new': is_new,
            'otp': otp
        }

        return Response(response_data, status=status.HTTP_200_OK)

class VerifyView(APIView):
    http_method_names = ['post']

    def post(self, request):
        phone = request.data.get('phone', '')
        otp_received = request.data.get('otp', '')

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'User with this phone number does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp_received:
            # Generate access token and refresh token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return tokens to the user
            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'OTP Code is wrong'}, status=status.HTTP_401_UNAUTHORIZED)