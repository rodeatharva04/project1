import uuid
from django.db import models
from django.utils import timezone

class Paste(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    max_views = models.IntegerField(null=True, blank=True)
    current_views = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_unavailable(self, current_time):
        # Check TTL
        if self.expires_at and current_time >= self.expires_at:
            return True
        # Check View Count
        if self.max_views is not None and self.current_views >= self.max_views:
            return True
        return False
