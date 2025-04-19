from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import hashlib


class Challenge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    docker_image = models.CharField(max_length=100, unique=True)
    docker_port = models.PositiveIntegerField()
    start_port = models.PositiveIntegerField()
    end_port = models.PositiveIntegerField()
    flag = models.CharField(max_length=255)  # Increased max_length for hashed value
    point = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_port > self.end_port:
            raise ValidationError(_("Start port must be less than or equal to end port."))

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure clean() is called before saving
        if self.flag and not self.flag.startswith("hashed_"):
            self.flag = "hashed_" + hashlib.sha256(self.flag.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_challenges')
    container_id = models.CharField(max_length=100)
    port = models.PositiveIntegerField()
    is_live = models.BooleanField(default=False)
    no_of_attempt = models.PositiveIntegerField(default=0)
    is_solved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-updated_at']
        verbose_name = 'User Challenge'
        verbose_name_plural = 'User Challenges'

    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"
