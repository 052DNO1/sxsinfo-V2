from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0004_add_order_number_to_work_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorder',
            name='laboratory_code',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='实训室编号'),
        ),
        migrations.AddField(
            model_name='workorder',
            name='laboratory_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='实训室名称'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='laboratory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_orders', to='laboratories.laboratory', verbose_name='实训室'),
        ),
    ]
