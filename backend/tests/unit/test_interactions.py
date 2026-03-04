"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    interactions = [_make_log(1, 2, 1), _make_log(2, 1, 1)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 2
    assert all(interaction.item_id == 1 for interaction in result)


def test_filter_with_zero_item_id() -> None:
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, 1)]
    result = _filter_by_item_id(interactions, 0)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_with_large_item_id() -> None:
    large_id = 2**31 - 1
    interactions = [_make_log(1, 1, large_id), _make_log(2, 2, 1)]
    result = _filter_by_item_id(interactions, large_id)
    assert len(result) == 1
    assert result[0].item_id == large_id


def test_filter_multiple_matching_item_ids() -> None:
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 1),
        _make_log(3, 3, 1),
        _make_log(4, 4, 2),
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 3
    assert all(interaction.item_id == 1 for interaction in result)


def test_filter_no_matches_for_nonexistent_item_id() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 999)
    assert result == []


def test_filter_preserves_order() -> None:
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 3, 1),
        _make_log(4, 4, 1),
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 3
    assert [i.id for i in result] == [1, 3, 4]


def test_filter_with_negative_item_id() -> None:
    """Test filtering with negative item_id values."""
    interactions = [
        _make_log(1, 1, -1),
        _make_log(2, 2, -1),
        _make_log(3, 3, 1),
    ]
    result = _filter_by_item_id(interactions, -1)
    assert len(result) == 2
    assert all(interaction.item_id == -1 for interaction in result)


def test_filter_with_single_item_list_match() -> None:
    """Test filtering a single-item list where the item matches."""
    interactions = [_make_log(1, 1, 42)]
    result = _filter_by_item_id(interactions, 42)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_with_single_item_list_no_match() -> None:
    """Test filtering a single-item list where the item does not match."""
    interactions = [_make_log(1, 1, 10)]
    result = _filter_by_item_id(interactions, 20)
    assert result == []


def test_filter_consecutive_duplicates() -> None:
    """Test filtering when matching items are consecutive in the list."""
    interactions = [
        _make_log(1, 1, 3),
        _make_log(2, 2, 3),
        _make_log(3, 3, 3),
        _make_log(4, 4, 7),
        _make_log(5, 5, 3),
    ]
    result = _filter_by_item_id(interactions, 3)
    assert len(result) == 4
    assert [i.id for i in result] == [1, 2, 3, 5]


def test_filter_alternating_pattern() -> None:
    """Test filtering when matching and non-matching items alternate."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 10),
        _make_log(3, 3, 5),
        _make_log(4, 4, 10),
        _make_log(5, 5, 5),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert [i.id for i in result] == [1, 3, 5]


def test_filter_none_match() -> None:
    """Test when no items in the list match the filter."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 3, 3),
    ]
    result = _filter_by_item_id(interactions, 999)
    assert result == []


def test_filter_first_and_last_only() -> None:
    """Test when only the first and last items match the filter."""
    interactions = [
        _make_log(1, 1, 7),
        _make_log(2, 2, 8),
        _make_log(3, 3, 8),
        _make_log(4, 4, 8),
        _make_log(5, 5, 7),
    ]
    result = _filter_by_item_id(interactions, 7)
    assert len(result) == 2
    assert [i.id for i in result] == [1, 5]


def test_filter_minimum_positive_item_id() -> None:
    """Test filtering with the minimum positive item_id value (1)."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 3, 1),
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 2
    assert all(interaction.item_id == 1 for interaction in result)