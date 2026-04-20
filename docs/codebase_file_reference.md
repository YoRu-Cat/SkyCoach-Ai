# Codebase File Reference

This document is generated from current source files and summarizes each file's responsibilities, key symbols, routes, and dependencies.

Total documented source files: 92

## app.py

- Role: Legacy Streamlit application entrypoint and end-to-end runtime flow.
- File size: 1337 lines
- Key symbols:
  - class Config
  - class TaskAnalysis
  - class HistoryEntry
  - class WeatherData
  - class SkyScoreResult
  - function analyze_task_openai
  - function analyze_task_fallback
  - function get_weather
  - function get_weather_by_city
  - function get_demo_weather
  - function calculate_sky_score
  - function inject_custom_css
  - function inject_gsap_animations
  - function render_hero
  - function render_score_gauge
  - function render_weather_card
  - function render_analysis_card
  - function render_factors_card
  - function render_map
  - function render_sidebar
- Primary dependencies/imports:
  - `from app_runtime import main as _run_app`
  - `import streamlit as st`
  - `import time`
  - `from datetime import datetime`
  - `from models.data_classes import Config, HistoryEntry`
  - `from themes.styles import inject_global_styles, inject_component_styles`
  - `from components.gauges import render_hero, render_input_section, render_score_gauge`
  - `from components.cards import (
    render_weather_card,
    render_analysis_card,
    render_factors_card,
    render_mini_forecast,
    render_alternatives
)`

## app_runtime.py

- Role: Primary runtime orchestrator for current Streamlit execution path.
- File size: 173 lines
- Key symbols:
  - function init_session_state
  - function configure_page
  - function main
- Primary dependencies/imports:
  - `import time`
  - `from datetime import datetime`
  - `import streamlit as st`
  - `from components.animations import render_motion_stage`
  - `from components.cards import (
    render_weather_card,
    render_analysis_card,
    render_factors_card,
    render_mini_forecast,
    render_alternatives,
)`
  - `from components.gauges import render_hero, render_input_section, render_score_gauge`
  - `from components.layout import render_sidebar`
  - `from components.responsive import ResponsiveLayout`

## backend/**init**.py

- Role: Module containing application logic.
- File size: 3 lines

## backend/api/**init**.py

- Role: HTTP route handling and request/response orchestration.
- File size: 6 lines
- Primary dependencies/imports:
  - `from backend.api.routes import router`

## backend/api/routes.py

- Role: HTTP route handling and request/response orchestration.
- File size: 542 lines
- API routes:
  - POST /analyze-task
  - POST /weather
  - POST /score
  - POST /alternatives
  - POST /analyze
  - GET /health
  - POST /predict
  - POST /feedback
  - GET /learning-status
  - POST /chat-assistant
  - POST /backend-cli
- Key symbols:
  - function convert_task_to_response
  - function convert_weather_to_response
  - function \_enrich_task_with_ml_suggestions
  - async function analyze_task
  - async function get_weather
  - async function calculate_score
  - async function get_alternatives
  - async function full_analysis
  - async function health_check
  - async function predict_activity_type
  - async function submit_prediction_feedback
  - async function get_learning_status
  - async function chat_assistant
  - async function backend_cli
- Primary dependencies/imports:
  - `from fastapi import APIRouter, HTTPException`
  - `from datetime import datetime, timezone`
  - `import sys`
  - `import os`
  - `import shlex`
  - `from services.ai_engine import (
    analyze_task_smart,
    get_demo_weather,
    get_demo_weather_forecast,
    get_weather,
    get_weather_by_city,
    get_weather_forecast,
    get_weather_forecast_by_city,
)`
  - `from services.maps import render_map`
  - `from services.chat_assistant import chat_assistant_reply`

## backend/main.py

- Role: Module containing application logic.
- File size: 66 lines
- API routes:
  - GET /
- Key symbols:
  - function \_parse_origins
  - async function root
