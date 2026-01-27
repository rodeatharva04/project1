import uuid
from django.db import models

class Paste(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    # If null, unlimited views
    max_views = models.IntegerField(null=True, blank=True)
    # Start at 0
    current_views = models.IntegerField(default=0)
    # If null, never expires
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_unavailable(self, now):
        """
        Checks if the paste is expired or view-limited based on the 'now' time passed in.
        Passing 'now' explicitly allows us to support the Time Travel requirement.
        """
        # 1. Check TTL
        if self.expires_at and now >= self.expires_at:
            return True
        
        # 2. Check View Count
        # If max_views is set and we have reached or exceeded it
        if self.max_views is not None and self.current_views >= self.max_views:
            return True
            
        return False
