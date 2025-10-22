import axiosInstance from '../config/axiosConfig';

/**
 * Fetch ratings for a center
 * @param {String} centerId
 */
export async function fetchRatings(centerId) {
  try {
    const response = await axiosInstance.get(`/api/admin/ratings/center/${centerId}`);
    return response;
  } catch (error) {
    console.error(`Error fetching ratings for center ${centerId}:`, error);
    throw error;
  }
}

/**
 * Delete a rating by ID
 * @param {String} ratingId
 */
export async function deleteRating(ratingId) {
  try {
    const response = await axiosInstance.delete(`/api/admin/ratings/${ratingId}`);
    return response;
  } catch (error) {
    console.error(`Error deleting rating ${ratingId}:`, error);
    throw error;
  }
}
