# -*- coding: utf-8 -*-
"""CI-OS 端 OTP 工蜂 v3：单 issue 闭环（发码→候评→验真→落态）。
[SENDCODE]/[OTP-LOOP] issue → 发码→轮询本 issue 评论(≤9min)取 4-8 位码→登录→storage_state 工件。
[OTP] xxxxxx issue → 直接验真（旧路兼容）。真码 ::add-mask:: + 即删（PII 闸）。"""
import asyncio, glob, json, os, sys, datetime, urllib.request

import re as _re
_raw = os.environ.get("OTP_PHONE", "").strip()
_digits = _re.sub(r"\D", "", _raw)
if len(_digits) == 13 and _digits.startswith("86"): _digits = _digits[2:]
PHONE = _digits
GH = os.environ.get("GITHUB_TOKEN", "").strip()
REPO = os.environ.get("GITHUB_REPOSITORY", "")
ISSUE_N = os.environ.get("ISSUE_NUMBER", "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def now(): return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
def write_state(status, note):
    json.dump({"status": status, "note": note, "ts": now(), "worker": "cios-otp-gate-v3"},
              open("inbox/otp_gate_state.json", "w"), ensure_ascii=False, indent=1)
    print(f"STATE={status}: {note}")

def comment(body):
    if not (GH and REPO and ISSUE_N): return
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/issues/{ISSUE_N}/comments",
        data=json.dumps({"body": body}).encode(), method="POST",
        headers={"Authorization": "Bearer "+GH, "Accept": "application/vnd.github+json", "User-Agent": "otp-gate"})
    try: urllib.request.urlopen(req, timeout=15)
    except Exception as e: print("comment fail:", e)

def poll_code(max_s=540):
    import re, time
    t0 = time.time(); seen = set()
    while time.time()-t0 < max_s:
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/issues/{ISSUE_N}/comments?per_page=100",
                headers={"Authorization": "Bearer "+GH, "Accept": "application/vnd.github+json", "User-Agent": "otp-gate"})
            for c in json.load(urllib.request.urlopen(req, timeout=15)):
                if c["id"] in seen: continue
                seen.add(c["id"])
                m = re.fullmatch(r"\s*(\d{4,8})\s*", c.get("body") or "")
                if m: return m.group(1)
        except Exception as e: print("poll err:", e)
        time.sleep(10)
    return None

async def open_login(pg):
    await pg.goto("https://www.kimi.com/", wait_until="commit", timeout=90000)
    await pg.wait_for_timeout(5000)
    for sel in ["text=登录以同步历史会话", "button:has-text('登录')"]:
        try: await pg.click(sel, timeout=4000); break
        except Exception: pass
    await pg.wait_for_timeout(1500)
    await pg.get_by_placeholder("手机号").fill(PHONE)

async def ensure_agree(pg):
    """协议勾选三轨：check → label 点击 → JS 强勾 + 事件。"""
    try: await pg.check("input[type=checkbox]", timeout=2500)
    except Exception:
        try: await pg.click("label:has-text('已阅读同意')", timeout=2500)
        except Exception: pass
    await pg.evaluate("""()=>{ for (const c of document.querySelectorAll('input[type=checkbox]')) {
        if (!c.checked) { c.click(); }
        c.dispatchEvent(new Event('input',{bubbles:true})); c.dispatchEvent(new Event('change',{bubbles:true})); } }""")

async def fill_code(pg, code):
    box = pg.get_by_placeholder("验证码")
    try:
        await box.fill(code, timeout=4000); return True
    except Exception:
        # 分格验证码兜底：逐格敲
        try:
            cells = await pg.locator("input[maxlength='1']").all()
            if len(cells) >= len(code):
                for cell, ch in zip(cells, code): await cell.fill(ch)
                return True
        except Exception: pass
    return False

async def click_login(pg):
    btn = pg.locator("button", has_text="登录").last
    for _ in range(40):                       # 等按钮 enabled 至多 20s
        try:
            if await btn.is_enabled(): break
        except Exception: pass
        await pg.wait_for_timeout(500)
    await btn.click(timeout=8000)

async def shot(pg, name):
    try: await pg.screenshot(path=f"inbox/{name}.png")
    except Exception: pass

async def main():
    from playwright.async_api import async_playwright
    verify_only = None
    for a in sys.argv:
        if a.startswith("--verify-only"): verify_only = a.split("=")[-1] if "=" in a else sys.argv[sys.argv.index(a)+1]
    loop_mode = "--loop" in sys.argv
    if not PHONE: write_state("FAILED", "OTP_PHONE 未设置"); sys.exit(1)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(user_agent=UA, viewport={"width":1440,"height":900}, locale="zh-CN")
        pg = await ctx.new_page()
        await pg.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        # —— 发码段（loop 与 send 都要）——
        if loop_mode or not verify_only:
            await open_login(pg); await ensure_agree(pg)
            await pg.locator("button", has_text="发送验证码").first.click()
            await pg.wait_for_timeout(3500)
            await shot(pg, "otp_aftersend")                     # 发码后必截图（诊断面）
            body = await pg.locator("body").inner_text()
            neg = [k for k in ["滑块","安全验证","格式","错误","失败","频繁","稍候","稍后","不正确"] if k in body]
            if neg:
                write_state("BLOCKED", f"发码受阻:{neg}"); comment(f"🚧 发码受阻:{neg}——见 artifacts 截图")
                await b.close(); sys.exit(0)
            write_state("CODE_SENT", "真短信已发（v3c loop）——请在本 issue 回评 6 位码")
            comment("📨 真码已发出——请**直接在本 issue 回评 6 位数字**，CI 在线候评（≤9 分钟）。")
        # —— 取码段 ——
        code = verify_only
        if loop_mode and not code:
            code = poll_code()
            if not code:
                write_state("FAILED", "候评超时未得码"); comment("⏱ 候评超时，请重开 [SENDCODE]。"); await b.close(); sys.exit(0)
        print(f"::add-mask::{code}")
        # —— 验真段 ——
        if not loop_mode:                      # 旧路：新面板重填手机
            await open_login(pg); await ensure_agree(pg)
        ok_fill = await fill_code(pg, code)
        if not ok_fill:
            await shot(pg, "otp_fillfail"); write_state("FAILED", "验证码框填充失败（面板变体）"); await b.close(); sys.exit(0)
        try:
            await click_login(pg)
        except Exception as e:
            await shot(pg, "otp_btnfail"); write_state("FAILED", f"登录钮不可点/点击超时：{str(e)[:80]}"); await b.close(); sys.exit(0)
        await pg.wait_for_timeout(6000)
        body = await pg.locator("body").inner_text()
        ok = ("我的 Kimi" in body or "历史会话" in body) and "手机号码登录" not in body \
             and not any(k in body for k in ["验证码错误", "不正确", "已过期", "失效", "频繁"])
        if ok:
            await ctx.storage_state(path="inbox/.kimi_session.json")
            write_state("DONE", "核对成功·登录态已成（v3）")
            comment("✅ **OTP 真码大循环闭环实证**：登录态工件已成。")
        else:
            await shot(pg, "otp_fail")
            write_state("FAILED", "码错误或已过期——重开 [SENDCODE] 再来")
            comment("⚠️ 核码失败（错/过期）——重开 [SENDCODE] issue 即自动重发。")
        for f in glob.glob("inbox/otp-*.json")+glob.glob("inbox/sendcode-*.json"): os.remove(f)
        await b.close()

asyncio.run(main())