- Primary dependencies/imports:
  - `import os`
  - `from fastapi import FastAPI`
  - `from fastapi.middleware.cors import CORSMiddleware`
  - `from backend.api import router`

## backend/schemas/**init**.py

- Role: Pydantic schema and contract modeling for backend APIs.
- File size: 22 lines
- Primary dependencies/imports:
  - `from .models import (
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    WeatherRequest,
    WeatherResponse,
    SkyScoreRequest,
    SkyScoreResponse,
    AlternativeActivitiesResponse,
)`

## backend/schemas/models.py

- Role: Pydantic schema and contract modeling for backend APIs.
- File size: 169 lines
- Key symbols:
  - class TaskAnalysisRequest
  - class TaskAnalysisResponse
  - class WeatherRequest
  - class WeatherResponse
  - class SkyScoreRequest
  - class FactorDetail
  - class SkyScoreResponse
  - class AlternativeActivitiesResponse
  - class AnalysisRequest
  - class AnalysisResponse
  - class ChatMessage
  - class ChatDraft
  - class ChatAssistantRequest
  - class ChatAssistantResponse
  - class BackendCliRequest
  - class BackendCliResponse
- Primary dependencies/imports:
  - `from pydantic import BaseModel, Field`
  - `from typing import List, Tuple, Optional, Literal`

## components/**init**.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 1 lines

## components/animations.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 341 lines
- Key symbols:
  - function render_motion_stage
  - class ParallaxEffect
- Primary dependencies/imports:
  - `import streamlit as st`
  - `from streamlit.components.v1 import html`

## components/cards.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 112 lines
- Key symbols:
  - function render_weather_card
  - function render_analysis_card
  - function render_factors_card
  - function render_mini_forecast
  - function render_alternatives
- Primary dependencies/imports:
  - `import streamlit as st`
  - `from typing import List, Tuple`
  - `from models.data_classes import WeatherData, TaskAnalysis, SkyScoreResult`
  - `from components.ui import badge, card_start, card_end, metric, separator`

## components/gauges.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 87 lines
- Key symbols:
  - function render_score_gauge
  - function render_hero
  - function render_input_section
- Primary dependencies/imports:
  - `import streamlit as st`
  - `from components.ui import card_start, card_end, badge, separator`

## components/layout.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 218 lines
- Key symbols:
  - function \_init_auto_location
  - function \_render_location_section
  - function render_sidebar
- Primary dependencies/imports:
  - `import json`
  - `import streamlit as st`
  - `from typing import List, Optional`
  - `from components.ui import card_start, card_end, separator`
  - `from models.data_classes import HistoryEntry`
  - `from services.geolocation import (
    auto_detect_location,
    reverse_geocode,
    get_browser_location_js,
    GeoLocation,
)`

## components/responsive.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 342 lines
- Key symbols:
  - class ResponsivePresets
  - class ResponsiveContainers
  - class BreakpointHelper
  - function get_responsive_columns
  - function render_responsive_grid
  - function end_responsive_grid
  - class ResponsiveLayout
  - function responsive_columns
- Primary dependencies/imports:
  - `import streamlit as st`

## components/ui.py

- Role: Streamlit rendering components and UI utility functions.
- File size: 58 lines
- Key symbols:
  - function card_start
  - function card_end
  - function badge
  - function metric
  - function section_title
  - function separator
- Primary dependencies/imports:
  - `import streamlit as st`
  - `from typing import Iterable, Optional`

## core/**init**.py

- Role: Core scoring and pipeline logic shared across execution paths.
- File size: 1 lines

## core/pipeline.py

- Role: Core scoring and pipeline logic shared across execution paths.
- File size: 32 lines
- Key symbols:
  - class PluginPipeline
- Primary dependencies/imports:
  - `from typing import Any, Iterable, List`

## core/scoring_engine.py

