
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,Card

# This class returns the string needed to generate the key for OTP


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__' 
        
    def validate(self, attrs):
        
        limit = attrs.get('limit')
        purchased_amount = attrs.get('purchased_amount')
        current_balance = attrs.get('current_balance')
        if purchased_amount > limit:
            raise serializers.ValidationError({"purchased_amount":'purchased_amount must be lower than card limit'}, code=status.HTTP_400_BAD_REQUEST)
        balance = limit - purchased_amount
        if balance != current_balance:
            raise serializers.ValidationError({"current_balance":'Balance not valid'}, code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)
        
class UserListCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'password',
        ]
        read_only_field = ['id','created_at']
        

    def validate(self, attrs):
        email = attrs.get('email', None)
        request = self.context.get('request')
        if request.method == "POST":
            if User.objects.filter(email__iexact=email).exists():
                return serializers.ValidationError('Email already exist! Please, try another email')

        return attrs

    def create(self, validated_data):

        newuser = User.objects.create(
            first_name=validated_data['name'],
            email=validated_data['email'],
        )
        newuser.set_password(validated_data['password'])
        newuser.save()
        return newuser


class UserDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name",  "email",]

        read_only_field = ['id', 'created_at']

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance=instance, *args, **kwargs)
        request = self.context.get('request')
        if request and (request.method == 'PUT' or request.method == 'PATCH' or request.method == "DELETE"):
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=120, required=True, min_length=3)
    password = serializers.CharField(max_length=68, min_length=5, write_only=True)
    access_token = serializers.CharField(max_length=200, min_length=5, read_only=True)
    refresh_token = serializers.CharField(max_length=200, min_length=5, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'access_token',
                  'refresh_token']
        read_only_fields = ['access_token', 'refresh_token', ]



    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "provided credentials are not valid/email"}, code=status.HTTP_401_UNAUTHORIZED)

        if user:
            if not user.check_password(password):
                raise serializers.ValidationError(
                    {"password": "provided credentials are not valid/password"}, code=status.HTTP_401_UNAUTHORIZED)
        if not user:
            raise serializers.ValidationError(
                {"email": "User not found"}, code=status.HTTP_401_UNAUTHORIZED)

        token = RefreshToken.for_user(user)
        attrs['id'] = int(user.id)
        attrs['name'] = str(user.name)
        attrs['email'] = str(user.email)
        attrs['access_token'] = str(token.access_token)
        attrs['refresh_token'] = str(token)
        return attrs
