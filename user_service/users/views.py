from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer, MyTokenObtainPairSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class CustomLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            user_data = UserProfileSerializer(user).data
            response.data['user'] = user_data
        return response

class CustomRefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def validate_token(request):
    """
    Endpoint for Traefik forward auth middleware.
    Validates JWT token and returns user info if valid.
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return Response({'error': 'No authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        prefix, token = auth_header.split(' ')
        if prefix.lower() != 'bearer':
            return Response({'error': 'Invalid token format'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Validate token
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        
        # Get user to ensure they exist
        user = User.objects.get(id=user_id)
        
        response = Response({
            'valid': True,
            'user_id': user_id,
            'email': user.email,
            'role': user.role
        }, status=status.HTTP_200_OK)
        
        # Set headers that Traefik will forward to the backend services
        response['X-User-Id'] = str(user_id)
        response['X-User-Email'] = user.email
        response['X-User-Role'] = user.role
        
        return response
        
    except (ValueError, KeyError):
        return Response({'error': 'Invalid token format'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': 'Token validation failed'}, status=status.HTTP_401_UNAUTHORIZED)