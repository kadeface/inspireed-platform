#!/usr/bin/env python3
"""
自学拍题多模态链路冒烟测试。

用法（在项目 backend 目录、已激活 venv 后）:
  python test_self_study_vision.py
  python test_self_study_vision.py --upload   # 额外测学生上传检查 API
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def make_test_image(path: Path) -> None:
    img = Image.new("RGB", (900, 700), "white")
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), "题目：小明有 12 个苹果，吃了 5 个，还剩几个？", fill="black")
    draw.text((40, 140), "学生作答：12 - 5 = 8", fill="blue")
    img.save(path, quality=95)


async def fetch_vision_config() -> dict:
    from app.core.database import AsyncSessionLocal
    from app.services.ai_settings import ai_settings_service

    async with AsyncSessionLocal() as db:
        config = await ai_settings_service.get_runtime_config(db)
        return {
            "base_url": config.self_study_vision.base_url,
            "model": config.self_study_vision.model,
            "max_tokens": config.self_study_vision.max_tokens,
            "temperature": config.self_study_vision.temperature,
            "api_key_configured": config.api_key_configured,
        }


async def test_vision_direct(image_path: Path, vision: dict) -> bool:
    from app.core.config import settings

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        print("❌ OPENAI_API_KEY 未配置")
        return False

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": vision["model"],
        "messages": [
            {"role": "system", "content": "你必须只返回 JSON。"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "检查这张小学数学题图片。只返回 JSON："
                            '{"accepted":true,"problem_text_preview":"...","student_work_text_preview":"..."}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            },
        ],
        "max_tokens": min(int(vision["max_tokens"]), 800),
        "temperature": float(vision["temperature"]),
    }

    url = f"{vision['base_url'].rstrip('/')}/chat/completions"
    print(f"\n🔍 直连视觉 API: {url}")
    print(f"   模型: {vision['model']}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    print(f"   HTTP {response.status_code}")
    if response.status_code != 200:
        print(f"❌ 视觉 API 失败: {response.text[:600]}")
        if "image_url" in response.text and "deepseek" in vision["base_url"]:
            print("   提示: DeepSeek Chat 不支持 image_url，请换视觉模型。")
        return False

    body = response.json()
    content = body["choices"][0]["message"]["content"]
    print(f"✅ 视觉 API 响应: {content[:400]}")
    return True


async def test_upload_api(image_path: Path) -> bool:
    base = "http://localhost:8000/api/v1"
    async with httpx.AsyncClient(timeout=60.0) as client:
        login = await client.post(
            f"{base}/auth/login",
            data={"username": "student@inspireed.com", "password": "student123"},
        )
        if login.status_code != 200:
            print(f"❌ 学生登录失败: {login.text}")
            return False
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with open(image_path, "rb") as f:
            files = {"file": ("self_study_test.jpg", f, "image/jpeg")}
            data = {"source": "upload"}
            response = await client.post(
                f"{base}/self-study/uploads/check",
                headers=headers,
                files=files,
                data=data,
            )

    print(f"\n🔍 上传检查 API: HTTP {response.status_code}")
    try:
        body = response.json()
    except Exception:
        print(f"❌ 非 JSON 响应: {response.text[:400]}")
        return False

    if response.status_code == 201:
        print("✅ 上传检查通过")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return True

    detail = body.get("detail")
    if isinstance(detail, dict):
        print(f"❌ 上传检查失败: {detail.get('detail')}")
        print(f"   error_code: {detail.get('error_code')}")
        for item in detail.get("suggestions") or []:
            print(f"   - {item}")
    else:
        print(f"❌ 上传检查失败: {body}")
    return False


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true", help="额外测试 /self-study/uploads/check")
    args = parser.parse_args()

    image_path = Path("/tmp/self_study_test.jpg")
    make_test_image(image_path)
    print(f"📷 测试图片: {image_path}")

    vision = await fetch_vision_config()
    print("\n📋 当前自学拍图视觉配置:")
    print(json.dumps(vision, ensure_ascii=False, indent=2))

    ok = await test_vision_direct(image_path, vision)
    if args.upload:
        ok = await test_upload_api(image_path) and ok

    if ok:
        print("\n🎉 测试通过。可在前端打开: http://localhost:5173/student/self-study")
        return 0

    print("\n⚠️  测试未通过。请检查:")
    print("  1. 管理后台 /admin/settings → AI 配置 → 自学拍题图像配置")
    print("  2. .env 中 OPENAI_API_KEY 必须与视觉 Base URL 对应（当前共用同一 Key）")
    print("  3. 修改 .env 或后台配置后执行 ./restart.sh")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