- Role: Core scoring and pipeline logic shared across execution paths.
- File size: 337 lines
- Key symbols:
  - function \_requires_travel
  - function calculate_sky_score
  - function get_alternative_activities
  - function \_score_slot_for_task
  - function recommend_best_schedule
- Primary dependencies/imports:
  - `from typing import List, Tuple, Optional`
  - `from datetime import datetime, timedelta`
  - `import re`
  - `from models.data_classes import TaskAnalysis, WeatherData, SkyScoreResult, Config`

## frontend/src/App.tsx

- Role: Module containing application logic.
- File size: 133 lines
- Key symbols:
  - function App
- Primary dependencies/imports:
  - `import { useState, useEffect } from "react";`
  - `import { QueryClient, QueryClientProvider } from "react-query";`
  - `import { API_BASE_URL, healthCheck } from "@services/api";`
  - `import AppShell from "@components/AppShell";`
  - `import "@styles/globals.css";`

## frontend/src/components/ActivityInput.tsx

- Role: Reusable UI components and presentation logic.
- File size: 270 lines
- Primary dependencies/imports:
  - `import { useEffect, useState } from "react";`
  - `import { usePreferredCity } from "@hooks/usePreferredCity";`

## frontend/src/components/AlternativesCard.tsx

- Role: Reusable UI components and presentation logic.
- File size: 35 lines

## frontend/src/components/AnalysisResult.tsx

- Role: Reusable UI components and presentation logic.
- File size: 75 lines
- Primary dependencies/imports:
  - `import { useEffect, useRef } from "react";`
  - `import { gsap } from "gsap";`
  - `import type { AnalysisResponse } from "@app-types/api";`
  - `import TaskCard from "./TaskCard";`
  - `import WeatherCard from "./WeatherCard";`
  - `import ScoreCard from "./ScoreCard";`
  - `import AlternativesCard from "./AlternativesCard";`

## frontend/src/components/AppShell.tsx

- Role: Reusable UI components and presentation logic.
- File size: 436 lines
- Key symbols:
  - type/interface AppView
- Primary dependencies/imports:
  - `import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";`
  - `import {`
  - `import { motion } from "framer-motion";`
  - `import { gsap } from "gsap";`
  - `import "locomotive-scroll/dist/locomotive-scroll.css";`
  - `import Dashboard from "../pages/Dashboard";`
  - `import TodoPage from "../pages/TodoPage";`
  - `import TimetablePage from "../pages/TimetablePage";`

## frontend/src/components/Header.tsx

- Role: Reusable UI components and presentation logic.
- File size: 24 lines

## frontend/src/components/index.ts

- Role: Reusable UI components and presentation logic.
- File size: 10 lines
- Primary dependencies/imports:
  - `export { default as Header } from "./Header";`
  - `export { default as ActivityInput } from "./ActivityInput";`
  - `export { default as AnalysisResult } from "./AnalysisResult";`
  - `export { default as TaskCard } from "./TaskCard";`
  - `export { default as WeatherCard } from "./WeatherCard";`
  - `export { default as ScoreCard } from "./ScoreCard";`
  - `export { default as AlternativesCard } from "./AlternativesCard";`
  - `export { default as ScoreGauge } from "./ScoreGauge";`

## frontend/src/components/ParticlesComponent.tsx

- Role: Reusable UI components and presentation logic.
- File size: 106 lines
- Primary dependencies/imports:
  - `import Particles, { initParticlesEngine } from "@tsparticles/react";`
  - `import { useEffect, useMemo, useState } from "react";`
  - `import { loadSlim } from "@tsparticles/slim";`

## frontend/src/components/ScoreCard.tsx

- Role: Reusable UI components and presentation logic.
- File size: 162 lines
- Primary dependencies/imports:
  - `import type { SkyScoreResult } from "@app-types/api";`
  - `import ScoreGauge from "@components/ScoreGauge";`

## frontend/src/components/ScoreGauge.tsx

