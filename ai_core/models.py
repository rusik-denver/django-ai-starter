from django.db import models


class AIRequest(models.Model):
    """Logs every LLM call for cost tracking and debugging."""

    class Provider(models.TextChoices):
        OLLAMA = "ollama", "Ollama"
        CLAUDE = "claude", "Claude API"
        DEMO = "demo", "Demo"

    task = models.CharField(max_length=60, db_index=True)
    provider = models.CharField(max_length=10, choices=Provider.choices)
    model = models.CharField(max_length=80)
    prompt_preview = models.CharField(max_length=200, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    fallback_used = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["task", "created"]),
            models.Index(fields=["provider", "created"]),
        ]

    def __str__(self):
        status = "OK" if not self.error else "ERR"
        return f"[{status}] {self.task} via {self.provider} ({self.latency_ms}ms)"
