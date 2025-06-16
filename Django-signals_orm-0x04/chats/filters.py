# chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by a specific participant's user_id
    participant = django_filters.NumberFilter(field_name="conversation__participants__user_id", lookup_expr="exact")

    # Filter messages sent after a specific date
    start_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")

    # Filter messages sent before a specific date
    end_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ['participant', 'start_date', 'end_date']