- Role: Reusable UI components and presentation logic.
- File size: 54 lines
- Primary dependencies/imports:
  - `import { useEffect, useMemo, useState } from "react";`
  - `import { gsap } from "gsap";`

## frontend/src/components/TaskCard.tsx

- Role: Reusable UI components and presentation logic.
- File size: 219 lines
- Primary dependencies/imports:
  - `import type { TaskAnalysis } from "@app-types/api";`

## frontend/src/components/WeatherBackground.tsx

- Role: Reusable UI components and presentation logic.
- File size: 75 lines
- Primary dependencies/imports:
  - `import type { WeatherData } from "@app-types/api";`

## frontend/src/components/WeatherCard.tsx

- Role: Reusable UI components and presentation logic.
- File size: 152 lines
- Primary dependencies/imports:
  - `import type { WeatherData } from "@app-types/api";`
  - `import { CircleMarker, MapContainer, TileLayer, Tooltip } from "react-leaflet";`

## frontend/src/hooks/useApi.ts

- Role: React hooks for API access, persistence, and state behavior.
- File size: 35 lines
- Key symbols:
  - const useAnalyzeTask
  - const useGetWeather
  - const useFullAnalysis
  - const useGetAlternatives
- Primary dependencies/imports:
  - `import { useMutation, useQuery } from "react-query";`
  - `import {`

## frontend/src/hooks/usePreferredCity.ts

- Role: React hooks for API access, persistence, and state behavior.
- File size: 89 lines
- Key symbols:
  - type/interface LocationMode
  - type/interface StoredLocation
  - const usePreferredCity
- Primary dependencies/imports:
  - `import { useCallback, useEffect, useState } from "react";`

## frontend/src/hooks/useTaskStore.ts

- Role: React hooks for API access, persistence, and state behavior.
- File size: 504 lines
- Key symbols:
  - type/interface RingtonePreset
  - const useTaskStore
  - type/interface TaskStore
- Primary dependencies/imports:
  - `import { useEffect, useMemo, useRef, useState } from "react";`
  - `import type { TaskCategory, UserTask } from "@app-types/tasks";`
  - `import {`

## frontend/src/main.tsx

- Role: Module containing application logic.
- File size: 11 lines
- Primary dependencies/imports:
  - `import React from "react";`
  - `import ReactDOM from "react-dom/client";`
  - `import App from "./App";`
  - `import "leaflet/dist/leaflet.css";`

## frontend/src/pages/ChatPage.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 244 lines
- Primary dependencies/imports:
  - `import { useEffect, useRef, useState } from "react";`
  - `import type { ChatDraft, ChatMessage } from "@app-types/api";`
  - `import type { TaskStore } from "@hooks/useTaskStore";`
  - `import { chatAssistant } from "@services/api";`

## frontend/src/pages/Dashboard.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 166 lines
- Primary dependencies/imports:
  - `import { useEffect, useRef, useState } from "react";`
  - `import { gsap } from "gsap";`
  - `import { useFullAnalysis } from "@hooks/useApi";`
  - `import ActivityInput from "@components/ActivityInput";`
  - `import AnalysisResult from "@components/AnalysisResult";`
  - `import Header from "@components/Header";`
  - `import WeatherBackground from "@components/WeatherBackground";`
  - `import { usePreferredCity } from "@hooks/usePreferredCity";`

## frontend/src/pages/HomePage.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 565 lines
- Primary dependencies/imports:
  - `import { useEffect, useMemo, useRef, useState } from "react";`
  - `import {`
  - `import type { ChatDraft, ChatMessage } from "@app-types/api";`
  - `import type { TaskStore } from "@hooks/useTaskStore";`
  - `import { chatAssistant, runBackendCliCommand } from "@services/api";`

