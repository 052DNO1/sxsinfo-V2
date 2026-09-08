from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maintenance', '0006_workorder_hidden_in_center'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='reporter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_orders', to=settings.AUTH_USER_MODEL, verbose_name='上报人'),
        ),
    ]
