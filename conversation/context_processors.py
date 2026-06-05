from django.db.models import F, Max, OuterRef, Q, Subquery

from .models import Conversation, ConversationMember


def inbox_badge(request):
    if not request.user.is_authenticated:
        return {'inbox_unread': 0}

    user_last_seen = Subquery(
        ConversationMember.objects.filter(
            conversation=OuterRef('pk'),
            user=request.user,
        ).values('last_seen')[:1]
    )

    unread = (
        Conversation.objects.filter(
            conversationmember__user=request.user,
            conversationmember__is_deleted=False,
        )
        .annotate(
            last_message_at=Max('messages__created_at'),
            user_last_seen=user_last_seen,
        )
        .filter(
            Q(last_message_at__isnull=False)
            & (Q(user_last_seen__isnull=True) | Q(last_message_at__gt=F('user_last_seen')))
        )
        .count()
    )

    return {'inbox_unread': unread}
