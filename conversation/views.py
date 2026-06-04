from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from item.models import Item
from conversation.models import Conversation, ConversationMember
from conversation.forms import ConversationMessageForm


@login_required
def new(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    if item.created_by == request.user:
        return redirect('dashboard:index')

    conversation = Conversation.objects.filter(
        item=item,
        members=request.user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(item=item)
        conversation.members.add(request.user)
        conversation.members.add(item.created_by)

        ConversationMember.objects.get_or_create(user=request.user, conversation=conversation)
        ConversationMember.objects.get_or_create(user=item.created_by, conversation=conversation)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.created_by = request.user
            message.save()

            return redirect('conversation:detail', pk=conversation.id)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/new.html', {'form': form})


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        members=request.user,
        conversationmember__user=request.user,
        conversationmember__is_deleted=False,
    )

    enriched = []

    for conv in conversations:
        member = ConversationMember.objects.filter(
            conversation=conv,
            user=request.user
        ).first()

        if member and member.last_seen:
            conv.unread = conv.modified_at > member.last_seen
        else:
            conv.unread = True

        enriched.append(conv)

    return render(request, 'conversation/inbox.html', {'conversations': enriched})


@login_required
def detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, members=request.user)

    member, _ = ConversationMember.objects.get_or_create(
        user=request.user,
        conversation=conversation,
    )
    member.last_seen = timezone.now()
    member.save()

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.created_by = request.user
            message.save()

            conversation.updated_at = timezone.now()
            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'form': form,
    })


@login_required
def delete_conversation(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)

    ConversationMember.objects.filter(
        conversation=conversation,
        user=request.user,
    ).update(is_deleted=True)

    return redirect('conversation:inbox')
