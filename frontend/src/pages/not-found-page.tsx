import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="mb-4 text-6xl font-bold text-orange-500">404</h1>
        <p className="mb-6 text-lg text-gray-600">
          ページが見つかりません
        </p>
        <Link
          to="/"
          className="rounded-md bg-orange-500 px-6 py-2 text-white hover:bg-orange-600"
        >
          トップへ戻る
        </Link>
      </div>
    </div>
  );
}