## frontend/src/pages/PlannerPage.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 363 lines
- Primary dependencies/imports:
  - `import { useEffect, useMemo } from "react";`
  - `import { useQuery } from "react-query";`
  - `import type { WeatherData } from "@app-types/api";`
  - `import type { TaskCategory, UserTask, WeekForecastDay } from "@app-types/tasks";`
  - `import { useGetWeather } from "@hooks/useApi";`
  - `import { usePreferredCity } from "@hooks/usePreferredCity";`
  - `import { fullAnalysis } from "@services/api";`
  - `import { buildLocalScheduledAt } from "@utils/taskScheduling";`

## frontend/src/pages/TimetablePage.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 118 lines
- Primary dependencies/imports:
  - `import { useMemo } from "react";`
  - `import { CalendarDays, Clock3 } from "lucide-react";`
  - `import type { TaskStore } from "@hooks/useTaskStore";`

## frontend/src/pages/TodoPage.tsx

- Role: Top-level view/page composition for user-facing flows.
- File size: 294 lines
- Primary dependencies/imports:
  - `import { useMemo, useState } from "react";`
  - `import { Check, Plus, Trash2 } from "lucide-react";`
  - `import type { TaskStore } from "@hooks/useTaskStore";`

## frontend/src/services/api.ts

- Role: Frontend service adapters and backend communication clients.
- File size: 126 lines
- Key symbols:
  - type/interface AnalysisParams
  - const API_BASE_URL
  - const analyzeTask
  - const getWeather
  - const fullAnalysis
  - const getAlternatives
  - const healthCheck
  - const chatAssistant
  - const runBackendCliCommand
- Primary dependencies/imports:
  - `import axios from "axios";`
  - `import type {`

## frontend/src/styles/globals.css

- Role: Module containing application logic.
- File size: 1543 lines

## frontend/src/types/api.ts

- Role: TypeScript type contracts used across frontend modules.
- File size: 110 lines
- Key symbols:
  - type/interface TaskAnalysis
  - type/interface WeatherData
  - type/interface SkyScoreResult
  - type/interface FactorDetail
  - type/interface AnalysisResponse
  - type/interface ChatRole
  - type/interface ChatMessage
  - type/interface ChatDraft
  - type/interface ChatTaskContext
  - type/interface ChatNavigateTo
  - type/interface ChatAssistantResponse
  - type/interface BackendCliResponse

## frontend/src/types/tasks.ts

- Role: TypeScript type contracts used across frontend modules.
- File size: 30 lines
- Key symbols:
  - type/interface UserTask
  - type/interface TaskCategory
  - type/interface WeekForecastDay
  - type/interface SequencedTask

## frontend/src/utils/taskScheduling.ts

- Role: Module containing application logic.
- File size: 72 lines
- Key symbols:
  - const buildLocalScheduledAt
  - const parseScheduledAt
  - const formatScheduledDate
  - const formatScheduledTime
  - const reserveNextAvailableSlot
- Primary dependencies/imports:
  - `import type { UserTask } from "@app-types/tasks";`

## frontend/src/vite-env.d.ts

- Role: Module containing application logic.
- File size: 2 lines

## ml_system/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/api.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 189 lines
- Key symbols:
  - class MLSystem
  - function get_ml_system
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from pathlib import Path`
  - `from ml_system.config.settings import CONFIG`
  - `from ml_system.schemas import PredictionRequest`
  - `from ml_system.inference.engine import InferenceEngine`
  - `from ml_system.learning.orchestrator import LearningOrchestrator`
  - `from ml_system.training.trainer import Trainer`
  - `from ml_system.pipelines.ingestion.pipeline import IngestionConfig, IngestionPipeline`

## ml_system/config/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/config/settings.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 55 lines
- Key symbols:
  - class MLSystemConfig
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from pathlib import Path`

## ml_system/data/datasets/generate_large_dataset.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 362 lines
- Key symbols:
  - function generate_activity_descriptions
  - function create_balanced_splits
  - function save_splits_to_jsonl
  - function print_dataset_summary
