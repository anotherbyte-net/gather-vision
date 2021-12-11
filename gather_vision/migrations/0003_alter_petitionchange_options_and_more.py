# Generated by Django 4.0 on 2021-12-11 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gather_vision', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='petitionchange',
            options={'ordering': ['retrieved_date']},
        ),
        migrations.RemoveConstraint(
            model_name='playlistentry',
            name='playlist_entry_unique_playlist_order',
        ),
        migrations.RenameField(
            model_name='playlistentry',
            old_name='order',
            new_name='position',
        ),
        migrations.AlterField(
            model_name='petitionitem',
            name='eligibility',
            field=models.CharField(blank=True, help_text='The eligibility to sign the petition.', max_length=100),
        ),
        migrations.AlterField(
            model_name='petitionitem',
            name='sponsor',
            field=models.CharField(blank=True, help_text='The name of the sponsor of the petition.', max_length=100),
        ),
        migrations.AlterField(
            model_name='playlistitem',
            name='source',
            field=models.ForeignKey(help_text='The source for this playlist.', on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to='gather_vision.informationsource'),
        ),
        migrations.AlterField(
            model_name='playlisttrack',
            name='source',
            field=models.ForeignKey(help_text='The source for this track information.', on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='gather_vision.informationsource'),
        ),
        migrations.AddConstraint(
            model_name='petitionitem',
            constraint=models.UniqueConstraint(fields=('source', 'code'), name='petition_item_unique_source_code'),
        ),
        migrations.AddConstraint(
            model_name='playlistentry',
            constraint=models.UniqueConstraint(fields=('playlist', 'position'), name='playlist_entry_unique_playlist_position'),
        ),
    ]
