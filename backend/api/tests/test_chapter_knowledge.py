from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import StudyNote
from api.tests.factories import make_chapter, make_question, make_user


class PearlsAndKnowledgeTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="pearl-user")
        self.chapter = make_chapter(
            slug="acute-kidney-injury-icu",
            title="AKI and ICU Nephrology",
        )
        make_question(
            1,
            chapter=self.chapter,
            clinical_pearl="FENa below 1 percent favors prerenal azotemia when the patient is not on a diuretic.",
        )
        StudyNote.objects.create(
            user=self.user,
            chapter=self.chapter,
            topic_title="Noise",
            content="This short personal note should not pollute exam pearls.",
        )

    def test_pearls_default_excludes_study_notes(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("board-pearls"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        texts = [p["pearl"] for g in response.data["chapters"] for p in g["pearls"]]
        self.assertTrue(any("FENa" in t or "Winter" in t or "ATN" in t for t in texts))
        self.assertFalse(any("personal note" in t.lower() for t in texts))

    def test_pearls_include_notes_opt_in(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("board-pearls"), {"include_notes": "1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        texts = [p["pearl"] for g in response.data["chapters"] for p in g["pearls"]]
        self.assertTrue(any("personal note" in t.lower() for t in texts))

    def test_legacy_slug_maps_to_canonical_knowledge(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/chapters/aki/knowledge/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["chapter"]["slug"], "acute-kidney-injury-icu")
        self.assertGreaterEqual(response.data["pearl_count"], 1)
        self.assertIn("ATN vs prerenal", response.data["high_yield"])
