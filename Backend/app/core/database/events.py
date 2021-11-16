# from sqlalchemy import text
# from sqlalchemy.engine import Engine
# from sqlalchemy import event
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Session
# from .session import async_engine
#
#
# # connect event on instance of Engine
# @event.listens_for(async_engine.sync_engine, "connect")
# def my_on_connect(dbapi_con, connection_record):
# 	print("New DBAPI connection:", dbapi_con)
# 	cursor = dbapi_con.cursor()
#
# 	# sync style API use for adapted DBAPI connection / cursor
# 	cursor.execute("select 'execute from event'")
# 	print(cursor.fetchone()[0])
#
#
# @event.listens_for(Engine, "connect")
# def my_on_connect(dbapi_con, connection_record):
# 	print("New DBAPI connection:", dbapi_con)
# 	cursor = dbapi_con.cursor()
#
# 	# sync style API use for adapted DBAPI connection / cursor
# 	cursor.execute("select 'execute from event'")
# 	print("cursor.fetchone()[0]")
#
#
# #
# #
# # before_execute event on all Engine instances
# @event.listens_for(Engine, "before_execute")
# def my_before_execute(conn, clauseelement, multiparams, params, execution_options):
# 	print("before engine execute!")
#
# ## ORM events ##
#
# session = AsyncSession(async_engine)
#
#
# # before_commit event on instance of Session
# @event.listens_for(session.sync_session_class, "before_commit")
# def my_before_commit(session):
#     print("before commit!")
#
#     # sync style API use on Session
#     connection = session.connection()
#
#     # sync style API use on Connection
#     result = connection.execute(text("select 'execute from event'"))
#     print(result.first())
#
#
# # after_commit event on all Session instances
# @event.listens_for(Session, "after_commit")
# def my_after_commit(session):
#     print("Session after commit!")
#
#
# @event.listens_for(session.sync_session_class, "after_commit")
# def my_after_commit2(session):
#     print("session.sync_session after_commit")
#
#
# async def go():
# 	await session.execute(text("select 1"))
# 	await session.commit()
#
# 	await session.close()
# 	await async_engine.dispose()
#
#
# # asyncio.run(go())
