#!/usr/bin/env python
"""Quick test of mock service."""
import asyncio
from app.core.service import CatalogServiceMock

async def test():
    service = CatalogServiceMock()
    try:
        result = await service.get_catalog_items_paginated(10, 0)
        print(f'Success: {result.total_items} items')
        print(f'First item: {result.data[0].name if result.data else "none"}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test())
