import { BrowserRouter, Routes, Route } from "react-router-dom";

import { NotFoundPage } from "@/pages/not-found-page";
import { SlideGeneratorPage } from "@/pages/slide-generator-page";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SlideGeneratorPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
