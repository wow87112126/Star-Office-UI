#!/usr/bin/env python3
"""
海辛办公室 - Agent 状态主动推送脚本

用法：
1. 填入下面的 JOIN_KEY（你从海辛那里拿到的一次性 join key）
2. 填入 AGENT_NAME（你想要在办公室里显示的名字）
3. 运行：python office-agent-push.py
4. 脚本会自动先 join（首次运行），然后每 30s 向海辛办公室推送一次你的当前状态
"""

import json
import os
import time
import sys
from datetime import datetime


def log(msg):
    """Best-effort logging that won't crash on Windows console encodings."""
    try:
        print(msg)
    except UnicodeEncodeError:
        safe = str(msg).encode("ascii", errors="ignore").decode("ascii", errors="ignore")
        print(safe)

# === 你需要填入的信息 ===
# 现在支持两种方式：
# 1) 直接改下面常量
# 2) 用环境变量覆盖（推荐，方便本地常驻/半自动化）
#    - OFFICE_JOIN_KEY
#    - OFFICE_AGENT_NAME
#    - OFFICE_URL
JOIN_KEY = os.environ.get("OFFICE_JOIN_KEY", "").strip()   # 必填：你的一次性 join key
AGENT_NAME = os.environ.get("OFFICE_AGENT_NAME", "").strip() # 必填：你在办公室里的名字
OFFICE_URL = os.environ.get("OFFICE_URL", "https://office.hyacinth.im").strip().rstrip("/")  # 海辛办公室地址（一般不用改）

# === 推送配置 ===
PUSH_INTERVAL_SECONDS = 15  # 每隔多少秒推送一次（更实时）
STATUS_ENDPOINT = "/status"
JOIN_ENDPOINT = "/join-agent"
PUSH_ENDPOINT = "/agent-push"
LEAVE_ENDPOINT = "/leave-agent"
MAIN_PUSH_ENDPOINT = "/main-agent-push"
SYNC_MAIN = os.environ.get("OFFICE_SYNC_MAIN", "0") in {"1", "true", "TRUE", "yes", "YES"}

# 自动状态守护：当本地状态文件不存在或长期不更新时，自动回 idle，避免“假工作中”
STALE_STATE_TTL_SECONDS = int(os.environ.get("OFFICE_STALE_STATE_TTL", "600"))

# 本地状态存储（记住上次 join 拿到的 agentId）
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "office-agent-state.json")

# 优先读取本机 OpenClaw 工作区的状态文件（更贴合 AGENTS.md 的工作流）
# 支持自动发现，减少对方手动配置成本，且避免硬编码绝对路径：
# - 优先使用环境变量 OPENCLAW_HOME / OPENCLAW_WORKSPACE_DIR
# - 其次使用当前用户 HOME/.openclaw
# - 再回落到当前工作目录与脚本所在目录
OPENCLAW_HOME = os.environ.get("OPENCLAW_HOME") or os.path.join(os.path.expanduser("~"), ".openclaw")
OPENCLAW_WORKSPACE_DIR = os.environ.get("OPENCLAW_WORKSPACE_DIR") or os.path.join(OPENCLAW_HOME, "workspace")

DEFAULT_STATE_CANDIDATES = [
    os.path.join(OPENCLAW_WORKSPACE_DIR, "star-office-ui", "state.json"),
    os.path.join(OPENCLAW_WORKSPACE_DIR, "state.json"),
    "/root/.openclaw/workspace/Star-Office-UI/state.json",  # 当前仓库（大小写精确）
    "/root/.openclaw/workspace/star-office-ui/state.json",  # 历史/兼容路径
    "/root/.openclaw/workspace/state.json",
    os.path.join(os.getcwd(), "state.json"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json"),
]

# 如果对方本地 /status 需要鉴权，可在这里填写 token（或通过环境变量 OFFICE_LOCAL_STATUS_TOKEN）
LOCAL_STATUS_TOKEN = os.environ.get("OFFICE_LOCAL_STATUS_TOKEN", "")
LOCAL_STATUS_URL = os.environ.get("OFFICE_LOCAL_STATUS_URL", "http://127.0.0.1:19000/status")
# 可选：直接指定本地状态文件路径（最简单方案：绕过 /status 鉴权）
LOCAL_STATE_FILE = os.environ.get("OFFICE_LOCAL_STATE_FILE", "")
VERBOSE = os.environ.get("OFFICE_VERBOSE", "0") in {"1", "true", "TRUE", "yes", "YES"}


def load_local_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "agentId": None,
        "joined": False,
        "joinKey": JOIN_KEY,
        "agentName": AGENT_NAME
    }


