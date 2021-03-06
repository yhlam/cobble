import csv
import json

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.views.generic.list import BaseListView
from django.utils.http import is_safe_url

import django_filters
from braces.views import (
    AnonymousRequiredMixin, LoginRequiredMixin, SuperuserRequiredMixin,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import StrictButton
from rest_framework.generics import (
    GenericAPIView, ListAPIView, RetrieveAPIView,
)
from rest_framework.filters import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import ISO_8601
from rest_framework import status

from utils.filters import IsoDateTimeFilter
from utils.io import EchoWriter
from .forms import UserConfigUpdateForm
from .models import Entry, UserConfig, UserEntryState
from .serializers import (
    EntrySerializer,
    UserConfigSerializer,
    SuccessSerializer,
    FetchOptionSerializer
)
from . import tasks


class EntryFilterSet(django_filters.FilterSet):
    last_updated = IsoDateTimeFilter(
        name='updated',
        lookup_type='lt',
        input_formats=(ISO_8601,),
    )

    read = django_filters.BooleanFilter(
        action=lambda qs, value: (
            qs.filter(user_state__read=True) if value
            else qs.filter(Q(user_state=None) | Q(user_state__read=False))
        ),
    )

    prioritize = django_filters.BooleanFilter(
        action=lambda qs, value: (
            qs.order_by('-userentrypriority__priority', '-time') if value
            else qs
        ),
    )

    offset = django_filters.NumberFilter(
        decimal_places=0,
        min_value=0,
        action=lambda qs, value: qs[int(value):],
    )

    limit = django_filters.NumberFilter(
        decimal_places=0,
        min_value=0,
        max_value=100,
        action=lambda qs, value: qs[:int(value)],
        required=True,
    )

    class Meta:
        model = Entry
        fields = ['last_updated', 'read', 'prioritize', 'offset', 'limit']


class EntryListAPIView(ListAPIView):
    serializer_class = EntrySerializer
    filter_class = EntryFilterSet
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        params = {
            'read': request.QUERY_PARAMS.get('read', True),
            'prioritize': request.QUERY_PARAMS.get('prioritize', False),
        }
        config_update_form = UserConfigUpdateForm(params)
        if config_update_form.is_valid():
            data = config_update_form.cleaned_data
            UserConfig.objects.update_or_create(
                user=self.request.user,
                defaults={
                    'mode': 'A' if data['read'] else 'U',
                    'sorting': 'I' if data['prioritize'] else 'T',
                }
            )

        return response

    def get_queryset(self):
        user = self.request.user
        return Entry.objects.filter(
            Q(feed__subscribers=user),
            Q(userentrypriority=None) | Q(userentrypriority__user=user),
        )


class UpdateEntryStateAPIView(GenericAPIView):
    queryset = Entry.objects.all()
    serializer_class = SuccessSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        entry = self.get_object()
        user = request.user
        entry.user_states.update_or_create(
            user=user,
            defaults={
                'user': user,
                'entry': entry,
                self.update_field: self.update_value
            },
        )
        return Response({'success': True})


class SetReadAPIView(UpdateEntryStateAPIView):
    update_field = 'read'
    update_value = True


class SetUnreadAPIView(UpdateEntryStateAPIView):
    update_field = 'read'
    update_value = False


class SetExpandedAPIView(UpdateEntryStateAPIView):
    update_field = 'expanded'
    update_value = True


class SetOpenedAPIView(UpdateEntryStateAPIView):
    update_field = 'opened'
    update_value = True


class SetStarredAPIView(UpdateEntryStateAPIView):
    update_field = 'starred'
    update_value = True


class SetUnstarredAPIView(UpdateEntryStateAPIView):
    update_field = 'starred'
    update_value = False


class RetrieveUserConfigAPIView(RetrieveAPIView):
    serializer_class = UserConfigSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        user = self.request.user

        if queryset is None:
            queryset = UserConfig.objects.filter(user=user)

        config, _ = queryset.get_or_create(
            defaults={'mode': 'A', 'sorting': 'T'}
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, config)

        return config


class FetchAPIView(GenericAPIView):
    serializer_class = FetchOptionSerializer
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA)

        if serializer.is_valid():
            if serializer.object['async'] == 'T':
                tasks.load_all_feeds.delay()
            else:
                tasks.load_all_feeds()
            return Response(status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DestoryReadEntryAPIView(GenericAPIView):
    serializer_class = SuccessSerializer
    permission_classes = (IsAdminUser,)

    def delete(self, request, *args, **kwargs):
        Entry.objects.select_related('user_states').filter(
            user_state__read=True
        ).delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class ReaderView(LoginRequiredMixin, TemplateView):
    template_name = 'reader.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class LoginView(AnonymousRequiredMixin, FormView):
    form_class = AuthenticationForm
    success_url = reverse_lazy('reader')
    template_name = 'login.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    authenticated_redirect_url = reverse_lazy('reader')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form_helper = FormHelper()
        form_helper.form_action = reverse('login')
        form_helper.form_class = 'form-horizontal'
        form_helper.label_class = 'hidden'
        form_helper.field_class = 'col-md-12'
        form_helper.layout = Layout(
            Field('username', placeholder='Username'),
            Field('password', placeholder='Password'),
            StrictButton(
                'Sign in',
                css_class='btn-primary pull-right',
                type='submit'
            ),
        )

        context['form_helper'] = form_helper
        return context


class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class StatExportView(LoginRequiredMixin, SuperuserRequiredMixin, BaseListView):
    login_url = reverse_lazy('login')
    context_object_name = 'user_entry_states'
    queryset = UserEntryState.objects.select_related(
        'user', 'entry', 'entry__feed'
    )

    def render_to_response(self, context):
        pseudo_buffer = EchoWriter()
        writer = csv.writer(pseudo_buffer)
        rows = self.get_csv_rows(context[self.context_object_name])
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows),
            content_type="text/csv")
        response['Content-Disposition'] = ('attachment; '
                                           'filename="stat.csv"')
        return response

    def get_csv_rows(self, user_entry_states):
        yield (
            'feed_name', 'feed_url',
            'entry_title', 'entry_url', 'entry_content', 'entry_time',
            'entry_details',
            'username',
            'read', 'expanded', 'opened', 'starred'
        )

        for state in user_entry_states:
            entry = state.entry
            feed = entry.feed
            yield (
                feed.name, feed.url,
                entry.title, entry.link, entry.content,
                entry.time.strftime('%Y-%m-%d %H:%M:%S %z'),
                json.dumps(entry.json),
                state.user.username,
                state.read, state.expanded, state.opened, state.starred,
            )
