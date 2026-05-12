---
tags: [javascript, foundations]
aliases: ["Prototypes", "JS Objects"]
status: stable
updated: 2026-04-26
---

# Objects, Prototypes, and Classes

> [!summary] Model
> Objects delegate property lookups through a prototype chain. `class` is syntactic sugar over prototypes. Master JavaScript's prototypal inheritance to write maintainable object-oriented code.

## Table of Contents

1. [Object Fundamentals](#object-fundamentals)
2. [Prototype Chain](#prototype-chain)
3. [Inheritance Patterns](#inheritance-patterns)
4. [ES6 Classes](#es6-classes)
5. [this Binding](#this-binding)
6. [Property Descriptors](#property-descriptors)
7. [Property Enumeration](#property-enumeration)
8. [Object Creation Patterns](#object-creation-patterns)
9. [Common Pitfalls](#common-pitfalls)
10. [Best Practices](#best-practices)
11. [Interview Questions](#interview-questions)

---

## Object Fundamentals

Objects are collections of properties (key-value pairs) and the fundamental building block of JavaScript.

### Creating Objects

#### 1. Object Literal (Most Common)

```js
const user = {
  name: 'Alice',
  age: 30,
  email: 'alice@example.com'
};
```

#### 2. Object Constructor

```js
const user = new Object();
user.name = 'Alice';
user.age = 30;
```

#### 3. Object.create()

```js
const proto = { kind: 'user' };
const user = Object.create(proto);
user.name = 'Alice';

console.log(user.kind); // 'user' (from prototype)
```

#### 4. Constructor Function

```js
function User(name, age) {
  this.name = name;
  this.age = age;
}

const user = new User('Alice', 30);
```

#### 5. ES6 Class

```js
class User {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
}

const user = new User('Alice', 30);
```

### Property Access

```js
const obj = { name: 'Alice', age: 30 };

// Dot notation
obj.name;           // 'Alice'

// Bracket notation (allows dynamic/invalid identifiers)
obj['name'];        // 'Alice'
obj['full-name'];   // Valid (hyphen not allowed in dot notation)

const key = 'age';
obj[key];           // 30 (dynamic)
```

### Property Addition/Deletion

```js
const obj = { name: 'Alice' };

// Add property
obj.age = 30;
obj['email'] = 'alice@example.com';

// Delete property
delete obj.age;     // true (successful deletion)
obj.age;            // undefined

// Delete returns false if property can't be deleted
delete obj.toString; // true (but doesn't actually delete inherited property)
```

### Computed Property Names

```js
const propName = 'dynamicKey';

const obj = {
  [propName]: 'value',           // dynamicKey: 'value'
  [`${propName}_2`]: 'value2',   // dynamicKey_2: 'value2'
  [Symbol('id')]: 123            // Symbol property
};
```

### Shorthand Properties and Methods

```js
const name = 'Alice';
const age = 30;

// Shorthand property
const user = { name, age }; // Same as { name: name, age: age }

// Shorthand method
const obj = {
  // Old way
  greet: function() {
    return 'Hello';
  },
  
  // Shorthand
  greet() {
    return 'Hello';
  }
};
```

---

## Prototype Chain

JavaScript uses **prototypal inheritance**. Every object has an internal `[[Prototype]]` link to another object.

### Understanding `[[Prototype]]`

```mermaid
graph TD
    A[user object] -->|[[Prototype]]| B[User.prototype]
    B -->|[[Prototype]]| C[Object.prototype]
    C -->|[[Prototype]]| D[null]
```

### Accessing Prototype

```js
const obj = {};

// Modern way (preferred)
Object.getPrototypeOf(obj);          // Object.prototype

// Legacy (non-standard but widely supported)
obj.__proto__;                       // Object.prototype

// Set prototype
Object.setPrototypeOf(obj, proto);   // Sets [[Prototype]]
```

### Prototype Lookup

When accessing a property, JavaScript searches:
1. The object itself
2. The object's prototype
3. The prototype's prototype
4. ... until reaching `null`

```js
const animal = {
  eats: true,
  walk() {
    console.log('Walking');
  }
};

const rabbit = Object.create(animal);
rabbit.jumps = true;

console.log(rabbit.eats);  // true (found in prototype)
console.log(rabbit.jumps); // true (own property)
rabbit.walk();             // 'Walking' (inherited method)

// Lookup chain:
// rabbit → animal → Object.prototype → null
```

### Own vs Inherited Properties

```js
const animal = { eats: true };
const rabbit = Object.create(animal);
rabbit.jumps = true;

rabbit.hasOwnProperty('jumps'); // true (own property)
rabbit.hasOwnProperty('eats');  // false (inherited)

'jumps' in rabbit;              // true (own)
'eats' in rabbit;               // true (inherited)
```

### Complete Prototype Chain Example

```js
const grandparent = {
  familyName: 'Smith',
  greet() {
    return `Hello from ${this.familyName}`;
  }
};

const parent = Object.create(grandparent);
parent.occupation = 'Engineer';

const child = Object.create(parent);
child.name = 'Alice';
child.age = 10;

console.log(child.name);        // 'Alice' (own)
console.log(child.occupation);  // 'Engineer' (parent)
console.log(child.familyName);  // 'Smith' (grandparent)
console.log(child.greet());     // 'Hello from Smith'

// Prototype chain:
// child → parent → grandparent → Object.prototype → null
```

### prototype vs __proto__

```js
function User(name) {
  this.name = name;
}

const user = new User('Alice');

// user.__proto__ === User.prototype
// User.prototype is an object
// user.__proto__ points to User.prototype

User.prototype;          // { constructor: User }
user.__proto__;          // { constructor: User } (same as User.prototype)
Object.getPrototypeOf(user) === User.prototype; // true

// Constructor function has its own prototype chain
User.__proto__ === Function.prototype; // true
```

### Shadowing Properties

```js
const parent = { value: 10 };
const child = Object.create(parent);

console.log(child.value); // 10 (inherited)

child.value = 20;         // Creates own property (shadows parent)
console.log(child.value); // 20 (own property)
console.log(parent.value);// 10 (unchanged)

delete child.value;       // Delete own property
console.log(child.value); // 10 (falls back to prototype)
```

---

## Inheritance Patterns

### 1. Prototypal Inheritance (Object.create)

```js
const animal = {
  eats: true,
  walk() {
    console.log('Animal walks');
  }
};

const rabbit = Object.create(animal);
rabbit.jumps = true;

rabbit.walk(); // 'Animal walks'
console.log(rabbit.jumps); // true
```

**Why use this?** Direct object-to-object inheritance without constructors. Enables flexible composition and delegation patterns.

**Where applicable?** Simple inheritance hierarchies, mixins, or when you want to avoid constructor functions. Ideal for utility objects or shared behaviors.

### 2. Constructor Pattern

```js
function Animal(name) {
  this.name = name;
}

Animal.prototype.walk = function() {
  console.log(`${this.name} walks`);
};

const dog = new Animal('Dog');
dog.walk(); // 'Dog walks'
```

**Why use this?** Creates instances with shared prototype methods, saving memory compared to factory pattern. Enables instanceof checks.

**Where applicable?** Pre-ES6 OOP codebases, when you need constructor logic and want to share methods across instances. Foundation for classical inheritance.

### 3. Parasitic Inheritance

```js
function createAnimal(name) {
  const animal = { name };
  
  animal.walk = function() {
    console.log(`${this.name} walks`);
  };
  
  return animal;
}

const cat = createAnimal('Cat');
cat.walk(); // 'Cat walks'
```

**Why use this?** Combines object creation with method assignment in one function. Each object gets its own method copies (no sharing).

**Where applicable?** When you want simple object creation without prototypes, or need to customize each object individually. Good for one-off objects.

### 4. Combination (Constructor + Prototype)

```js
function Animal(name) {
  this.name = name;        // Instance property
  this.actions = [];       // Instance property (not shared)
}

Animal.prototype.walk = function() {  // Shared method
  console.log(`${this.name} walks`);
};

const dog1 = new Animal('Dog1');
const dog2 = new Animal('Dog2');

dog1.actions.push('bark');
console.log(dog2.actions); // [] (not shared)

dog1.walk === dog2.walk;   // true (shared method)
```

**Why use this?** Balances instance-specific data with shared methods. Memory efficient for methods while allowing per-instance state.

**Where applicable?** Complex objects needing both unique data and shared behavior. Traditional OOP patterns before classes.

### 5. Classical Inheritance with Constructors

```js
function Animal(name) {
  this.name = name;
}

Animal.prototype.walk = function() {
  console.log(`${this.name} walks`);
};

function Dog(name, breed) {
  Animal.call(this, name);  // Call parent constructor
  this.breed = breed;
}

// Set up prototype chain
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog; // Fix constructor reference

Dog.prototype.bark = function() {
  console.log(`${this.name} barks`);
};

const myDog = new Dog('Buddy', 'Golden Retriever');
myDog.walk(); // 'Buddy walks'
myDog.bark(); // 'Buddy barks'
```

**Why use this?** Enables hierarchical inheritance with parent-child relationships. Supports method overriding and polymorphism.

**Where applicable?** Complex inheritance hierarchies, frameworks, or when you need classical OOP patterns. Common in large codebases before ES6 classes.

---

## ES6 Classes

Classes are syntactic sugar over constructor functions and prototypes.

### Basic Class Syntax

```js
class User {
  constructor(name, age) {
    this.name = name;     // Instance property
    this.age = age;
  }
  
  // Method (added to prototype)
  greet() {
    return `Hello, I'm ${this.name}`;
  }
  
  // Another method
  getAge() {
    return this.age;
  }
}

const user = new User('Alice', 30);
user.greet(); // "Hello, I'm Alice"

// Behind the scenes:
// User.prototype.greet = function() { ... }
```

### Class Fields (Properties)

```js
class User {
  // Public field (ES2022)
  role = 'user';
  
  // Without initializer
  status;
  
  constructor(name) {
    this.name = name;
    this.status = 'active';
  }
}

const user = new User('Alice');
console.log(user.role);   // 'user'
console.log(user.status); // 'active'
```

### Static Methods and Properties

Static members belong to the class itself, not instances.

```js
class User {
  static userCount = 0;
  
  constructor(name) {
    this.name = name;
    User.userCount++;
  }
  
  static getCount() {
    return User.userCount;
  }
  
  static create(name) {
    return new User(name);
  }
}

const user1 = new User('Alice');
const user2 = User.create('Bob');

console.log(User.getCount()); // 2
console.log(User.userCount);  // 2

// Static methods not available on instances
user1.getCount(); // TypeError: user1.getCount is not a function
```

### Getters and Setters

```js
class User {
  constructor(firstName, lastName) {
    this.firstName = firstName;
    this.lastName = lastName;
  }
  
  // Getter
  get fullName() {
    return `${this.firstName} ${this.lastName}`;
  }
  
  // Setter
  set fullName(value) {
    const [firstName, lastName] = value.split(' ');
    this.firstName = firstName;
    this.lastName = lastName;
  }
  
  get age() {
    return this._age;
  }
  
  set age(value) {
    if (value < 0) throw new Error('Age must be positive');
    this._age = value;
  }
}

const user = new User('Alice', 'Smith');
console.log(user.fullName);  // 'Alice Smith' (getter)

user.fullName = 'Bob Jones';  // (setter)
console.log(user.firstName);  // 'Bob'

user.age = 30;                // Setter with validation
console.log(user.age);        // 30
```

### Class Inheritance (extends)

```js
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  walk() {
    console.log(`${this.name} walks`);
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name);        // Call parent constructor (required!)
    this.breed = breed;
  }
  
  bark() {
    console.log(`${this.name} barks`);
  }
  
  // Override parent method
  walk() {
    super.walk();       // Call parent method
    console.log(`${this.name} wags tail while walking`);
  }
}

const dog = new Dog('Buddy', 'Golden Retriever');
dog.walk();
// Output:
// Buddy walks
// Buddy wags tail while walking
dog.bark(); // 'Buddy barks'
```

### Private Fields and Methods (ES2022)

```js
class BankAccount {
  // Private field (# prefix)
  #balance = 0;
  #pin;
  
  constructor(initialBalance, pin) {
    this.#balance = initialBalance;
    this.#pin = pin;
  }
  
  // Private method
  #validatePin(pin) {
    return pin === this.#pin;
  }
  
  // Public method using private members
  withdraw(amount, pin) {
    if (!this.#validatePin(pin)) {
      throw new Error('Invalid PIN');
    }
    
    if (amount > this.#balance) {
      throw new Error('Insufficient funds');
    }
    
    this.#balance -= amount;
    return this.#balance;
  }
  
  getBalance(pin) {
    if (!this.#validatePin(pin)) {
      throw new Error('Invalid PIN');
    }
    return this.#balance;
  }
}

const account = new BankAccount(1000, '1234');
console.log(account.getBalance('1234')); // 1000

// Private fields not accessible
console.log(account.#balance); // SyntaxError
```

### Static Initialization Blocks (ES2022)

```js
class Database {
  static #connection;
  
  static {
    // Static initialization block
    console.log('Initializing database...');
    this.#connection = this.#createConnection();
  }
  
  static #createConnection() {
    return { connected: true };
  }
  
  static getConnection() {
    return this.#connection;
  }
}

// Static block runs when class is evaluated
const conn = Database.getConnection();
```

---

## this Binding

`this` is dynamically bound based on how a function is called.

### Binding Rules (Priority Order)

1. **new binding** (highest priority)
2. **Explicit binding** (call, apply, bind)
3. **Implicit binding** (method call)
4. **Default binding** (lowest priority)

### 1. Default Binding

In non-strict mode, `this` defaults to global object.

```js
function foo() {
  console.log(this); // global object (window in browser)
}

foo();

// Strict mode
'use strict';
function bar() {
  console.log(this); // undefined
}

bar();
```

### 2. Implicit Binding

`this` is the object before the dot.

```js
const obj = {
  name: 'Alice',
  greet() {
    console.log(this.name);
  }
};

obj.greet(); // 'Alice' (this = obj)

// Lost binding
const greet = obj.greet;
greet(); // undefined (this = global or undefined in strict mode)
```

### 3. Explicit Binding (call, apply, bind)

#### call()

```js
function greet(greeting, punctuation) {
  console.log(`${greeting}, ${this.name}${punctuation}`);
}

const user = { name: 'Alice' };

greet.call(user, 'Hello', '!'); // 'Hello, Alice!'
```

#### apply()

```js
function greet(greeting, punctuation) {
  console.log(`${greeting}, ${this.name}${punctuation}`);
}

const user = { name: 'Bob' };

greet.apply(user, ['Hi', '.']); // 'Hi, Bob.'
```

#### bind()

Creates new function with fixed `this`.

```js
const obj = {
  name: 'Alice',
  greet() {
    console.log(this.name);
  }
};

const greet = obj.greet;
greet(); // undefined (lost binding)

const boundGreet = obj.greet.bind(obj);
boundGreet(); // 'Alice' (this permanently bound to obj)
```

### 4. new Binding

When using `new`, `this` is the newly created object.

```js
function User(name) {
  this.name = name;
  console.log(this); // New object
}

const user = new User('Alice');
console.log(user.name); // 'Alice'

// What 'new' does:
// 1. Create empty object: {}
// 2. Set prototype: {}.__proto__ = User.prototype
// 3. Bind 'this' to new object
// 4. Execute constructor
// 5. Return the object (unless constructor returns object)
```

### Arrow Functions (Lexical this)

Arrow functions **don't have their own `this`**. They inherit from surrounding scope.

```js
const obj = {
  name: 'Alice',
  greet: () => {
    console.log(this.name); // undefined (this from outer scope)
  },
  greetCorrect() {
    const inner = () => {
      console.log(this.name); // 'Alice' (inherits from greetCorrect)
    };
    inner();
  }
};

obj.greet();        // undefined
obj.greetCorrect(); // 'Alice'
```

### this in Event Handlers

```js
const button = document.querySelector('button');

// Regular function
button.addEventListener('click', function() {
  console.log(this); // <button> element
});

// Arrow function
button.addEventListener('click', () => {
  console.log(this); // Outer scope (not button)
});

// Common pattern: Arrow function in class
class Counter {
  count = 0;
  
  constructor() {
    // Arrow function preserves class instance
    button.addEventListener('click', () => {
      this.count++; // 'this' is Counter instance
    });
  }
}
```

### this Binding Examples

```js
// Example 1: Implicit binding
const user = {
  name: 'Alice',
  greet() {
    console.log(this.name);
  }
};

user.greet(); // 'Alice'

// Example 2: Lost binding
const greet = user.greet;
greet(); // undefined (this = global/undefined)

// Example 3: Fix with bind
const boundGreet = user.greet.bind(user);
boundGreet(); // 'Alice'

// Example 4: Fix with arrow function
const user2 = {
  name: 'Bob',
  greet: function() {
    const inner = () => console.log(this.name);
    inner();
  }
};

user2.greet(); // 'Bob' (arrow inherits this from greet)

// Example 5: Callback with lost binding
setTimeout(user.greet, 1000); // undefined

// Example 6: Fix callback
setTimeout(() => user.greet(), 1000); // 'Alice'
setTimeout(user.greet.bind(user), 1000); // 'Alice'
```

---

## Property Descriptors

Properties have hidden metadata (attributes) that control behavior.

### Property Attributes

- **value**: The property's value
- **writable**: Can the value be changed? (default: true)
- **enumerable**: Does it show in `for...in`? (default: true)
- **configurable**: Can descriptor be modified/property deleted? (default: true)

### Getting Property Descriptor

```js
const obj = { name: 'Alice' };

Object.getOwnPropertyDescriptor(obj, 'name');
// {
//   value: 'Alice',
//   writable: true,
//   enumerable: true,
//   configurable: true
// }
```

### Defining Properties

```js
const obj = {};

Object.defineProperty(obj, 'name', {
  value: 'Alice',
  writable: false,      // Read-only
  enumerable: true,
  configurable: false   // Can't delete or reconfigure
});

obj.name = 'Bob';      // Silently fails (strict mode: TypeError)
console.log(obj.name); // 'Alice'

delete obj.name;       // false (can't delete)
console.log(obj.name); // 'Alice' (still there)
```

### Getters and Setters in Descriptors

```js
const obj = {};

Object.defineProperty(obj, 'fullName', {
  get() {
    return `${this.firstName} ${this.lastName}`;
  },
  set(value) {
    [this.firstName, this.lastName] = value.split(' ');
  },
  enumerable: true,
  configurable: true
});

obj.fullName = 'Alice Smith';
console.log(obj.firstName); // 'Alice'
console.log(obj.fullName);  // 'Alice Smith'
```

### Defining Multiple Properties

```js
const obj = {};

Object.defineProperties(obj, {
  name: {
    value: 'Alice',
    writable: true
  },
  age: {
    value: 30,
    writable: false
  }
});
```

### Object Sealing and Freezing

#### Object.preventExtensions()

Prevents adding new properties.

```js
const obj = { name: 'Alice' };
Object.preventExtensions(obj);

obj.age = 30;           // Silently fails
console.log(obj.age);   // undefined

obj.name = 'Bob';       // Can modify existing
delete obj.name;        // Can delete existing

Object.isExtensible(obj); // false
```

#### Object.seal()

Prevents adding/removing properties. Existing properties can still be modified.

```js
const obj = { name: 'Alice' };
Object.seal(obj);

obj.age = 30;           // Silently fails (can't add)
delete obj.name;        // Silently fails (can't delete)
obj.name = 'Bob';       // Works (can modify)

Object.isSealed(obj);   // true
```

#### Object.freeze()

Prevents any changes (add/delete/modify).

```js
const obj = { name: 'Alice' };
Object.freeze(obj);

obj.name = 'Bob';       // Silently fails
obj.age = 30;           // Silently fails
delete obj.name;        // Silently fails

Object.isFrozen(obj);   // true
```

**Note**: Freeze is shallow.

```js
const obj = { 
  name: 'Alice',
  address: { city: 'NYC' }
};

Object.freeze(obj);

obj.name = 'Bob';           // Fails
obj.address.city = 'LA';    // Works! (nested object not frozen)
```

---

## Property Enumeration

### Iteration Methods

```js
const parent = { inherited: true };
const obj = Object.create(parent);
obj.own = 'value';
obj[Symbol('sym')] = 'symbol value';

Object.defineProperty(obj, 'nonEnum', {
  value: 'hidden',
  enumerable: false
});
```

#### for...in

Iterates over **enumerable** properties (own + inherited).

```js
for (const key in obj) {
  console.log(key); // 'own', 'inherited'
}

// Filter to own properties only
for (const key in obj) {
  if (obj.hasOwnProperty(key)) {
    console.log(key); // 'own'
  }
}
```

#### Object.keys()

Returns array of **own enumerable** property names.

```js
Object.keys(obj); // ['own']
```

#### Object.values()

Returns array of **own enumerable** property values.

```js
Object.values(obj); // ['value']
```

#### Object.entries()

Returns array of [key, value] pairs.

```js
Object.entries(obj); // [['own', 'value']]

// Use with destructuring
for (const [key, value] of Object.entries(obj)) {
  console.log(key, value);
}
```

#### Object.getOwnPropertyNames()

Returns **all own** properties (including non-enumerable).

```js
Object.getOwnPropertyNames(obj); // ['own', 'nonEnum']
```

#### Object.getOwnPropertySymbols()

Returns **symbol** properties.

```js
Object.getOwnPropertySymbols(obj); // [Symbol(sym)]
```

#### Reflect.ownKeys()

Returns **all own** property keys (strings + symbols).

```js
Reflect.ownKeys(obj); // ['own', 'nonEnum', Symbol(sym)]
```

### Comparison Table

| Method | Own | Inherited | Enumerable | Non-enumerable | Symbols |
|--------|-----|-----------|------------|----------------|---------|
| `for...in` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `Object.keys()` | ✅ | ❌ | ✅ | ❌ | ❌ |
| `Object.getOwnPropertyNames()` | ✅ | ❌ | ✅ | ✅ | ❌ |
| `Object.getOwnPropertySymbols()` | ✅ | ❌ | ✅ | ✅ | ✅ (only) |
| `Reflect.ownKeys()` | ✅ | ❌ | ✅ | ✅ | ✅ |

---

## Object Creation Patterns

### 1. Factory Pattern

```js
function createUser(name, email) {
  return {
    name,
    email,
    greet() {
      return `Hello, ${this.name}`;
    }
  };
}

const user1 = createUser('Alice', 'alice@example.com');
const user2 = createUser('Bob', 'bob@example.com');

// Problem: Each object has own copy of methods (memory inefficient)
user1.greet === user2.greet; // false
```

**Why use this?** Simple object creation without `new`. Each object gets its own method copies, enabling customization per instance.

**Where applicable?** Small projects, one-off objects, or when you want to avoid `new`. Good for data-only objects or simple APIs.

### 2. Constructor Pattern

```js
function User(name, email) {
  this.name = name;
  this.email = email;
}

User.prototype.greet = function() {
  return `Hello, ${this.name}`;
};

const user1 = new User('Alice', 'alice@example.com');
const user2 = new User('Bob', 'bob@example.com');

// Methods shared via prototype
user1.greet === user2.greet; // true
```

**Why use this?** Memory efficient for multiple instances. Enables instanceof checks and shared methods via prototype.

**Where applicable?** Pre-ES6 OOP, libraries needing constructor checks, or when you want shared behavior across instances.

### 3. Class Pattern (Modern)

```js
class User {
  constructor(name, email) {
    this.name = name;
    this.email = email;
  }
  
  greet() {
    return `Hello, ${this.name}`;
  }
}

const user = new User('Alice', 'alice@example.com');
```

**Why use this?** Clean, declarative syntax for OOP. Built-in validation (must use `new`), private fields, and modern tooling support.

**Where applicable?** Modern JavaScript projects, large applications, or when you need encapsulation and inheritance. Preferred over constructors.

### 4. Module Pattern (Encapsulation)

```js
const User = (function() {
  // Private variables
  const users = new Map();
  let nextId = 1;
  
  // Private function
  function validateEmail(email) {
    return email.includes('@');
  }
  
  // Public API
  return {
    create(name, email) {
      if (!validateEmail(email)) {
        throw new Error('Invalid email');
      }
      
      const id = nextId++;
      const user = { id, name, email };
      users.set(id, user);
      return user;
    },
    
    get(id) {
      return users.get(id);
    },
    
    getAll() {
      return Array.from(users.values());
    }
  };
})();

const user = User.create('Alice', 'alice@example.com');
```

**Why use this?** Provides encapsulation and private state without classes. Single instance with controlled access.

**Where applicable?** Utility modules, singletons, or when you need private state and controlled public interface. Good for data management.

### 5. Mixin Pattern

```js
const canWalk = {
  walk() {
    console.log(`${this.name} walks`);
  }
};

const canEat = {
  eat() {
    console.log(`${this.name} eats`);
  }
};

class Person {
  constructor(name) {
    this.name = name;
  }
}

// Apply mixins
Object.assign(Person.prototype, canWalk, canEat);

const person = new Person('Alice');
person.walk(); // 'Alice walks'
person.eat();  // 'Alice eats'
```

**Why use this?** Enables composition over inheritance. Mix in behaviors from multiple sources without complex hierarchies.

**Where applicable?** Multiple inheritance needs, shared behaviors across different classes, or when you want flexible composition. Useful in game development or UI components.

---

## Common Pitfalls

### 1. Forgetting `new` with Constructors

```js
function User(name) {
  this.name = name;
}

const user = User('Alice'); // ❌ Forgot 'new'
console.log(user);          // undefined
console.log(window.name);   // 'Alice' (polluted global!)

// Fix: Always use 'new' or switch to classes
```

### 2. Lost `this` Binding

```js
const obj = {
  name: 'Alice',
  greet() {
    console.log(this.name);
  }
};

setTimeout(obj.greet, 1000); // undefined (lost binding)

// Fix: Arrow function or bind
setTimeout(() => obj.greet(), 1000);
setTimeout(obj.greet.bind(obj), 1000);
```

### 3. Modifying `Object.prototype`

```js
// ❌ NEVER do this
Object.prototype.customMethod = function() {};

// Now ALL objects have this method
const obj = {};
obj.customMethod; // Exists! (pollutes all objects)
```

### 4. Forgetting `super()` in Subclass Constructor

```js
class Animal {
  constructor(name) {
    this.name = name;
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    // ❌ Forgot super()
    this.breed = breed; // ReferenceError: Must call super constructor
  }
}

// Fix: Call super first
class Dog extends Animal {
  constructor(name, breed) {
    super(name); // ✅
    this.breed = breed;
  }
}
```

### 5. Shared Prototype Properties

```js
function User(name) {
  this.name = name;
}

User.prototype.hobbies = []; // ❌ Shared array!

const user1 = new User('Alice');
const user2 = new User('Bob');

user1.hobbies.push('reading');
console.log(user2.hobbies); // ['reading'] ⚠️ Shared!

// Fix: Instance properties
function User(name) {
  this.name = name;
  this.hobbies = []; // ✅ Each instance gets own array
}
```

### 6. Using `this` in Arrow Functions

```js
const obj = {
  name: 'Alice',
  greet: () => {
    console.log(this.name); // undefined (arrow doesn't bind this)
  }
};

obj.greet(); // undefined

// Fix: Use regular function
const obj = {
  name: 'Alice',
  greet() {
    console.log(this.name); // 'Alice'
  }
};
```

### 7. Property Name Collisions

```js
const obj = {
  constructor: 'custom' // Shadows Object.prototype.constructor
};

obj.constructor; // 'custom' (not the constructor function)
```

### 8. Shallow Freeze/Seal

```js
const obj = {
  name: 'Alice',
  address: { city: 'NYC' }
};

Object.freeze(obj);

obj.address.city = 'LA'; // ✅ Works (nested object not frozen)

// Deep freeze needed for nested objects
function deepFreeze(obj) {
  Object.freeze(obj);
  Object.keys(obj).forEach(key => {
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      deepFreeze(obj[key]);
    }
  });
  return obj;
}
```

### 9. `hasOwnProperty` Not Safe

```js
const obj = Object.create(null); // No prototype
obj.hasOwnProperty; // undefined

// Safe way
Object.prototype.hasOwnProperty.call(obj, 'prop');

// Or use modern alternative
Object.hasOwn(obj, 'prop'); // ES2022
```

### 10. Enumerable Symbol Properties

```js
const sym = Symbol('id');
const obj = { [sym]: 123, name: 'Alice' };

Object.keys(obj);    // ['name'] (symbols excluded)
Object.values(obj);  // ['Alice']

// Include symbols
Object.getOwnPropertySymbols(obj); // [Symbol(id)]
Reflect.ownKeys(obj);              // ['name', Symbol(id)]
```

---

## Best Practices

### 1. Use Classes for OOP

```js
// ✅ Modern, clear intent
class User {
  constructor(name) {
    this.name = name;
  }
  
  greet() {
    return `Hello, ${this.name}`;
  }
}
```

### 2. Use Object.create() for Prototypal Inheritance

```js
// ✅ Clear prototype relationship
const animal = { eats: true };
const rabbit = Object.create(animal);
```

### 3. Bind Event Handlers in Classes

```js
class Component {
  constructor() {
    // ✅ Bind in constructor or use arrow function
    this.handleClick = this.handleClick.bind(this);
  }
  
  handleClick() {
    console.log(this); // Correct binding
  }
  
  // Or use class field with arrow function
  handleClick2 = () => {
    console.log(this); // Also correct
  }
}
```

### 4. Use `Object.assign()` for Shallow Copy

```js
const original = { a: 1, b: 2 };
const copy = Object.assign({}, original);

// Or spread operator
const copy2 = { ...original };
```

### 5. Check Property Existence Safely

```js
// ✅ Modern (ES2022)
Object.hasOwn(obj, 'prop');

// ✅ Traditional
Object.prototype.hasOwnProperty.call(obj, 'prop');

// ❌ Unsafe (obj might not have hasOwnProperty)
obj.hasOwnProperty('prop');
```

### 6. Prefer Composition Over Inheritance

```js
// ✅ Composition
class Logger {
  log(message) {
    console.log(message);
  }
}

class User {
  constructor(name) {
    this.name = name;
    this.logger = new Logger(); // Composed
  }
  
  greet() {
    this.logger.log(`Hello, ${this.name}`);
  }
}
```

### 7. Use Private Fields for Encapsulation

```js
// ✅ Modern encapsulation
class User {
  #password; // Private
  
  constructor(name, password) {
    this.name = name;
    this.#password = password;
  }
  
  authenticate(password) {
    return password === this.#password;
  }
}
```

### 8. Avoid Modifying Built-in Prototypes

```js
// ❌ Never do this
Array.prototype.customMethod = function() {};

// ✅ Create utility functions instead
function customArrayMethod(arr) {
  // ...
}
```

---

## Interview Questions

### Q1: What is prototypal inheritance?

**Answer**: Prototypal inheritance is JavaScript's inheritance model where objects can inherit properties and methods from other objects through the prototype chain. Every object has an internal `[[Prototype]]` link. When accessing a property, JavaScript searches the object, then its prototype, continuing up the chain until finding the property or reaching `null`.

```js
const animal = { eats: true };
const rabbit = Object.create(animal);
rabbit.jumps = true;

rabbit.eats; // true (inherited from animal)
rabbit.jumps; // true (own property)
```

### Q2: Explain `this` binding in JavaScript.

**Answer**: `this` is dynamically bound based on how a function is called, following these rules (in priority order):

1. **new binding**: `this` = newly created object
2. **Explicit binding** (call/apply/bind): `this` = specified object
3. **Implicit binding** (method call): `this` = object before dot
4. **Default binding**: `this` = global object (or undefined in strict mode)

**Arrow functions** don't have their own `this`; they lexically inherit from surrounding scope.

### Q3: What's the difference between `__proto__` and `prototype`?

**Answer**:

- `__proto__`: Property on **every object** that points to its prototype (the object it inherits from). It's the actual prototype link.
- `prototype`: Property on **constructor functions** that becomes the `__proto__` of instances created with `new`.

```js
function User(name) {
  this.name = name;
}

const user = new User('Alice');

user.__proto__ === User.prototype; // true
```

### Q4: How do ES6 classes differ from constructor functions?

**Answer**: Classes are syntactic sugar over constructor functions but have key differences:

1. **Must use `new`**: Classes throw error if called without `new`
2. **No hoisting**: Class declarations aren't hoisted
3. **Strict mode**: Class bodies run in strict mode
4. **Methods non-enumerable**: Class methods aren't enumerable by default
5. **Private fields**: Classes support `#privateField` syntax

```js
class User {} // Not hoisted
User(); // TypeError (must use new)

function User2() {} // Hoisted
User2(); // Works (no error)
```

### Q5: What are property descriptors?

**Answer**: Property descriptors are objects that define a property's metadata:

- **value**: The property's value
- **writable**: Can the value be changed?
- **enumerable**: Does it appear in `for...in` loops?
- **configurable**: Can the descriptor be modified/property deleted?

Alternatively, properties can have **get/set** instead of value/writable.

```js
Object.defineProperty(obj, 'name', {
  value: 'Alice',
  writable: false,
  enumerable: true,
  configurable: false
});
```

### Q6: How do you create truly private properties in JavaScript?

**Answer**: Several approaches:

1. **Private fields** (ES2022): Use `#` prefix
```js
class User {
  #password;
  constructor(pwd) {
    this.#password = pwd;
  }
}
```

2. **Closures**: Encapsulate in function scope
```js
function createUser() {
  let privateData = {};
  return {
    getData() { return privateData; }
  };
}
```

3. **WeakMap**: Store private data externally
```js
const privateData = new WeakMap();
class User {
  constructor() {
    privateData.set(this, { secret: 'value' });
  }
}
```

### Q7: Explain the difference between `Object.freeze()`, `Object.seal()`, and `Object.preventExtensions()`.

**Answer**:

| Method | Add Properties | Delete Properties | Modify Properties |
|--------|----------------|-------------------|-------------------|
| `preventExtensions()` | ❌ | ✅ | ✅ |
| `seal()` | ❌ | ❌ | ✅ |
| `freeze()` | ❌ | ❌ | ❌ |

All are **shallow** - only affect the object itself, not nested objects.

### Q8: What is the difference between `for...in` and `Object.keys()`?

**Answer**:

- **`for...in`**: Iterates over **own + inherited enumerable** properties (strings only, no symbols)
- **`Object.keys()`**: Returns array of **own enumerable** property names (strings only)

```js
const parent = { inherited: true };
const obj = Object.create(parent);
obj.own = 'value';

for (const key in obj) {
  console.log(key); // 'own', 'inherited'
}

Object.keys(obj); // ['own']
```

**Best practice**: Use `Object.keys()` when you only want own properties.

---

## Cross-Links

- **Types and coercion**: [[JavaScript/01_Foundations/02_Values_Types_and_Coercion]]
- **Closures and scope**: [[JavaScript/03_Advanced/01_Closures_Scopes_and_Garbage_Collection]]
- **V8 optimization (hidden classes)**: [[JavaScript/03_Advanced/04_V8_Basics_Hidden_Classes_and_ICs]]
- **TypeScript classes**: [[TypeScript/01_Foundations/03_Classes_and_Interfaces]]

## References

- [MDN: Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
- [MDN: Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)
- [MDN: this](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this)
- [YDKJS: this & Object Prototypes](https://github.com/getify/You-Dont-Know-JS/tree/2nd-ed/this%20%26%20object%20prototypes)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 1100+
