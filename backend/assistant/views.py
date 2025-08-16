from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .chat import answer_query

@csrf_exempt
def chat_with_document(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "")
        file = request.FILES.get("document", None)
        if not file or not user_input:
            return JsonResponse({"error": "Missing message or document"}, status=400)

        try:
            result = answer_query(user_input, file)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
