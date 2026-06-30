#!/usr/bin/env python3
"""TRMNL private plugin: Patticus Solar / Victron summary.

Designed for private-plugin use via Tailscale Serve on serenity. No OAuth
install flow, no public internet exposure. TRMNL POSTs to /markup with a
user_uuid and the `trmnl` metadata object; we return all required layouts.

Expected host: https://serenity.tail4695cd.ts.net/trmnl-solar/markup
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = Path("/var/www/venus/venus-mqtt.json")

app = FastAPI(title="TRMNL Patticus Solar (Private)")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
class SolarData(BaseModel):
    updated_ts: int = 0
    house_soc: float | None = None
    house_pv_w: float | None = None
    house_battery_w: float | None = None
    house_load_w: float | None = None
    house_grid_w: float | None = None
    shop_soc: float | None = None
    shop_pv_w: float | None = None
    shop_battery_w: float | None = None
    shop_load_w: float | None = None
    shop_grid_w: float | None = None
    total_pv_w: float | None = None
    total_load_w: float | None = None
    battery_voltage: float | None = None
    time_since_full_s: int | None = None
    source: str = "unknown"

    @property
    def fresh(self) -> bool:
        return (int(time.time()) - self.updated_ts) < 300


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_solar_data() -> SolarData:
    """Load current solar data from the local Venus MQTT bridge JSON file."""
    data: dict[str, Any] = {}
    if DATA_PATH.exists():
        try:
            data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    updated = data.get("updated", int(time.time()))

    return SolarData(
        updated_ts=int(updated),
        house_soc=_f(data.get("house_soc_pct")),
        house_pv_w=_f(data.get("house_pv_power_w")),
        house_battery_w=_f(data.get("house_battery_power_w")),
        house_load_w=_f(data.get("house_ac_output_load_w") or data.get("house_ac_input_load_w")),
        house_grid_w=_f(data.get("house_grid_power_w")),
        shop_soc=_f(data.get("shop_soc_pct")),
        shop_pv_w=_f(data.get("shop_pv_power_w")),
        shop_battery_w=_f(data.get("shop_battery_power_w")),
        shop_load_w=_f(data.get("shop_ac_output_load_w") or data.get("shop_ac_input_load_w")),
        shop_grid_w=_f(data.get("shop_grid_power_w")),
        total_pv_w=_f(data.get("total_pv_power_w")),
        total_load_w=_f(data.get("total_ac_load_w")),
        battery_voltage=_f(data.get("house_battery_voltage_v")),
        time_since_full_s=_i(data.get("house_time_since_full_s")),
        source="venus_mqtt_bridge",
    )


def _f(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _i(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def fmt_w(value: float | None) -> str:
    if value is None:
        return "--"
    if abs(value) >= 1000:
        return f"{value / 1000:.1f}kW"
    return f"{value:.0f}W"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:.0f}%"


def fmt_v(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:.1f}V"


# ---------------------------------------------------------------------------
# Markup rendering
# ---------------------------------------------------------------------------
SHARED_CSS = """
<style>
  .solar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }
  .solar-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.75; margin-bottom: 2px; }
  .solar-value { font-size: 26px; font-weight: 700; line-height: 1.1; }
  .solar-sub { font-size: 10px; opacity: 0.65; margin-top: 2px; }
  .solar-grid-in { color: #7effb2; }
  .solar-grid-out { color: #ff7a4d; }
  .solar-title { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
</style>
"""


def render(data: SolarData) -> dict[str, str]:
    house_pv = fmt_w(data.house_pv_w)
    shop_pv = fmt_w(data.shop_pv_w)
    total_pv = fmt_w(data.total_pv_w)
    total_load = fmt_w(data.total_load_w)
    house_soc = fmt_pct(data.house_soc)
    shop_soc = fmt_pct(data.shop_soc)
    battery_v = fmt_v(data.battery_voltage)
    freshness = "LIVE" if data.fresh else "STALE"
    updated_time = time.strftime("%H:%M", time.localtime(data.updated_ts))

    full = f"""
<div class="view view--full">
  <div class="layout layout--single">
    <div class="content">
      <div class="solar-title" style="margin-bottom: 10px;">Patticus Power Grid</div>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 8px;">
        <div class="solar-card"><div class="solar-label">Solar</div><div class="solar-value">{total_pv}</div><div class="solar-sub">H {house_pv} / S {shop_pv}</div></div>
        <div class="solar-card"><div class="solar-label">Load</div><div class="solar-value">{total_load}</div><div class="solar-sub">AC total</div></div>
        <div class="solar-card"><div class="solar-label">Battery</div><div class="solar-value">{house_soc}</div><div class="solar-sub">{battery_v}</div></div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
        <div class="solar-card"><div class="solar-label">House SOC</div><div class="solar-value">{house_soc}</div></div>
        <div class="solar-card"><div class="solar-label">Shop SOC</div><div class="solar-value">{shop_soc}</div></div>
      </div>
      <div class="solar-sub" style="margin-top: 6px;">{freshness} · {updated_time}</div>
    </div>
  </div>
</div>
"""

    half_h = f"""
<div class="view view--half_horizontal">
  <div class="layout layout--single">
    <div class="content">
      <div class="solar-title" style="font-size: 12px; margin-bottom: 6px;">House</div>
      <div class="solar-value" style="font-size: 32px;">{fmt_w(data.house_pv_w)}</div>
      <div class="solar-label">Solar</div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 8px;">
        <div class="solar-card"><div class="solar-value" style="font-size: 18px;">{fmt_pct(data.house_soc)}</div><div class="solar-label">SOC</div></div>
        <div class="solar-card"><div class="solar-value" style="font-size: 18px;">{fmt_w(data.house_load_w)}</div><div class="solar-label">Load</div></div>
      </div>
    </div>
  </div>
</div>
"""

    half_v = f"""
<div class="view view--half_vertical">
  <div class="layout layout--single">
    <div class="content">
      <div class="solar-title" style="font-size: 12px; margin-bottom: 6px;">Shop</div>
      <div class="solar-value" style="font-size: 32px;">{fmt_w(data.shop_pv_w)}</div>
      <div class="solar-label">Solar</div>
      <div style="margin-top: 8px;">
        <div class="solar-card"><div class="solar-value" style="font-size: 20px;">{fmt_pct(data.shop_soc)}</div><div class="solar-label">SOC</div></div>
        <div class="solar-card" style="margin-top: 6px;"><div class="solar-value" style="font-size: 20px;">{fmt_w(data.shop_load_w)}</div><div class="solar-label">Load</div></div>
      </div>
    </div>
  </div>
</div>
"""

    grid_class = "solar-grid-out" if (data.total_load_w or 0) > (data.total_pv_w or 0) else "solar-grid-in"
    quadrant = f"""
<div class="view view--quadrant">
  <div class="layout layout--quadrant" style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; height: 100%;">
    <div class="solar-card" style="border-right: 1px solid rgba(0,0,0,0.1); border-bottom: 1px solid rgba(0,0,0,0.1);">
      <div class="solar-label">Solar</div>
      <div class="solar-value">{total_pv}</div>
      <div class="solar-sub">H {house_pv}</div>
    </div>
    <div class="solar-card" style="border-bottom: 1px solid rgba(0,0,0,0.1);">
      <div class="solar-label">Load</div>
      <div class="solar-value {grid_class}">{total_load}</div>
      <div class="solar-sub">AC now</div>
    </div>
    <div class="solar-card" style="border-right: 1px solid rgba(0,0,0,0.1);">
      <div class="solar-label">House SOC</div>
      <div class="solar-value">{house_soc}</div>
      <div class="solar-sub">{battery_v}</div>
    </div>
    <div class="solar-card">
      <div class="solar-label">Shop SOC</div>
      <div class="solar-value">{shop_soc}</div>
      <div class="solar-sub">Tinker Town</div>
    </div>
  </div>
</div>
"""

    return {
        "markup": full.strip(),
        "markup_half_horizontal": half_h.strip(),
        "markup_half_vertical": half_v.strip(),
        "markup_quadrant": quadrant.strip(),
        "shared": SHARED_CSS.strip(),
    }


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h1>Patticus Solar TRMNL Plugin (Private)</h1>
    <p>Private plugin endpoints:</p>
    <ul>
      <li>POST /markup</li>
      <li>GET /health</li>
    </ul>
    <p>Data source: /var/www/venus/venus-mqtt.json</p>
    """


@app.post("/markup")
def markup(
    request: Request,
    user_uuid: str = Form(""),
    trmnl: str = Form("{}"),
    authorization: str | None = Header(None),
):
    data = load_solar_data()
    payload = render(data)
    return JSONResponse(content=payload)


@app.get("/health")
def health():
    data = load_solar_data()
    return {
        "ok": data.fresh,
        "updated_ts": data.updated_ts,
        "source": data.source,
        "house_soc": data.house_soc,
        "shop_soc": data.shop_soc,
        "total_pv_w": data.total_pv_w,
    }


# ---------------------------------------------------------------------------
# Local dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8123"))
    uvicorn.run(app, host="127.0.0.1", port=port)