- Primary dependencies/imports:
  - `import json`
  - `import random`
  - `from pathlib import Path`
  - `from collections import defaultdict`

## ml_system/data/datasets/generate_massive_dataset.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 279 lines
- Key symbols:
  - function \_clean_space
  - function typo_noise
  - function grammar_noise
  - function make_base_phrase
  - function expand_variants
  - function generate_records
  - function split_records
  - function write_jsonl
  - function main
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import argparse`
  - `import json`
  - `import random`
  - `import re`
  - `from pathlib import Path`
  - `from typing import Dict, List`

## ml_system/inference/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/inference/engine.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 119 lines
- Key symbols:
  - function load_tokenizer_from_json
  - function load_model_from_json
  - function load_report_from_json
  - class InferenceEngine
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `import math`
  - `from pathlib import Path`
  - `from ml_system.config.settings import CONFIG`
  - `from ml_system.schemas import PredictionRequest, PredictionResponse`
  - `from ml_system.training.tokenizer import Tokenizer`
  - `from ml_system.training.models import NaiveBayesModel, LinearSoftmaxModel`

## ml_system/learning/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/learning/drift_monitor.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 76 lines
- Key symbols:
  - class DriftMonitor
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from datetime import datetime`

## ml_system/learning/feedback_store.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 81 lines
- Key symbols:
  - class FeedbackStore
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from ml_system.schemas import PredictionFeedback, UncertainPrediction`

## ml_system/learning/model_versioning.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 78 lines
- Key symbols:
  - class ModelVersionRegistry
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from datetime import datetime, timezone`

## ml_system/learning/orchestrator.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 208 lines
- Key symbols:
  - class ContinuousLearningEngine
  - class LearningOrchestrator
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from datetime import datetime, timezone`
  - `from pathlib import Path`
  - `from ml_system.config.settings import CONFIG`
  - `from ml_system.schemas import PredictionFeedback, UncertainPrediction`
  - `from .drift_monitor import DriftMonitor`
  - `from .feedback_store import FeedbackStore`

## ml_system/learning/retrainer.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 88 lines
- Key symbols:
  - class LearningRetrainer
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from .feedback_store import FeedbackStore`
  - `from .model_versioning import ModelVersionRegistry`

## ml_system/pipelines/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/pipelines/annotation/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/pipelines/annotation/schema.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 60 lines
- Key symbols:
  - class AnnotationRecord
  - class ResolvedRecord
  - function utc_now_iso
  - function normalize_phrase
  - function validate_annotation_row
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from datetime import datetime, timezone`
  - `import re`
  - `from typing import Any`

## ml_system/pipelines/annotation/workflow.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 145 lines
- Key symbols:
  - class AnnotationConfig
  - class AnnotationReport
  - class AnnotationWorkflow
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `import hashlib`
  - `import json`
  - `from pathlib import Path`
  - `from typing import Iterable`
  - `from .schema import AnnotationRecord, normalize_phrase, validate_annotation_row`

## ml_system/pipelines/ingestion/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/pipelines/ingestion/adapters.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 33 lines
- Key symbols:
  - class SourceAdapter
  - class InMemoryAdapter
  - class JsonlFileAdapter
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from typing import Iterable, Protocol`

## ml_system/pipelines/ingestion/pipeline.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 89 lines
- Key symbols:
  - class IngestionConfig
  - class IngestionReport
  - class IngestionPipeline
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `import hashlib`
  - `import json`
  - `from pathlib import Path`
  - `from typing import Iterable`
  - `from .schema import RawPhraseRecord, normalize_phrase, validate_raw_record`

