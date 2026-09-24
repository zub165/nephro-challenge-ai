"""Verify pearls and MCQs against literature using LLaMA + rule checks."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from api.data.board_pearls import BOARD_PEARLS
from api.data.chapter_seed import CHAPTERS
from api.data.reference_sync import sync_question_references_from_seed
from api.models import Question, StudyNote
from api.services.content_verification_service import (
    apply_mcq_correction,
    verify_mcq,
    verify_pearl,
)


class Command(BaseCommand):
    help = (
        "Verify board pearls and MCQ content against medical references. "
        "Use --sync-db after deploy to sync citations and audit all DB questions. "
        "Use --llama for full LLaMA/OpenAI verification on the VPS."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sync-db",
            action="store_true",
            help="Sync reference IDs from seed data into DB, then verify all published questions.",
        )
        parser.add_argument(
            "--llama",
            action="store_true",
            help="Use LLaMA/OpenAI for verification (requires Ollama or OPENAI_API_KEY on VPS).",
        )
        parser.add_argument(
            "--no-llm",
            action="store_true",
            help="Rule-based checks only (default when --llama is not set).",
        )
        parser.add_argument(
            "--pearls-only",
            action="store_true",
            help="Verify curated board pearls only.",
        )
        parser.add_argument(
            "--mcqs-only",
            action="store_true",
            help="Verify chapter seed MCQs and DB questions only.",
        )
        parser.add_argument(
            "--notes-only",
            action="store_true",
            help="Enrich and verify user study notes (My Book) only.",
        )
        parser.add_argument(
            "--fix-notes",
            action="store_true",
            help="Apply LLM text corrections when enriching study notes.",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Apply suggested corrections to DB questions (not seed files).",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="",
            help="Write JSON report to this path.",
        )
        parser.add_argument(
            "--learn",
            action="store_true",
            help="Record verification findings into AI learning memory (always on with --llama).",
        )

    def handle(self, *args, **options):
        if options["llama"] and options["no_llm"]:
            self.stderr.write(self.style.ERROR("Use either --llama or --no-llm, not both."))
            return

        use_llm = bool(options["llama"])
        if use_llm and not options["learn"]:
            self.stdout.write("Note: --llama stores findings in AI learning memory automatically.")
        report = {"pearls": [], "mcqs": [], "study_notes": [], "summary": {}}
        verified_ok = 0
        verified_fail = 0

        if options["notes_only"]:
            from api.services.notes_enrichment_service import enrich_study_notes_queryset

            qs = StudyNote.objects.all().select_related("chapter", "user")
            self.stdout.write(f"Enriching {qs.count()} user study notes...")
            batch = enrich_study_notes_queryset(
                qs,
                use_llm=use_llm,
                apply_correction=bool(options["fix_notes"]),
            )
            report["study_notes"] = batch["notes"]
            verified_ok += batch["verified_ok"]
            verified_fail += batch["verified_fail"]
            report["summary"]["study_notes_enriched"] = batch["enriched"]
            self.stdout.write(
                self.style.SUCCESS(
                    f"Study notes: {batch['enriched']} enriched, "
                    f"{batch['verified_ok']} verified, {batch['verified_fail']} need review"
                )
            )
            if not (use_llm or options["learn"]):
                pass
            elif use_llm or options["learn"]:
                from api.services.ai_learning_service import (
                    learning_stats,
                    maybe_export_learning,
                    seed_baseline_rules,
                )

                seed_baseline_rules()
                maybe_export_learning()
                stats = learning_stats()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"AI learning (auto): {stats['approved']} approved, {stats['pending']} pending"
                    )
                )
            if options["output"]:
                out = Path(options["output"])
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(report, indent=2, default=str))
            return

        if options["sync_db"]:
            stats = sync_question_references_from_seed()
            self.stdout.write(
                self.style.SUCCESS(
                    "Reference sync: "
                    f"{stats['updated']} updated, "
                    f"{stats['unchanged']} unchanged, "
                    f"{stats['missing']} seed MCQs not in DB"
                )
            )
            report["summary"]["reference_sync"] = stats

        if not options["mcqs_only"]:
            self.stdout.write("Verifying board pearls...")
            for pearl in BOARD_PEARLS:
                result = verify_pearl(pearl, use_llm=use_llm)
                v = result["verification"]
                ok = v.get("verified")
                if ok:
                    verified_ok += 1
                else:
                    verified_fail += 1
                report["pearls"].append(result)
                label = "OK" if ok else "REVIEW"
                self.stdout.write(f"  [{label}] {pearl['topic']}: {v.get('confidence', '?')}")
                for issue in v.get("issues") or []:
                    self.stdout.write(f"    - {issue}")

        if not options["pearls_only"]:
            self.stdout.write("Verifying chapter seed MCQs...")
            for ch in CHAPTERS:
                for topic in ch.get("topics", []):
                    for mcq in topic.get("mcqs", []):
                        result = verify_mcq(
                            question_text=mcq["question_text"],
                            explanation=mcq.get("explanation", ""),
                            clinical_pearl=mcq.get("clinical_pearl", ""),
                            reference_ids=mcq.get("reference_ids", []),
                            use_llm=use_llm,
                        )
                        v = result["verification"]
                        if v.get("verified"):
                            verified_ok += 1
                        else:
                            verified_fail += 1
                        report["mcqs"].append({"chapter": ch["slug"], **result})

            db_qs = Question.objects.filter(is_published=True).order_by("id")
            if not options["sync_db"]:
                db_qs = db_qs[:50]
            label = "all published" if options["sync_db"] else "sample"
            self.stdout.write(f"Verifying {label} DB questions...")
            for q in db_qs:
                ref_ids = []
                if q.reference and q.reference.strip().startswith("["):
                    try:
                        ref_ids = json.loads(q.reference)
                    except json.JSONDecodeError:
                        pass
                result = verify_mcq(
                    question_text=q.question_text,
                    explanation=q.explanation,
                    clinical_pearl=q.clinical_pearl,
                    reference_ids=ref_ids,
                    use_llm=use_llm,
                )
                v = result["verification"]
                if v.get("verified"):
                    verified_ok += 1
                else:
                    verified_fail += 1
                if options["fix"] and not v.get("verified"):
                    updated = apply_mcq_correction(
                        {
                            "explanation": q.explanation,
                            "clinical_pearl": q.clinical_pearl,
                            "reference_ids": ref_ids,
                        },
                        v,
                    )
                    q.explanation = updated.get("explanation", q.explanation)
                    q.clinical_pearl = updated.get("clinical_pearl", q.clinical_pearl)
                    if updated.get("reference"):
                        q.reference = updated["reference"]
                    q.save(update_fields=["explanation", "clinical_pearl", "reference"])
                    self.stdout.write(self.style.SUCCESS(f"  Fixed Q#{q.id}"))
                report["mcqs"].append({"question_id": q.id, **result})

            if options["sync_db"]:
                from api.services.notes_enrichment_service import enrich_study_notes_queryset

                note_qs = StudyNote.objects.all().select_related("chapter", "user")
                self.stdout.write(f"Enriching {note_qs.count()} user study notes...")
                batch = enrich_study_notes_queryset(
                    note_qs,
                    use_llm=use_llm,
                    apply_correction=bool(options["fix_notes"]),
                )
                report["study_notes"] = batch["notes"]
                verified_ok += batch["verified_ok"]
                verified_fail += batch["verified_fail"]
                report["summary"]["study_notes_enriched"] = batch["enriched"]

        report["summary"].update({
            "verified_ok": verified_ok,
            "verified_fail": verified_fail,
            "llm_used": use_llm,
            "sync_db": bool(options["sync_db"]),
        })
        self.stdout.write(
            self.style.SUCCESS(f"\nDone: {verified_ok} verified, {verified_fail} need review")
        )

        if options["output"]:
            out = Path(options["output"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(report, indent=2, default=str))
            self.stdout.write(f"Report written to {out}")

        if use_llm or options["learn"]:
            from api.services.ai_learning_service import (
                export_learning_snapshot,
                learning_stats,
                maybe_export_learning,
                seed_baseline_rules,
            )

            seed_baseline_rules()
            maybe_export_learning()
            stats = learning_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f"AI learning (auto): {stats['approved']} approved, {stats['pending']} pending"
                )
            )
            if options["output"]:
                export_learning_snapshot()
