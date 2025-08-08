import axios from "axios"
axios.defaults.baseURL = "http://127.0.0.1:8000"


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