def save_local_state(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_state(s):
    """兼容不同本地状态词，并映射到办公室识别状态。"""
    s = (s or "").strip().lower()
    if s in {"writing", "researching", "executing", "syncing", "error", "idle"}:
        return s
    if s in {"working", "busy", "write"}:
        return "writing"
    if s in {"run", "running", "execute", "exec"}:
        return "executing"
    if s in {"research", "search"}:
        return "researching"
    if s in {"sync"}:
        return "syncing"
    return "idle"


def map_detail_to_state(detail, fallback_state="idle"):
    """当只有 detail 时，用关键词推断状态（贴近 AGENTS.md 的办公区逻辑）。"""
    d = (detail or "").lower()
    if any(k in d for k in ["报错", "error", "bug", "异常", "报警"]):
        return "error"
    if any(k in d for k in ["同步", "sync", "备份"]):
        return "syncing"
    if any(k in d for k in ["调研", "research", "搜索", "查资料"]):
        return "researching"
    if any(k in d for k in ["执行", "run", "推进", "处理任务", "工作中", "writing"]):
        return "writing"
    if any(k in d for k in ["待命", "休息", "idle", "完成", "done"]):
        return "idle"
    return fallback_state


def _state_age_seconds(data):
    try:
        ts = (data or {}).get("updated_at")
        if not ts:
            return None
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            from datetime import timezone
            return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
        return (datetime.now() - dt).total_seconds()
    except Exception:
        return None


def fetch_local_status():
    """读取本地状态：
    1) 优先 state.json（符合 AGENTS.md：任务前切 writing，完成后切 idle）
    2) 其次尝试本地 HTTP /status
    3) 最后 fallback idle

    额外防抖：如果本地状态更新时间超过 STALE_STATE_TTL_SECONDS，自动视为 idle。
    """
    # 1) 读本地 state.json（优先读取显式指定路径，其次自动发现）
    candidate_files = []
    if LOCAL_STATE_FILE:
        candidate_files.append(LOCAL_STATE_FILE)
    for fp in DEFAULT_STATE_CANDIDATES:
        if fp not in candidate_files:
            candidate_files.append(fp)

    for fp in candidate_files:
        try:
            if fp and os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # 只接受“状态文件”结构；避免误把 office-agent-state.json（仅缓存 agentId）当状态源
                    if not isinstance(data, dict):
                        continue
                    has_state = "state" in data
                    has_detail = "detail" in data
                    if (not has_state) and (not has_detail):
                        continue

                    state = normalize_state(data.get("state", "idle"))
                    detail = data.get("detail", "") or ""
                    # detail 兜底纠偏，确保“工作/休息/报警”能正确落区
                    state = map_detail_to_state(detail, fallback_state=state)

                    # 防止状态文件久未更新仍停留在 working 态
                    age = _state_age_seconds(data)
                    if age is not None and age > STALE_STATE_TTL_SECONDS:
                        state = "idle"
                        detail = f"本地状态超过{STALE_STATE_TTL_SECONDS}s未更新，自动回待命"

                    if VERBOSE:
                        log(f"[status-source:file] path={fp} state={state} detail={detail[:60]}")
                    return {"state": state, "detail": detail}
        except Exception:
            pass

    # 2) 尝试本地 /status（可能需要鉴权）
    try:
        import requests
        headers = {}
        if LOCAL_STATUS_TOKEN:
            headers["Authorization"] = f"Bearer {LOCAL_STATUS_TOKEN}"
        r = requests.get(LOCAL_STATUS_URL, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            state = normalize_state(data.get("state", "idle"))
            detail = data.get("detail", "") or ""
            state = map_detail_to_state(detail, fallback_state=state)

            age = _state_age_seconds(data)
            if age is not None and age > STALE_STATE_TTL_SECONDS:
                state = "idle"
                detail = f"本地/status 超过{STALE_STATE_TTL_SECONDS}s未更新，自动回待命"

            if VERBOSE:
                log(f"[status-source:http] url={LOCAL_STATUS_URL} state={state} detail={detail[:60]}")
            return {"state": state, "detail": detail}
        # 如果 401，说明需要 token
        if r.status_code == 401:
            return {"state": "idle", "detail": "本地/status需要鉴权（401），请设置 OFFICE_LOCAL_STATUS_TOKEN"}
    except Exception:
        pass

    # 3) 默认 fallback
    if VERBOSE:
        log("[status-source:fallback] state=idle detail=待命中")
    return {"state": "idle", "detail": "待命中"}


def do_join(local):
    import requests
    payload = {
        "name": local.get("agentName", AGENT_NAME),
        "joinKey": local.get("joinKey", JOIN_KEY),
        "state": "idle",
        "detail": "刚刚加入"
    }
    r = requests.post(f"{OFFICE_URL}{JOIN_ENDPOINT}", json=payload, timeout=10)
    if r.status_code in (200, 201):
        data = r.json()
        if data.get("ok"):
            local["joined"] = True
            local["agentId"] = data.get("agentId")
            save_local_state(local)
            log(f"OK joined office, agentId={local['agentId']}")
            return True
    log(f"JOIN failed: {r.text}")
    return False


def do_leave(local):
    import requests
    agent_id = (local.get("agentId") or "").strip()
    if not agent_id:
        local["joined"] = False
        local["agentId"] = None
        save_local_state(local)
        return True

    payload = {
        "agentId": agent_id,
        "name": local.get("agentName", AGENT_NAME),
    }
    r = requests.post(f"{OFFICE_URL}{LEAVE_ENDPOINT}", json=payload, timeout=10)
    if r.status_code in (200, 201):
        try:
            data = r.json()
            if data.get("ok"):
                log(f"OK left office, agentId={agent_id}")
        except Exception:
            pass
        local["joined"] = False
        local["agentId"] = None
        save_local_state(local)
        return True

    log(f"WARN leave failed: {r.text}")
    return False


def do_push(local, status_data):
    import requests
    if SYNC_MAIN:
        main_payload = {
            "state": status_data.get("state", "idle"),
            "detail": status_data.get("detail", ""),
            "name": local.get("agentName", AGENT_NAME),
        }
        r_main = requests.post(f"{OFFICE_URL}{MAIN_PUSH_ENDPOINT}", json=main_payload, timeout=10)
        if r_main.status_code not in (200, 201):
            log(f"WARN main push failed: {r_main.text}")
            return False
        try:
            main_data = r_main.json()
            if main_data.get("ok"):
                log(f"OK synced main anchor, area={main_data.get('area', 'breakroom')}")
                return True
        except Exception:
            pass
        return True

    payload = {
        "agentId": local.get("agentId"),
        "joinKey": local.get("joinKey", JOIN_KEY),
        "state": status_data.get("state", "idle"),
        "detail": status_data.get("detail", ""),
        "name": local.get("agentName", AGENT_NAME)
    }
    r = requests.post(f"{OFFICE_URL}{PUSH_ENDPOINT}", json=payload, timeout=10)
    if r.status_code in (200, 201):
        data = r.json()
        if data.get("ok"):
            area = data.get("area", "breakroom")
            log(f"OK pushed status, area={area}")
            return True

    # 403/404：拒绝/移除 → 停止推送
    if r.status_code in (403, 404):
        msg = ""
        try:
            msg = (r.json() or {}).get("msg", "")
        except Exception:
            msg = r.text
        log(f"WARN rejected/removed ({r.status_code}), stop pushing: {msg}")
        local["joined"] = False
        local["agentId"] = None
        save_local_state(local)
        sys.exit(1)

    log(f"WARN push failed: {r.text}")
    return False


def main():
    local = load_local_state()

    # Startup hint for state source and URL (helps with port/state issues, e.g. issue #31)
    if LOCAL_STATE_FILE:
        log(f"State file: {LOCAL_STATE_FILE}")
    else:
        first_existing = next((p for p in DEFAULT_STATE_CANDIDATES if p and os.path.exists(p)), None)
        if first_existing:
            log(f"State file (auto): {first_existing}")
        else:
            log("State file: auto-discover (set OFFICE_LOCAL_STATE_FILE if state not found)")
    log(f"Local status URL: {LOCAL_STATUS_URL} (set OFFICE_LOCAL_STATUS_URL if backend uses another port)")

    # 先确认配置是否齐全
    if not JOIN_KEY or not AGENT_NAME:
        log("Please configure JOIN_KEY and AGENT_NAME first")
        log("  Option A: edit script constants")
        log("  Option B (recommended): set OFFICE_JOIN_KEY / OFFICE_AGENT_NAME / OFFICE_URL")
        sys.exit(1)

    # 主锚点投影模式：只同步 main anchor，不再额外挂一个 joined 访客
    if SYNC_MAIN:
        if local.get("joined") or local.get("agentId"):
            do_leave(local)
        local["joined"] = False
        local["agentId"] = None
        save_local_state(local)
    else:
        # 如果之前没 join，先 join
        if not local.get("joined") or not local.get("agentId"):
            ok = do_join(local)
            if not ok:
                sys.exit(1)

    # 持续推送
    log(f"Bridge loop started, interval={PUSH_INTERVAL_SECONDS}s")
    log("State mapping: active->workspace; idle/done->breakroom; error->bug area")
    if SYNC_MAIN:
        log("Main anchor projection: enabled (main-only mode, no joined guest)")
    log("If local /status returns 401, set OFFICE_LOCAL_STATUS_TOKEN or OFFICE_LOCAL_STATUS_URL")
    try:
        while True:
            try:
                status_data = fetch_local_status()
                do_push(local, status_data)
            except Exception as e:
                log(f"WARN push exception: {e}")
            time.sleep(PUSH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log("Bridge stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
