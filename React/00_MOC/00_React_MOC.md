---
tags: [react, frontend, moc]
aliases: ["React MOC"]
status: stable
updated: 2026-04-26
---

# React Map of Content

> [!summary] Scope
> Comprehensive TypeScript-first React ecosystem: Hooks, Rendering Cycle, Redux Toolkit, RTK Query, React Router, Forms, Testing, Performance, React 19, Next.js, Portals, Tailwind CSS, E2E Testing, TypeScript Patterns, Real-Time, Design Systems, and Production Architecture.

## Overview

This MOC covers the complete modern React stack with 17 comprehensive guides totaling 25,000+ lines of production-ready content, code examples, and best practices.

**What You'll Learn:**
- Core React concepts (mental model, rendering, hooks)
- State management (Redux Toolkit + RTK Query)
- Routing (React Router 6)
- Forms (React Hook Form + Zod)
- Testing (Testing Library + MSW)
- Performance optimization
- Production architecture patterns
- Debugging workflows
- Real-world projects

---

## Learning Paths

### Path 1: Beginner → Intermediate (2-3 weeks)

**Week 1: React Fundamentals**
1. [[01_React_Mental_Model_and_Rendering]] - Understanding how React works
2. [[02_Hooks_Complete_Reference]] - Master all built-in hooks
3. [[03_State_and_Effects_Common_Pitfalls]] - Avoid common mistakes

**Week 2: Core Tools**
4. [[03_Routing_with_React_Router]] - Client-side routing
5. [[04_Forms_and_Validation]] - Form handling with validation
6. [[01_Redux_Toolkit_Essentials]] - Global state management

**Week 3: Advanced Topics**
7. [[02_RTK_Query_Essentials]] - Data fetching and caching
8. [[01_Testing_React_TL_and_MSW]] - Testing strategies
9. [[02_Performance_and_Profiling]] - Optimization techniques
10. [[04_Playbooks/04_Next.js_App_Router_and_Server_Components]] - Next.js basics

**Practice Project:**
- [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]] - Build complete starter app

---

### Path 2: Intermediate → Advanced (1-2 weeks)

**Advanced Concepts:**
1. [[03_React_App_Architecture_Playbook]] - Production architecture
2. [[01_Debug_Rerenders_and_Perf_Issues]] - Performance debugging
3. [[02_Debug_Data_Fetching_and_Caching_RTKQ]] - RTK Query debugging
4. [[03_Testing_Checklist_and_MSW_Setup]] - Comprehensive testing
5. [[04_Playbooks/05_Portals_and_Teleporting_UI]] - Portal patterns
6. [[04_Playbooks/06_Tailwind_CSS_and_Styling_Strategies]] - Tailwind CSS
7. [[04_Playbooks/07_E2E_Testing_with_Playwright]] - E2E testing
8. [[04_Playbooks/08_React_TypeScript_Advanced_Patterns]] - TypeScript patterns
9. [[04_Playbooks/09_WebSocket_and_Real_Time_Patterns]] - Real-time
10. [[04_Playbooks/04_Next.js_App_Router_and_Server_Components]] - Next.js deep dive

**Practice Projects:**
- [[02_Form_Heavy_App_With_Validation]] - Complex forms
- [[03_Perf_Case_Study_Virtualized_List]] - Performance optimization

---

### Path 3: Interview Preparation (1 week)

**Day 1-2: Core Concepts**
- Review [[01_React_Mental_Model_and_Rendering]] interview questions
- Practice [[02_Hooks_Complete_Reference]] hook implementations
- Study [[03_State_and_Effects_Common_Pitfalls]] common mistakes

**Day 3-4: State Management**
- Master [[01_Redux_Toolkit_Essentials]] patterns
- Understand [[02_RTK_Query_Essentials]] caching
- Practice [[03_Routing_with_React_Router]] scenarios

**Day 5-6: Advanced Topics**
- Review [[02_Performance_and_Profiling]] optimization techniques
- Study [[03_React_App_Architecture_Playbook]] architecture decisions
- Practice [[01_Debug_Rerenders_and_Perf_Issues]] debugging workflow

**Day 7: Projects & Review**
- Build mini-project using [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]]
- Review all interview questions (8 per file = 72 total)
- Practice explaining concepts out loud

---

## Quick Reference Tables

### All React Hooks

