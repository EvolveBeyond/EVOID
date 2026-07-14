"""@controller Example — Class-based routes, IOP underneath.

Flow:
  @Controller("/users")
      ↓
  @GET("/{user_id}")
      ↓
  Intent(name="GET:/users/{user_id}", level=STANDARD)  ← AUTO-CREATED
      ↓
  register(intent)
      ↓
  register_processor(intent.name, handler)
      ↓
  Ready to execute

User doesn't define Intent — decorators create them automatically.
"""

import asyncio

from evoid.web.controller import Service, Controller, GET, POST, run
from evoid.engines.logger import loguru as log
from evoid.core import all_intents, all_processors


# Create service
app = Service("my-api")


# Define controller — Intents AUTO-CREATED for each route
@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        log.info(f"Getting user {user_id}")
        return {"id": user_id, "name": f"User {user_id}"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        log.info(f"Creating user: {name}")
        return {"status": "created", "user": {"name": name, "email": email}}


@Controller("/health")
class HealthController:
    @GET("/")
    async def health(self) -> dict:
        return {"status": "healthy"}


# Show what was registered
print("Registered Intents:")
for name, intent in all_intents().items():
    print(f"  {name} [{intent.level.value}]")

print("\nRegistered Processors:")
for name in all_processors():
    print(f"  {name}")


# Run
if __name__ == "__main__":
    log.init("evoid-nestjs", level="INFO")
    asyncio.run(run(app, port=8000))
