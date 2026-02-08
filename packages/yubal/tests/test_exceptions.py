"""Tests for exceptions."""

import pytest
from yubal.exceptions import (
    PlaylistNotFoundError,
    PlaylistParseError,
    UpstreamAPIError,
    YubalError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    @pytest.mark.parametrize(
        "exception_class",
        [PlaylistParseError, PlaylistNotFoundError, UpstreamAPIError],
    )
    def test_all_exceptions_inherit_from_base(
        self, exception_class: type[YubalError]
    ) -> None:
        """All custom exceptions should inherit from YubalError."""
        assert issubclass(exception_class, YubalError)

    @pytest.mark.parametrize(
        "exception_class",
        [PlaylistParseError, PlaylistNotFoundError, UpstreamAPIError],
    )
    def test_catch_all_with_base_class(self, exception_class: type[YubalError]) -> None:
        """Should be able to catch all errors with YubalError."""
        with pytest.raises(YubalError) as exc_info:
            raise exception_class("test message")
        assert exc_info.value.message == "test message"

    def test_exception_message_attribute(self) -> None:
        """Exceptions should have message attribute and string representation."""
        error = YubalError("test message")
        assert error.message == "test message"
        assert str(error) == "test message"
