import axios from "axios"
import { API_BASE_URL } from "../config"
axios.defaults.baseURL = API_BASE_URL


export async function startCoreLoopApiCall() {
  try {
    const res = await axios.get<StartLoopResponse>("/start-loop")
    return res.data
  } catch (error) {
    console.error(error)
    return false
  }
}

export async function stopCoreLoopApiCall() {
  try {
    const res = await axios.get<StopLoopResponse>("/start-loop")
    return res.data
  } catch (error) {
    console.error(error)
    return false
  }
}