## ml_system/pipelines/ingestion/schema.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 79 lines
- Key symbols:
  - class SourceInfo
  - class RawPhraseRecord
  - function normalize_phrase
  - function utc_now_iso
  - function \_is_valid_url
  - function validate_raw_record
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from datetime import datetime, timezone`
  - `import re`
  - `from typing import Any`

## ml_system/pipelines/quality/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/pipelines/quality/pipeline.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 150 lines
- Key symbols:
  - class QualityConfig
  - class QualityReport
  - class QualityPipeline
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from collections import Counter, defaultdict`
  - `import hashlib`
  - `import json`
  - `from pathlib import Path`
  - `from difflib import SequenceMatcher`
  - `from typing import Iterable`

## ml_system/pipelines/quality/schema.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 110 lines
- Key symbols:
  - class QualitySource
  - class QualityRecord
  - function utc_now_iso
  - function normalize_phrase
  - function validate_quality_record
  - function is_noise_phrase
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from datetime import datetime, timezone`
  - `import re`
  - `from typing import Any`

## ml_system/schemas.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 127 lines
- Key symbols:
  - class RawPhraseRecord
  - class QualityRecord
  - class AnnotatedRecord
  - class TrainingRecord
  - class PredictionRequest
  - class PredictionResponse
  - class PredictionFeedback
  - class UncertainPrediction
  - class ModelVersion
  - class TrainingReport
  - class DriftMetrics
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from typing import Optional`

## ml_system/training/**init**.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 1 lines

## ml_system/training/models.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 154 lines
- Key symbols:
  - class NaiveBayesModel
  - class LinearSoftmaxModel
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from collections import Counter`
  - `import math`

## ml_system/training/tokenizer.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 86 lines
- Key symbols:
  - class Tokenizer
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import re`
  - `from collections import Counter`
  - `import math`

## ml_system/training/trainer.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 234 lines
- Key symbols:
  - function load_dataset
  - function split_xy
  - function accuracy_score
  - function macro_f1_score
  - class Trainer
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `import json`
  - `from pathlib import Path`
  - `from ml_system.config.settings import CONFIG`
  - `from .tokenizer import Tokenizer`
  - `from .models import NaiveBayesModel, LinearSoftmaxModel`

## ml_system/validate_structure.py

- Role: ML system training, inference, feedback, and pipeline internals.
- File size: 127 lines
- Primary dependencies/imports:
  - `import os`
  - `import sys`
  - `from pathlib import Path`

## models/**init**.py

- Role: Shared dataclasses and domain model definitions.
- File size: 1 lines

## models/data_classes.py

- Role: Shared dataclasses and domain model definitions.
- File size: 95 lines
- Key symbols:
  - class Config
  - class TaskAnalysis
  - class HistoryEntry
  - class WeatherData
  - class SkyScoreResult
- Primary dependencies/imports:
  - `from dataclasses import dataclass, field`
  - `from typing import Literal, Optional, List`

## plugins/**init**.py

- Role: Plugin contracts and extension points for text processing/quality.
- File size: 1 lines

## plugins/normalization.py

- Role: Plugin contracts and extension points for text processing/quality.
- File size: 17 lines
- Key symbols:
  - class InputNormalizationPlugin
- Primary dependencies/imports:
  - `import re`

## plugins/quality.py

- Role: Plugin contracts and extension points for text processing/quality.
- File size: 13 lines
- Key symbols:
  - class ScoreSafetyPlugin

## plugins/registry.py

- Role: Plugin contracts and extension points for text processing/quality.
- File size: 11 lines
- Key symbols:
  - function get_default_plugins
- Primary dependencies/imports:
  - `from plugins.normalization import InputNormalizationPlugin`
  - `from plugins.quality import ScoreSafetyPlugin`

## services/**init**.py

- Role: Business logic services used by API and UI layers.
- File size: 1 lines

## services/ai_engine.py

