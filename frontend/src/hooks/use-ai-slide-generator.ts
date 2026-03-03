import axios from "axios";
import { useState } from "react";

import { ERROR_MESSAGES } from "@/constants/errors";
import { GENERATED_FILENAME } from "@/constants/slide";
import { slideService } from "@/services/slide-service";
import type { AiGenerateResponse } from "@/types/slide";

type AiFlowStep = "input" | "preview";

interface UseAiSlideGeneratorReturn {
  step: AiFlowStep;
  loading: boolean;
  error: string;
  generatedContent: AiGenerateResponse | null;
  generateFromTheme: (theme: string, numSlides: number) => Promise<void>;
  reviseContent: (instruction: string) => Promise<void>;
  downloadPptx: () => Promise<void>;
  resetToInput: () => void;
}

export function useAiSlideGenerator(): UseAiSlideGeneratorReturn {
  const [step, setStep] = useState<AiFlowStep>("input");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [generatedContent, setGeneratedContent] =
    useState<AiGenerateResponse | null>(null);

  const generateFromTheme = async (
    theme: string,
    numSlides: number,
  ): Promise<void> => {
    setLoading(true);
    setError("");

    try {
      const response = await slideService.aiGenerate({
        theme,
        num_slides: numSlides,
      });
      setGeneratedContent(response.data);
      setStep("preview");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(ERROR_MESSAGES.AI_GENERATE_FAILED);
      } else {
        setError(ERROR_MESSAGES.UNKNOWN_ERROR);
      }
    } finally {
      setLoading(false);
    }
  };

  const reviseContent = async (instruction: string): Promise<void> => {
    if (!generatedContent) return;

    setLoading(true);
    setError("");

    try {
      const response = await slideService.aiRevise({
        current_content: generatedContent,
        revision_instruction: instruction,
      });
      setGeneratedContent(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(ERROR_MESSAGES.AI_REVISE_FAILED);
      } else {
        setError(ERROR_MESSAGES.UNKNOWN_ERROR);
      }
    } finally {
      setLoading(false);
    }
  };

  const downloadPptx = async (): Promise<void> => {
    if (!generatedContent) return;

    setLoading(true);
    setError("");

    try {
      const requestData = {
        deck_title: generatedContent.deck_title,
        author: generatedContent.author,
        slides: generatedContent.slides.map((s) => ({
          title: s.title,
          subtitle: s.subtitle,
          content: s.content,
          bullet_points: s.bullet_points,
        })),
      };

      const response = await slideService.generate(requestData);
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = GENERATED_FILENAME;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(ERROR_MESSAGES.GENERATE_SLIDES_FAILED);
      } else {
        setError(ERROR_MESSAGES.UNKNOWN_ERROR);
      }
    } finally {
      setLoading(false);
    }
  };

  const resetToInput = () => {
    setStep("input");
    setGeneratedContent(null);
    setError("");
  };

  return {
    step,
    loading,
    error,
    generatedContent,
    generateFromTheme,
    reviseContent,
    downloadPptx,
    resetToInput,
  };
}
