from datetime import datetime
import asyncio
import httpx
import requests


a = httpx.get('http://api.myawesomesite.io/posts/session')
print(a)


async def test_speed(rounds=222):
	start = datetime.now()
	a = []
	async with httpx.AsyncClient() as client:
		# client=httpx
		for i in range(rounds):
			j = await client.get('http://api.myawesomesite.io/posts/async_scoped')
			a.append(j)
	end = datetime.now()
	total = end - start
	print(f"{rounds} Http requests take {total.seconds} seconds and {total.microseconds} microsecends")
	print(a)


if __name__ == "__main__":
	asyncio.run(test_speed(250))