| Hook | Use Case | When to Use | Example |
|------|----------|-------------|---------|
| `useState` | Local component state | Simple values that trigger re-renders | `const [count, setCount] = useState(0)` |
| `useEffect` | Side effects, subscriptions | API calls, timers, DOM manipulation | `useEffect(() => { fetch('/api/data') }, [])` |
| `useReducer` | Complex state logic | Multiple related state updates | `const [state, dispatch] = useReducer(reducer, init)` |
| `useContext` | Access context value | Share data without props drilling | `const value = useContext(MyContext)` |
| `useMemo` | Memoize expensive calculations | Avoid re-computing on every render | `const value = useMemo(() => expensive(a, b), [a, b])` |
| `useCallback` | Memoize functions | Prevent child re-renders | `const fn = useCallback(() => {}, [deps])` |
| `useRef` | Persist values without re-render | DOM refs, previous values | `const ref = useRef<HTMLDivElement>(null)` |
| `useId` | Generate unique IDs | Form labels, accessibility | `const id = useId()` |
| `useTransition` | Mark state updates as low priority | Defer expensive updates | `const [isPending, startTransition] = useTransition()` |
| `useDeferredValue` | Defer value updates | Keep UI responsive during updates | `const deferred = useDeferredValue(value)` |
| `useLayoutEffect` | Synchronous effects | Measure DOM before paint | `useLayoutEffect(() => { measure() }, [])` |
| `useImperativeHandle` | Customize ref value | Expose imperative methods | `useImperativeHandle(ref, () => ({ focus }))` |
| `useDebugValue` | Custom hook debugging | DevTools label | `useDebugValue(isOnline ? 'Online' : 'Offline')` |
| `useSyncExternalStore` | Subscribe to external stores | Browser APIs, non-React state | `useSyncExternalStore(subscribe, getSnapshot)` |
| `useInsertionEffect` | CSS-in-JS style injection | Before DOM mutations (library authors) | `useInsertionEffect(() => { style.textContent = css }, [css])` |

---

### Component Patterns Comparison

| Pattern | Best For | Pros | Cons | Example File |
|---------|----------|------|------|--------------|
| **Container/Presentational** | Separating logic from UI | Easy to test, reusable UI | More files | [[03_React_App_Architecture_Playbook]] |
| **Compound Components** | Flexible, composable APIs | Great API, flexible | Slightly complex | [[03_React_App_Architecture_Playbook]] |
| **Render Props** | Sharing stateful logic | Flexible, explicit | Verbose, callback hell | [[02_Hooks_Complete_Reference]] |
| **Higher-Order Components** | Cross-cutting concerns | Composition | Props confusion (legacy) | [[03_React_App_Architecture_Playbook]] |
| **Custom Hooks** | Reusable stateful logic | Simple, composable | Modern best practice | [[02_Hooks_Complete_Reference]] |

**Modern Recommendation:** Prefer Custom Hooks > Compound Components > Others

---

### State Management Decision Matrix

| State Type | Scope | Frequency | Solution | Example |
|------------|-------|-----------|----------|---------|
| UI state (local) | Component | Often | `useState` | Modal open/closed |
| Form state | Component/Form | Often | React Hook Form | Login form |
| Derived state | Component | Often | `useMemo` | Filtered list |
| Server data | App-wide | Varies | RTK Query | Product list |
| Global app state | App-wide | Often | Redux Toolkit | Auth status |
| Shared UI state | Feature | Medium | Context + useReducer | Theme, locale |
| URL state | Route | Rarely | React Router | Page number |
| Persistent state | App-wide | Rarely | localStorage + Redux | User preferences |

**Decision Tree:**
```
Is it server data? → RTK Query
Is it in URL? → React Router params/search
Is it local to component? → useState
Is it global & complex? → Redux Toolkit
Is it shared in subtree? → Context
Is it derived? → useMemo
```

---

### Testing Strategies

| What to Test | Tool | Priority | Example |
|--------------|------|----------|---------|
| Component rendering | Testing Library | High | [[01_Testing_React_TL_and_MSW]] |
| User interactions | userEvent | High | Click, type, submit |
| API calls | MSW | High | [[03_Testing_Checklist_and_MSW_Setup]] |
| Hooks | renderHook | Medium | Custom hook behavior |
| Accessibility | jest-axe | Medium | ARIA, semantic HTML |
| Performance | React Profiler | Low | Re-render count |
| Integration | Testing Library | High | Full user flows |
| E2E | Playwright/Cypress | Medium | Critical paths |

