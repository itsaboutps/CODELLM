# Software Architecture Design Patterns

## Introduction to Design Patterns

Design patterns are reusable solutions to commonly occurring problems in software design. They represent best practices evolved over time by experienced developers and provide a shared vocabulary for discussing architectural solutions.

## Creational Patterns

### Singleton Pattern

Ensures a class has only one instance and provides global access to it.

#### Implementation Example
```python
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        # Database connection logic
        pass
```

#### Use Cases
- Database connections
- Logging services
- Configuration managers
- Thread pools

#### Benefits and Drawbacks
**Benefits**: Controlled access, global state, lazy initialization
**Drawbacks**: Global state issues, testing difficulties, tight coupling

### Factory Method Pattern

Creates objects without specifying exact classes to create.

#### Implementation Strategy
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via credit card"

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via PayPal"

class PaymentFactory:
    @staticmethod
    def create_processor(payment_type):
        if payment_type == "credit_card":
            return CreditCardProcessor()
        elif payment_type == "paypal":
            return PayPalProcessor()
        else:
            raise ValueError("Unknown payment type")
```

#### Advantages
- Decoupling of object creation
- Easy to extend with new types
- Follows open/closed principle

### Builder Pattern

Constructs complex objects step by step.

#### Application Areas
- Building SQL queries
- Creating configuration objects
- Constructing UI components
- Assembling data structures

## Structural Patterns

### Adapter Pattern

Allows incompatible interfaces to work together.

#### Real-World Example
```python
class LegacyPrinter:
    def old_print(self, text):
        print(f"Legacy: {text}")

class ModernPrinter:
    def print(self, text):
        print(f"Modern: {text}")

class PrinterAdapter:
    def __init__(self, legacy_printer):
        self.legacy_printer = legacy_printer
    
    def print(self, text):
        self.legacy_printer.old_print(text)
```

#### Integration Scenarios
- Third-party library integration
- Legacy system modernization
- API compatibility layers
- Database driver abstraction

### Decorator Pattern

Adds new functionality to objects dynamically.

#### Implementation Approaches
- Function decorators in Python
- Wrapper classes
- Middleware patterns
- Aspect-oriented programming

#### Common Applications
- Authentication and authorization
- Logging and monitoring
- Caching mechanisms
- Rate limiting

### Facade Pattern

Provides simplified interface to complex subsystems.

#### System Integration Benefits
- Reduces coupling between clients and subsystems
- Simplifies complex interfaces
- Provides single point of access
- Encapsulates subsystem complexity

## Behavioral Patterns

### Observer Pattern

Defines one-to-many dependency between objects.

#### Event-Driven Architecture
```python
class Subject:
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self._state)
    
    def set_state(self, state):
        self._state = state
        self.notify()

class ConcreteObserver:
    def __init__(self, name):
        self.name = name
    
    def update(self, state):
        print(f"{self.name} received update: {state}")
```

#### Use Cases in Modern Applications
- Model-View architectures
- Event systems
- Reactive programming
- Publish-subscribe patterns

### Strategy Pattern

Encapsulates algorithms and makes them interchangeable.

#### Algorithm Selection
- Sorting algorithms based on data size
- Compression strategies for different file types
- Routing algorithms for different network conditions
- Pricing strategies for different customer types

### Command Pattern

Encapsulates requests as objects.

#### Benefits for System Design
- Undo/redo functionality
- Queuing and logging operations
- Macro recording and playback
- Transactional behavior

## Architectural Patterns

### Model-View-Controller (MVC)

Separates application into three interconnected components.

#### Component Responsibilities
- **Model**: Data and business logic
- **View**: User interface presentation
- **Controller**: Handles user input and coordinates Model/View

#### Advantages
- Separation of concerns
- Parallel development
- Code reusability
- Easier testing

#### Modern Variations
- Model-View-Presenter (MVP)
- Model-View-ViewModel (MVVM)
- Component-based architectures

### Repository Pattern

Encapsulates data access logic.

#### Data Access Abstraction
```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id):
        pass
    
    @abstractmethod
    def save(self, user):
        pass
    
    @abstractmethod
    def find_all(self):
        pass

class DatabaseUserRepository(UserRepository):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def find_by_id(self, user_id):
        # Database query implementation
        pass
    
    def save(self, user):
        # Database save implementation
        pass
