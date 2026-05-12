---
tags: [typescript, playbook, react, jsx, hooks, components]
aliases: ["TypeScript with React", "React Typing", "TS React Patterns", "Typed React Components"]
status: stable
updated: 2026-05-03
---

# Playbook: TypeScript with React

> [!summary] Goal
> Type React components, hooks, events, and context safely — writing components that are ergonomic to use and impossible to misuse.

## Table of Contents

1. [Why TypeScript with React](#why-typescript-with-react)
2. [Component Typing Patterns](#component-typing-patterns)
3. [Props and Defaults](#props-and-defaults)
4. [Typing Hooks](#typing-hooks)
5. [Typing Events](#typing-events)
6. [Generic Components](#generic-components)
7. [Typing Context](#typing-context)
8. [`forwardRef` and `useImperativeHandle`](#forwardref-and-useimperativehandle)
9. [Typing Custom Hooks](#typing-custom-hooks)
10. [Pitfalls](#pitfalls)

---

## Why TypeScript with React

TypeScript catches common React errors at compile time: missing props, wrong event types, incorrect state mutations.

```mermaid
flowchart LR
    A[React + TypeScript] --> B[Props: type-checked at call site]
    A --> C[State: inferred from initial value]
    A --> D[Events: typed handlers]
    A --> E[Context: type-safe providers/consumers]
    B --> F[No more "cannot read property of undefined"]
    C --> G[No more "setCount('string') instead of number"]
```

---

## Component Typing Patterns

### Function component with `interface Props`

```tsx
interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  onClick: () => void;
}

function Button({ label, variant = 'primary', disabled, onClick }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
```

### `React.FC` — avoid it

```tsx
// AVOID — adds implicit children, breaks default props inference
const Button: React.FC<ButtonProps> = ({ label }) => <button>{label}</button>;
```

| Aspect | `function Component(props: Props)` | `React.FC<Props>` |
|--------|------------------------------------|-------------------|
| `children` | Explicit | Implicit |
| Default props | Works | Broken |
| Generic components | Easy | Awkward |
| Bundle size | Same | Same |
| **Recommendation** | ✅ Prefer | ❌ Avoid |

### Children prop explicitly

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
}

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}
```

---

## Props and Defaults

### Destructuring with defaults

```tsx
interface UserCardProps {
  name: string;
  email?: string;
  role?: 'admin' | 'user';
}

function UserCard({
  name,
  email = 'no-email',
  role = 'user',
}: UserCardProps) {
  return <div>{name} — {role}</div>;
}
```

### `React.ComponentProps` — extract props from HTML elements

```tsx
// Get the exact props of a native element
type InputProps = React.ComponentProps<'input'>;

function ValidatedInput(props: InputProps) {
  const [value, setValue] = useState(props.value ?? '');
  return <input {...props} value={value} onChange={e => setValue(e.target.value)} />;
}
```

### Extending native element props

```tsx
interface StyledButtonProps extends React.ComponentProps<'button'> {
  variant?: 'primary' | 'secondary';
}

function StyledButton({ variant = 'primary', className, ...rest }: StyledButtonProps) {
  return (
    <button className={`btn btn-${variant} ${className ?? ''}`} {...rest} />
  );
}
```

---

## Typing Hooks

### `useState` — type inference

```tsx
const [count, setCount] = useState(0);
// count: number, setCount: React.Dispatch<React.SetStateAction<number>>

const [user, setUser] = useState<User | null>(null);
// user: User | null
```

### `useReducer` — typed actions

```tsx
type Action =
  | { type: 'increment'; payload: number }
  | { type: 'decrement'; payload: number }
  | { type: 'reset' };

interface State { count: number }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment': return { count: state.count + action.payload };
    case 'decrement': return { count: state.count - action.payload };
    case 'reset': return { count: 0 };
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0 });
dispatch({ type: 'increment', payload: 5 });  // typed
// dispatch({ type: 'unknown' });  // Error: type not in Action
```

### `useRef`

```tsx
// Mutable ref (DOM element):
const inputRef = useRef<HTMLInputElement>(null);
// typeof inputRef.current: HTMLInputElement | null

// Immutable ref (stored value):
const renderCount = useRef(0);
renderCount.current += 1;  // OK — .current is mutable
```

### `useCallback` and `useMemo`

```tsx
// Inferred types:
const handleClick = useCallback((id: string) => {
  console.log(id);
}, []);

const sorted = useMemo(() => {
  return items.sort((a, b) => a.name.localeCompare(b.name));
}, [items]);
```

---

## Typing Events

```tsx
function Form() {
  // Form events
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // process form
  };

  // Input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);  // typed as string
  };

  // Mouse events
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log(e.clientX, e.clientY);
  };

  // Keyboard events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') { /* submit */ }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} onKeyDown={handleKeyDown} />
      <button onClick={handleClick}>Submit</button>
    </form>
  );
}
```

### Common event types

| Event type | HTML element |
|-----------|--------------|
| `React.ChangeEvent<HTMLInputElement>` | `<input>`, `<select>`, `<textarea>` |
| `React.MouseEvent<HTMLButtonElement>` | `<button>`, `<div>` (onClick) |
| `React.FormEvent<HTMLFormElement>` | `<form>` (onSubmit) |
| `React.KeyboardEvent<HTMLInputElement>` | `<input>` (onKeyDown) |
| `React.FocusEvent<HTMLInputElement>` | onFocus, onBlur |
| `React.DragEvent<HTMLDivElement>` | Drag and drop |

---

## Generic Components

```tsx
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map((item, i) => <li key={i}>{renderItem(item, i)}</li>)}</ul>;
}

