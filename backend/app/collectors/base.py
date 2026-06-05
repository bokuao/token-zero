"""
Base collector — shared logic untuk semua provider adapter.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Any
from supabase import Client

logger = logging.getLogger(__name__)


class CollectorBase:
    """Base class untuk provider collector."""

    def __init__(self, supabase: Client, provider_id: str):
        self.supabase = supabase
        self.provider_id = provider_id

    def fetch_models(self) -> list[dict]:
        """Override di subclass — ambil list model dari provider API."""
        raise NotImplementedError

    def is_free(self, raw_model: dict) -> bool:
        """Override di subclass — tentuin apakah model gratis."""
        raise NotImplementedError

    def normalize(self, raw_model: dict) -> dict:
        """Override di subclass — normalisasi ke schema models table."""
        raise NotImplementedError

    def run(self) -> int:
        """Jalankan collector: fetch → normalize → upsert → events."""
        run_id = self._start_run()
        try:
            raw_models = self.fetch_models()
            free_models = [m for m in raw_models if self.is_free(m)]

            count = 0
            seen_ids = set()
            for raw in free_models:
                model = self.normalize(raw)
                self._upsert_model(model)
                seen_ids.add(model["model_id"])
                count += 1

            # Soft-delete models not seen this run
            self._soft_delete_unseen(seen_ids)

            self._finish_run(run_id, "success", count)
            logger.info(f"[{self.provider_id}] {count} free models collected")
            return count
        except Exception as e:
            logger.error(f"[{self.provider_id}] collector failed: {e}")
            self._finish_run(run_id, "failed", 0, error=str(e))
            raise

    # --- Internal helpers ---

    def _start_run(self) -> int:
        result = (
            self.supabase.table("t0_collection_runs")
            .insert({
                "provider_id": self.provider_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status": "running",
            })
            .execute()
        )
        return result.data[0]["id"]

    def _finish_run(self, run_id: int, status: str, count: int, error: str = ""):
        self.supabase.table("t0_collection_runs").update({
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "models_found": count,
            "error": error or None,
        }).eq("id", run_id).execute()

    def _upsert_model(self, model: dict):
        """Insert or update model by (provider_id, model_id)."""
        existing = (
            self.supabase.table("t0_models")
            .select("id, is_free, is_active")
            .eq("provider_id", self.provider_id)
            .eq("model_id", model["model_id"])
            .execute()
        )

        now = datetime.now(timezone.utc).isoformat()

        if existing.data:
            row = existing.data[0]
            # Emit event kalau baru jadi free
            if not row["is_free"] and model["is_free"]:
                self.supabase.table("t0_model_events").insert({
                    "model_id": row["id"],
                    "event_type": "became_free",
                    "occurred_at": now,
                }).execute()
                model["free_since"] = now

            # Reappeared?
            if not row["is_active"]:
                self.supabase.table("t0_model_events").insert({
                    "model_id": row["id"],
                    "event_type": "reappeared",
                    "occurred_at": now,
                }).execute()
                model["is_active"] = True
                model["first_seen_at"] = now

            model["updated_at"] = now
            model["last_seen_at"] = now
            self.supabase.table("t0_models").update(model).eq("id", row["id"]).execute()
        else:
            # New model
            model["first_seen_at"] = now
            model["last_seen_at"] = now
            model["free_since"] = now
            model["updated_at"] = now
            result = (
                self.supabase.table("t0_models")
                .insert(model)
                .execute()
            )
            new_id = result.data[0]["id"]
            self.supabase.table("t0_model_events").insert({
                "model_id": new_id,
                "event_type": "appeared",
                "occurred_at": now,
            }).execute()

    def _soft_delete_unseen(self, seen_ids: set[str]):
        """Mark models not in seen_ids as inactive."""
        if not seen_ids:
            return
        now = datetime.now(timezone.utc).isoformat()
        result = (
            self.supabase.table("t0_models")
            .select("id, model_id")
            .eq("provider_id", self.provider_id)
            .eq("is_active", True)
            .execute()
        )
        for row in result.data:
            if row["model_id"] not in seen_ids:
                self.supabase.table("t0_models").update({
                    "is_active": False,
                    "updated_at": now,
                }).eq("id", row["id"]).execute()
                self.supabase.table("t0_model_events").insert({
                    "model_id": row["id"],
                    "event_type": "disappeared",
                    "occurred_at": now,
                }).execute()