```

#### Benefits
- Testability through mocking
- Database technology independence
- Centralized data access logic
- Query optimization opportunities

### Dependency Injection Pattern

Provides dependencies from external sources rather than creating them internally.

#### Inversion of Control Benefits
- Loose coupling between components
- Enhanced testability
- Configuration flexibility
- Easier component replacement

## Microservices Patterns

### Service Discovery

Enables services to find and communicate with each other.

#### Implementation Approaches
- Client-side discovery (Eureka)
- Server-side discovery (Load balancer)
- Service mesh (Istio, Linkerd)
- DNS-based discovery

### Circuit Breaker

Prevents cascading failures in distributed systems.

#### Failure Handling States
- **Closed**: Normal operation, requests pass through
- **Open**: Failure threshold exceeded, requests fail fast
- **Half-Open**: Testing if service has recovered

#### Implementation Considerations
- Failure threshold configuration
- Timeout settings
- Fallback mechanisms
- Monitoring and alerting

### Saga Pattern

Manages data consistency across multiple services.

#### Transaction Coordination
- **Choreography**: Each service publishes events
- **Orchestration**: Central coordinator manages flow

#### Compensation Strategies
- Semantic rollback operations
- Idempotent service operations
- Event sourcing for auditability

## Performance Patterns

### Caching Patterns

#### Cache-Aside (Lazy Loading)
```python
def get_user(user_id):
    # Check cache first
    user = cache.get(f"user:{user_id}")
    if user is None:
        # Load from database
        user = database.find_user(user_id)
        # Store in cache
        cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

#### Write-Through and Write-Behind
- **Write-Through**: Update cache synchronously with database
- **Write-Behind**: Update cache immediately, database asynchronously

#### Cache Invalidation Strategies
- Time-based expiration (TTL)
- Event-based invalidation
- Cache versioning
- Cache warming techniques

### Connection Pooling

Manages database connections efficiently.

#### Pool Configuration Parameters
- Initial pool size
- Maximum pool size
- Connection timeout
- Idle connection timeout
- Validation queries

## Security Patterns

### Authentication and Authorization

#### Token-Based Authentication
- JSON Web Tokens (JWT)
- OAuth 2.0 flows
- Session management
- Multi-factor authentication

#### Role-Based Access Control (RBAC)
- User roles and permissions
- Hierarchical role structures
- Dynamic permission evaluation
- Audit logging

### Secure Communication

#### Transport Layer Security
- TLS/SSL encryption
- Certificate management
- Mutual authentication
- Perfect forward secrecy

#### API Security Patterns
- Rate limiting
- Input validation
- SQL injection prevention
- Cross-site scripting (XSS) protection

## Testing Patterns

### Test Doubles

#### Mock Objects
Replace dependencies with controlled implementations:
```python
from unittest.mock import Mock

def test_payment_processing():
    # Create mock payment gateway
    mock_gateway = Mock()
    mock_gateway.charge.return_value = {"status": "success"}
    
    # Test the payment service
    payment_service = PaymentService(mock_gateway)
    result = payment_service.process_payment(100.0)
    
    assert result["status"] == "success"
    mock_gateway.charge.assert_called_once_with(100.0)
```

#### Stub vs Mock vs Fake
- **Stub**: Returns predefined responses
- **Mock**: Verifies interaction behavior  
- **Fake**: Working implementation with shortcuts

### Page Object Model

Encapsulates UI elements and operations for automated testing.

#### Benefits for UI Testing
- Reduces code duplication
- Improves test maintainability
- Provides abstraction layer
- Enables reusable components

## Anti-Patterns to Avoid

### Common Design Anti-Patterns

#### God Object
- Single class doing too much
- Violates single responsibility principle
- Difficult to test and maintain

#### Spaghetti Code
- Unstructured control flow
- Excessive coupling
- Poor readability

#### Copy-Paste Programming
- Code duplication
- Maintenance nightmares
- Inconsistent behavior

### Performance Anti-Patterns

#### N+1 Query Problem
- Multiple database queries in loops
- Solution: Use batch loading or joins

#### Premature Optimization
- Optimizing before identifying bottlenecks
- Focus on correct design first

## Best Practices

### Pattern Selection Guidelines

#### Consider Context
- Problem domain requirements
- Team expertise and experience
- Technology stack constraints
- Performance requirements
- Scalability needs

#### Avoid Pattern Abuse
- Don't force patterns where they don't fit
- Prefer simplicity over complexity
- Understand trade-offs
- Consider maintenance burden

### Documentation and Communication

#### Pattern Documentation
- Intent and motivation
- Structure and participants
- Collaboration diagrams
- Implementation guidelines
- Known uses and consequences

#### Team Knowledge Sharing
- Code reviews focusing on patterns
- Architecture decision records
- Pattern libraries and catalogs
- Training and mentorship

## Conclusion

Design patterns provide proven solutions to recurring design problems. However, they should be applied judiciously, considering the specific context and requirements of each project. The key is to understand the problem space thoroughly and select appropriate patterns that add value without unnecessary complexity.

### Key Takeaways

1. **Understand Before Applying**: Learn the intent and trade-offs of each pattern
2. **Context Matters**: Consider project requirements and constraints
3. **Simplicity First**: Don't over-engineer solutions
4. **Team Alignment**: Ensure shared understanding of chosen patterns
5. **Continuous Learning**: Stay updated with evolving architectural trends

---

*Guide compiled by the Software Architecture Team, 2024*