from fastapi import Query
from typing import Tuple

from core.base_settings import settings


async def pagination(
	page: int = Query(
		default=1, ge=1, title='Page number',
		description='Integer type for page number'
	),
	per_page: int = Query(
		default=5, title='items per page',
		description='integer type, numbers of each page posts'
	)
) -> Tuple[int, int]:
	skip = (page - 1) * per_page
	limit = per_page
	
	return skip, limit


class Pagination:
	def __init__(self, max_limit: int = 50):
		self.max_limit = max_limit
	
	def __call__(
		self,
		page: int = Query(
			default=1, ge=1,
			title='Page number', description='Integer type for page number'
		),
		per_page: int = Query(
			default=5, title='items per page',
			description='integer type, numbers of each page items'
		)
	) -> Tuple[int, int]:
		skip = (page - 1) * per_page
		limit = min(self.max_limit, per_page)
		return skip, limit
	
	async def page_size(
		self,
		page: int = Query(
			default=1, ge=1,
			title='Page number', description='Integer type for page number'
		),
		size: int = Query(
			default=5, title='items per page',
			description='integer type, numbers of each page items'
		)
	) -> Tuple[int, int]:
		skip = (page - 1) * size
		limit = min(self.max_limit, size)
		return skip, limit


paginator = Pagination(max_limit=settings.MAXIMUM_ITEMS_PER_PAGE)
