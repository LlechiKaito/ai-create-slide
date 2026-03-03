import { RevisionForm } from "@/components/ai-slide/revision-form";
import { SlidePreview } from "@/components/ai-slide/slide-preview";
import { ThemeInputForm } from "@/components/ai-slide/theme-input-form";
import { useAiSlideGenerator } from "@/hooks/use-ai-slide-generator";

export function SlideGeneratorPage() {
  const {
    step,
    loading,
    error,
    generatedContent,
    generateFromTheme,
    reviseContent,
    downloadPptx,
    resetToInput,
  } = useAiSlideGenerator();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-orange-200 bg-white shadow-sm">
        <div className="mx-auto max-w-4xl px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-800">
            <span className="text-orange-500">AI</span> Slide Generator
          </h1>
          <p className="text-sm text-gray-500">
            テーマを入力するだけでAIがスライドを自動生成
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-8">
        {error && (
          <div
            className="mb-6 rounded-md bg-red-50 p-4 text-red-600"
            data-testid="error-message"
          >
            {error}
          </div>
        )}

        {step === "input" && (
          <ThemeInputForm
            onGenerate={generateFromTheme}
            loading={loading}
          />
        )}

        {step === "preview" && generatedContent && (
          <div className="space-y-6">
            <SlidePreview content={generatedContent} />
            <RevisionForm
              onRevise={reviseContent}
              onDownload={downloadPptx}
              onReset={resetToInput}
              loading={loading}
            />
          </div>
        )}
      </main>
    </div>
  );
}
