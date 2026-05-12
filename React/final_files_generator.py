#!/usr/bin/env python3
"""
Generate the final 4 comprehensive React documentation files
"""

def generate_file_5_vite_starter():
    """Generate comprehensive Vite starter app guide (1200+ lines)"""
    content = """---
tags: [react, vite, typescript, rtk-query, project, starter]
aliases: ["Vite Starter App"]
status: stable
updated: 2026-04-26
---

# Vite + React Router + TypeScript + RTK + RTK Query Starter App

> [!summary] Goal
> Production-ready starter template with authentication, routing, state management, and API integration. 100% copy-paste ready code.

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Setup Instructions](#setup-instructions)
- [Complete Code](#complete-code)
- [Authentication Flow](#authentication-flow)
- [API Integration](#api-integration)
- [Routing Setup](#routing-setup)
- [Redux Configuration](#redux-configuration)
- [Form Validation](#form-validation)
- [Deployment](#deployment)

---

## Project Overview

Complete production-ready starter with:

✅ **Authentication System**
- Login/Logout flow
- JWT token management
- Automatic token refresh
- Protected routes
- Persistent auth state (localStorage)

✅ **Routing**
- React Router 6
- Nested routes
- Protected routes
- 404 handling
- Programmatic navigation

✅ **State Management**
- Redux Toolkit for global state
- RTK Query for server data
- Automatic cache management
- Optimistic updates
- Tag-based invalidation

✅ **Forms**
- React Hook Form integration
- Zod schema validation
- Type-safe forms
- Error handling
- Field-level validation

✅ **Developer Experience**
- TypeScript strict mode
- ESLint + Prettier
- Hot Module Replacement
- Path aliases (@/)
- Environment variables

✅ **Production Ready**
- Docker support
- Nginx configuration
- Error boundaries
- Loading states
- Environment configs

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Vite** | 5.x | Lightning-fast build tool |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **React Router** | 6.x | Client-side routing |
| **Redux Toolkit** | 2.x | State management |
| **RTK Query** | 2.x | Data fetching & caching |
| **React Hook Form** | 7.x | Form handling |
| **Zod** | 3.x | Schema validation |

---

## Folder Structure

```
my-app/
├── public/
│   └── vite.svg
├── src/
│   ├── app/                          # Application core
│   │   ├── App.tsx                   # Main app component
│   │   ├── AppProviders.tsx          # Redux/Router providers
│   │   ├── router.tsx                # Route configuration
│   │   ├── store.ts                  # Redux store setup
│   │   └── api/
│   │       └── baseApi.ts            # RTK Query base API
│   │
│   ├── features/                     # Feature modules
│   │   ├── auth/
│   │   │   ├── api/
│   │   │   │   └── authApi.ts        # Auth endpoints
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx     # Login form component
│   │   │   │   └── ProtectedRoute.tsx # Route guard
│   │   │   ├── slices/
│   │   │   │   └── authSlice.ts      # Auth Redux slice
│   │   │   ├── types/
│   │   │   │   └── index.ts          # Auth types
│   │   │   └── index.ts              # Public API
│   │   │
│   │   └── products/
│   │       ├── api/
│   │       │   └── productsApi.ts    # Product endpoints
│   │       ├── components/
│   │       │   ├── ProductList.tsx
│   │       │   ├── ProductCard.tsx
│   │       │   ├── ProductDetails.tsx
│   │       │   └── ProductForm.tsx
│   │       ├── types/
│   │       │   └── index.ts
│   │       └── index.ts
│   │
│   ├── shared/                       # Shared code
│   │   ├── components/               # Reusable UI components
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.module.css
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Input.module.css
│   │   │   │   └── index.ts
│   │   │   ├── Spinner/
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── Spinner.module.css
│   │   │   ├── ErrorBoundary/
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   └── index.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useDebounce.ts
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   ├── storage.ts            # localStorage wrapper
│   │   │   ├── validators.ts
│   │   │   └── index.ts
│   │   └── types/
│   │       ├── api.ts
│   │       └── index.ts
│   │
│   ├── pages/                        # Route pages
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── ProductsPage.tsx
│   │   ├── ProductDetailPage.tsx
│   │   ├── NotFoundPage.tsx
│   │   └── index.ts
│   │
│   ├── layouts/                      # Layout components
│   │   ├── MainLayout.tsx
│   │   └── AuthLayout.tsx
│   │
│   ├── styles/
│   │   └── global.css
│   │
│   ├── main.tsx                      # Entry point
│   └── vite-env.d.ts
│
├── .env.development
├── .env.production
├── .eslintrc.cjs
├── .prettier rc
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── package.json
└── README.md
```

---

## Setup Instructions

### 1. Create Project

```bash
# Create Vite project with React + TypeScript template
npm create vite@latest my-app -- --template react-ts
cd my-app
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install react-router-dom @reduxjs/toolkit react-redux

# Form handling
npm install react-hook-form zod @hookform/resolvers

# Dev dependencies
npm install --save-dev @types/node
```

### 3. Configure Path Aliases

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**vite.config.ts:**
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'redux-vendor': ['@reduxjs/toolkit', 'react-redux'],
        },
      },
    },
  },
});
```

### 4. Create Folder Structure

```bash
mkdir -p src/{app/{api},features/{auth/{api,components,slices,types},products/{api,components,types}},shared/{components,hooks,utils,types},pages,layouts,styles}
```

---

## Complete Code

### Package.json

```json
{
  "name": "vite-react-starter",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.22.3",
    "@reduxjs/toolkit": "^2.2.1",
    "react-redux": "^9.1.0",
    "react-hook-form": "^7.51.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/node": "^20.11.30",
    "@typescript-eslint/eslint-plugin": "^7.2.0",
    "@typescript-eslint/parser": "^7.2.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.6",
    "prettier": "^3.2.5",
    "typescript": "^5.4.3",
    "vite": "^5.2.0"
  }
}
```

### Redux Store

```ts
// src/app/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { baseApi } from './api/baseApi';
import authReducer from '@/features/auth/slices/authSlice';

export const store = configureStore({
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
  devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
import { useDispatch, useSelector } from 'react-redux';
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
```

### RTK Query Base API

```ts
// src/app/api/baseApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store';

const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:3000/api',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

// Base query with automatic re-authentication
const baseQueryWithReauth = async (args: any, api: any, extraOptions: any) => {
  let result = await baseQuery(args, api, extraOptions);
  
  if (result.error && result.error.status === 401) {
    // Try to refresh token
    const refreshResult = await baseQuery(
      { url: '/auth/refresh', method: 'POST' },
      api,
      extraOptions
    );
    
    if (refreshResult.data) {
      // Store new token and retry request
      api.dispatch({
        type: 'auth/tokenRefreshed',
        payload: refreshResult.data,
      });
      result = await baseQuery(args, api, extraOptions);
    } else {
      // Refresh failed, logout user
      api.dispatch({ type: 'auth/logout' });
    }
  }
  
  return result;
};

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Product', 'User'],
  endpoints: () => ({}),
});
```

### Auth Slice

```ts
// src/features/auth/slices/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { storage } from '@/shared/utils/storage';

export interface User {
  id: number;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

// Initialize with token from localStorage
const token = storage.getToken();

const initialState: AuthState = {
  user: null,
  token,
  isAuthenticated: !!token,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string }>
    ) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      storage.setToken(action.payload.token);
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      storage.removeToken();
    },
    tokenRefreshed: (state, action: PayloadAction<{ token: string }>) => {
      state.token = action.payload.token;
      storage.setToken(action.payload.token);
    },
  },
});

export const { setCredentials, logout, tokenRefreshed } = authSlice.actions;
export default authSlice.reducer;
```

### Auth API

```ts
// src/features/auth/api/authApi.ts
import { baseApi } from '@/app/api/baseApi';
import type { User } from '../slices/authSlice';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  user: User;
  token: string;
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
    }),
    getProfile: builder.query<User, void>({
      query: () => '/auth/profile',
      providesTags: ['User'],
    }),
  }),
});

export const {
  useLoginMutation,
  useLogoutMutation,
  useGetProfileQuery,
} = authApi;
```

### Login Form

```tsx
// src/features/auth/components/LoginForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { useLoginMutation } from '../api/authApi';
import { useAppDispatch } from '@/app/store';
import { setCredentials } from '../slices/authSlice';
import { Button, Input } from '@/shared/components';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [login, { isLoading, error }] = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      const result = await login(data).unwrap();
      dispatch(setCredentials(result));
      navigate('/products');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="login-form">
      <div className="form-group">
        <Input
          label="Email"
          type="email"
          error={errors.email?.message}
          {...register('email')}
        />
      </div>

      <div className="form-group">
        <Input
          label="Password"
          type="password"
          error={errors.password?.message}
          {...register('password')}
        />
      </div>

      {error && (
        <div className="error-message">
          Login failed. Please check your credentials.
        </div>
      )}

      <Button type="submit" loading={isLoading} className="submit-button">
        Log In
      </Button>
    </form>
  );
};
```

### Protected Route

```tsx
// src/features/auth/components/ProtectedRoute.tsx
import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '@/app/store';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated } = useAppSelector(state => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

### Products API

```ts
// src/features/products/api/productsApi.ts
import { baseApi } from '@/app/api/baseApi';

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl?: string;
}

export const productsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getProducts: builder.query<Product[], void>({
      query: () => '/products',
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Product' as const, id })),
              { type: 'Product', id: 'LIST' },
            ]
          : [{ type: 'Product', id: 'LIST' }],
    }),

    getProduct: builder.query<Product, number>({
      query: (id) => `/products/${id}`,
      providesTags: (result, error, id) => [{ type: 'Product', id }],
    }),

    createProduct: builder.mutation<Product, Partial<Product>>({
      query: (body) => ({
        url: '/products',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
    }),

    updateProduct: builder.mutation<
      Product,
      { id: number; data: Partial<Product> }
    >({
      query: ({ id, data }) => ({
        url: `/products/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Product', id },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    deleteProduct: builder.mutation<void, number>({
      query: (id) => ({
        url: `/products/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Product', id },
        { type: 'Product', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetProductsQuery,
  useGetProductQuery,
  useCreateProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
} = productsApi;
```

### Product List Component

```tsx
// src/features/products/components/ProductList.tsx
import { useGetProductsQuery } from '../api/productsApi';
import { ProductCard } from './ProductCard';
import { Spinner } from '@/shared/components';

export const ProductList = () => {
  const { data: products, isLoading, error } = useGetProductsQuery();

  if (isLoading) {
    return (
      <div className="loading-container">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>Error loading products. Please try again later.</p>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="empty-state">
        <p>No products found.</p>
      </div>
    );
  }

  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};
```

### Product Card Component

```tsx
// src/features/products/components/ProductCard.tsx
import { Link } from 'react-router-dom';
import type { Product } from '../api/productsApi';
import { useDeleteProductMutation } from '../api/productsApi';
import { Button } from '@/shared/components';

interface ProductCardProps {
  product: Product;
}

export const ProductCard = ({ product }: ProductCardProps) => {
  const [deleteProduct, { isLoading }] = useDeleteProductMutation();

  const handleDelete = async () => {
    if (confirm(`Delete ${product.name}?`)) {
      try {
        await deleteProduct(product.id).unwrap();
      } catch (err) {
        console.error('Delete failed:', err);
      }
    }
  };

  return (
    <div className="product-card">
      {product.imageUrl && (
        <img src={product.imageUrl} alt={product.name} />
      )}
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="product-description">{product.description}</p>
        <p className="product-price">${product.price}</p>
        <div className="product-actions">
          <Link to={`/products/${product.id}`}>
            <Button variant="secondary">View Details</Button>
          </Link>
          <Button onClick={handleDelete} loading={isLoading} variant="danger">
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};
```

### Router Configuration

```tsx
// src/app/router.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '@/layouts/MainLayout';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { HomePage } from '@/pages/HomePage';
import { LoginPage } from '@/pages/LoginPage';
import { ProductsPage } from '@/pages/ProductsPage';
import { ProductDetailPage } from '@/pages/ProductDetailPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/products" replace />,
      },
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'products',
        element: (
          <ProtectedRoute>
            <ProductsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'products/:id',
        element: (
          <ProtectedRoute>
            <ProductDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);
```

### App Providers

```tsx
// src/app/AppProviders.tsx
import { Provider } from 'react-redux';
import { RouterProvider } from 'react-router-dom';
import { store } from './store';
import { router } from './router';

export const AppProviders = () => {
  return (
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  );
};
```

### Main App Component

```tsx
// src/app/App.tsx
import { AppProviders } from './AppProviders';
import { ErrorBoundary } from '@/shared/components/ErrorBoundary';
import '@/styles/global.css';

export const App = () => {
  return (
    <ErrorBoundary>
      <AppProviders />
    </ErrorBoundary>
  );
};

export default App;
```

### Main Layout

```tsx
// src/layouts/MainLayout.tsx
import { Outlet, Link } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '@/app/store';
import { logout } from '@/features/auth/slices/authSlice';
import { useLogoutMutation } from '@/features/auth/api/authApi';
import { Button } from '@/shared/components';

export const MainLayout = () => {
  const { isAuthenticated, user } = useAppSelector(state => state.auth);
  const dispatch = useAppDispatch();
  const [logoutMutation] = useLogoutMutation();

  const handleLogout = async () => {
    try {
      await logoutMutation().unwrap();
    } finally {
      dispatch(logout());
    }
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <nav>
          <Link to="/" className="logo">
            My App
          </Link>
          <div className="nav-links">
            {isAuthenticated ? (
              <>
                <Link to="/products">Products</Link>
                <span>Welcome, {user?.name}</span>
                <Button onClick={handleLogout} variant="secondary">
                  Logout
                </Button>
              </>
            ) : (
              <Link to="/login">Login</Link>
            )}
          </div>
        </nav>
      </header>

      <main className="app-main">
        <Outlet />
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 My App. All rights reserved.</p>
      </footer>
    </div>
  );
};
```

### Shared Components

**Button:**

```tsx
// src/shared/components/Button/Button.tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
  children: ReactNode;
}

export const Button = ({
  children,
  variant = 'primary',
  loading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) => {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <span className={styles.spinner} /> : null}
      {children}
    </button>
  );
};
```

**Input:**

```tsx
// src/shared/components/Input/Input.tsx
import { forwardRef, InputHTMLAttributes } from 'react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className={styles.wrapper}>
        {label && (
          <label htmlFor={props.id} className={styles.label}>
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`${styles.input} ${error ? styles.error : ''} ${className}`}
          {...props}
        />
        {error && <span className={styles.errorText}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

**Spinner:**

```tsx
// src/shared/components/Spinner/Spinner.tsx
import styles from './Spinner.module.css';

export const Spinner = () => {
  return (
    <div className={styles.spinner}>
      <div className={styles.circle}></div>
    </div>
  );
};
```

**Error Boundary:**

```tsx
// src/shared/components/ErrorBoundary/ErrorBoundary.tsx
import { Component, ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Utility Functions

**Storage:**

```ts
// src/shared/utils/storage.ts
const TOKEN_KEY = 'auth_token';

export const storage = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  clear(): void {
    localStorage.clear();
  },
};
```

### Environment Files

**.env.development:**

```bash
VITE_API_URL=http://localhost:3000/api
VITE_APP_ENV=development
```

**.env.production:**

```bash
VITE_API_URL=https://api.example.com
VITE_APP_ENV=production
```

### Deployment

**Dockerfile:**

```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf:**

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  # Enable gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

  # Security headers
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-XSS-Protection "1; mode=block" always;

  # SPA routing
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API proxy
  location /api {
    proxy_pass http://backend:3000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  # Cache static assets
  location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
}
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://backend:3000/api
    depends_on:
      - backend

  backend:
    image: your-backend-image:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant LoginForm
    participant RTK Query
    participant Redux Store
    participant LocalStorage
    participant API Server

    User->>LoginForm: Enter credentials
    LoginForm->>RTK Query: login mutation
    RTK Query->>API Server: POST /auth/login
    API Server-->>RTK Query: { user, token }
    RTK Query-->>LoginForm: Success
    LoginForm->>Redux Store: dispatch setCredentials
    Redux Store->>LocalStorage: Save token
    Redux Store-->>User: Redirect to /products
```

---

## Build and Run

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
npm run preview
```

### Docker

```bash
# Build
docker build -t my-app .

# Run
docker run -p 80:80 my-app

# Or use docker-compose
docker-compose up -d
```

---

## Next Steps

1. **Add Features:**
   - User profile page
   - Settings page
   - Admin panel
   - Search functionality

2. **Testing:**
   - Add Vitest + Testing Library
   - Write unit tests
   - Write integration tests

3. **Performance:**
   - Add code splitting
   - Implement virtualization for lists
   - Optimize images

4. **Monitoring:**
   - Add Sentry for error tracking
   - Add analytics (Google Analytics, Mixpanel)
   - Add performance monitoring

5. **CI/CD:**
   - Set up GitHub Actions
   - Automate testing
   - Automate deployment

---

## Related

- [[01_Redux_Toolkit_Essentials]]
- [[02_RTK_Query_Essentials]]
- [[03_Routing_with_React_Router]]
- [[04_Forms_and_Validation]]
- [[03_React_App_Architecture_Playbook]]

## References

- [Vite Documentation](https://vitejs.dev/)
- [React Router v6](https://reactrouter.com/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [RTK Query](https://redux-toolkit.js.org/rtk-query/overview)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)
"""
    return content

# Generate file content
content = generate_file_5_vite_starter()

# Write to file
with open('/home/rishav/Documents/personal/dsaPrep/React/05_Projects/01_Vite_RR_TS_RTK_RTKQ_Starter_App.md', 'w') as f:
    f.write(content)

# Count lines
line_count = content.count('\n')
print(f"File 5 complete: {line_count} lines")

