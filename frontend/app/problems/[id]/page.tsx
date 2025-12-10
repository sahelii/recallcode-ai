"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { problemService, submissionService, aiService, Problem, Submission } from "@/lib/api";
import Layout from "@/components/Layout";
import dynamic from "next/dynamic";
import toast from "react-hot-toast";

// Dynamically import Monaco Editor (client-side only)
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function ProblemDetailPage() {
  const params = useParams();
  const router = useRouter();
  const problemId = parseInt(params.id as string);
  
  const [problem, setProblem] = useState<Problem | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [hint, setHint] = useState("");

  useEffect(() => {
    fetchData();
  }, [problemId]);

  const fetchData = async () => {
    try {
      const [problemData, submissions] = await Promise.all([
        problemService.getById(problemId),
        submissionService.getAll({ problem: problemId }),
      ]);
      
      setProblem(problemData);
      
      if (submissions.length > 0) {
        const latestSubmission = submissions[0];
        setSubmission(latestSubmission);
        setCode(latestSubmission.code);
        setNotes(latestSubmission.notes);
        setLanguage(latestSubmission.language);
      } else {
        // Default code template
        setCode(getDefaultCode(language));
      }
    } catch (error) {
      console.error("Error fetching problem:", error);
      toast.error("Failed to load problem");
    } finally {
      setLoading(false);
    }
  };

  const getDefaultCode = (lang: string) => {
    const templates: Record<string, string> = {
      python: "def solution():\n    # Your code here\n    pass\n\nsolution()",
      javascript: "function solution() {\n    // Your code here\n}\n\nsolution();",
      java: "public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}",
      cpp: "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}",
    };
    return templates[lang] || templates.python;
  };

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    if (!submission || code === getDefaultCode(language)) {
      setCode(getDefaultCode(newLang));
    }
  };

  const handleSubmit = async () => {
    if (!problem) return;

    try {
      setExecuting(true);
      const submissionData = await problemService.submitCode(
        problemId,
        code,
        language,
        notes
      );
      setSubmission(submissionData);
      toast.success("Code submitted successfully!");
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Failed to submit code");
    } finally {
      setExecuting(false);
    }
  };

  const handleExecute = async () => {
    if (!submission) {
      toast.error("Please submit your code first");
      return;
    }

    try {
      setExecuting(true);
      const result = await problemService.executeCode(
        submission.id,
        code,
        language
      );
      
      if (result.success) {
        toast.success("Code executed successfully!");
        // Refresh submission to get updated results
        const updated = await submissionService.getById(submission.id);
        setSubmission(updated);
      } else {
        toast.error(result.error_message || "Execution failed");
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Failed to execute code");
    } finally {
      setExecuting(false);
    }
  };

  const handleGetHint = async () => {
    if (!problem) return;

    try {
      const hintText = await aiService.generateHint(
        problemId,
        submission?.id
      );
      setHint(hintText);
      setShowHint(true);
    } catch (error: any) {
      toast.error("Failed to generate hint");
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">Loading...</div>
        </div>
      </Layout>
    );
  }

  if (!problem) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">Problem not found</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Problem Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <h1 className="text-2xl font-bold">{problem.title}</h1>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  problem.difficulty === "easy"
                    ? "bg-green-100 text-green-800"
                    : problem.difficulty === "medium"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {problem.difficulty}
              </span>
            </div>

            <div className="prose max-w-none mb-6">
              <p className="whitespace-pre-wrap">{problem.description}</p>
            </div>

            {problem.constraints && (
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Constraints:</h3>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">
                  {problem.constraints}
                </p>
              </div>
            )}

            {problem.examples && problem.examples.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Examples:</h3>
                {problem.examples.map((example: any, idx: number) => (
                  <div key={idx} className="mb-4 p-4 bg-gray-50 rounded">
                    <p className="text-sm">
                      <strong>Input:</strong> {JSON.stringify(example.input)}
                    </p>
                    <p className="text-sm">
                      <strong>Output:</strong> {JSON.stringify(example.output)}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {problem.patterns && problem.patterns.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {problem.patterns.map((pattern, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded"
                  >
                    {pattern}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Code Editor */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Code Editor</h2>
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            </div>

            <div className="mb-4 border rounded-lg overflow-hidden" style={{ height: "400px" }}>
              <MonacoEditor
                height="400px"
                language={language}
                value={code}
                onChange={(value) => setCode(value || "")}
                theme="vs-light"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: "on",
                }}
              />
            </div>

            <div className="flex gap-2 mb-4">
              <button
                onClick={handleSubmit}
                disabled={executing}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {executing ? "Submitting..." : "Submit"}
              </button>
              <button
                onClick={handleExecute}
                disabled={executing || !submission}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {executing ? "Executing..." : "Run"}
              </button>
              <button
                onClick={handleGetHint}
                className="bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700"
              >
                Get Hint
              </button>
            </div>

            {submission && (
              <div className="mb-4 p-4 bg-gray-50 rounded">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Status:</span>{" "}
                    <span
                      className={
                        submission.is_accepted
                          ? "text-green-600 font-semibold"
                          : "text-red-600 font-semibold"
                      }
                    >
                      {submission.is_accepted ? "Accepted" : "Failed"}
                    </span>
                  </div>
                  {submission.runtime && (
                    <div>
                      <span className="text-gray-600">Runtime:</span>{" "}
                      <span className="font-semibold">{submission.runtime}ms</span>
                    </div>
                  )}
                  {submission.memory && (
                    <div>
                      <span className="text-gray-600">Memory:</span>{" "}
                      <span className="font-semibold">{submission.memory}KB</span>
                    </div>
                  )}
                </div>
                {submission.error_message && (
                  <div className="mt-2 text-sm text-red-600">
                    {submission.error_message}
                  </div>
                )}
              </div>
            )}

            {showHint && hint && (
              <div className="mb-4 p-4 bg-purple-50 border border-purple-200 rounded">
                <h3 className="font-semibold mb-2">AI Hint:</h3>
                <p className="text-sm">{hint}</p>
                <button
                  onClick={() => setShowHint(false)}
                  className="mt-2 text-sm text-purple-600 hover:underline"
                >
                  Hide
                </button>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Notes (Markdown):</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Add your notes here..."
              />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

