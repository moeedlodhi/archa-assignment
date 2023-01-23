from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User,Card,Member
from rest_framework.views import APIView
from .serializers import (SignInSerializer,UserDetailViewSerializer, UserListCreateSerializer, CardSerializer)


# Create your views here.
class SigninView(generics.GenericAPIView):
    serializer_class = SignInSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": self.request})
        if serializer.is_valid():
            data_dict={"data":serializer.validated_data}

            member_obj=Member.objects.filter(user__email=request.data.get('email'))
            if member_obj:
                data_dict['member_obj'] = member_obj.values_list('id', flat=True)
            return Response(data_dict, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListCreateSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        if 'id' in self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)           

                
    def get_queryset(self):
        member_id = self.kwargs.get('m_id', None)
        if member_id:
            if 'id' in self.kwargs:
                return self.queryset
            else:
                queryset = User.objects.all()
                member_obj = Member.objects.get(id=member_id)

                if member_obj:
                    if member_obj.user_role == 'admin':
                        return queryset
                    else:
                        return queryset.filter(id = self.request.user.id).first()
                else:
                    return None
        else:
            return None        

    def get_serializer_class(self):
        if 'id' in self.kwargs:
            return UserDetailViewSerializer
        else:
            return self.serializer_class

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)



class CardApiView(generics.ListCreateAPIView):
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardSerializer
    queryset = Card.objects.all()
    
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        member_id=self.kwargs.get("m_id")
        queryset = Card.objects.all()
        member = member_detail(member_id)
        if member:
            return queryset            
        else:
            return queryset.filter(user__id = self.request.user.id).first()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
           serializer.save()            
           return Response(serializer.data)
        return Response(serializer.errors)



class CardDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardSerializer
    queryset = Card.objects.all()
    lookup_field = "id"
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id == self.request.user.id:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return None

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        if serializer.validated_data['user'].id == self.request.user.id:
            serializer.save()
        else:
            return None
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id == self.request.user.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return None
        
        
    def perform_destroy(self, instance):
        instance.delete()
    
    
    
def member_detail(member_id):
    member_obj =Member.objects.get(id=member_id)
    if member_obj.user_role == 'admin':
        return True
    else:
        return False