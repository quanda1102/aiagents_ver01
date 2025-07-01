import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Gửi request chat đến backend
 * @param {Object} payload Dữ liệu người dùng nhập
 * @returns {Promise<Object>} Phản hồi từ server
 */
export const sendChatRequest = async (payload) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, payload);
    return response.data;
  } catch (error) {
    // Trả về lỗi chi tiết từ backend nếu có
    if (error.response?.data) {
      throw error.response.data;
    }
    throw new Error("Something went wrong when calling the chat API.");
  }
};
