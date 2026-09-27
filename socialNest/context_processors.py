def notifications(request):
    """Expose unread notification count to every template."""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count()
        }
    return {'unread_notifications_count': 0}
