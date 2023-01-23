from django.db import models

# Create your models here.
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.db import models


user_roles = [('admin','admin'), ('user','user')]
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if email is None:
            raise TypeError('User should have a Email')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError('Password should not be none')
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.is_approved = True
        user.is_admin = True
        user.save()
        return user


    
class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return "%s" % (self.email)
    
    def get_card(self):
        return Card.objects.get_or_create(user=self)

    def has_perm(self, perm , obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True       

class Company(models.Model):
    name = models.CharField(max_length=250)
    
    def __str__(self) -> str:
        return self.name

class Member(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    user    = models.ForeignKey(User, on_delete=models.PROTECT)
    user_role = models.CharField(max_length=250, choices=user_roles)
    
    def __str__(self) -> str:
        return str(self.user_role)
    
    class Meta:
        unique_together = ('company', 'user')
        
 

class Card(models.Model):
    
    user             = models.OneToOneField(User,on_delete=models.PROTECT)
    expiration_date  = models.DateField()
    masked_number    = models.IntegerField()
    limit            =models.IntegerField()
    purchased_amount = models.IntegerField()
    current_balance  = models.IntegerField()
    
    def __str__(self) -> str:
        return str(self.masked_number)