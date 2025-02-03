import asyncio

from databases_sync	import DatabaseSync


async def sync_pipeline():
	databases_sync_instance =  DatabaseSync()
	await databases_sync_instance.sync_databases()

if __name__ == "__main__":
	asyncio.run(sync_pipeline())
