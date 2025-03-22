from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Create your models here.



class CustomUserManager(BaseUserManager):
    def create_user(self, email,password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValueError(f"Password validation error: {e.messages}")
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)



class CustUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.email
    

class History(models.Model):
    user = models.ForeignKey(CustUser,on_delete=models.CASCADE)
    image = models.FileField(upload_to='uploaded_images')