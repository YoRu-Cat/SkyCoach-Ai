import { expect, test } from "@playwright/test";

const healthyResponse = { status: "healthy" };

const successResponse = {
  task: {
    original_text: "playing soccer",
    cleaned_text: "Playing Soccer",
    activity: "playing soccer",
    classification: "Outdoor",
    confidence: 0.92,
    reasoning: "Detected as outdoor",
    needs_clarification: false,
    issue: null,
    suggested_activity: null,
    suggested_classification: null,
    suggestion_confidence: 0,
  },
  weather: {
    city: "New York",
    country: "US",
    latitude: 40.7128,
    longitude: -74.006,
    temperature: 20,
    feels_like: 19,
    humidity: 55,
    rain_1h: 0,
    is_raining: false,
    wind_speed: 3.2,
    wind_mph: 7.2,
    condition: "Clouds",
    description: "scattered clouds",
    icon_code: "03d",
    units: "metric",
    temp_unit: "°C",
  },
  score_result: {
    score: 84,
    classification: "Outdoor",
    weather_factors: ["No rain"],
    bonuses: [],
    penalties: [],
    recommendation: "Good time for outdoor activity",
  },
  alternatives: [["Cycling", "Great cardio in dry weather"]],
};

test("sends coordinates when geolocation is granted", async ({ page }) => {
  await page.route("**/api/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(healthyResponse),
    });
  });

  await page.addInitScript(() => {
    Object.defineProperty(navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition: (success: any) => {
          success({
            coords: {
              latitude: 40.7128,
              longitude: -74.006,
              accuracy: 12,
              altitude: null,
              altitudeAccuracy: null,
              heading: null,
              speed: null,
              toJSON: () => ({}),
            },
            timestamp: Date.now(),
            toJSON: () => ({}),
          } as any);
        },
      },
    });
  });

  let analyzeBody: Record<string, unknown> | undefined;
  await page.route("**/api/analyze", async (route) => {
    analyzeBody = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(successResponse),
    });
  });

  await page.goto("/");
  await page
    .getByPlaceholder("e.g., playing soccer, doing homework, washing car...")
    .fill("playing soccer");
  await page
    .getByRole("button", { name: "Analyze Activity" })
    .click({ force: true });

  await expect.poll(() => analyzeBody).not.toBeUndefined();
  expect(analyzeBody?.latitude).toBe(40.7128);
  expect(analyzeBody?.longitude).toBe(-74.006);
});

test("falls back to city-only payload when geolocation is denied", async ({
  page,
}) => {
  await page.route("**/api/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(healthyResponse),
    });
  });

  await page.addInitScript(() => {
    Object.defineProperty(navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition: (_success: any, error?: any) => {
          if (error) {
            error({ code: 1, message: "Permission denied" } as any);
          }
        },
      },
    });
  });

  let analyzeBody: Record<string, unknown> | undefined;
  await page.route("**/api/analyze", async (route) => {
    analyzeBody = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(successResponse),
    });
  });

  await page.goto("/");
  await expect(
    page.getByText(
      "Location permission denied or unavailable. Switch to manual location.",
    ),
  ).toBeVisible();

  await page
    .getByPlaceholder("e.g., playing soccer, doing homework, washing car...")
    .fill("playing soccer");
  await page
    .getByRole("button", { name: "Analyze Activity" })
    .click({ force: true });

  await expect.poll(() => analyzeBody).not.toBeUndefined();
  expect(analyzeBody?.latitude).toBeUndefined();
  expect(analyzeBody?.longitude).toBeUndefined();
  expect(analyzeBody?.city).toBe("New York");
});