---

### Performance Optimization Techniques

| Issue | Solution | Tool | Complexity | Impact |
|-------|----------|------|------------|--------|
| Unnecessary re-renders | React.memo | DevTools Profiler | Low | High |
| Expensive calculations | useMemo | DevTools Profiler | Low | High |
| Inline function props | useCallback | why-did-you-render | Low | Medium |
| Large lists | react-window | Lighthouse | Medium | Very High |
| Bundle size | Code splitting | Bundle Analyzer | Medium | High |
| Context re-renders | Split contexts | why-did-you-render | Low | Medium |
| Slow images | Lazy loading, WebP | Lighthouse | Low | Medium |
| Redux selectors | createSelector | Redux DevTools | Low | Medium |

---

## Common Patterns Summary

### Data Fetching Pattern

```tsx
// Using RTK Query (Recommended)
const { data, error, isLoading } = useGetProductsQuery();

if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return <EmptyState />;

return <ProductList products={data} />;
```

**Reference:** [[02_RTK_Query_Essentials]]

---

### Form Handling Pattern

```tsx
// Using React Hook Form + Zod
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});

const onSubmit = (data) => {
  // Type-safe data
};
```

**Reference:** [[04_Forms_and_Validation]]

---

### Authentication Pattern

```tsx
// Protected Route
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAppSelector(state => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Usage in router
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

**Reference:** [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]]

---

### Error Handling Pattern

```tsx
// Component Level
const Component = () => {
  const { data, error } = useGetDataQuery();
  
  if (error) {
    if (error.status === 404) return <NotFound />;
    if (error.status >= 500) return <ServerError retry={refetch} />;
    return <GenericError />;
  }
  
  return <Content data={data} />;
};

// App Level (Error Boundary)
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

**Reference:** [[03_React_App_Architecture_Playbook]]

---

### Performance Optimization Pattern

```tsx
// Memoize expensive component
const ExpensiveComponent = React.memo(({ data }) => {
  const result = useMemo(() => expensiveCalculation(data), [data]);
  const handler = useCallback(() => handleClick(), []);
  
  return <div onClick={handler}>{result}</div>;
});

// Virtualize long list
<FixedSizeList height={600} itemCount={items.length} itemSize={50}>
  {({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  )}
</FixedSizeList>
```

**Reference:** [[03_Perf_Case_Study_Virtualized_List]]

---

## Troubleshooting Quick Links

### Issue: Component Re-renders Too Often
→ Read [[01_Debug_Rerenders_and_Perf_Issues]]
- Use React DevTools Profiler
- Enable why-did-you-render
- Check parent re-renders, context changes, prop identity

### Issue: RTK Query Cache Not Updating
→ Read [[02_Debug_Data_Fetching_and_Caching_RTKQ]]
- Check invalidatesTags in mutations
- Check providesTags in queries
- Inspect Redux DevTools for invalidation actions

### Issue: Tests Failing or Flaky
→ Read [[03_Testing_Checklist_and_MSW_Setup]]
- Use findBy instead of getBy for async
- Set up MSW correctly
- Check for act() warnings

### Issue: Slow Performance
→ Read [[02_Performance_and_Profiling]]
- Profile with React DevTools
- Check for large lists (virtualize)
- Memoize expensive calculations

### Issue: Forms Not Validating
→ Read [[04_Forms_and_Validation]]
- Check Zod schema
- Verify resolver setup
- Test validation manually

---

## Complete Topic Organization

### 01_Foundations (3 files, 5,533 lines)
1. [[01_React_Mental_Model_and_Rendering]] (1,806 lines)
   - How React works under the hood
   - Rendering behavior
   - Reconciliation
   - 8 interview questions

2. [[02_Hooks_Complete_Reference]] (2,317 lines)
   - All 13 React hooks
   - Custom hooks patterns
   - Best practices
   - 8 interview questions

3. [[03_State_and_Effects_Common_Pitfalls]] (1,410 lines)
   - useState pitfalls
   - useEffect pitfalls
   - Solutions and patterns
   - 8 interview questions

---

