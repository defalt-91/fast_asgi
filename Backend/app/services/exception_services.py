import logging

from fastapi import Request, Response, responses
from slowapi.errors import RateLimitExceeded


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
	"""
	Build a simple JSON response that includes the details of the rate limit
	that was hit. If no limit is hit, the countdown is added to headers.
	"""
	response = responses.JSONResponse(
		{"error": f"Rate limit exceeded: {exc.detail}"}, status_code=429
	)
	a = logging.Logger(level=4, name='rate limiter')
	a.info(request.scope['state']['view_rate_limit'])
	a.log(level=3, msg=f'logging ::: {request.state.view_rate_limit}')
	response = request.app.state.limiter._inject_headers(
		response, request.state.view_rate_limit
	)
	return response
