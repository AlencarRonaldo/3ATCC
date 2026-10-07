from rest_framework_simplejwt.authentication import JWTAuthentication
class ActiveJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user=super().get_user(validated_token)
        if not user.active or not user.is_active: from rest_framework.exceptions import AuthenticationFailed; raise AuthenticationFailed('Usuário inativo.')
        return user
