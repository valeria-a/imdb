from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from imdb_app.models import Review
from imdb_app.serializers.reviews import ReviewSerializer, CreateReviewSerializer


# only logged-in users can create a review
# only user that created a review can update/delete it
class ReviewsPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST']:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'PUT', 'DELETE']:
            return request.user.is_authenticated and request.user.id == obj.user_id
        return True


class ReviewsViewSet(ModelViewSet):

    queryset = Review.objects.all()

    permission_classes = [ReviewsPermissions]

    # we need different serializers for different actions
    serializer_class = ReviewSerializer

    # We override this method in order to use CreateReviewSerializer
    # that does not require a user during creation of the review.
    # The user will be injected in perform_create() after the data is validated
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        return self.serializer_class

    def get_queryset(self):
        qs = self.queryset
        if self.action == 'list':
            if 'user' in self.request.query_params and self.request.query_params['user'] == 'me':
                qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        if Review.objects.filter(user=self.request.user, movie_id=serializer.validated_data['movie']).exists():
            raise ValidationError(detail="User can create only one review per movie")
        serializer.validated_data['user'] = self.request.user
        serializer.save()

