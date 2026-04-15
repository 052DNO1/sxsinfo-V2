from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagerecord',
            name='laboratory_code',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='实训室编号'),
        ),
        migrations.AddField(
            model_name='usagerecord',
            name='laboratory_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='实训室名称'),
        ),
        migrations.AlterField(
            model_name='usagerecord',
            name='laboratory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usage_records', to='laboratories.laboratory', verbose_name='实训室'),
        ),
    ]
