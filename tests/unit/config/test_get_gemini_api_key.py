from unittest.mock import MagicMock, patch

import pytest

from backend.src.constants.aws import GEMINI_API_KEY_MISSING_ERROR, SSM_PARAM_NAME_ENV_KEY


def _reset_cache() -> None:
    import backend.src.config.settings as mod

    mod._gemini_api_key_cache = None


@pytest.fixture(autouse=True)
def _clear_cache():
    _reset_cache()
    yield
    _reset_cache()


class TestGetGeminiApiKey:
    def test_returns_env_var_when_set(self) -> None:
        from backend.src.config.settings import get_gemini_api_key

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-123"}, clear=False):
            result = get_gemini_api_key()

        assert result == "test-key-123"

    def test_ignores_placeholder_value(self) -> None:
        from backend.src.config.settings import get_gemini_api_key

        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "your_api_key_here"},
            clear=False,
        ):
            with pytest.raises(RuntimeError, match=GEMINI_API_KEY_MISSING_ERROR):
                get_gemini_api_key()

    def test_reads_from_ssm_when_env_var_missing(self) -> None:
        from backend.src.config.settings import get_gemini_api_key

        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {
            "Parameter": {"Value": "ssm-api-key-456"},
        }

        env = {SSM_PARAM_NAME_ENV_KEY: "/test/param"}
        with (
            patch.dict("os.environ", env, clear=False),
            patch("backend.src.config.settings.boto3") as mock_boto3,
        ):
            mock_boto3.client.return_value = mock_ssm
            # Remove GEMINI_API_KEY if present
            with patch.dict("os.environ", {}, clear=False):
                import os

                os.environ.pop("GEMINI_API_KEY", None)
                result = get_gemini_api_key()

        assert result == "ssm-api-key-456"
        mock_ssm.get_parameter.assert_called_once_with(
            Name="/test/param", WithDecryption=True,
        )

    def test_caches_result(self) -> None:
        from backend.src.config.settings import get_gemini_api_key

        with patch.dict("os.environ", {"GEMINI_API_KEY": "cached-key"}, clear=False):
            first = get_gemini_api_key()
            second = get_gemini_api_key()

        assert first == second == "cached-key"

    def test_raises_when_no_config(self) -> None:
        from backend.src.config.settings import get_gemini_api_key

        import os

        env_copy = os.environ.copy()
        env_copy.pop("GEMINI_API_KEY", None)
        env_copy.pop(SSM_PARAM_NAME_ENV_KEY, None)

        with patch.dict("os.environ", env_copy, clear=True):
            with pytest.raises(RuntimeError, match=GEMINI_API_KEY_MISSING_ERROR):
                get_gemini_api_key()
