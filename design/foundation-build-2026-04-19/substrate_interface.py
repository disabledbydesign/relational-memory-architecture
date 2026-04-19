# SPDX-FileCopyrightText: 2026 L. June Bloch
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Substrate interface + local file adapter.

The crystallization layer talks to a substrate through this interface. The
substrate is pluggable: a Kintsugi adapter can be plugged in later without
changing anything in the crystallization layer — that is the load-bearing
commitment made when June is reaching out to Thomas E. about the LIRA
ecosystem but has not yet had that conversation.

The local adapter stores each CrystallizationObject as a JSON file under a
configurable root. It is the working implementation until substrate decisions
are resolved relationally. It is sufficient for the matcher integration
(foundation build) and for the activation-findings apparatus.

Reference: relational-memory-design-direction.md §"Who this system is for"
and the standing constraint in the session prompt.
"""
from __future__ import annotations

import json
import logging
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from crystallization_schema import (
    ActivationScope,
    CrystallizationObject,
    MechanismType,
    now_iso,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Substrate interface
# ---------------------------------------------------------------------------


class CrystallizationSubstrate(ABC):
    """
    The abstract interface between the crystallization layer and storage.

    Implementations must preserve three properties:
    1. **Immutable records** except through explicit write operations.
       A load(id) followed by save(obj) with no mutation must not drift.
    2. **Lineage-integrity queries**. `referrers_of(id)` returns all
       crystallizations with `id` in their lineage. The instrument uses this
       to enforce lineage_lock before any modify/archive.
    3. **Scope-filtered listing**. `list_ids(scope=...)` supports loading
       always-active FoundationalCommitments separately from contextual
       crystallizations. The matcher only sees contextual; the bootstrap
       loader only sees always.

    A Kintsugi adapter implementing this interface will translate these
    operations to Kintsugi's storage primitives. The crystallization layer
    code does not import from any substrate implementation — it receives a
    CrystallizationSubstrate instance from wiring code.
    """

    @abstractmethod
    def save(self, obj: CrystallizationObject) -> None:
        """Persist the crystallization. Overwrites if `obj.id` already exists."""

    @abstractmethod
    def load(self, crystallization_id: str) -> Optional[CrystallizationObject]:
        """Return the stored crystallization, or None if not found."""

    @abstractmethod
    def exists(self, crystallization_id: str) -> bool:
        """Whether a crystallization with this id is stored."""

    @abstractmethod
    def list_ids(
        self,
        *,
        scope: Optional[ActivationScope] = None,
        mechanism_type: Optional[MechanismType] = None,
    ) -> List[str]:
        """
        Return ids matching the filter. `scope=None, mechanism_type=None` lists
        all stored crystallizations.
        """

    @abstractmethod
    def load_all(
        self,
        *,
        scope: Optional[ActivationScope] = None,
        mechanism_type: Optional[MechanismType] = None,
    ) -> List[CrystallizationObject]:
        """Convenience: list_ids + load for each."""

    @abstractmethod
    def referrers_of(self, crystallization_id: str) -> List[str]:
        """
        Return ids of crystallizations whose lineage contains `crystallization_id`.
        Used by the instrument to enforce lineage_lock.
        """

    @abstractmethod
    def archive(self, crystallization_id: str) -> str:
        """
        Move the crystallization to archived storage. Return the archive id
        (which may be the same as the original id plus an archive prefix).

        Raises LineageLockViolation if lineage_lock is set and other active
        crystallizations reference this one in lineage.
        """

    @abstractmethod
    def archive_prior_version(
        self,
        crystallization_id: str,
        *,
        new_version: CrystallizationObject,
    ) -> str:
        """
        Specialised archive for FoundationalCommitment revisions:
        archive the current version (under a derived archive id), append
        its id to `new_version.persistence_policy.prior_versions`, then
        save the new version at the same id. Return the archive id of the
        version that was displaced.
        """


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SubstrateError(Exception):
    """Base class for substrate-level errors."""


class LineageLockViolation(SubstrateError):
    """Raised when an operation violates an active lineage_lock."""


# ---------------------------------------------------------------------------
# Local file adapter
# ---------------------------------------------------------------------------


class LocalFileSubstrate(CrystallizationSubstrate):
    """
    Filesystem-backed adapter. One JSON file per crystallization.

    Layout::

        <root>/
            active/
                <slugified-id>.json
            archive/
                <slugified-id>.<timestamp>.json
            index.json          # { id: relative-path } mapping (derived; rebuildable)

    Thread-safe for intra-process concurrent access via an internal lock.
    Not safe for cross-process concurrent writes — wrap with a file lock
    when that becomes necessary.
    """

    def __init__(self, root: Path):
        self._root = Path(root)
        self._active_dir = self._root / "active"
        self._archive_dir = self._root / "archive"
        self._active_dir.mkdir(parents=True, exist_ok=True)
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # CrystallizationSubstrate implementation
    # ------------------------------------------------------------------

    def save(self, obj: CrystallizationObject) -> None:
        obj.validate()
        with self._lock:
            path = self._path_for(obj.id)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(obj.to_json(), encoding="utf-8")

    def load(self, crystallization_id: str) -> Optional[CrystallizationObject]:
        path = self._path_for(crystallization_id)
        if not path.exists():
            return None
        try:
            return CrystallizationObject.from_json(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Failed to load crystallization %s: %s", crystallization_id, exc)
            return None

    def exists(self, crystallization_id: str) -> bool:
        return self._path_for(crystallization_id).exists()

    def list_ids(
        self,
        *,
        scope: Optional[ActivationScope] = None,
        mechanism_type: Optional[MechanismType] = None,
    ) -> List[str]:
        ids: List[str] = []
        for obj in self._iter_active():
            if scope is not None and obj.activation_scope != scope:
                continue
            if mechanism_type is not None and obj.mechanism_type != mechanism_type:
                continue
            ids.append(obj.id)
        return sorted(ids)

    def load_all(
        self,
        *,
        scope: Optional[ActivationScope] = None,
        mechanism_type: Optional[MechanismType] = None,
    ) -> List[CrystallizationObject]:
        result: List[CrystallizationObject] = []
        for obj in self._iter_active():
            if scope is not None and obj.activation_scope != scope:
                continue
            if mechanism_type is not None and obj.mechanism_type != mechanism_type:
                continue
            result.append(obj)
        result.sort(key=lambda o: o.id)
        return result

    def referrers_of(self, crystallization_id: str) -> List[str]:
        referrers: List[str] = []
        for obj in self._iter_active():
            if obj.lineage and crystallization_id in obj.lineage:
                referrers.append(obj.id)
        return sorted(referrers)

    def archive(self, crystallization_id: str) -> str:
        with self._lock:
            obj = self.load(crystallization_id)
            if obj is None:
                raise SubstrateError(f"{crystallization_id!r} not found")

            if (
                obj.mechanism_type == MechanismType.EMERGENT_TOUCHSTONE
                and obj.persistence_policy.lineage_lock
            ):
                referrers = self.referrers_of(crystallization_id)
                if referrers:
                    raise LineageLockViolation(
                        f"Cannot archive {crystallization_id!r}; referenced in "
                        f"lineage of: {', '.join(referrers)}"
                    )

            timestamp = now_iso().replace(":", "-")
            archive_id = f"{crystallization_id}@{timestamp}"
            archive_path = self._archive_path_for(archive_id)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(obj.to_json(), encoding="utf-8")

            active_path = self._path_for(crystallization_id)
            if active_path.exists():
                active_path.unlink()

            return archive_id

    def archive_prior_version(
        self,
        crystallization_id: str,
        *,
        new_version: CrystallizationObject,
    ) -> str:
        with self._lock:
            if new_version.id != crystallization_id:
                raise SubstrateError(
                    "archive_prior_version: new_version.id must match crystallization_id"
                )
            if new_version.mechanism_type != MechanismType.FOUNDATIONAL_COMMITMENT:
                raise SubstrateError(
                    "archive_prior_version is only valid for FoundationalCommitment"
                )

            prior = self.load(crystallization_id)
            if prior is None:
                # First write of this commitment — no prior to archive.
                self.save(new_version)
                return ""

            timestamp = now_iso().replace(":", "-")
            archive_id = f"{crystallization_id}@v{prior.persistence_policy.version}@{timestamp}"
            archive_path = self._archive_path_for(archive_id)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(prior.to_json(), encoding="utf-8")

            if archive_id not in new_version.persistence_policy.prior_versions:
                new_version.persistence_policy.prior_versions.append(archive_id)
            new_version.updated_at = now_iso()

            self.save(new_version)
            return archive_id

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _iter_active(self) -> Iterable[CrystallizationObject]:
        for path in sorted(self._active_dir.rglob("*.json")):
            try:
                yield CrystallizationObject.from_json(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Skipping unreadable crystallization at %s: %s", path, exc)
                continue

    def _path_for(self, crystallization_id: str) -> Path:
        return self._active_dir / f"{_slugify(crystallization_id)}.json"

    def _archive_path_for(self, archive_id: str) -> Path:
        return self._archive_dir / f"{_slugify(archive_id)}.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slugify(identifier: str) -> str:
    """
    Convert an identifier into a filesystem-safe path component.

    Preserves structure by mapping `/` to `__` rather than flattening, so that
    `touchstone/05-bearing` becomes `touchstone__05-bearing.json` and collisions
    between `a/b` and `a-b` are avoided.
    """
    safe = []
    for ch in identifier:
        if ch.isalnum() or ch in ("-", "_", "."):
            safe.append(ch)
        elif ch == "/":
            safe.append("__")
        else:
            safe.append("_")
    return "".join(safe)
