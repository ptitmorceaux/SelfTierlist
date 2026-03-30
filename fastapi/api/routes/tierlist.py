from copy import deepcopy

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.jwt import jwt_required
from db.session import get_db
from models.tierlist import Tierlist
from models.user import User
from schemas.tierlist import TierlistCreate, TierlistRead, TierlistUpdate

router = APIRouter(tags=["Tierlist"])


def _flatten_to_blank(data: dict) -> dict:
    normalized = deepcopy(data)
    tiers = normalized.get("tiers", [])
    items = []
    for tier in tiers:
        items.extend(tier.get("items", []))

    normalized["tiers"] = [{"id": 0, "name": "_blank", "color": "#FFFFFF", "items": items}]
    normalized["order"] = [0]
    return normalized


@router.post("/tierlist", response_model=dict, status_code=201)
async def create_tierlist(payload: TierlistCreate, user_jwt=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    if payload.user_id != user_jwt["user_id"]:
        raise HTTPException(status_code=403, detail="Cannot create tierlist for another user")

    tierlist = Tierlist(
        user_id=payload.user_id,
        name=payload.name,
        description=payload.description,
        data=payload.data,
        is_private=payload.is_private,
    )
    db.add(tierlist)
    await db.commit()
    await db.refresh(tierlist)

    return {"status": 201, "data": TierlistRead.model_validate(tierlist).model_dump()}


@router.get("/tierlist", response_model=dict)
async def list_tierlists(user_jwt=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    stmt = select(Tierlist).where(
        or_(Tierlist.user_id == user_jwt["user_id"], Tierlist.is_private.is_(False))
    )
    rows = (await db.execute(stmt)).scalars().all()
    return {
        "status": 200,
        "data": [TierlistRead.model_validate(row).model_dump() for row in rows],
    }


@router.get("/tierlist/{tierlist_id}", response_model=dict)
async def get_tierlist(tierlist_id: int, user_jwt=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    tierlist = (await db.execute(select(Tierlist).where(Tierlist.id == tierlist_id))).scalar_one_or_none()
    if not tierlist:
        raise HTTPException(status_code=404, detail="Tierlist not found")

    if tierlist.is_private and tierlist.user_id != user_jwt["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return {"status": 200, "data": TierlistRead.model_validate(tierlist).model_dump()}


@router.put("/tierlist/{tierlist_id}", response_model=dict)
async def update_tierlist(
    tierlist_id: int,
    payload: TierlistUpdate,
    user_jwt=Depends(jwt_required),
    db: AsyncSession = Depends(get_db),
):
    tierlist = (await db.execute(select(Tierlist).where(Tierlist.id == tierlist_id))).scalar_one_or_none()
    if not tierlist:
        raise HTTPException(status_code=404, detail="Tierlist not found")

    user = (await db.execute(select(User).where(User.id == user_jwt["user_id"]))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if tierlist.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tierlist, key, value)

    await db.commit()
    await db.refresh(tierlist)
    return {"status": 200, "data": TierlistRead.model_validate(tierlist).model_dump()}


@router.delete("/tierlist/{tierlist_id}", response_model=dict)
async def delete_tierlist(tierlist_id: int, user_jwt=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    tierlist = (await db.execute(select(Tierlist).where(Tierlist.id == tierlist_id))).scalar_one_or_none()
    if not tierlist:
        raise HTTPException(status_code=404, detail="Tierlist not found")

    user = (await db.execute(select(User).where(User.id == user_jwt["user_id"]))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if tierlist.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    await db.delete(tierlist)
    await db.commit()
    return {"status": 200, "message": "Tierlist deleted successfully"}


@router.post("/tierlist/duplicate/{tierlist_id}", response_model=dict, status_code=201)
async def duplicate_tierlist(
    tierlist_id: int,
    maintain_order: int = Query(default=1, ge=0, le=1),
    user_jwt=Depends(jwt_required),
    db: AsyncSession = Depends(get_db),
):
    source = (await db.execute(select(Tierlist).where(Tierlist.id == tierlist_id))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Tierlist not found")

    if source.is_private and source.user_id != user_jwt["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    data = deepcopy(source.data)
    if maintain_order == 0:
        data = _flatten_to_blank(data)

    duplicated = Tierlist(
        user_id=user_jwt["user_id"],
        name=f"{source.name} (copy)",
        description=source.description,
        data=data,
        is_private=True,
    )
    db.add(duplicated)
    await db.commit()
    await db.refresh(duplicated)

    return {"status": 201, "data": TierlistRead.model_validate(duplicated).model_dump()}
