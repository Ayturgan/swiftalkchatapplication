from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from apps.messenger.models import Thread, ChatMessage


@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')

    context = {
        'Threads': threads
    }

    return render(request, 'swiftalk/settings.html', context)


@login_required
def get_latest_messages(request):
    # Запрашиваем последние 10 сообщений для текущего пользователя
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')

    # Сериализуем сообщения в формат JSON
    messages_data = [{
        "message": msg.message,
        "timestamp": msg.timestamp,
        "avatar": msg.user.avatar.url if msg.user.avatar else None
    } for msg in messages]

    return JsonResponse(messages_data, safe=False)
