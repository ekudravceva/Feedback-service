import django.db.models.expressions
import django.db.models.fields.generated
import django.db.models.functions.text
import django.db.models.lookups
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='slug',
            field=models.SlugField(blank=True, default='', editable=False, max_length=180, verbose_name='URL-идентификатор'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='is_long',
            field=models.GeneratedField(db_persist=True, expression=models.Case(models.When(django.db.models.lookups.GreaterThanOrEqual(django.db.models.functions.text.Length('text'), 200), then=models.Value(True)), default=models.Value(False), output_field=models.BooleanField()), output_field=models.BooleanField(), verbose_name='Длинное сообщение'),
        ),
    ]
