"""LMS API client with Bearer token authentication."""

import httpx
from config import settings


class ApiError(Exception):
    """API request failed with a user-friendly error message."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class LmsApiClient:
    """Client for the LMS backend API."""

    def __init__(self):
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self.timeout = 10.0  # seconds

    def _get_headers(self) -> dict[str, str]:
        """Return headers with Bearer token authentication."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def _handle_request_error(self, error: Exception, endpoint: str) -> ApiError:
        """Convert raw exceptions into user-friendly API errors."""
        if isinstance(error, httpx.TimeoutException):
            return ApiError(
                f"Backend timeout: {endpoint} did not respond within {self.timeout}s. "
                "The service may be overloaded."
            )
        elif isinstance(error, httpx.ConnectError):
            # Extract the core error message (e.g., "Connection refused")
            error_str = str(error)
            # Try to extract just the key part like "Connection refused"
            if "Connection refused" in error_str:
                return ApiError(
                    f"Backend connection refused ({self.base_url}). "
                    "Check that the backend service is running."
                )
            elif "Name resolution" in error_str:
                return ApiError(
                    f"Backend hostname not found ({self.base_url}). "
                    "Check your LMS_API_BASE_URL configuration."
                )
            else:
                return ApiError(
                    f"Backend connection failed: {error_str}. "
                    "Check that the backend service is running."
                )
        elif isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            if status == 401:
                return ApiError(
                    "Backend authentication failed (HTTP 401). "
                    "Check LMS_API_KEY in .env.bot.secret."
                )
            elif status == 403:
                return ApiError(
                    "Backend access denied (HTTP 403). "
                    "Your API key may not have permission."
                )
            elif status == 404:
                return ApiError(f"Backend resource not found (HTTP 404): {endpoint}")
            elif status == 502:
                return ApiError(
                    f"Backend unavailable (HTTP 502 Bad Gateway). "
                    "The backend service may be starting up or crashed."
                )
            elif status == 503:
                return ApiError(
                    f"Backend service unavailable (HTTP 503). "
                    "The service may be down for maintenance."
                )
            elif status >= 500:
                return ApiError(
                    f"Backend server error (HTTP {status}). "
                    "The service may be down or experiencing issues."
                )
            else:
                return ApiError(f"Backend error: HTTP {status} for {endpoint}")
        else:
            return ApiError(f"Backend error: {str(error)}")

    def get_items(self) -> list[dict]:
        """Fetch all items (labs and tasks) from the backend."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise self._handle_request_error(e, "/items/")

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Fetch pass rates for a specific lab."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/analytics/pass-rates",
                    headers=self._get_headers(),
                    params={"lab": lab},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise self._handle_request_error(e, f"/analytics/pass-rates?lab={lab}")

    def get_learners(self) -> list[dict]:
        """Fetch enrolled learners."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/learners/",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise self._handle_request_error(e, "/learners/")


# Global API client instance
api_client = LmsApiClient()
