from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.select_related('sender', 'post')
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': request.user.notifications.filter(is_read=False).count(),
    })


@login_required
@require_POST
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})
