import { useCallback, useEffect, useState } from "react";

const USER_LOCATION_STORAGE_KEY = "skycoach_user_location_v1";
const DEFAULT_CITY = "New York";

export type LocationMode = "auto" | "manual";

export interface StoredLocation {
  city: string;
  latitude?: number;
  longitude?: number;
  mode: LocationMode;
}

const defaultLocation: StoredLocation = {
  city: DEFAULT_CITY,
  mode: "auto",
};

const readStoredLocation = (): StoredLocation => {
  if (typeof window === "undefined") {
    return defaultLocation;
  }

  const value = window.localStorage.getItem(USER_LOCATION_STORAGE_KEY);
  if (!value) {
    return defaultLocation;
  }

  try {
    const parsed = JSON.parse(value) as StoredLocation;
    const city = parsed.city?.trim() || DEFAULT_CITY;
    const mode = parsed.mode === "manual" ? "manual" : "auto";
    return {
      city,
      latitude: parsed.latitude,
      longitude: parsed.longitude,
      mode,
    };
  } catch {
    return defaultLocation;
  }
};

export const usePreferredCity = () => {
  const [location, setLocationState] = useState<StoredLocation>(() =>
    readStoredLocation(),
  );

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const normalized: StoredLocation = {
      city: location.city.trim() || DEFAULT_CITY,
      latitude: location.latitude,
      longitude: location.longitude,
      mode: location.mode,
    };

    window.localStorage.setItem(
      USER_LOCATION_STORAGE_KEY,
      JSON.stringify(normalized),
    );
  }, [location]);

  const setCity = useCallback((nextCity: string) => {
    setLocationState((prev) => ({ ...prev, city: nextCity }));
  }, []);

  const setLocation = useCallback((next: Partial<StoredLocation>) => {
    setLocationState((prev) => ({ ...prev, ...next }));
  }, []);

  const clearLocation = useCallback(() => {
    setLocationState(defaultLocation);
  }, []);

  return {
    city: location.city,
    setCity,
    location,
    setLocation,
    clearLocation,
    defaultCity: DEFAULT_CITY,
  };
};
