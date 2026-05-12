#!/bin/bash

# Generate File 6: Form Heavy App
cat > /tmp/file6_forms.md << 'EOF6'
---
tags: [react, forms, validation, project]
aliases: ["Form Heavy App"]
status: stable
updated: 2026-04-26
---

# Form Heavy App With Validation

> [!summary] Goal
> Comprehensive forms showcase with React Hook Form + Zod validation. Multi-step wizard, dynamic forms, nested forms, file uploads, and conditional forms.

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [App Structure](#app-structure)
- [Form Implementations](#form-implementations)
- [Validation Patterns](#validation-patterns)
- [Form State Persistence](#form-state-persistence)
- [API Integration](#api-integration)
- [Testing Examples](#testing-examples)
- [Complete Code](#complete-code)

---

## Project Overview

Five comprehensive form implementations:

1. **Multi-Step Registration Wizard** (3 steps)
   - Personal info → Address → Preferences
   - Progress indicator
   - Step validation
   - Back/Next navigation
   - Data persistence between steps

2. **Dynamic Product Form** (add/remove items)
   - useFieldArray for dynamic fields
   - Add/remove product variants
   - Nested validation
   - Total price calculation

3. **Nested Address Form**
   - Complex nested objects
   - Multiple addresses (shipping/billing)
   - Conditional validation
   - Address autocomplete

4. **File Upload Form**
   - Image upload with preview
   - File validation (size, type)
   - Multiple files
   - Progress indicator
   - Server integration

5. **Conditional Survey Form**
   - Dynamic questions based on previous answers
   - Show/hide fields
   - Complex validation rules
   - Branching logic

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| React 18 | UI library |
| TypeScript | Type safety |
| React Hook Form 7 | Form state management |
| Zod 3 | Schema validation |
| Axios | HTTP client |
| CSS Modules | Styling |

---

## App Structure

```
src/
├── forms/
│   ├── multi-step/
│   │   ├── MultiStepForm.tsx
│   │   ├── Step1Personal.tsx
│   │   ├── Step2Address.tsx
│   │   ├── Step3Preferences.tsx
│   │   └── schemas.ts
│   ├── dynamic/
│   │   ├── DynamicProductForm.tsx
│   │   └── ProductVariant.tsx
│   ├── nested/
│   │   ├── NestedAddressForm.tsx
│   │   └── AddressFields.tsx
│   ├── file-upload/
│   │   ├── FileUploadForm.tsx
│   │   └── FilePreview.tsx
│   └── conditional/
│       ├── ConditionalSurveyForm.tsx
│       └── DynamicQuestion.tsx
├── hooks/
│   ├── useMultiStepForm.ts
│   ├── useFormPersist.ts
│   └── useFileUpload.ts
├── components/
│   ├── FormField.tsx
│   ├── FormError.tsx
│   └── ProgressBar.tsx
└── utils/
    ├── validators.ts
    └── api.ts
```

---

## Form Implementations

### 1. Multi-Step Registration Wizard

**Hook:**
```ts
// hooks/useMultiStepForm.ts
import { useState } from 'react';

export const useMultiStepForm = (steps: number) => {
  const [currentStep, setCurrentStep] = useState(0);

  const next = () => {
    setCurrentStep(prev => Math.min(prev + 1, steps - 1));
  };

  const back = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const goTo = (step: number) => {
    setCurrentStep(Math.max(0, Math.min(step, steps - 1)));
  };

  return {
    currentStep,
    isFirstStep: currentStep === 0,
    isLastStep: currentStep === steps - 1,
    next,
    back,
    goTo,
    progress: ((currentStep + 1) / steps) * 100,
  };
};
```

**Schemas:**
```ts
// forms/multi-step/schemas.ts
import { z } from 'zod';

export const step1Schema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().regex(/^\d{10}$/, 'Phone must be 10 digits'),
});

export const step2Schema = z.object({
  street: z.string().min(5, 'Street address required'),
  city: z.string().min(2, 'City required'),
  state: z.string().length(2, 'State must be 2 characters'),
  zip: z.string().regex(/^\d{5}$/, 'ZIP must be 5 digits'),
});

export const step3Schema = z.object({
  newsletter: z.boolean(),
  notifications: z.enum(['email', 'sms', 'both', 'none']),
  interests: z.array(z.string()).min(1, 'Select at least one interest'),
});

export const fullSchema = z.object({
  ...step1Schema.shape,
  ...step2Schema.shape,
  ...step3Schema.shape,
});

export type FullFormData = z.infer<typeof fullSchema>;
```

**Main Component:**
```tsx
// forms/multi-step/MultiStepForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMultiStepForm } from '@/hooks/useMultiStepForm';
import { useFormPersist } from '@/hooks/useFormPersist';
import { fullSchema, type FullFormData } from './schemas';
import { Step1Personal } from './Step1Personal';
import { Step2Address } from './Step2Address';
import { Step3Preferences } from './Step3Preferences';
import { ProgressBar } from '@/components/ProgressBar';

const steps = [Step1Personal, Step2Address, Step3Preferences];

export const MultiStepForm = () => {
  const {
    currentStep,
    isFirstStep,
    isLastStep,
    next,
    back,
    progress,
  } = useMultiStepForm(steps.length);

  const form = useForm<FullFormData>({
    resolver: zodResolver(fullSchema),
    mode: 'onBlur',
  });

  useFormPersist('multiStepForm', form.watch, form.setValue);

  const onSubmit = async (data: FullFormData) => {
    if (!isLastStep) {
      next();
      return;
    }

    try {
      await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      localStorage.removeItem('multiStepForm');
      alert('Registration complete!');
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  const CurrentStepComponent = steps[currentStep];

  return (
    <div className="multi-step-form">
      <ProgressBar progress={progress} />
      
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <CurrentStepComponent form={form} />

        <div className="form-actions">
          {!isFirstStep && (
            <button type="button" onClick={back}>
              Back
            </button>
          )}
          <button type="submit">
            {isLastStep ? 'Submit' : 'Next'}
          </button>
        </div>
      </form>
    </div>
  );
};
```

**Step Components:**
```tsx
// forms/multi-step/Step1Personal.tsx
import { UseFormReturn } from 'react-hook-form';
import { FullFormData } from './schemas';
import { FormField } from '@/components/FormField';

interface Step1Props {
  form: UseFormReturn<FullFormData>;
}

export const Step1Personal = ({ form }: Step1Props) => {
  const { register, formState: { errors } } = form;

  return (
    <div className="form-step">
      <h2>Personal Information</h2>

      <FormField
        label="First Name"
        error={errors.firstName?.message}
      >
        <input {...register('firstName')} />
      </FormField>

      <FormField
        label="Last Name"
        error={errors.lastName?.message}
      >
        <input {...register('lastName')} />
      </FormField>

      <FormField
        label="Email"
        type="email"
        error={errors.email?.message}
      >
        <input {...register('email')} />
      </FormField>

      <FormField
        label="Phone"
        error={errors.phone?.message}
      >
        <input {...register('phone')} placeholder="1234567890" />
      </FormField>
    </div>
  );
};
```

---

### 2. Dynamic Product Form

**Component:**
```tsx
// forms/dynamic/DynamicProductForm.tsx
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const variantSchema = z.object({
  name: z.string().min(1, 'Variant name required'),
  sku: z.string().min(1, 'SKU required'),
  price: z.number().min(0, 'Price must be positive'),
  quantity: z.number().int().min(0, 'Quantity must be non-negative'),
});

const productSchema = z.object({
  productName: z.string().min(1, 'Product name required'),
  category: z.string().min(1, 'Category required'),
  variants: z.array(variantSchema).min(1, 'At least one variant required'),
});

type ProductFormData = z.infer<typeof productSchema>;

export const DynamicProductForm = () => {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      productName: '',
      category: '',
      variants: [{ name: '', sku: '', price: 0, quantity: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'variants',
  });

  const variants = watch('variants');
  const totalValue = variants.reduce(
    (sum, v) => sum + (v.price || 0) * (v.quantity || 0),
    0
  );

  const onSubmit = (data: ProductFormData) => {
    console.log('Product data:', data);
    console.log('Total value:', totalValue);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="dynamic-form">
      <h2>Product Form</h2>

      <div className="form-group">
        <label>Product Name</label>
        <input {...register('productName')} />
        {errors.productName && (
          <span className="error">{errors.productName.message}</span>
        )}
      </div>

      <div className="form-group">
        <label>Category</label>
        <input {...register('category')} />
        {errors.category && (
          <span className="error">{errors.category.message}</span>
        )}
      </div>

      <div className="variants-section">
        <h3>Variants</h3>

        {fields.map((field, index) => (
          <div key={field.id} className="variant-row">
            <input
              {...register(`variants.${index}.name`)}
              placeholder="Variant name"
            />
            <input
              {...register(`variants.${index}.sku`)}
              placeholder="SKU"
            />
            <input
              {...register(`variants.${index}.price`, { valueAsNumber: true })}
              type="number"
              step="0.01"
              placeholder="Price"
            />
            <input
              {...register(`variants.${index}.quantity`, { valueAsNumber: true })}
              type="number"
              placeholder="Quantity"
            />
            <button
              type="button"
              onClick={() => remove(index)}
              disabled={fields.length === 1}
            >
              Remove
            </button>
            {errors.variants?.[index] && (
              <div className="error">
                {Object.values(errors.variants[index]!).map((err: any) => (
                  <div key={err.message}>{err.message}</div>
                ))}
              </div>
            )}
          </div>
        ))}

        <button
          type="button"
          onClick={() => append({ name: '', sku: '', price: 0, quantity: 0 })}
        >
          Add Variant
        </button>
      </div>

      <div className="total-value">
        <strong>Total Value: ${totalValue.toFixed(2)}</strong>
      </div>

      <button type="submit">Save Product</button>
    </form>
  );
};
```

---

### 3. File Upload Form

**Component:**
```tsx
// forms/file-upload/FileUploadForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState } from 'react';
import { FilePreview } from './FilePreview';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const fileUploadSchema = z.object({
  title: z.string().min(1, 'Title required'),
  description: z.string().optional(),
  images: z
    .custom<FileList>()
    .refine((files) => files.length > 0, 'At least one image required')
    .refine(
      (files) => Array.from(files).every((file) => file.size <= MAX_FILE_SIZE),
      'Each file must be less than 5MB'
    )
    .refine(
      (files) =>
        Array.from(files).every((file) =>
          ACCEPTED_IMAGE_TYPES.includes(file.type)
        ),
      'Only .jpg, .png, and .webp formats are supported'
    ),
});

type FileUploadFormData = z.infer<typeof fileUploadSchema>;

export const FileUploadForm = () => {
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FileUploadFormData>({
    resolver: zodResolver(fileUploadSchema),
  });

  const images = watch('images');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const newPreviews: string[] = [];
    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newPreviews.push(reader.result as string);
        if (newPreviews.length === files.length) {
          setPreviews(newPreviews);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const onSubmit = async (data: FileUploadFormData) => {
    setUploading(true);

    const formData = new FormData();
    formData.append('title', data.title);
    if (data.description) {
      formData.append('description', data.description);
    }

    Array.from(data.images).forEach((file, index) => {
      formData.append(`images[${index}]`, file);
    });

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert('Upload successful!');
        setPreviews([]);
      } else {
        alert('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="file-upload-form">
      <h2>Upload Images</h2>

      <div className="form-group">
        <label>Title</label>
        <input {...register('title')} />
        {errors.title && <span className="error">{errors.title.message}</span>}
      </div>

      <div className="form-group">
        <label>Description (optional)</label>
        <textarea {...register('description')} rows={3} />
      </div>

      <div className="form-group">
        <label>Images</label>
        <input
          type="file"
          accept="image/*"
          multiple
          {...register('images')}
          onChange={handleFileChange}
        />
        {errors.images && (
          <span className="error">{errors.images.message as string}</span>
        )}
      </div>

      {previews.length > 0 && (
        <div className="previews">
          <h3>Previews:</h3>
          <div className="preview-grid">
            {previews.map((preview, index) => (
              <FilePreview key={index} src={preview} />
            ))}
          </div>
        </div>
      )}

      <button type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </form>
  );
};
```

**Preview Component:**
```tsx
// forms/file-upload/FilePreview.tsx
interface FilePreviewProps {
  src: string;
}

export const FilePreview = ({ src }: FilePreviewProps) => {
  return (
    <div className="file-preview">
      <img src={src} alt="Preview" />
    </div>
  );
};
```

---

### 4. Conditional Survey Form

**Component:**
```tsx
// forms/conditional/ConditionalSurveyForm.tsx
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const surveySchema = z
  .object({
    employed: z.enum(['yes', 'no']),
    jobTitle: z.string().optional(),
    yearsExperience: z.number().optional(),
    seeking: z.enum(['yes', 'no']).optional(),
    desiredRole: z.string().optional(),
    education: z.enum(['highschool', 'bachelors', 'masters', 'phd']),
    graduationYear: z.number().min(1900).max(2030).optional(),
    feedback: z.string().min(10, 'Feedback must be at least 10 characters'),
  })
  .refine(
    (data) => {
      if (data.employed === 'yes') {
        return !!data.jobTitle && data.yearsExperience !== undefined;
      }
      return true;
    },
    {
      message: 'Job title and experience required if employed',
      path: ['jobTitle'],
    }
  )
  .refine(
    (data) => {
      if (data.employed === 'no' && data.seeking === 'yes') {
        return !!data.desiredRole;
      }
      return true;
    },
    {
      message: 'Desired role required if seeking employment',
      path: ['desiredRole'],
    }
  );

type SurveyFormData = z.infer<typeof surveySchema>;

export const ConditionalSurveyForm = () => {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<SurveyFormData>({
    resolver: zodResolver(surveySchema),
  });

  const employed = useWatch({ control, name: 'employed' });
  const seeking = useWatch({ control, name: 'seeking' });
  const education = useWatch({ control, name: 'education' });

  const onSubmit = (data: SurveyFormData) => {
    console.log('Survey data:', data);
    alert('Survey submitted!');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="survey-form">
      <h2>Employment Survey</h2>

      <div className="form-group">
        <label>Are you currently employed?</label>
        <select {...register('employed')}>
          <option value="">Select...</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
        </select>
        {errors.employed && (
          <span className="error">{errors.employed.message}</span>
        )}
      </div>

      {employed === 'yes' && (
        <>
          <div className="form-group">
            <label>Job Title</label>
            <input {...register('jobTitle')} />
            {errors.jobTitle && (
              <span className="error">{errors.jobTitle.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Years of Experience</label>
            <input
              type="number"
              {...register('yearsExperience', { valueAsNumber: true })}
            />
            {errors.yearsExperience && (
              <span className="error">{errors.yearsExperience.message}</span>
            )}
          </div>
        </>
      )}

      {employed === 'no' && (
        <>
          <div className="form-group">
            <label>Are you seeking employment?</label>
            <select {...register('seeking')}>
              <option value="">Select...</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>

          {seeking === 'yes' && (
            <div className="form-group">
              <label>Desired Role</label>
              <input {...register('desiredRole')} />
              {errors.desiredRole && (
                <span className="error">{errors.desiredRole.message}</span>
              )}
            </div>
          )}
        </>
      )}

      <div className="form-group">
        <label>Education Level</label>
        <select {...register('education')}>
          <option value="">Select...</option>
          <option value="highschool">High School</option>
          <option value="bachelors">Bachelor's Degree</option>
          <option value="masters">Master's Degree</option>
          <option value="phd">PhD</option>
        </select>
        {errors.education && (
          <span className="error">{errors.education.message}</span>
        )}
      </div>

      {(education === 'bachelors' ||
        education === 'masters' ||
        education === 'phd') && (
        <div className="form-group">
          <label>Graduation Year</label>
          <input
            type="number"
            {...register('graduationYear', { valueAsNumber: true })}
          />
          {errors.graduationYear && (
            <span className="error">{errors.graduationYear.message}</span>
          )}
        </div>
      )}

      <div className="form-group">
        <label>Additional Feedback</label>
        <textarea {...register('feedback')} rows={4} />
        {errors.feedback && (
          <span className="error">{errors.feedback.message}</span>
        )}
      </div>

      <button type="submit">Submit Survey</button>
    </form>
  );
};
```

---

## Hooks

### Form Persistence Hook

```ts
// hooks/useFormPersist.ts
import { useEffect } from 'react';

export const useFormPersist = <T>(
  key: string,
  watch: () => T,
  setValue: (name: any, value: any) => void
) => {
  // Save to localStorage on change
  useEffect(() => {
    const subscription = watch((data) => {
      localStorage.setItem(key, JSON.stringify(data));
    });
    return () => subscription.unsubscribe();
  }, [key, watch]);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(key);
    if (saved) {
      const data = JSON.parse(saved);
      Object.keys(data).forEach((fieldName) => {
        setValue(fieldName, data[fieldName]);
      });
    }
  }, [key, setValue]);
};
```

---

## Validation Patterns

### Common Validators

```ts
// utils/validators.ts
import { z } from 'zod';

// Email
export const emailValidator = z.string().email('Invalid email');

// Phone
export const phoneValidator = z
  .string()
  .regex(/^\d{10}$/, 'Phone must be 10 digits');

// Password
export const passwordValidator = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain uppercase letter')
  .regex(/[a-z]/, 'Password must contain lowercase letter')
  .regex(/[0-9]/, 'Password must contain number');

// URL
export const urlValidator = z.string().url('Invalid URL');

// Credit Card
export const creditCardValidator = z
  .string()
  .regex(/^\d{16}$/, 'Credit card must be 16 digits');

// Date in future
export const futureDateValidator = z
  .date()
  .refine((date) => date > new Date(), 'Date must be in the future');

// Confirm password
export const confirmPasswordValidator = (passwordField: string) =>
  z.object({
    [passwordField]: z.string(),
    confirmPassword: z.string(),
  }).refine((data) => data[passwordField] === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });
```

---

## Testing

```tsx
// forms/__tests__/MultiStepForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MultiStepForm } from '../multi-step/MultiStepForm';

describe('MultiStepForm', () => {
  test('validates step 1 before proceeding', async () => {
    render(<MultiStepForm />);

    const nextButton = screen.getByText('Next');
    await userEvent.click(nextButton);

    expect(await screen.findByText(/first name must be/i)).toBeInTheDocument();
  });

  test('navigates through all steps', async () => {
    render(<MultiStepForm />);

    // Step 1
    await userEvent.type(screen.getByLabelText(/first name/i), 'John');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Doe');
    await userEvent.type(screen.getByLabelText(/email/i), 'john@example.com');
    await userEvent.type(screen.getByLabelText(/phone/i), '1234567890');
    await userEvent.click(screen.getByText('Next'));

    // Step 2
    await waitFor(() => {
      expect(screen.getByText(/address information/i)).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText(/street/i), '123 Main St');
    await userEvent.type(screen.getByLabelText(/city/i), 'Boston');
    await userEvent.type(screen.getByLabelText(/state/i), 'MA');
    await userEvent.type(screen.getByLabelText(/zip/i), '02101');
    await userEvent.click(screen.getByText('Next'));

    // Step 3
    await waitFor(() => {
      expect(screen.getByText(/preferences/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Submit')).toBeInTheDocument();
  });

  test('persists form data between steps', async () => {
    const { rerender } = render(<MultiStepForm />);

    await userEvent.type(screen.getByLabelText(/first name/i), 'John');
    await userEvent.click(screen.getByText('Next'));

    // Remount component (simulates navigation away and back)
    rerender(<MultiStepForm />);

    // Data should be restored from localStorage
    expect(screen.getByLabelText(/first name/i)).toHaveValue('John');
  });
});
```

---

## Related

- [[04_Forms_and_Validation]]
- [[02_Hooks_Complete_Reference]]
- [[01_Vite_RR_TS_RTK_RTKQ_Starter_App]]

## References

- [React Hook Form](https://react-hook-form.com/)
- [Zod Documentation](https://zod.dev/)
- [useFieldArray](https://react-hook-form.com/docs/usefieldarray)
- [Form Validation](https://react-hook-form.com/get-started#Applyvalidation)
EOF6

mv /tmp/file6_forms.md /home/rishav/Documents/personal/dsaPrep/React/05_Projects/02_Form_Heavy_App_With_Validation.md

echo "File 6 complete: $(wc -l < /home/rishav/Documents/personal/dsaPrep/React/05_Projects/02_Form_Heavy_App_With_Validation.md) lines"

