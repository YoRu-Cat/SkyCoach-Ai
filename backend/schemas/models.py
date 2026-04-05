"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Literal


class TaskAnalysisRequest(BaseModel):
    """Request to analyze an activity task."""
    text: str = Field(..., description="Activity description in plain language", min_length=1)
    use_openai: bool = Field(False, description="Use OpenAI API instead of fallback")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key if using OpenAI")
    openai_model: Optional[str] = Field(None, description="OpenAI model override, e.g. gpt-4.1-mini")


class TaskAnalysisResponse(BaseModel):
    """Response from task analysis."""
    original_text: str
    cleaned_text: str
    activity: str
    classification: Literal["Indoor", "Outdoor"]
    confidence: float
    reasoning: str
    needs_clarification: bool = False
    issue: Optional[str] = None
    suggested_activity: Optional[str] = None
    suggested_classification: Optional[str] = None
    suggestion_confidence: float = 0.0


class WeatherRequest(BaseModel):
    """Request weather data by city or coordinates."""
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    api_key: Optional[str] = None
    use_demo: bool = True


class WeatherResponse(BaseModel):
    """Response with weather information."""
    city: str
    country: str
    latitude: float
    longitude: float
    temperature: float
    feels_like: float
    humidity: int
    rain_1h: float
    is_raining: bool
    wind_speed: float
    wind_mph: float
    condition: str
    description: str
    icon_code: str
    units: str
    temp_unit: str


class SkyScoreRequest(BaseModel):
    """Request to calculate SkyScore."""
    task: TaskAnalysisResponse
    weather: WeatherResponse
    rain_threshold: float = 0.0
    wind_threshold_mph: float = 15.0
    heat_threshold_c: float = 30.0


class FactorDetail(BaseModel):
    """Detail of a scoring factor."""
    name: str
    value: int
    description: str


class SkyScoreResponse(BaseModel):
    """Response with SkyScore calculation."""
    score: int
    classification: str
    weather_factors: List[str]
    bonuses: List[FactorDetail]
    penalties: List[FactorDetail]
    recommendation: str


class AlternativeActivitiesResponse(BaseModel):
    """Response with alternative activity suggestions."""
    suggestions: List[Tuple[str, str]]
    reason: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Complete analysis request combining task, weather, and scoring."""
    activity_text: str
    city: str = "New York"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    use_openai: bool = False
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    weather_api_key: Optional[str] = None
    use_demo_weather: bool = True


class AnalysisResponse(BaseModel):
    """Complete analysis response."""
    task: TaskAnalysisResponse
    weather: WeatherResponse
    score_result: SkyScoreResponse
    alternatives: List[Tuple[str, str]]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatDraft(BaseModel):
    task_title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None


class ChatAssistantRequest(BaseModel):
    class ChatTaskContext(BaseModel):
        id: str
        title: str
        completed: bool = False
        scheduled_at: Optional[str] = None

    messages: List[ChatMessage]
    draft: ChatDraft = Field(default_factory=ChatDraft)
    task_context: List[ChatTaskContext] = Field(default_factory=list)
    today_iso: Optional[str] = None
    use_openai: bool = True
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None


class ChatAssistantResponse(BaseModel):
    assistant_message: str
    draft: ChatDraft
    missing_fields: List[Literal["task_title", "date", "time"]]
    requires_confirmation: bool
    create_task: bool
    remove_task_id: Optional[str] = None
    complete_task_id: Optional[str] = None
    uncomplete_task_id: Optional[str] = None
    reschedule_task_id: Optional[str] = None
    reschedule_date: Optional[str] = None
    reschedule_time: Optional[str] = None
    clear_completed: bool = False
    navigate_to: Literal["dashboard", "todo", "timetable", "planner", "chat"]
    reset_draft: bool


class BackendCliRequest(BaseModel):
    command: str = Field(..., min_length=1, description="CLI command text")


class BackendCliResponse(BaseModel):
    command: str
    output: str
    ok: bool = True
    timestamp: str
