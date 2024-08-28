import uuid
from django.db import models

class BaseAbstractModel(models.Model):
    """
     This model defines base models that implements common fields like:
     created_at
     updated_at
     is_deleted
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4,
                        editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        """soft delete a model instance"""
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True
        ordering = ['-created_at']