### 02_Core (4 files, 7,428 lines)
1. [[01_Redux_Toolkit_Essentials]] (2,150 lines)
   - Store setup
   - Slices and reducers
   - Typed hooks
   - 8 interview questions

2. [[02_RTK_Query_Essentials]] (2,226 lines)
   - API slice setup
   - Queries and mutations
   - Cache management
   - 8 interview questions

3. [[03_Routing_with_React_Router]] (1,623 lines)
   - Route configuration
   - Navigation
   - Protected routes
   - 8 interview questions

4. [[04_Forms_and_Validation]] (1,429 lines)
   - React Hook Form
   - Zod validation
   - Form patterns
   - 8 interview questions

---

### 03_Advanced (3 files, 6,475 lines)
1. [[01_Testing_React_TL_and_MSW]] (2,737 lines)
   - Testing Library
   - MSW setup
   - Testing patterns
   - 8 interview questions

2. [[02_Performance_and_Profiling]] (1,869 lines)
   - Profiling tools
   - Optimization techniques
   - Measuring performance
   - 8 interview questions

3. [[03_React_App_Architecture_Playbook]] (1,869 lines)
   - Folder structures
   - Architecture patterns
   - Best practices
   - 8 interview questions

---

### 04_Playbooks (3 files, 3,862 lines)
1. [[01_Debug_Rerenders_and_Perf_Issues]] (1,336 lines)
   - React DevTools Profiler
   - why-did-you-render
   - 15+ re-render scenarios
   - Debugging workflow

2. [[02_Debug_Data_Fetching_and_Caching_RTKQ]] (1,134 lines)
   - RTK Query debugging
   - Cache behavior
   - 12+ caching scenarios
   - Network analysis

3. [[03_Testing_Checklist_and_MSW_Setup]] (1,392 lines)
   - MSW setup guide
   - 60+ testing checklist items
   - Common pitfalls
   - CI/CD integration

---

### 05_Projects (3 files, 3,016 lines)
1. [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]] (1,339 lines)
   - Production starter template
   - Authentication flow
   - Complete code
   - Docker deployment

2. [[02_Form_Heavy_App_With_Validation]] (953 lines)
   - 5 form implementations
   - Multi-step wizard
   - Dynamic forms
   - File uploads

3. [[03_Perf_Case_Study_Virtualized_List]] (724 lines)
   - 10,000-item list optimization
   - Before/after metrics
   - Virtualization
   - Lessons learned

---

## Interview Preparation Guide

### Core Concepts to Master

**Must Know (30 minutes each):**
1. How React rendering works
2. Virtual DOM and reconciliation
3. All hooks (especially useState, useEffect, useMemo, useCallback)
4. State management (when to use what)
5. Component lifecycle
6. Re-rendering causes and prevention
7. Forms and validation
8. Routing (React Router 6)

**Should Know (15 minutes each):**
1. Redux Toolkit patterns
2. RTK Query caching
3. Performance optimization
4. Testing strategies
5. Error boundaries
6. Code splitting
7. TypeScript with React
8. Accessibility

**Nice to Know:**
1. Server Components (React 19)
2. Concurrent features
3. Build tools (Vite, webpack)
4. Deployment strategies

---

### Common Interview Questions Index

Each guide has 8 interview questions. Total: **72 questions across 9 guides**.

**Top 20 Most Common:**
1. How does React rendering work? → [[01_React_Mental_Model_and_Rendering]]
2. When does a component re-render? → [[01_React_Mental_Model_and_Rendering]]
3. What's the difference between useMemo and useCallback? → [[02_Hooks_Complete_Reference]]
4. How do you prevent unnecessary re-renders? → [[01_Debug_Rerenders_and_Perf_Issues]]
5. When should you use Redux vs Context? → [[01_Redux_Toolkit_Essentials]]
6. How does RTK Query caching work? → [[02_RTK_Query_Essentials]]
7. What are the common useEffect pitfalls? → [[03_State_and_Effects_Common_Pitfalls]]
8. How do you handle forms in React? → [[04_Forms_and_Validation]]
9. How do you test React components? → [[01_Testing_React_TL_and_MSW]]
10. How do you optimize a slow React app? → [[02_Performance_and_Profiling]]
11. What's your folder structure? → [[03_React_App_Architecture_Playbook]]
12. How do you handle authentication? → [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]]
13. How do you debug re-renders? → [[01_Debug_Rerenders_and_Perf_Issues]]
14. What's the difference between controlled and uncontrolled components? → [[04_Forms_and_Validation]]
15. How do you handle errors in React? → [[03_React_App_Architecture_Playbook]]
16. What are React keys and why are they important? → [[01_React_Mental_Model_and_Rendering]]
17. How do you handle side effects? → [[03_State_and_Effects_Common_Pitfalls]]
18. What's the difference between useEffect and useLayoutEffect? → [[02_Hooks_Complete_Reference]]
19. How do you structure a large React app? → [[03_React_App_Architecture_Playbook]]
20. How do you mock API calls in tests? → [[03_Testing_Checklist_and_MSW_Setup]]