- Role: Business logic services used by API and UI layers.
- File size: 862 lines
- Key symbols:
  - function \_extract_word_units
  - function \_token_semantic_analysis
  - function \_stable_fallback_coords
  - function \_resolve_demo_city_coords
  - function \_count_keyword_matches
  - function \_score_keyword_matches
  - function \_detect_input_issue
  - function \_has_word_overlap
  - function \_apply_auto_judge_resolution
  - function \_openai_json_response
  - function \_verify_openai_classification
  - function analyze_task_openai
  - function analyze_task_fallback
  - function analyze_task_smart
  - function get_weather
  - function get_weather_by_city
  - function \_format_slot_time_range
  - function get_weather_forecast
  - function get_weather_forecast_by_city
  - function get_demo_weather_forecast
- Primary dependencies/imports:
  - `import hashlib`
  - `import os`
  - `import re`
  - `import requests`
  - `import json`
  - `from datetime import datetime, timedelta`
  - `from typing import Optional`
  - `from models.data_classes import WeatherData, TaskAnalysis, Config`

## services/auto_judge.py

- Role: Business logic services used by API and UI layers.
- File size: 457 lines
- Key symbols:
  - function \_normalize
  - function \_tokenize
  - function \_content_tokens
  - function \_phrase_variants
  - function \_build_token_priors
  - function \_fetch_runtime_slang_context
  - function \_token_prior_votes
  - function classify_with_dictionary
  - function calculate_similarity
  - function extract_words
  - function \_looks_broken_for_suggestion
  - function suggest_activity
  - function auto_judge_input
- Primary dependencies/imports:
  - `import re`
  - `from functools import lru_cache`
  - `from difflib import SequenceMatcher, get_close_matches`
  - `import requests`
  - `from typing import Optional, Tuple`

## services/chat_assistant.py

- Role: Business logic services used by API and UI layers.
- File size: 553 lines
- Key symbols:
  - function \_normalize_space
  - function \_normalize_typos
  - function \_normalize_text
  - function \_parse_time
  - function \_parse_part_of_day
  - function \_parse_date
  - function \_extract_task
  - function \_extract_notes
  - function \_is_yes
  - function \_is_no
  - function \_resolve_task_target
  - function \_detect_control_intent
  - function \_detect_navigation_target
  - function \_infer_pending_intent
  - function \_should_use_local_controller
  - function \_base_response
  - function \_local_assistant_response
  - function chat_assistant_reply
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from datetime import datetime, timedelta`
  - `from difflib import get_close_matches`
  - `import json`
  - `import os`
  - `import re`
  - `from typing import Any, Optional`

## services/geolocation.py

- Role: Business logic services used by API and UI layers.
- File size: 166 lines
- Key symbols:
  - class GeoLocation
  - function detect_location_by_ip
  - function reverse_geocode
  - function get_browser_location_js
  - function auto_detect_location
- Primary dependencies/imports:
  - `import requests`
  - `from dataclasses import dataclass`
  - `from typing import Optional`

## services/maps.py

- Role: Business logic services used by API and UI layers.
- File size: 93 lines
- Key symbols:
  - function render_map
  - function display_map_section
- Primary dependencies/imports:
  - `import folium`
  - `from folium.plugins import Fullscreen, MiniMap, MousePosition`
  - `from streamlit_folium import st_folium`
  - `import streamlit as st`
  - `from models.data_classes import WeatherData`

## services/task_classifier_ml.py

- Role: Business logic services used by API and UI layers.
- File size: 204 lines
- Key symbols:
  - class ModelInfo
  - class PredictionResult
  - function \_normalize_text
  - function \_activity_variants
  - function \_build_training_set
  - function \_build_pipeline
  - function \_candidate_models
  - function \_trained_ensemble
  - function predict_task_label
  - function model_summary
- Primary dependencies/imports:
  - `from __future__ import annotations`
  - `from dataclasses import dataclass`
  - `from functools import lru_cache`
  - `import re`
  - `from typing import Literal, cast`
  - `from sklearn.decomposition import TruncatedSVD`
  - `from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier`
  - `from sklearn.feature_extraction.text import TfidfVectorizer`

## utils/**init**.py

- Role: Shared utility functions and package wiring.
- File size: 1 lines

End of reference.
