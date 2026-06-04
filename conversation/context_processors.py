from .models import Conversation, ConversationMember

def inbox_badge(request):
    if not request.user.is_authenticated:
        return {'inbox_unread': 0}

    conversations = Conversation.objects.filter(members=request.user)

    unread = 0

    for c in conversations:
        last_msg = c.messages.order_by('-created_at').first()

        if not last_msg:
            continue

        member = ConversationMember.objects.filter(
            user=request.user,
            conversation=c
        ).first()

        # ako ne postoji member → unread
        if not member or not member.last_seen:
            unread += 1
            continue

        # ako ima novih poruka → unread
        if last_msg.created_at > member.last_seen:
            unread += 1

    return {'inbox_unread': unread}