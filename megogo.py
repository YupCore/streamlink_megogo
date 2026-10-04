"""
$description Ukrainian OTT TV and media streaming platform owned by LLC Megogo.
$url megogo.net
$type live, vod
"""

import re

from streamlink.logger import getLogger
from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream

log = getLogger(__name__)


@pluginmatcher(
    re.compile(
        r"https?://(?:www\.)?megogo\.net/(?:[a-z]{2}/)?(?:tv/channels|view)/(?P<id>\d+)",
    ),
)
class Megogo(Plugin):
    URL_CSRF = "https://megogo.net/r/csrf"
    URL_STREAM = "https://megogo.net/wb/desktop-megogo-tvVideoEmbed_v1/stream"

    _RESTRICTION_MESSAGES = {
        "NOT_PURCHASABLE": "This channel requires an active subscription or account login",
        "UNAUTHORIZED": "This channel requires an account login",
        "USER_UNAUTHORIZED": "This channel requires an account login",
        "SUBSCRIPTION_REQUIRED": "This channel requires an active subscription",
        "SUBSCRIPTION": "This channel requires an active subscription",
        "SVOD_EXPIRED": "Subscription has expired",
        "GEO_UNAVAILABLE": "This stream is not available in your region (geo-restricted)",
        "GEO_BLOCKED": "This stream is not available in your region (geo-restricted)",
        "AGE_RESTRICTED": "This channel has age restrictions or parental control enabled",
    }

    _SCHEMA_CSRF = validate.Schema(
        str,
        validate.transform(str.strip),
    )

    _SCHEMA_STREAM = validate.Schema(
        validate.parse_json(),
        validate.get(("data", "widgets", "desktop-megogo-tvVideoEmbed_v1", "json")),
        validate.none_or_all({
            "video_id": validate.any(int, str),
            "title": str,
            validate.optional("src"): validate.any("", None, validate.url()),
            validate.optional("is_wvdrm"): bool,
            validate.optional("drm_type"): validate.none_or_all(str),
            validate.optional("license_server"): validate.none_or_all(str),
            validate.optional("parental_control_required"): bool,
            validate.optional("restrictions"): validate.none_or_all([
                {
                    validate.optional("code"): validate.none_or_all(str),
                    validate.optional("message"): validate.none_or_all(str),
                },
            ]),
        }),
    )

    def _get_streams(self):
        channel_id = self.match["id"]

        csrf_token = self.session.http.get(
            self.URL_CSRF,
            schema=self._SCHEMA_CSRF,
        )

        headers = {
            "Referer": self.url,
            "csrf-token": csrf_token,
        }

        data = self.session.http.get(
            self.URL_STREAM,
            params={
                "lang": "ua",
                "obj_id": channel_id,
            },
            headers=headers,
            schema=self._SCHEMA_STREAM,
        )

        if not data:
            return

        if data.get("is_wvdrm") or data.get("drm_type") or data.get("license_server"):
            log.error("This stream is protected by DRM and cannot be played")
            return

        if data.get("parental_control_required"):
            log.error("This stream requires parental control PIN")
            return

        restrictions = data.get("restrictions")
        if restrictions:
            messages = []
            for r in restrictions:
                code = r.get("code")
                msg = self._RESTRICTION_MESSAGES.get(code) if code else None
                if not msg and r.get("message"):
                    msg = r["message"]
                if msg:
                    messages.append(f"{msg} ({code})" if code and code not in self._RESTRICTION_MESSAGES else msg)

            if messages:
                log.error(f"Stream is not available: {'; '.join(messages)}")
                return

        src = data.get("src")
        if not src:
            log.error("No playable stream URL returned (this channel may require an active subscription or login)")
            return

        self.id = str(data["video_id"])
        self.title = data["title"]

        return HLSStream.parse_variant_playlist(
            self.session,
            src,
            headers={"Referer": self.url},
        )


__plugin__ = Megogo
