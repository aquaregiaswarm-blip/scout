"""Portfolio API endpoints."""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.database import get_db
from app.db import tables
from app.models.portfolio import (
    PortfolioItemCreate,
    PortfolioItemUpdate,
    PortfolioItemResponse,
    PortfolioBulkImport,
)

logger = structlog.get_logger()
router = APIRouter()


def _item_to_response(item: tables.PortfolioItem) -> PortfolioItemResponse:
    """Convert ORM item to response model."""
    return PortfolioItemResponse(
        id=item.id,
        team_id=item.team_id,
        vendor_name=item.vendor_name,
        partnership_level=item.partnership_level,
        capabilities=item.capabilities,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[PortfolioItemResponse])
async def list_portfolio(
    db: AsyncSession = Depends(get_db),
):
    """List all portfolio items for the current team."""
    # Placeholder team_id - will use auth
    team_id = "default-team"

    result = await db.execute(
        select(tables.PortfolioItem)
        .where(tables.PortfolioItem.team_id == team_id)
        .order_by(tables.PortfolioItem.vendor_name)
    )
    items = result.scalars().all()

    return [_item_to_response(i) for i in items]


@router.post("", response_model=PortfolioItemResponse)
async def create_portfolio_item(
    request: PortfolioItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new portfolio item."""
    # Placeholder team_id - will use auth
    team_id = "default-team"

    item = tables.PortfolioItem(
        id=str(uuid.uuid4()),
        team_id=team_id,
        vendor_name=request.vendor_name,
        partnership_level=request.partnership_level,
        capabilities=request.capabilities,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return _item_to_response(item)


@router.put("/{item_id}", response_model=PortfolioItemResponse)
async def update_portfolio_item(
    item_id: str,
    request: PortfolioItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a portfolio item."""
    result = await db.execute(
        select(tables.PortfolioItem).where(tables.PortfolioItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    # Update fields if provided
    if request.vendor_name is not None:
        item.vendor_name = request.vendor_name
    if request.partnership_level is not None:
        item.partnership_level = request.partnership_level
    if request.capabilities is not None:
        item.capabilities = request.capabilities

    item.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)

    return _item_to_response(item)


@router.delete("/{item_id}")
async def delete_portfolio_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a portfolio item."""
    result = await db.execute(
        select(tables.PortfolioItem).where(tables.PortfolioItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    await db.delete(item)
    await db.commit()

    return {"status": "deleted"}


@router.post("/bulk", response_model=list[PortfolioItemResponse])
async def bulk_import_portfolio(
    request: PortfolioBulkImport,
    db: AsyncSession = Depends(get_db),
):
    """Bulk import portfolio items."""
    # Placeholder team_id - will use auth
    team_id = "default-team"

    created_items = []
    for item_data in request.items:
        item = tables.PortfolioItem(
            id=str(uuid.uuid4()),
            team_id=team_id,
            vendor_name=item_data.vendor_name,
            partnership_level=item_data.partnership_level,
            capabilities=item_data.capabilities,
        )
        db.add(item)
        created_items.append(item)

    await db.commit()

    # Refresh all items
    for item in created_items:
        await db.refresh(item)

    return [_item_to_response(i) for i in created_items]
