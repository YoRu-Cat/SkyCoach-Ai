import { useMutation, useQuery } from "react-query";
import {
  analyzeTask,
  getWeather,
  fullAnalysis,
  getAlternatives,
  type AnalysisParams,
} from "@services/api";

export const useAnalyzeTask = () => {
  return useMutation((text: string) => analyzeTask(text));
};

export const useGetWeather = (city: string) => {
  return useQuery(["weather", city], () => getWeather(city), {
    staleTime: 5 * 60 * 1000,
    enabled: !!city,
  });
};

export const useFullAnalysis = () => {
  return useMutation((params: AnalysisParams) => fullAnalysis(params));
};

export const useGetAlternatives = (classification: string | null) => {
  return useQuery(
    ["alternatives", classification],
    () => getAlternatives(classification!),
    {
      staleTime: 10 * 60 * 1000,
      enabled: !!classification,
    },
  );
};
