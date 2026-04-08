# ML System Integration

## Backend Integration Points

`backend/api/routes.py` integrates `ml_system` through:

- `POST /api/predict` -> `get_ml_system().predict(...)`
- `POST /api/feedback` -> `get_ml_system().submit_feedback(...)`
- `GET /api/learning-status` -> `get_ml_system().get_status()`

## Analyze Route Relationship

- `POST /api/analyze-task` and `POST /api/analyze` use local task analysis flow.
- Those task-analysis routes are not OpenAI-first in active behavior.

## Confidence and Uncertainty

- Runtime confidence threshold: 0.62
- Predictions below threshold can map to `Unclear` and feed learning queues.

## Minimal Validation Commands

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/health
```

```powershell
$body = '{"phrase":"going to tobacco shop"}'
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/predict -Method Post -ContentType 'application/json' -Body $body
```

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/learning-status
```
