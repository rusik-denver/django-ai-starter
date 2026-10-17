import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ai_core import tasks

from .models import Lead


def demo(request):
    leads = Lead.objects.all()[:20]
    return render(request, "example_app/demo.html", {"leads": leads})


@csrf_exempt
@require_POST
def submit_lead(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    lead = Lead.objects.create(
        name=data.get("name", ""),
        email=data.get("email", ""),
        company=data.get("company", ""),
        industry=data.get("industry", ""),
        message=data.get("message", ""),
    )

    result = tasks.score_lead(lead.name, lead.industry, lead.message)
    lead.ai_score = result.get("score", 5)
    lead.ai_label = result.get("label", "warm")
    lead.ai_reason = result.get("reason", "")
    lead.status = Lead.Status.SCORED
    lead.save()

    return JsonResponse({
        "id": lead.id,
        "score": lead.ai_score,
        "label": lead.ai_label,
        "reason": lead.ai_reason,
    })
