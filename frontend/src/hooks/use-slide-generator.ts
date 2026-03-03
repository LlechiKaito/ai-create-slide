import axios from "axios";
import { useState } from "react";

import { ERROR_MESSAGES } from "@/constants/errors";
import { GENERATED_FILENAME } from "@/constants/slide";
import { slideService } from "@/services/slide-service";
import type { SlideInput } from "@/types/slide";

interface UseSlideGeneratorReturn {
  loading: boolean;
  error: string;
  generateSlides: (
    deckTitle: string,
    author: string,
    slides: SlideInput[],
  ) => Promise<void>;
}

export function useSlideGenerator(): UseSlideGeneratorReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateSlides = async (
    deckTitle: string,
    author: string,
    slides: SlideInput[],
  ): Promise<void> => {
    setLoading(true);
    setError("");

    try {
      const requestData = {
        deck_title: deckTitle,
        author,
        slides: slides.map((s) => ({
          title: s.title,
          subtitle: s.subtitle,
          content: s.content,
          bullet_points: s.bulletPoints.filter((bp) => bp.trim() !== ""),
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

  return { loading, error, generateSlides };
}
