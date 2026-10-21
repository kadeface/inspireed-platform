"""返回本机局域网地址，供访客观摩二维码在回环地址下改写。"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.lan_host import detect_lan_ipv4

router = APIRouter()


class LanHostResponse(BaseModel):
    lan_host: Optional[str]


@router.get("/lan-host", response_model=LanHostResponse)
def read_lan_host() -> LanHostResponse:
    return LanHostResponse(lan_host=detect_lan_ipv4())
