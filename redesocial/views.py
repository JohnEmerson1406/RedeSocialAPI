from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *

from rest_framework import generics
from rest_framework.reverse import reverse

from django.http import Http404

from .permissions import *
from rest_framework import permissions

from django.shortcuts import get_object_or_404


class ImportJson(APIView):
    name = 'import'

    def post(self, request, format=None):
        profiles = request.data['users']
        posts = request.data['posts']
        comments = request.data['comments']

        profile_serializer = ProfileSerializer(data=profiles, many=True)
        if profile_serializer.is_valid():
            profile_serializer.save()

        post_serializer = PostSerializer(data=posts, many=True)
        if post_serializer.is_valid():
            post_serializer.save()

        comment_serializer = CommentSerializer(data=comments, many=True)
        if comment_serializer.is_valid():
            comment_serializer.save()


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = "user-list"
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserOrReadOnly,)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = "user-detail"
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserOrReadOnly,)


class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    name = 'profile-list'


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    name = 'profile-detail'


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    name = 'post-list'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    name = 'post-detail'
    permission_classes = (IsUserOrReadOnly,)


class ProfilePostList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilePostSerializer
    name = 'profile-post-list'


class ProfilePostDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilePostSerializer
    name = 'profile-post-detail'


class PostCommentList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCommentSerializer
    name = 'post-comment-list'
    

class PostCommentDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCommentSerializer
    name = 'post-comment-detail'


class CommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    name = 'comment-list'

    def get_queryset(self):
        post_pk = self.kwargs['pk']
        return Comment.objects.filter(postId=post_pk)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    name = 'comment-detail'
    #lookup_field = 'pk' # o padrão ja é 'pk', a nivel de Model
    lookup_url_kwarg = 'comment_pk' # define qual URL kwarg vai ser usado no get_object, o padrão é o mesmo valor de lookup_field

    def get_queryset(self):
        post_pk = self.kwargs['pk']
        return Comment.objects.filter(postId=post_pk)


# class CommentDetail(APIView):
#     permission_classes = (IsOwnerOrReadOnly,)
#     name = 'comment-detail'

#     def get_comment(self, post_pk,comment_pk):
#         try:
#             post = Post.objects.get(pk=post_pk)
#             try:
#                 comment =  post.comments.get(pk=comment_pk)
#                 return comment
#             except Comment.DoesNotExist:
#                 raise Http404
#         except Post.DoesNotExist:
#             raise Http404

#     def get(self, request, post_pk,comment_pk, format=None):
#         comment = self.get_comment(post_pk,comment_pk)
#         comment_s = CommentSerializer(comment)
#         return Response(comment_s.data)

#     def put(self, request, post_pk,comment_pk, format=None):
#         comment = self.get_comment(post_pk,comment_pk)
#         comment_data = request.data
#         comment_data['postId'] = post_pk
#         comment_s = CommentSerializer(comment, data=comment_data)
#         if comment_s.is_valid():
#             comment_s.save()
#             return Response(comment_s.data)
#         return Response(comment_s.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, post_pk,comment_pk, format=None):
#         comment = self.get_comment(post_pk,comment_pk)
#         comment.delete()
#         return Response(status=status.HTTP_200_OK)


class ProfilePostsComments(APIView):
    name = 'profile-posts-comments'

    def get(self, request, format=None):
        profiles = Profile.objects.all()
        status_list = []
        
        for profile in profiles:
            profile_status = {}
            profile_posts = 0
            post_comments = 0

            for post in Post.objects.filter(userId=profile.pk):
                profile_posts += 1
                for comment in Comment.objects.filter(postId=post.pk):
                    post_comments += 1

            profile_status['pk'] = profile.pk
            profile_status['name'] = profile.name
            profile_status['total_posts'] = profile_posts
            profile_status['total_comments'] = post_comments
            
            status_list.append(profile_status)
        
        return Response(status_list, status=status.HTTP_200_OK)


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'import': reverse(ImportJson.name, request=request),
            'users': reverse(UserList.name, request=request),
            'profile': reverse(ProfileList.name, request=request),
            'posts': reverse(PostList.name, request=request),
            'profile-posts': reverse(ProfilePostList.name, request=request),
            'posts-comments': reverse(PostCommentList.name, request=request),
            'profile-posts-comments': reverse(ProfilePostsComments.name, request=request)
        })
