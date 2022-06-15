from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from polymorphic.models import PolymorphicModel, PolymorphicManager


class UserManager(BaseUserManager, PolymorphicManager):
    def _create_user(self, email, first_name, last_name, password, is_staff, is_superuser):
        if not email:
            raise ValueError('User must have an email address.')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name.upper(),
            last_name=last_name.upper(),
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, first_name, last_name, password):
        return self._create_user(
            email, first_name, last_name, password, False, False
        )

    def create_superuser(self, email, first_name, last_name, password):
        return self._create_user(
            email, first_name, last_name, password, True, True
        )


class User(AbstractBaseUser, PermissionsMixin, PolymorphicModel):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name()

    def requires_update(self, properties):
        if self.first_name is not properties['first_name']:
            return True
        if self.last_name is not properties['last_name']:
            return True
        return False

class StudentUser(User):
    hubspot_contact_id = models.IntegerField(null=True, blank=True)
