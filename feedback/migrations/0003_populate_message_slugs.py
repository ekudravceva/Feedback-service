from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_message_slugs(apps, schema_editor):
    # Историческая модель соответствует состоянию БД на момент миграции.
    Message = apps.get_model("feedback", "Message")
    for message in Message.objects.all().order_by("pk"):
        base_slug = slugify(unidecode(message.category)) or "message"
        # Идентификатор в конце гарантирует уникальность.
        message.slug = f"{base_slug}-{message.pk}"
        message.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_message_slug_is_long'),
    ]

    operations = [
        migrations.RunPython(populate_message_slugs, migrations.RunPython.noop),
    ]
