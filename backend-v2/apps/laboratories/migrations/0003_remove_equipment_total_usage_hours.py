from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('laboratories', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment',
            name='total_usage_hours',
        ),
    ]
