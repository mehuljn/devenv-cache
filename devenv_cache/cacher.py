import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)

class PyPIClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _http_get_json(self, url: str) -> dict | None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "devenv-cache/0.1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    data = response.read()
                    return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # 404 is a standard fallback trigger or not-found indicator
                logger.debug(f"Metadata not found (404) at: {url}")
            else:
                logger.warning(f"HTTP error {e.code} fetching metadata from {url}: {e.reason}")
        except Exception as e:
            logger.warning(f"Failed to fetch metadata from {url}: {str(e)}")
        return None

    def fetch_metadata(self, package: str, version: str = "") -> dict[str, str]:
        """Fetch package metadata from PyPI.
        
        Attempts to fetch version-specific metadata first. If that fails or isn't 
        provided, falls back to the general package metadata.
        """
        metadata = {"summary": "", "description": ""}
        
        # Try version-specific URL first
        if version:
            version_url = f"https://pypi.org/pypi/{package}/{version}/json"
            data = self._http_get_json(version_url)
            if data and "info" in data:
                metadata["summary"] = data["info"].get("summary") or ""
                metadata["description"] = data["info"].get("description") or ""
                return metadata

        # Fallback to general package URL
        fallback_url = f"https://pypi.org/pypi/{package}/json"
        data = self._http_get_json(fallback_url)
        if data and "info" in data:
            metadata["summary"] = data["info"].get("summary") or ""
            metadata["description"] = data["info"].get("description") or ""

        return metadata
