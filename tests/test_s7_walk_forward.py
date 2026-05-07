from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.core.replay import build_walk_forward_splits


def _snapshot_rows(count: int) -> list[tuple[int, datetime]]:
    start = datetime(2020, 1, 1)
    rows: list[tuple[int, datetime]] = []
    for idx in range(count):
        rows.append((idx + 1, start + timedelta(days=idx)))
    return rows


def test_build_walk_forward_splits_deterministic_schedule() -> None:
    rows = _snapshot_rows(8)
    splits = build_walk_forward_splits(rows, train_size=3, test_size=2, step_size=2)
    assert [split.split_id for split in splits] == [1, 2]
    assert splits[0].train_snapshot_ids == (1, 2, 3)
    assert splits[0].test_snapshot_ids == (4, 5)
    assert splits[1].train_snapshot_ids == (3, 4, 5)
    assert splits[1].test_snapshot_ids == (6, 7)


def test_build_walk_forward_splits_uses_test_size_step_by_default() -> None:
    rows = _snapshot_rows(10)
    splits = build_walk_forward_splits(rows, train_size=4, test_size=2)
    assert [split.train_snapshot_ids for split in splits] == [
        (1, 2, 3, 4),
        (3, 4, 5, 6),
        (5, 6, 7, 8),
    ]


@pytest.mark.parametrize(
    "train_size,test_size,step_size",
    [
        (0, 2, 1),
        (2, 0, 1),
        (2, 2, 0),
    ],
)
def test_build_walk_forward_splits_rejects_nonpositive_sizes(
    train_size: int,
    test_size: int,
    step_size: int,
) -> None:
    with pytest.raises(ValueError):
        build_walk_forward_splits(
            _snapshot_rows(8),
            train_size=train_size,
            test_size=test_size,
            step_size=step_size,
        )
