# EVOID Tutorial Plan

> ALL content in English — this is an international project
> Inspired by FastAPI's visual storytelling style
> Focus: IOP paradigm, not just syntax

---

## Phase 1: First Steps (@route)

### 1. First Steps
- Create first service with `Service()` and `@get`
- Run with `python main.py`
- Test with `curl`
- **Key insight:** Behind every decorator, an Intent is auto-created

### 2. Path Parameters
- `@get("/users/{user_id}")`
- Type conversion
- **Key insight:** Path becomes Intent name

### 3. Query Parameters
- Query string parameters
- Default values
- **Key insight:** Query params stored in Intent metadata

### 4. Request Body
- JSON body
- Pydantic models
- **Key insight:** Body data flows through Intent

### 5. Response
- Return dict
- Status codes
- **Key insight:** Handler returns result, Intent handles infrastructure

---

## Phase 2: Why IOP? (The Inspiring Part)

### 6. Why IOP? ⭐ (Like FastAPI's async page)
**Storytelling approach with emojis and visual metaphors**

**The Problem Story:**
- "Imagine you're building a web app..."
- "Every time you write a new endpoint, you have to decide: Which database? How to cache? Should I encrypt this? What priority?"
- "This is like being a chef who has to also build the kitchen, buy the groceries, and clean up — every single time you cook a meal."

**The IOP Solution:**
- "What if your data could tell the kitchen what it needs?"
- "What if a field saying 'this is a credit card number' automatically means: encrypt it, audit it, store it safely?"
- "That's IOP. Your data model IS your infrastructure policy."

**Visual Metaphors:**
- 🏗️ Traditional: You build everything from scratch each time
- 🎯 IOP: You declare intent, framework builds for you
- 🧩 Like LEGO: Snap pieces together, system handles the rest

**Code Comparison:**
```python
# Traditional: 10 lines of infrastructure per endpoint
# IOP: 1 line of intent per field
```

**The Three Levels:**
- EPHEMERAL: "I don't care if this disappears" 🗑️
- STANDARD: "Normal business data" 📊
- CRITICAL: "This must never be lost" 🔒

**Conclusion:**
- "IOP is not just a syntax change. It's a paradigm shift."
- "Your data tells the system what to do. You focus on what matters."

---

## Phase 3: Understanding the Pipeline

### 7. How Decorators Create Intents
- Show the code behind `@get("/users/{id}")`
- Show `all_intents()` after decorator
- **Key insight:** Decorator is just sugar over Intent system

### 8. The Pipeline
- Intent → Resolver → Pipeline → Processors → Result
- Default processors per level
- **Key insight:** Pipeline is just a list of function names

### 9. What is a Processor?
- Processor = pure function
- Takes Context, returns result
- **Key insight:** Processors are independent, composable

### 10. Built-in Processors
- intent_extractor, auth_checker, rate_limiter, etc.
- **Key insight:** Reuse existing processors

---

## Phase 4: Customizing Pipelines

### 11. Custom Pipelines
- `add_intent_with_pipeline()`
- Replace entire pipeline
- **Key insight:** You control execution flow

### 12. Extending Pipelines
- `before()` / `after()`
- `before_processor()` / `after_processor()`
- **Key insight:** Add logic without modifying existing code

---

## Phase 5: IOP Native Style

### 13. IOP Style Introduction
- Create Intent manually
- Create handler manually
- Register with `add_intent()`
- **Key insight:** Full control over everything

### 14. IOP vs @route
- Side-by-side comparison
- When to use which
- **Key insight:** Both are IOP, just different sugar

---

## Phase 6: @controller (For Large Projects)

### 15. @controller Introduction
- `@Controller()` and `@GET()` decorators
- Class-based routes
- **Key insight:** Organized structure for big projects

### 16. Managing Many Endpoints
- Multiple controllers
- Organized file structure
- **Key insight:** NestJS style scales better for 50+ endpoints

### 17. When to Use @controller
- Large teams
- Many endpoints
- Domain-driven design
- **Key insight:** Choose style based on project size

---

## Phase 7: Advanced Features

### 18. Parallel Execution
- `gather()` — parallel intents
- `gather_with_priority()` — priority ordering
- `IntentQueue` — priority queue
- **Key insight:** IOP + async = maximum performance

### 19. Inter-Service Communication
- `Service()` — create service
- `call()` — direct call
- `emit()` — fire-and-forget
- **Key insight:** Intent-based communication, no HTTP overhead

### 20. Plugin System
- Register custom plugins
- Load from config
- **Key insight:** Everything is a plugin

### 21. Configuration
- `evoid.toml`
- Engine selection
- `evo sync`
- **Key insight:** Config is the composition root

---

## Phase 8: Project Structure

### 22. Creating a Project
- `evo init`
- `evo service new`
- Project structure
- **Key insight:** Project = collection of services

### 23. Service Configuration
- `evoid.toml` per service
- Engine selection per service
- **Key insight:** Each service can have different engines

---

## Phase 9: Building a Complete App

### 24. REST API
- CRUD operations
- Validation
- Error handling
- **Key insight:** Combining everything learned

### 25. Authentication
- Auth processor
- Custom auth logic
- **Key insight:** Auth is just another processor

### 26. Caching
- Cache engine
- Cache strategies per intent level
- **Key insight:** Intent level determines caching strategy

### 27. Background Tasks
- Background processors
- Async execution
- **Key insight:** Processors can run in background

---

## Phase 10: Testing & Deployment

### 28. Testing
- Unit tests
- Override dependencies
- **Key insight:** Testing Intent-based systems

### 29. Production Configuration
- Production engines
- Environment variables
- **Key insight:** Config doesn't change, only engines

### 30. Deployment
- Docker
- Cloud deployment
- **Key insight:** EVOID runs anywhere Python runs

---

## Summary

```
Phase 1-2:  @route + Why IOP? (7 lessons)
Phase 3-4:  Pipeline Understanding (6 lessons)
Phase 5:    IOP Native Style (2 lessons)
Phase 6:    @controller for Large Projects (3 lessons)
Phase 7:    Advanced Features (4 lessons)
Phase 8:    Project Structure (2 lessons)
Phase 9:    Complete App (4 lessons)
Phase 10:   Testing & Deployment (3 lessons)
```

**Total: 30 lessons**