---

### Project Ideas for Practice

**Beginner:**
- Todo list with filtering and persistence
- Weather app with API integration
- Simple blog with routing

**Intermediate:**
- E-commerce product catalog (use [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]])
- Admin dashboard with charts
- Social media feed with infinite scroll

**Advanced:**
- Full-stack app with authentication
- Real-time chat application
- Complex forms application (use [[02_Form_Heavy_App_With_Validation]])

---

## External Resources

### Official Documentation
- [React Docs](https://react.dev/) - Official React documentation
- [Redux Toolkit](https://redux-toolkit.js.org/) - Official Redux Toolkit docs
- [React Router](https://reactrouter.com/) - Official routing docs
- [Testing Library](https://testing-library.com/) - Official testing docs

### Recommended Courses
- [Epic React by Kent C. Dodds](https://epicreact.dev/) - Comprehensive React course
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/) - TypeScript patterns
- [Total TypeScript](https://www.totaltypescript.com/) - TypeScript mastery

### Community Resources
- [React Newsletter](https://react.statuscode.com/) - Weekly React news
- [This Week in React](https://thisweekinreact.com/) - Weekly newsletter
- [r/reactjs](https://reddit.com/r/reactjs) - Reddit community
- [Reactiflux Discord](https://www.reactiflux.com/) - Discord community

### Tools and Extensions
- [React DevTools](https://react.dev/learn/react-developer-tools) - Browser extension
- [Redux DevTools](https://github.com/reduxjs/redux-devtools) - State debugging
- [React Hook Form DevTools](https://react-hook-form.com/dev-tools) - Form debugging

---

## Cross-Links to Related Topics

### TypeScript
- [[TypeScript_Fundamentals]] - TypeScript basics for React
- [[TypeScript_Advanced_Types]] - Advanced type patterns
- [[TypeScript_React_Patterns]] - React-specific TypeScript patterns

### Testing
- [[Jest_Configuration]] - Test runner setup
- [[Vitest_Migration]] - Migrating from Jest to Vitest
- [[E2E_Testing_Playwright]] - End-to-end testing

### Build Tools
- [[Vite_Configuration]] - Vite setup and optimization
- [[ESLint_Prettier_Setup]] - Code quality tools

### Deployment
- [[Docker_React_Deployment]] - Containerizing React apps
- [[CI_CD_GitHub_Actions]] - Automated deployment

---

## Statistics

- **Total Files:** 24 comprehensive guides + 1 MOC
- **Total Lines:** ~30,000
- **Total Interview Questions:** ~80 (8 per guide × 10+ guides)
- **Code Examples:** 500+
- **Diagrams:** 50+ Mermaid diagrams
- **Complete Projects:** 3
- **Debugging Workflows:** 3
- **Playbooks:** 10 (including Animation + E2E + Tailwind + Real-Time)

---

## Contributing

This is a living document. Update dates and add new content as React evolves.

**Last Major Update:** 2026-05-09
- ✅ All 24 files completed
- ✅ React 18/19 patterns
- ✅ TypeScript-first approach
- ✅ Production-ready examples
- ✅ Animation (Framer Motion)
- ✅ E2E Testing (Playwright)
- ✅ Real-Time patterns (WebSocket)
- ✅ Next.js App Router + Server Components
- ✅ Portals + Tailwind + TypeScript patterns

---

## Related

- [[JavaScript_Fundamentals_MOC]]
- [[TypeScript_MOC]]
- [[Web_Development_MOC]]

## References

- [React Official Docs](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [React Router](https://reactrouter.com/)
- [Testing Library](https://testing-library.com/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
