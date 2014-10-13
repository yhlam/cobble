from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.utils.http import is_safe_url

import django_filters
from braces.views import AnonymousRequiredMixin, LoginRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import StrictButton
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.filters import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import ISO_8601
from rest_framework import status

from utils.filters import IsoDateTimeFilter
from .models import Entry
from .serializers import (
    EntrySerializer, SuccessSerializer, FetchOptionSerializer
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
        fields = ['last_updated', 'read', 'offset', 'limit']


class EntryListAPIView(ListAPIView):
    serializer_class = EntrySerializer
    filter_class = EntryFilterSet
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Entry.objects.filter(feed__subscribers=user)


class UpdateReadAPIView(GenericAPIView):
    queryset = Entry.objects.all()
    read = False
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
                'read': self.read
            },
        )
        return Response({'success': True})


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
