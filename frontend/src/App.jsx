import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Video,
  MessageSquare,
  Send,
  Loader2,
  CheckCircle,
  User,
  Eye,
  ThumbsUp,
  MessageCircle,
  TrendingUp,
} from "lucide-react";
import axios from "axios";

function App() {
  const [videoA, setVideoA] = useState("");
  const [videoB, setVideoB] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [dbStatus, setDbStatus] = useState("");
  const [extractedData, setExtractedData] = useState(null);

  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isChatting, setIsChatting] = useState(false);

  const handleProcessVideos = async () => {
    if (!videoA || !videoB)
      return alert("Bhai, dono video URLs daalna zaroori hai!");

    setIsProcessing(true);
    setDbStatus("");
    setExtractedData(null);
    setChatHistory([]);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/process-videos",
        {
          video_a_url: videoA,
          video_b_url: videoB,
        },
      );

      setDbStatus(response.data.database.message);

      setExtractedData({
        videoA: response.data.video_a.metadata,
        videoB: response.data.video_b.metadata,
      });
    } catch (error) {
      console.error(error);
      setDbStatus("Error processing videos.");
    }
    setIsProcessing(false);
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !extractedData) return;

    const userMsg = chatInput;
    setChatInput("");
    setChatHistory((prev) => [...prev, { role: "user", text: userMsg }]);
    setIsChatting(true);

    try {
      setChatHistory((prev) => [
        ...prev,
        { role: "ai", text: "", sources: [] },
      ]);

      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          chat_history: chatHistory,
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;

      let aiFullText = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunkText = decoder.decode(value, { stream: true });
          const lines = chunkText
            .split("\n")
            .filter((line) => line.trim() !== "");

          for (const line of lines) {
            const parsed = JSON.parse(line);

            if (parsed.type === "sources") {
              setChatHistory((prev) => {
                const newHistory = [...prev];
                newHistory[newHistory.length - 1].sources = parsed.data;
                return newHistory;
              });
            } else if (parsed.type === "chunk") {
              aiFullText += parsed.data;
              setChatHistory((prev) => {
                const newHistory = [...prev];
                newHistory[newHistory.length - 1].text = aiFullText;
                return newHistory;
              });
            } else if (parsed.type === "error") {
              setChatHistory((prev) => {
                const newHistory = [...prev];
                newHistory[newHistory.length - 1].text =
                  "Error: " + parsed.data;
                return newHistory;
              });
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setChatHistory((prev) => {
        const newHistory = [...prev];
        newHistory[newHistory.length - 1].text = "Error fetching answer.";
        return newHistory;
      });
    }
    setIsChatting(false);
  };
  const renderStatsCard = (title, data) => {
    if (!data) return null;
    return (
      <div className="bg-gray-50 border border-gray-100 p-3 rounded-lg flex-1 overflow-hidden">
        <h3 className="text-xs font-bold text-gray-500 uppercase mb-2">
          {title}
        </h3>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <User className="w-4 h-4 text-blue-500 shrink-0" />
            <span className="truncate w-full" title={data.creator}>
              {data.creator || "Unknown"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <Eye className="w-4 h-4 text-green-500 flex-shrink-0" />
            <span>
              {data.views != null ? data.views.toLocaleString() : "N/A"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <ThumbsUp className="w-4 h-4 text-yellow-500 flex-shrink-0" />
            <span>
              {data.likes != null ? data.likes.toLocaleString() : "N/A"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <MessageCircle className="w-4 h-4 text-purple-500 flex-shrink-0" />
            <span>
              {data.comments != null ? data.comments.toLocaleString() : "N/A"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <TrendingUp className="w-4 h-4 text-orange-500 flex-shrink-0" />
            <span className="font-semibold text-green-600">
              {data.engagement_rate != null
                ? `${data.engagement_rate}%`
                : "N/A"}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen p-8 font-sans text-gray-800">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-600 flex items-center justify-center gap-2">
          <Video className="w-8 h-8 text-red-500" />
          Creator Analytics AI
        </h1>
        <p className="text-gray-500 mt-2">
          Compare videos and generate insights using RAG
        </p>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-4">1. Process Videos</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Video A URL
                </label>
                <input
                  type="text"
                  value={videoA}
                  onChange={(e) => setVideoA(e.target.value)}
                  placeholder="Paste YouTube/Shorts link here..."
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Video B URL
                </label>
                <input
                  type="text"
                  value={videoB}
                  onChange={(e) => setVideoB(e.target.value)}
                  placeholder="Paste YouTube/Shorts link here..."
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <button
                onClick={handleProcessVideos}
                disabled={isProcessing}
                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2 disabled:bg-blue-300"
              >
                {isProcessing ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  "Extract & Build Vector DB"
                )}
              </button>

              {dbStatus && (
                <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 shrink-0" />
                  {dbStatus}
                </div>
              )}
            </div>
          </div>

          {extractedData && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-in fade-in slide-in-from-bottom-2">
              <h2 className="text-sm font-semibold mb-3 text-gray-600">
                Extracted Metadata
              </h2>
              <div className="flex gap-4">
                {renderStatsCard("Video A", extractedData.videoA)}
                {renderStatsCard("Video B", extractedData.videoB)}
              </div>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col h-[600px]">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-500" />
            2. Ask AI
          </h2>

          <div className="flex-1 bg-gray-50 rounded-lg p-4 mb-4 overflow-y-auto border border-gray-100 flex flex-col gap-3">
            {chatHistory.length === 0 ? (
              <div className="text-gray-400 text-center mt-20">
                Process videos first, then ask a question!
              </div>
            ) : (
              chatHistory.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg max-w-[85%] ${
                    msg.role === "user"
                      ? "bg-blue-100 text-blue-900 self-end"
                      : "bg-white border text-gray-800 self-start shadow-sm"
                  }`}
                >
                  <div className="text-sm leading-relaxed text-gray-700">
                    {msg.role === "user" ? (
                      <div>{msg.text}</div>
                    ) : (
                      <div className="flex flex-col gap-2 [&>p]:mb-2">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    )}
                  </div>

                  {msg.role === "ai" &&
                    msg.sources &&
                    msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <span className="text-xs font-semibold text-gray-500">
                          Sources:
                        </span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {msg.sources
                            .filter(
                              (src, index, self) =>
                                index ===
                                self.findIndex(
                                  (t) => t.video_tag === src.video_tag,
                                ),
                            )
                            .map((src, i) => (
                              <span
                                key={i}
                                className="px-2 py-1 bg-gray-100 text-gray-600 text-[10px] rounded-full border"
                              >
                                Video {src.video_tag} ({src.creator})
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                </div>
              ))
            )}
            {isChatting && (
              <div className="text-gray-400 text-sm self-start animate-pulse p-3">
                AI is thinking...
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="e.g., Compare the hooks..."
              disabled={isChatting}
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={!extractedData || isChatting}
              className="bg-gray-800 text-white p-3 rounded-lg hover:bg-gray-900 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
