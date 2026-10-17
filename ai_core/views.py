import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import tasks


@csrf_exempt
@require_POST
def score_lead_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    result = tasks.score_lead(
        name=data.get("name", ""),
        industry=data.get("industry", ""),
        message=data.get("message", ""),
    )
    return JsonResponse(result)


@csrf_exempt
@require_POST
def summarize_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    text = data.get("text", "")
    if not text:
        return JsonResponse({"error": "text is required"}, status=400)

    result = tasks.summarize_text(text, max_sentences=data.get("max_sentences", 3))
    return JsonResponse({"summary": result})


@csrf_exempt
@require_POST
def classify_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    text = data.get("text", "")
    if not text:
        return JsonResponse({"error": "text is required"}, status=400)

    result = tasks.classify_intent(text)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def draft_email_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    context = data.get("context", "")
    if not context:
        return JsonResponse({"error": "context is required"}, status=400)

    result = tasks.draft_email(context, tone=data.get("tone", "professional"))
    return JsonResponse({"email": result})
