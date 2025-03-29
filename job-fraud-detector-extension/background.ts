import { Storage } from "@plasmohq/storage"

export {}

const storage = new Storage()

chrome.runtime.onInstalled.addListener(() => {
  storage.set('fraudulentJobsCount', 0)
})