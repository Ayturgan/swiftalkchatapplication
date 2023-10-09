function getActiveElements() {
    let active_thread_id = get_active_thread_id();
    let input_message = $('#input-message-' + active_thread_id);
    let send_message_form = $('#send-message-form-' + active_thread_id);
    return {
        input_message: input_message,
        send_message_form: send_message_form
    };
};

const USER_ID = $('#logged-in-user').val();


let loc = window.location;
let wsStart = 'ws://';

if (loc.protocol === 'https:') {
    wsStart = 'wss://';
}
let endpoint = wsStart + loc.host + loc.pathname;

const socket = new WebSocket(endpoint);

function fetchAndDisplayLatestMessages() {
    let thread_id = get_active_thread_id();
    let sent_by_id = get_active_other_user_id();

    $.ajax({
        url: '/get_latest_messages/',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            data.forEach(msg => {
                console.log(msg);

                newMessage(msg.message, sent_by_id, thread_id, msg.avatar, msg.timestamp);
            });
        }
    });
}

// Вы можете вызывать эту функцию регулярно для обновления чата, например, каждые 10 секунд:
// setInterval(fetchAndDisplayLatestMessages, 10000);

function scrollToBottomOfActiveChat() {
    let activeChatContent = $('.messages-wrapper.is_active .msg_card_body');
    activeChatContent.scrollTop(activeChatContent.prop('scrollHeight'));
}

function convertToTimeZone(timestamp) {
    let localTime = moment.utc(timestamp).tz("Asia/Almaty");
    return localTime.format("HH:mm");
}

socket.onopen = async function (e) {
    console.log('open', e);
    $(document).on('submit', '.chat-footer form', function (e) {
        e.preventDefault();

        let formId = $(this).attr('id');
        let threadId = formId.replace('send-message-form-', '');
        let inputMessageSelector = '#input-message-' + threadId;
        let message = $(inputMessageSelector).val();

        let send_to = get_active_other_user_id();

        let fileUrl = null;
        if (window.latestFileUrl) {
            fileUrl = window.latestFileUrl;
        }

        if (!message && !window.latestFileUrl) {
            return false;
        }

        let data = {
            'message': message,
            'sent_by': USER_ID,
            'send_to': send_to,
            'thread_id': threadId,
            'file_url': fileUrl
        };
        console.log("Data to be sent:", data);

        if (window.latestFileUrl) {
            data = JSON.stringify(data);
        } else {
            data = JSON.stringify(data);
        }

        socket.send(data);
        $(inputMessageSelector).val('');
        $('.dropzone-previews-js').empty();

        window.latestFileUrl = null;
    });
};


socket.onmessage = async function (e) {
    console.log('message', e);
    let data = JSON.parse(e.data);
    let message = data['message'];
    let sent_by_id = data['sent_by'];
    let thread_id = data['thread_id'];
    let avatar = data['avatar'];
    let timestamp = convertToTimeZone(data['timestamp']);
    let fileUrl = data['file_url'];
    newMessage(message, sent_by_id, thread_id, avatar, timestamp, fileUrl);
    scrollToBottomOfActiveChat();
};

socket.onerror = async function (e) {
    console.log('error', e);
};

socket.onclose = async function (e) {
    console.log('close', e);
};


function newMessage(message, sent_by_id, thread_id, avatar, timestamp, fileUrl) {
    console.log("Timestamp received:", timestamp);
    if ($.trim(message) === '' && !fileUrl) {
        return false;
    }

    if (fileUrl) {
        if (fileUrl.endsWith(".jpg") || fileUrl.endsWith(".png") || fileUrl.endsWith(".jpeg")) {
            message += `<br/><img src="${fileUrl}" alt="Uploaded Image" width="200" />`;
        } else {
            message += `<br/><a class=" btn btn-primary" href="${fileUrl}" download>Скачать файл</a>`;
        }
    }

    let elements = getActiveElements();
    let message_element;
    let chat_id = 'chat_' + thread_id
    if (sent_by_id == USER_ID) {
        message_element = `
                    <!-- Message -->
                    <div class="message message-right">
                        <!-- Avatar -->
                        <div class="avatar avatar-sm ml-4 ml-lg-5 d-none d-lg-block">
                            <img class="avatar-img" src="${avatar}">
                        </div>

                        <!-- Message: body -->
                        <div class="message-body">

                            <!-- Message: row -->
                            <div class="message-row">
                                <div class="d-flex align-items-center justify-content-end">

                                    <!-- Message: dropdown -->
                                    <div class="dropdown">
                                        <a class="text-muted opacity-60 mr-3" href="#"
                                           data-toggle="dropdown" aria-haspopup="true"
                                           aria-expanded="false">
                                            <i class="fe-more-vertical"></i>
                                        </a>

                                        <div class="dropdown-menu">
                                            <a class="dropdown-item d-flex align-items-center"
                                               href="#">
                                                Edit <span class="ml-auto fe-edit-3"></span>
                                            </a>
                                            <a class="dropdown-item d-flex align-items-center"
                                               href="#">
                                                Share <span class="ml-auto fe-share-2"></span>
                                            </a>
                                            <a class="dropdown-item d-flex align-items-center"
                                               href="#">
                                                Delete <span class="ml-auto fe-trash-2"></span>
                                            </a>
                                        </div>
                                    </div>
                                    <!-- Message: dropdown -->

                                    <!-- Message: content -->
                                    <div class="message-content bg-primary text-white">
                                        <div> ${message}
                                        </div>
                                        <div class="mt-1">
                                            <small class="opacity-65">
                                            ${timestamp}
                                            </small>
                                        </div>
                                        </div>
                                    </div>
                                    <!-- Message: content -->

                                </div>
                            </div>
                            <!-- Message: row -->

                        </div>
                        <!-- Message: body -->
                    </div>
                    <!-- Message -->
	            `
    } else {
        message_element = `
                    <!-- Message -->
                    <div class="message">
                        <!-- Avatar -->
                        <a class="avatar avatar-sm mr-4 mr-lg-5" href="#"
                           data-chat-sidebar-toggle="#chat-2-info">
                            <img class="avatar-img" src="${avatar}">
                        </a>

                        <!-- Message: body -->
                        <div class="message-body">

                            <!-- Message: row -->
                            <div class="message-row">
                                <div class="d-flex align-items-center">

                                    <!-- Message: content -->
                                    <div class="message-content bg-light">
                                        <div>${message}
                                        </div>

                                        <div class="mt-1">
                                            <small class="opacity-65">
                                            ${timestamp}
                                            </small>
                                        </div>
                                    </div>
                                    <!-- Message: content -->

                                </div>
                            </div>
                            <!-- Message: row -->

                        </div>
                        <!-- Message: body -->
                    </div>
                    <!-- Message -->
                `
    }

    let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .msg_card_body')
    message_body.append($(message_element))
    elements.input_message.val(null);
}

let activeChatId;

$('.contact-li').on('click', function () {
    activeChatId = $(this).attr('chat-id');
    setTimeout(scrollToBottomOfActiveChat, 100);
});


function get_active_other_user_id() {
    let other_user_id = $('.messages-wrapper.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id() {
    let chat_id = $('.messages-wrapper.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}

