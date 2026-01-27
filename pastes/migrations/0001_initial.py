# Generated manually to ensure perfect schema match
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paste',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('max_views', models.IntegerField(blank=True, null=True)),
                ('current_views', models.IntegerField(default=0)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                # This is the column that was missing in your error
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
