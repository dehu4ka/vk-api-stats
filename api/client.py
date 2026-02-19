import requests
from config import BASE_URL, AUTH_HEADER, PER_PAGE


class RTCameraClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers["Authorization"] = AUTH_HEADER

    def _get(self, path: str, params: dict | None = None, auth: bool = True) -> dict:
        url = f"{self.base_url}{path}"
        if auth:
            resp = self.session.get(url, params=params, timeout=30)
        else:
            resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_health(self) -> dict:
        return self._get("/v1/health.json", auth=False)

    def get_all_cameras(self) -> list[dict]:
        cameras = []
        page = 1
        while True:
            data = self._get("/v3/user/cameras.json", params={
                "page": page,
                "per_page": PER_PAGE,
            })
            cameras.extend(data.get("cameras", []))
            if page >= data.get("total_pages", 1):
                break
            page += 1
        return cameras

    def get_camera_fragments(self, uid: str, since: int, till: int) -> list[dict]:
        data = self._get(f"/v1/user/cameras/{uid}/estore_fragments.json", params={
            "since": since,
            "till": till,
        })
        return data.get("fragments", [])

    def get_baked_archives(self, offset: int = 0, limit: int = 50,
                           sort_column: str = "updated_at",
                           sort_order: str = "desc",
                           **kwargs) -> dict:
        params = {
            "offset": offset,
            "limit": limit,
            "sort_column": sort_column,
            "sort_order": sort_order,
        }
        params.update(kwargs)
        return self._get("/v1/user/baked_archives.json", params=params)
