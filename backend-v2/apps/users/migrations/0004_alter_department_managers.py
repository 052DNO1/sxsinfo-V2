from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_department_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='managers',
            field=models.ManyToManyField(blank=True, db_table='department_managers', related_name='managed_departments', to=settings.AUTH_USER_MODEL, verbose_name='分院管理员'),
        ),
    ]
