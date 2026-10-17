from django.contrib import admin

from .models import AIRequest


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ["task", "provider", "model", "latency_ms", "cost_usd", "fallback_used", "created"]
    list_filter = ["provider", "task", "fallback_used"]
    readonly_fields = ["prompt_preview", "error", "created"]
    date_hierarchy = "created"
