"use client";

import { useEffect, useState } from "react";
import { srsService, SRSReview } from "@/lib/api";
import Layout from "@/components/Layout";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<SRSReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState<Record<number, number>>({});
  const router = useRouter();

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const data = await srsService.getDueReviews(10);
      setReviews(data);
    } catch (error) {
      console.error("Error fetching reviews:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (reviewId: number, ratingValue: number) => {
    try {
      await srsService.rateReview(reviewId, ratingValue);
      toast.success("Review rated successfully!");
      setRating({ ...rating, [reviewId]: ratingValue });
      
      // Remove reviewed item from list after a short delay
      setTimeout(() => {
        setReviews(reviews.filter((r) => r.id !== reviewId));
        setRating({ ...rating, [reviewId]: ratingValue });
      }, 1000);
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Failed to rate review");
    }
  };

  const getRatingLabel = (value: number) => {
    const labels: Record<number, string> = {
      1: "Again - Hard",
      2: "Hard",
      3: "Good",
      4: "Easy",
      5: "Perfect",
    };
    return labels[value] || "";
  };

  const getRatingColor = (value: number) => {
    const colors: Record<number, string> = {
      1: "bg-red-100 text-red-800 hover:bg-red-200",
      2: "bg-orange-100 text-orange-800 hover:bg-orange-200",
      3: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200",
      4: "bg-green-100 text-green-800 hover:bg-green-200",
      5: "bg-blue-100 text-blue-800 hover:bg-blue-200",
    };
    return colors[value] || "";
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

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">SRS Reviews</h1>

        {reviews.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">No reviews due today!</p>
            <p className="text-gray-400 text-sm">
              Great job! You're all caught up with your spaced repetition reviews.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="bg-white rounded-lg shadow p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      {review.problem.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>
                        Difficulty:{" "}
                        <span className="font-medium">{review.problem.difficulty}</span>
                      </span>
                      <span>
                        Repetitions: <span className="font-medium">{review.repetitions}</span>
                      </span>
                      <span>
                        Interval: <span className="font-medium">{review.interval_days} days</span>
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => router.push(`/problems/${review.problem.id}`)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Problem →
                  </button>
                </div>

                {rating[review.id] ? (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
                    <p className="text-green-800 font-semibold">
                      Rated: {getRatingLabel(rating[review.id])}
                    </p>
                    <p className="text-sm text-green-600 mt-1">
                      Next review scheduled based on your rating.
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-600 mb-4">
                      How well did you remember this problem?
                    </p>
                    <div className="grid grid-cols-5 gap-2">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          onClick={() => handleRate(review.id, value)}
                          className={`px-4 py-3 rounded-lg font-medium text-sm transition-colors ${getRatingColor(
                            value
                          )}`}
                        >
                          <div className="font-semibold">{value}</div>
                          <div className="text-xs mt-1">{getRatingLabel(value)}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}

