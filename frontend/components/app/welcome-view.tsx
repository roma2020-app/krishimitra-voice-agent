import { Button } from "@/components/ui/button";

function WelcomeImage() {
  return (
    <div className="flex justify-center">
      <img
        src="/krishi-logo.png"
        alt="Krishi Mitra"
        className="h-32 w-32 rounded-full shadow-xl"
      />
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<"div"> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="flex min-h-screen flex-col items-center justify-center bg-[url('/farm-bg.jpg')] bg-cover bg-center p-6"
    >
      <div className="max-w-4xl rounded-3xl border border-green-200 bg-white/80 p-10 text-center shadow-2xl backdrop-blur-md">

        <WelcomeImage />

        <h1 className="mt-6 text-5xl font-bold text-green-700">
          🌾 Krishi Mitra
        </h1>

        <h2 className="mt-3 text-2xl font-semibold text-green-900">
          AI Voice Assistant for Indian Farmers
        </h2>

        <p className="mt-4 text-lg text-gray-700">
          Get instant help with weather forecasts, crop diseases,
          market prices and government schemes using your voice.
        </p>

        {/* Feature Cards */}
        <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-4">

         <div className="rounded-xl bg-green-50 p-5 shadow-lg hover:bg-green-100 hover:scale-105 transition-all duration-300">
            <div className="text-3xl">🌦️</div>
             <p className="mt-3 text-lg font-bold text-green-800">Weather </p> <p className="mt-1 text-sm text-gray-600">
    Live forecasts & rain alerts
  </p>
          </div>

          <div className="rounded-xl bg-green-50 p-5 shadow-lg hover:bg-green-100 hover:scale-105 transition-all duration-300">
            <div className="text-3xl">🌱</div>
            <p className="mt-3 text-lg font-bold text-green-800">Crop Advice</p><p className="mt-2 text-sm text-gray-600">
    Get AI-powered recommendations for healthy crop growth.
  </p>
          </div>

          <div className="rounded-xl bg-green-50 p-5 shadow-lg hover:bg-green-100 hover:scale-105 transition-all duration-300">
            <div className="text-3xl">💰</div>
            <p className="mt-3 text-lg font-bold text-green-800">Market Prices</p><p className="mt-2 text-sm text-gray-600">
    Check today's mandi prices and market trends instantly.
  </p>
          </div>

          <div className="rounded-xl bg-green-50 p-5 shadow-lg hover:bg-green-100 hover:scale-105 transition-all duration-300">
            <div className="text-3xl">🏛️</div>
            <p className="mt-3 text-lg font-bold text-green-800">Govt Schemes</p> <p className="mt-2 text-sm text-gray-600">
    Explore subsidies, loans and farmer welfare programs.
  </p>
          </div>

        </div>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-12 w-80 rounded-full bg-green-700 hover:bg-green-800 text-white text-lg font-bold shadow-xl"
        >
          {startButtonText}
        </Button>

        <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer"className="dashboard-button">
              👨‍🌾 Dashboard
               </a>

      </div>

      <p className="mt-8 rounded-full bg-black/40 px-5 py-2 text-sm text-white">
        Powered by Murf Falcon • LiveKit • Google Gemini
      </p>

    </div>
  );
};
