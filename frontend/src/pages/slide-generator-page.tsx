import { SlideForm } from "@/components/slide/slide-form";
import { useSlideGenerator } from "@/hooks/use-slide-generator";

export function SlideGeneratorPage() {
  const { loading, error, generateSlides } = useSlideGenerator();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-orange-200 bg-white shadow-sm">
        <div className="mx-auto max-w-4xl px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-800">
            <span className="text-orange-500">AI</span> Slide Generator
          </h1>
          <p className="text-sm text-gray-500">
            フォームに入力してスライドを自動生成
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

        <SlideForm onGenerate={generateSlides} loading={loading} />
      </main>
    </div>
  );
}
