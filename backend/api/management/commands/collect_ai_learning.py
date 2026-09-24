"""Collect, approve, and export AI learning entries (RAG memory for Ollama)."""

from django.core.management.base import BaseCommand

from api.services.ai_learning_service import (
    export_learning_snapshot,
    learning_stats,
    seed_baseline_rules,
)


class Command(BaseCommand):
    help = (
        "Manage AI learning memory: seed baseline rules, export snapshot, show stats. "
        "Run weekly via cron after verify_medical_content --llama --learn."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed-baseline",
            action="store_true",
            help="Insert built-in nephrology rule lessons (idempotent).",
        )
        parser.add_argument(
            "--export",
            action="store_true",
            help="Export approved lessons to api/data/ai_learned_context.json",
        )
        parser.add_argument(
            "--approve-all-pending",
            action="store_true",
            help="Approve all pending lessons (admin review shortcut).",
        )

    def handle(self, *args, **options):
        if options["seed_baseline"]:
            n = seed_baseline_rules()
            self.stdout.write(self.style.SUCCESS(f"Baseline rules: {n} new entry/entries"))

        if options["approve_all_pending"]:
            from api.models import AIKnowledgeEntry
            from django.utils import timezone

            count = AIKnowledgeEntry.objects.filter(
                status=AIKnowledgeEntry.Status.PENDING,
            ).update(
                status=AIKnowledgeEntry.Status.APPROVED,
                approved_at=timezone.now(),
            )
            self.stdout.write(self.style.SUCCESS(f"Approved {count} pending lesson(s)"))

        stats = learning_stats()
        self.stdout.write(
            f"Learning memory: {stats['approved']} approved, "
            f"{stats['pending']} pending, {stats['rejected']} rejected"
        )

        if options["export"]:
            payload = export_learning_snapshot()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Exported {payload['count']} lesson(s) to api/data/ai_learned_context.json"
                )
            )
