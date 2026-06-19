from __future__ import annotations

from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    """Enable the pgvector extension before any VectorField table is created.

    The jobs and resumes initial migrations both depend on this one (jobs implicitly
    as the same app's next migration; resumes via an explicit dependency), so the
    extension always exists before a VectorField column is created.
    """

    initial = True

    dependencies = []

    operations = [
        VectorExtension(),
    ]
