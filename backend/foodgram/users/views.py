from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Follow
from rest_framework import generics, permissions, pagination, mixins, viewsets, status, views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import FollowSerializer, TokenSerializer, FollowCreateSerializer

User = get_user_model()


class RetrieveDestroy(mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    pass


class UserAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid()
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': str(token)},
            status=status.HTTP_200_OK
        )


class UserDeleteToken(views.APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class UserFollowListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowSerializer
    http_method_names = ['get', 'head', 'options', 'trace']
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        follower = self.request.user
        return User.objects.filter(following__user=follower)


class Subscribe(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, author_id):
        user = request.user.id
        data = {
            'user': user,
            'author': author_id
        }
        serializer = FollowCreateSerializer(
            data=data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, pk=author_id)
        follow = Follow.objects.filter(author=author, user=user)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
