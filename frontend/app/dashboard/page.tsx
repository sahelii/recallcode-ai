"use client";

import { useEffect, useState } from "react";
import { dailyPlanService, problemService } from "@/lib/api";
import { DailyPlan, Problem } from "@/lib/api";
import Link from "next/link";
import Layout from "@/components/Layout";

export default function DashboardPage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const planData = await dailyPlanService.getToday();
        setPlan(planData);
        
        // Fetch problem details for plan
        if (planData.problems && planData.problems.length > 0) {
          const problemDetails = await Promise.all(
            planData.problems.map((id: number) => problemService.getById(id))
          );
          setProblems(problemDetails);
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">Today's Plan</h1>
        
        {plan && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-2">SRS Reviews</h2>
              <p className="text-3xl font-bold text-blue-600">{plan.srs_problems.length}</p>
              <p className="text-sm text-gray-500 mt-2">Problems to review</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-2">New Problems</h2>
              <p className="text-3xl font-bold text-green-600">{plan.new_problems.length}</p>
              <p className="text-sm text-gray-500 mt-2">New problems to solve</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-2">Progress</h2>
              <p className="text-3xl font-bold text-purple-600">
                {plan.completed_problems.length} / {plan.problems.length}
              </p>
              <p className="text-sm text-gray-500 mt-2">Completed today</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Today's Problems</h2>
          </div>
          <div className="p-6">
            {problems.length === 0 ? (
              <p className="text-gray-500">No problems in today's plan. Start by adding problems!</p>
            ) : (
              <div className="space-y-4">
                {problems.map((problem) => (
                  <Link
                    key={problem.id}
                    href={`/problems/${problem.id}`}
                    className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-lg">{problem.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">{problem.description.substring(0, 100)}...</p>
                      </div>
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
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

