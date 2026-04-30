import asyncio
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl

async def main():
    PostgresConnection.init_pool()
    repo = TeacherRepositoryImpl()
    try:
        metrics = await repo.get_teacher_metrics(1)
        print("Metrics:", metrics)
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
