# @controller — For Large Projects

When your project grows to 50+ endpoints, organization becomes critical. @controller syntax provides the structure you need.

## The Challenge 😰

With @route, you might end up with:

```python
# main.py — 500 lines! 😱
@get("/users")
async def list_users(): ...

@get("/users/{id}")
async def get_user(id): ...

@post("/users")
async def create_user(data): ...

@put("/users/{id}")
async def update_user(id, data): ...

@delete("/users/{id}")
async def delete_user(id): ...

@get("/orders")
async def list_orders(): ...

@get("/orders/{id}")
async def get_order(id): ...

# ... 43 more endpoints 😱
```

**One file. 500 lines. Hard to navigate.** 😰

## The NestJS Solution 🎯

Organize by **domain** using Controllers:

```python
# users.py — Just user-related endpoints
from evoid.web.controller import Controller, GET, POST, PUT, DELETE

@Controller("/users")
class UserController:
    @GET("/")
    async def list_users(self): ...

    @GET("/{id}")
    async def get_user(self, id): ...

    @POST("/")
    async def create_user(self, data): ...

    @PUT("/{id}")
    async def update_user(self, id, data): ...

    @DELETE("/{id}")
    async def delete_user(self, id): ...
```

```python
# orders.py — Just order-related endpoints
from evoid.web.controller import Controller, GET, POST

@Controller("/orders")
class OrderController:
    @GET("/")
    async def list_orders(self): ...

    @GET("/{id}")
    async def get_order(self, id): ...

    @POST("/")
    async def create_order(self, data): ...
```

```python
# main.py — Clean and simple
from evoid.web.controller import Service
from users import UserController
from orders import OrderController

app = Service("my-api")
```

**One file per domain. 50 lines each. Easy to navigate.** ✅

## Real-World Example 🏢

Let's build a complete e-commerce API with NestJS style:

### Project Structure 📁

```
my-api/
├── main.py
├── users/
│   ├── __init__.py
│   └── controller.py
├── products/
│   ├── __init__.py
│   └── controller.py
├── orders/
│   ├── __init__.py
│   └── controller.py
├── payments/
│   ├── __init__.py
│   └── controller.py
└── shared/
    ├── __init__.py
    └── models.py
```

### Users Controller 👤

```python
# users/controller.py
from evoid.web.controller import Controller, GET, POST, PUT, DELETE

@Controller("/users")
class UserController:
    @GET("/")
    async def list_users(self) -> dict:
        """List all users."""
        return {"users": []}

    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        """Get user by ID."""
        return {"id": user_id, "name": f"User {user_id}"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        """Create a new user."""
        return {"status": "created", "user": {"name": name, "email": email}}

    @PUT("/{user_id}")
    async def update_user(self, user_id: int, name: str = None) -> dict:
        """Update a user."""
        return {"status": "updated", "user_id": user_id}

    @DELETE("/{user_id}")
    async def delete_user(self, user_id: int) -> dict:
        """Delete a user."""
        return {"status": "deleted", "user_id": user_id}
```

### Products Controller 📦

```python
# products/controller.py
from evoid.web.controller import Controller, GET, POST, PUT, DELETE

@Controller("/products")
class ProductController:
    @GET("/")
    async def list_products(self) -> dict:
        return {"products": []}

    @GET("/{product_id}")
    async def get_product(self, product_id: int) -> dict:
        return {"id": product_id, "name": f"Product {product_id}"}

    @POST("/")
    async def create_product(self, name: str, price: float) -> dict:
        return {"status": "created", "product": {"name": name, "price": price}}

    @PUT("/{product_id}")
    async def update_product(self, product_id: int, name: str = None) -> dict:
        return {"status": "updated", "product_id": product_id}

    @DELETE("/{product_id}")
    async def delete_product(self, product_id: int) -> dict:
        return {"status": "deleted", "product_id": product_id}
```

### Orders Controller 🛒

```python
# orders/controller.py
from evoid.web.controller import Controller, GET, POST

@Controller("/orders")
class OrderController:
    @GET("/")
    async def list_orders(self) -> dict:
        return {"orders": []}

    @GET("/{order_id}")
    async def get_order(self, order_id: int) -> dict:
        return {"id": order_id, "status": "pending"}

    @POST("/")
    async def create_order(self, user_id: int, product_id: int) -> dict:
        return {"status": "created", "order": {"user_id": user_id, "product_id": product_id}}
```

### Main File 🚀

```python
# main.py
from evoid.web.controller import Service, run
from users.controller import UserController
from products.controller import ProductController
from orders.controller import OrderController

app = Service("ecommerce-api")

import asyncio
asyncio.run(run(app, port=8000))
```

## @controller Benefits ✅

| Benefit | Description |
|---------|-------------|
| 📁 **Organization** | One controller per domain |
| 🔍 **Navigation** | Easy to find endpoints |
| 👥 **Teamwork** | Multiple devs can work on different controllers |
| 🧪 **Testing** | Test each controller independently |
| 📈 **Scalability** | Add new controllers without touching existing code |
| 🎯 **Clear Intent** | Each controller has clear responsibility |

## When to Use @controller 🤔

| Scenario | Recommended Style |
|----------|-------------------|
| < 10 endpoints | @route ✅ |
| 10-30 endpoints | Either works ✅ |
| 30-50 endpoints | @controller recommended ✅ |
| 50+ endpoints | @controller strongly recommended ✅ |
| Multiple domains | @controller ✅ |
| Large team | @controller ✅ |

## What's Next?

Now that you understand both styles, let's learn about [parallel execution](parallel.md) to make your APIs even faster.
