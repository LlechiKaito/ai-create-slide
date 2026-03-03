import { useState } from "react";

import { ERROR_MESSAGES } from "@/constants/errors";

interface RevisionFormProps {
  onRevise: (instruction: string) => Promise<void>;
  onDownload: () => Promise<void>;
  onReset: () => void;
  loading: boolean;
}

export function RevisionForm({
  onRevise,
  onDownload,
  onReset,
  loading,
}: RevisionFormProps) {
  const [instruction, setInstruction] = useState("");
  const [validationError, setValidationError] = useState("");

  const handleRevise = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError("");

    if (!instruction.trim()) {
      setValidationError(ERROR_MESSAGES.EMPTY_REVISION);
      return;
    }

    await onRevise(instruction);
    setInstruction("");
  };

  return (
    <div className="space-y-4" data-testid="revision-form">
      <form onSubmit={handleRevise} className="space-y-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            修正内容を入力
          </label>
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
            rows={3}
            placeholder="例: 3枚目のスライドにもっと具体例を追加してください"
            data-testid="revision-input"
          />
        </div>

        {validationError && (
          <div
            className="rounded-md bg-red-50 p-3 text-sm text-red-600"
            data-testid="revision-validation-error"
          >
            {validationError}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-orange-500 px-6 py-2 font-bold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:bg-gray-400"
          data-testid="revise-button"
        >
          {loading ? "AIが修正中..." : "AIに修正を依頼"}
        </button>
      </form>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onDownload}
          disabled={loading}
          className="flex-1 rounded-md bg-green-600 px-6 py-2 font-bold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-400"
          data-testid="download-button"
        >
          {loading ? "ダウンロード中..." : "この内容でダウンロード"}
        </button>
        <button
          type="button"
          onClick={onReset}
          disabled={loading}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed"
          data-testid="reset-button"
        >
          最初からやり直す
        </button>
      </div>
    </div>
  );
}
