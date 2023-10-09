import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from apps.messenger.models import Thread, ChatMessage, ChatFile
from apps.users.models import CustomUser


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        try:
            print('receive', event)
        except UnicodeEncodeError:
            pass
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')
        file_url = received_data.get('file_url')

        if not msg and not file_url:
            print('Error:: empty message and no file')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        chat_message = await self.create_chat_message(thread_obj, sent_by_user, msg, file_url)

        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']

        response = {
            'message': msg,
            'sent_by': self_user.id,
            'thread_id': thread_id,
            'avatar': chat_message.user.avatar.url if chat_message.user.avatar else None,
            'timestamp': str(chat_message.timestamp) if chat_message.timestamp else None,
            'file_url': chat_message.file.file.url if chat_message.file else None,
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )
    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = CustomUser.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg, file_url=None):
        chat_file = None
        if file_url:
            file_path = file_url.replace("/media/", "", 1)
            try:
                chat_file = ChatFile.objects.get(file=file_path)
            except ChatFile.DoesNotExist:
                print(f"Error: No ChatFile found for path {file_path}")

        return ChatMessage.objects.create(
            thread=thread,
            user=user,
            message=msg,
            file=chat_file  # If chat_file is None, it will just be a message without a file.
        )
