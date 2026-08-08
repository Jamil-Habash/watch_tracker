import json

from django.test import TestCase
from django.urls import reverse

from .models import ShowEntry


class ShowEntryApiTests(TestCase):
    def test_create_entry_via_api(self):
        payload = {
            "type": "movie",
            "title": "Parasite",
            "year": 2019,
            "status": "completed",
            "rating": 8.5,
            "dateWatched": "2024-05-01",
            "notes": "Great film",
        }

        response = self.client.post(
            reverse("entries_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ShowEntry.objects.count(), 1)
        entry = ShowEntry.objects.get(pk=response.json()["id"])
        self.assertEqual(entry.title, "Parasite")
        self.assertEqual(entry.status, "completed")
