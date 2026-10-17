from django.db import models


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        SCORED = "scored", "Scored"
        CONTACTED = "contacted", "Contacted"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=120, blank=True)
    industry = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    ai_score = models.PositiveSmallIntegerField(null=True, blank=True)
    ai_label = models.CharField(max_length=10, blank=True)
    ai_reason = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        label = f" [{self.ai_label}]" if self.ai_label else ""
        return f"{self.name}{label}"
