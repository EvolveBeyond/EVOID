"""@route Example — Function-based routes, IOP underneath.

Flow:
  @get("/users/{user_id}")
      ↓
  Intent(name="GET:/users/{user_id}", level=STANDARD)  ← AUTO-CREATED
      ↓
  register(intent)
      ↓
  register_processor(intent.name, handler)
      ↓
  Ready to execute

User doesn't define Intent — decorator creates it automatically.
"""

import asyncio

from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log
from evoid.core import all_intents, all_processors


# Create service
app = Service("my-api")


# Define routes — Intent is AUTO-CREATED from path + method
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    log.info(f"Getting user {user_id}")
    return {"id": user_id, "name": f"User {user_id}"}


@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    log.info(f"Creating user: {name}")
    return {"status": "created", "user": {"name": name, "email": email}}


@app.get("/health")
async def health() -> dict:
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
    log.init("evoid-fastapi", level="INFO")
    asyncio.run(run(app, port=8000))
