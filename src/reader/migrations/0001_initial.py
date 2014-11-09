# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('entry_id', models.CharField(max_length=1024)),
                ('title', models.CharField(max_length=1024)),
                ('content', models.TextField()),
                ('link', models.URLField(max_length=1024)),
                ('time', models.DateTimeField()),
                ('json', jsonfield.fields.JSONField()),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'entries',
                'ordering': ['-time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('url', models.URLField()),
                ('homepage', models.URLField()),
                ('etag', models.CharField(blank=True, max_length=1024)),
                ('last_modified', models.DateTimeField(null=True, blank=True)),
                ('subscribers', models.ManyToManyField(related_query_name='feed', to=settings.AUTH_USER_MODEL, related_name='feeds')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('mode', models.CharField(choices=[('A', 'All Items'), ('U', 'Unread Only')], default='A', max_length=1)),
                ('sorting', models.CharField(choices=[('T', 'Time'), ('I', 'Intelligence')], default='T', max_length=1)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserEntryState',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('read', models.BooleanField(default=False)),
                ('expanded', models.BooleanField(default=False)),
                ('opened', models.BooleanField(default=False)),
                ('starred', models.BooleanField(default=False)),
                ('entry', models.ForeignKey(to='reader.Entry', related_name='user_states', related_query_name='user_state')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='entry_states', related_query_name='entry_state')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entry',
            name='feed',
            field=models.ForeignKey(to='reader.Feed'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('feed', 'entry_id')]),
        ),
    ]
