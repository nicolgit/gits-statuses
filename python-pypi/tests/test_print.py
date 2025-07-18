"""
Unit tests for the print utility functions.
"""

from unittest.mock import patch
import sys
from io import StringIO

from utils.print import print_error, print_info


class TestPrintError:
    """Tests for print_error function."""

    @patch("sys.stderr")
    def test_print_error_basic(self, mock_stderr):
        """Test print_error with basic message."""
        mock_stderr_buffer = StringIO()
        mock_stderr.write = mock_stderr_buffer.write
        mock_stderr.flush = lambda: None

        with patch("builtins.print") as mock_print:
            print_error("Test error message")

        mock_print.assert_called_once_with("Error: Test error message", file=sys.stderr)

    def test_print_error_with_real_stderr(self):
        """Test print_error with real stderr capture."""
        # Capture stderr output
        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()

        try:
            print_error("Test error message")
            output = captured_stderr.getvalue()
            assert output == "Error: Test error message\n"
        finally:
            sys.stderr = old_stderr

    @patch("sys.stderr")
    def test_print_error_empty_message(self, mock_stderr):
        """Test print_error with empty message."""
        with patch("builtins.print") as mock_print:
            print_error("")

        mock_print.assert_called_once_with("Error: ", file=sys.stderr)

    @patch("sys.stderr")
    def test_print_error_multiline_message(self, mock_stderr):
        """Test print_error with multiline message."""
        multiline_message = "Line 1\nLine 2\nLine 3"

        with patch("builtins.print") as mock_print:
            print_error(multiline_message)

        mock_print.assert_called_once_with(
            f"Error: {multiline_message}", file=sys.stderr
        )

    @patch("sys.stderr")
    def test_print_error_unicode_message(self, mock_stderr):
        """Test print_error with unicode characters."""
        unicode_message = "Error with unicode: 🚨 αβγ"

        with patch("builtins.print") as mock_print:
            print_error(unicode_message)

        mock_print.assert_called_once_with(f"Error: {unicode_message}", file=sys.stderr)

    @patch("sys.stderr")
    def test_print_error_long_message(self, mock_stderr):
        """Test print_error with very long message."""
        long_message = "A" * 1000

        with patch("builtins.print") as mock_print:
            print_error(long_message)

        mock_print.assert_called_once_with(f"Error: {long_message}", file=sys.stderr)


class TestPrintInfo:
    """Tests for print_info function."""

    def test_print_info_basic(self):
        """Test print_info with basic message."""
        with patch("builtins.print") as mock_print:
            print_info("Test info message")

        mock_print.assert_called_once_with("Test info message")

    def test_print_info_with_real_stdout(self):
        """Test print_info with real stdout capture."""
        # Capture stdout output
        old_stdout = sys.stdout
        sys.stdout = captured_stdout = StringIO()

        try:
            print_info("Test info message")
            output = captured_stdout.getvalue()
            assert output == "Test info message\n"
        finally:
            sys.stdout = old_stdout

    def test_print_info_empty_message(self):
        """Test print_info with empty message."""
        with patch("builtins.print") as mock_print:
            print_info("")

        mock_print.assert_called_once_with("")

    def test_print_info_multiline_message(self):
        """Test print_info with multiline message."""
        multiline_message = "Line 1\nLine 2\nLine 3"

        with patch("builtins.print") as mock_print:
            print_info(multiline_message)

        mock_print.assert_called_once_with(multiline_message)

    def test_print_info_unicode_message(self):
        """Test print_info with unicode characters."""
        unicode_message = "Info with unicode: ✅ αβγ"

        with patch("builtins.print") as mock_print:
            print_info(unicode_message)

        mock_print.assert_called_once_with(unicode_message)

    def test_print_info_long_message(self):
        """Test print_info with very long message."""
        long_message = "B" * 1000

        with patch("builtins.print") as mock_print:
            print_info(long_message)

        mock_print.assert_called_once_with(long_message)

    def test_print_info_none_message(self):
        """Test print_info with None message."""
        with patch("builtins.print") as mock_print:
            print_info(None)

        mock_print.assert_called_once_with(None)

    def test_print_info_numeric_message(self):
        """Test print_info with numeric message."""
        with patch("builtins.print") as mock_print:
            print_info(42)

        mock_print.assert_called_once_with(42)


class TestPrintFunctionsIntegration:
    """Integration tests for print functions."""

    def test_print_error_vs_print_info_output_streams(self):
        """Test that print_error and print_info use different output streams."""
        # Capture both stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        captured_stdout = StringIO()
        captured_stderr = StringIO()

        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            print_info("Info message")
            print_error("Error message")

            stdout_output = captured_stdout.getvalue()
            stderr_output = captured_stderr.getvalue()

            assert stdout_output == "Info message\n"
            assert stderr_output == "Error: Error message\n"

            # Verify messages don't cross streams
            assert "Info message" not in stderr_output
            assert "Error message" not in stdout_output

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def test_print_functions_return_none(self):
        """Test that both print functions return None."""
        with patch("builtins.print"):
            result_info = print_info("Test")
            result_error = print_error("Test")

            assert result_info is None
            assert result_error is None

    def test_print_functions_with_string_formatting(self):
        """Test print functions with formatted strings."""
        with patch("builtins.print") as mock_print:
            name = "Alice"
            age = 30

            print_info(f"User {name} is {age} years old")
            print_error(f"Failed to process user {name}")

            assert mock_print.call_count == 2
            mock_print.assert_any_call("User Alice is 30 years old")
            mock_print.assert_any_call(
                "Error: Failed to process user Alice", file=sys.stderr
            )
