from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.banking.forms import TopUpBalance, TransferBalance
from apps.banking.models import Wallet, Transaction
from apps.messenger.models import Thread, ChatMessage, ChatFile
from apps.users.forms import UserUpdateForm
from django.contrib import messages

from apps.users.models import CustomUser
from .templatetags import templatetags


@login_required
def get_latest_messages(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    messages_data = [{
        "message": msg.message,
        "timestamp": msg.timestamp,
        "avatar": msg.user.avatar.url if msg.user.avatar else None
    } for msg in messages]

    return JsonResponse(messages_data, safe=False)


@login_required
def combined_view(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    form = None
    users = CustomUser.objects.all()
    for a in threads:
        for chat in a.chatmessage_thread.all():
            if chat.file and chat.file.file.url and (
                    chat.file.file.url.endswith(".jpg") or chat.file.file.url.endswith(".png") or chat.file.file.url.endswith(".jpeg")):
                chat.is_image = True
            else:
                chat.is_image = False

    if request.method == "POST":
        if 'form_type' in request.POST:
            if request.POST['form_type'] == 'profile':
                form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
                if form.is_valid():
                    form.save()
                    return redirect('home')

            elif request.POST['form_type'] == 'top_up':
                top_up_form = TopUpBalance(request.POST)
                print("Before form validation")

                if top_up_form.is_valid():
                    print("Form is valid")
                    amount = top_up_form.cleaned_data['balance']

                    user_wallet = Wallet.objects.get(user=request.user)

                    Transaction.objects.create(wallet=user_wallet, amount=amount, description="Top up")
                    user_wallet.balance += amount
                    user_wallet.save()
                    messages.success(request, f"Successfully added {amount} to your wallet!")
                else:
                    messages.error(request, "Form is not valid!")
            elif request.POST['form_type'] == 'transfer':
                transfer_form = TransferBalance(request.POST)
                if transfer_form.is_valid():
                    user_id = transfer_form.cleaned_data['user'].id
                    amount = transfer_form.cleaned_data['balance']
                    if request.user.id == user_id:
                        messages.error(request, "You cannot transfer money to yourself!")
                        return redirect('home')
                    sender_wallet = Wallet.objects.get(user=request.user)
                    recipient_wallet = Wallet.objects.get(user__id=user_id)
                    if sender_wallet.balance < amount:
                        messages.error(request, "Not enough funds for the transfer!")
                        print("Not enough funds for the transfer!!")
                        return redirect('home')
                    sender_wallet.balance -= amount
                    sender_wallet.save()
                    Transaction.objects.create(wallet=sender_wallet, amount=-amount,
                                               description=f"Transfer to {user_id}")
                    recipient_wallet.balance += amount
                    recipient_wallet.save()
                    Transaction.objects.create(wallet=recipient_wallet, amount=amount,
                                               description=f"Received from {request.user.username}")

                    messages.success(request, f"Successfully transferred {amount} to {user_id}!")
                else:
                    messages.error(request, "Form is not valid!")
            elif request.POST['form_type'] == 'create_chat':
                user_to_chat = CustomUser.objects.get(pk=request.POST.get('user_id_get'))
                if not Thread.objects.filter(
                        Q(first_person=request.user, second_person=user_to_chat) |
                        Q(first_person=user_to_chat, second_person=request.user)
                ).exists():
                    Thread.objects.create(first_person=request.user, second_person=user_to_chat)
                    messages.success(request, f"Chat with {user_to_chat.username} was created!")
                else:
                    messages.warning(request, f"You already have a chat with {user_to_chat.username}!")
            elif request.POST['form_type'] == 'delete_acc':
                user = request.user
                user.delete()
                messages.success(request, 'Your account has been deleted.')
                return redirect('login')
    else:
        form = UserUpdateForm(instance=request.user)


    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = None

    def get_thread_id_between_users(user1, user2):
        try:
            thread = Thread.objects.get(
                Q(first_person=user1, second_person=user2) |
                Q(first_person=user2, second_person=user1)
            )
            return thread.id
        except Thread.DoesNotExist:
            return None

    users_with_threads = {}
    for user in users:
        if user != request.user:
            thread_id = get_thread_id_between_users(request.user, user)
            users_with_threads[user] = thread_id

    context = {
        'Threads': threads,
        'form': form,
        'Users': users,
        'Wallet': wallet,
        'UsersWithThreads': users_with_threads,
        'alert_message': "Ваше сообщение здесь",
    }
    return render(request, 'swiftalk/settings.html', context)


def upload_chat_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file_instance = ChatFile(file=request.FILES['file'])
        file_instance.save()
        return JsonResponse({'file_url': file_instance.file.url})
