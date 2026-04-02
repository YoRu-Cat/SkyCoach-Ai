# Frontend Hooks

**Location:** `frontend/src/hooks/`

## useApi.ts

### `useFullAnalysis()`

React Query mutation hook for complete activity analysis.

**Mutation Function:**

```typescript
(data) =>
  apiClient.post("/analyze", {
    activity_text: data.activity,
    city: data.city,
    use_openai: false,
    weather_api_key: null,
    openai_api_key: null,
    use_demo_weather: true,
  });
```

**Returns:**

- `mutate(data, options)` - Trigger analysis
- `isLoading` - Loading state
- Error and data states via React Query

**Usage:**

```typescript
const { mutate: runAnalysis, isLoading } = useFullAnalysis();

runAnalysis(
  { activity: "playing soccer", city: "New York" },
  {
    onSuccess: (data) => setAnalysis(data),
    onError: (error) => console.error(error),
  },
);
```

### Error Handling

- Errors passed to `onError` callback
- Loading state managed automatically
- Allows retry and error recovery
