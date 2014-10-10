# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('entry_id', models.CharField(max_length=1024)),
                ('title', models.CharField(max_length=1024)),
                ('content', models.TextField()),
                ('link', models.URLField()),
                ('time', models.DateTimeField()),
                ('json', jsonfield.fields.JSONField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('read', models.BooleanField(default=False)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('url', models.URLField()),
                ('homepage', models.URLField()),
                ('etag', models.CharField(blank=True, max_length=1024)),
                ('last_modified', models.DateTimeField(null=True, blank=True)),
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