// Usage — T is inferred from items:
<List
  items={[
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
  ]}
  renderItem={(user) => <span>{user.name}</span>}
/>
```

### Generic component with constraints

```tsx
interface HasId { id: string | number }

function KeyedList<T extends HasId>(
  { items, renderItem }: {
    items: T[];
    renderItem: (item: T) => React.ReactNode;
  }
) {
  return <ul>{items.map(item => <li key={item.id}>{renderItem(item)}</li>)}</ul>;
}
```

---

## Typing Context

```tsx
interface AuthContextValue {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const u = await api.login(email, password);
    setUser(u);
  };

  const logout = () => { setUser(null); };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be inside AuthProvider');
  return context;
}

// Usage:
function UserProfile() {
  const { user, logout } = useAuth();
  return (
    <div>
      <p>Welcome, {user?.name}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

## `forwardRef` and `useImperativeHandle`

```tsx
interface FancyInputProps {
  placeholder?: string;
}

export interface FancyInputHandle {
  focus: () => void;
  clear: () => void;
  value: string;
}

const FancyInput = forwardRef<FancyInputHandle, FancyInputProps>(
  (props, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => ({
      focus: () => inputRef.current?.focus(),
      clear: () => { if (inputRef.current) inputRef.current.value = ''; },
      get value() { return inputRef.current?.value ?? ''; },
    }));

    return <input ref={inputRef} {...props} />;
  }
);

// Parent component:
function Form() {
  const inputRef = useRef<FancyInputHandle>(null);

  const handleSubmit = () => {
    inputRef.current?.focus();
    console.log(inputRef.current?.value);
  };

  return (
    <>
      <FancyInput ref={inputRef} placeholder="Enter name" />
      <button onClick={handleSubmit}>Submit</button>
    </>
  );
}
```

---

## Typing Custom Hooks

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    setStoredValue(prev => {
      const valueToStore = value instanceof Function ? value(prev) : value;
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
      return valueToStore;
    });
  }, [key]);

  return [storedValue, setValue] as const;
}

// Usage — T is inferred from the initial value:
const [theme, setTheme] = useLocalStorage('theme', 'light');
// theme: string, setTheme: (value: string | ((val: string) => string)) => void
```

---

## Pitfalls

### `children` type too broad

```tsx
// TOO BROAD:
function Card(props: { children?: any }) { ... }

// BETTER:
function Card(props: { children: React.ReactNode }) { ... }

// MOST PRECISE:
function Card(props: { children: React.ReactElement }) { ... }
// ReactElement = single JSX element (not string, number, array)
```

### Missing key prop in lists

TypeScript does not enforce the `key` prop in mapped lists — it's a React requirement, not a TS one. Use ESLint's `react/jsx-key` rule.

### `React.FC` with generics

```tsx
// BROKEN: React.FC doesn't support generics well
const List: React.FC<ListProps<T>> = ...  // can't express T

// FIX: use function syntax
function List<T>(props: ListProps<T>) { ... }
```

### `useRef` type confusion

```tsx
// Mutable ref (initially null, then DOM element):
const ref = useRef<HTMLDivElement>(null!);  // Using `null!` assertion
// VS:
const ref = useRef<HTMLDivElement>(null);   // ref.current is HTMLDivElement | null
```

**Fix**: Use `null!` only when you're certain it will be set before access.

---

> [!question]- Interview Questions
>
> **Q: How do you type React component props?**
> A: Define an interface for the props and pass it as a type parameter to the function: `function Button({ label }: ButtonProps)`. Prefer explicit props over `React.FC`.
>
> **Q: How do you type `useReducer`?**
> A: Define an `Action` union type with a `type` discriminant and a `State` interface. The reducer function takes `(state: State, action: Action) => State`. Use discriminated unions for the actions.
>
> **Q: How do you type `forwardRef`?**
> A: `forwardRef<RefType, PropsType>((props, ref) => ...)`. Define the ref handle interface and pass a `ref={ref}` from the parent using `useRef<RefType>()`.
>
> **Q: What is the `React.ComponentProps` utility type used for?**
> A: It extracts the complete props type of any React component or HTML element: `type ButtonProps = React.ComponentProps<'button'>`. Useful for wrapping native elements.

---

## Cross-Links

- [[TypeScript/01_Foundations/02_Functions_Objects_and_Interfaces]] for interface patterns
- [[TypeScript/02_Core/03_Discriminated_Unions]] for reducer action types
- [[TypeScript/02_Core/05_Classes_and_OOP]] for class components
- [[TypeScript/04_Playbooks/03_Testing_TypeScript]] for testing React components
- [[TypeScript/04_Playbooks/05_Migrating_JS_to_TS]] for converting JS React code
- [[React/00_MOC/00_React_MOC]] for React fundamentals

---

## References

- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [TypeScript Handbook: React](https://www.typescriptlang.org/docs/handbook/react-&-webpack.html)
- [React + TypeScript: Patterns](https://github.com/typescript-cheatsheets/react)
