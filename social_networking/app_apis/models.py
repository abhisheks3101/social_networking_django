from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from .base_models import BaseAbstractModel


class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a SuperUser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, BaseAbstractModel):
    """
    User Main Table
    """
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class FriendRequest(BaseAbstractModel):
    """
    Handles friend requests between users
    """
    RequestStatus = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )
    sender = models.ForeignKey(User,
                            related_name='sent_friend_requests',
                            on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,
                                related_name='received_friend_requests',
                                on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices = RequestStatus, default='pending')

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"


class Friendship(BaseAbstractModel):
    """
    Stores established friendships between users
    """
    user1 = models.ForeignKey(
        User,
        related_name='friends1',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User,
        related_name='friends2',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1} <-> {self.user2}"