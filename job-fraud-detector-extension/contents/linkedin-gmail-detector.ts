// import {Storage} from "@plasmohq/storage"
// export const config  = {
//     matches: ["https://www.linkedin.com/*", "https://mail.google.com/*"]
// }
// const storage = new Storage

// async function detectLinks() {
//     console.log("Detector function called")
//     const platforms = {
//         linkedin: {
//             selector:'.feed-shared-inline-show-more-text, .comments-comment-item__main-content, .msg-s-event-listitem__body',
//             linkFilter: (link:HTMLAnchorElement)=>
//                 !link.href.includes('linkedin.com/feed/update/')
//         },
//         gmail:{
//             selector: 'div.ii.gt',
//             linkFilter: ()=>true
//         }
//     }
//     const currentPlatform = window.location.hostname.includes('linkedin.com')?'linkedin':'gmail'
//     const {selector,linkFilter} = platforms[currentPlatform]

//     const containers = document.querySelectorAll(selector)
//     const links = Array.from(containers)
//         .flatMap(container => Array.from(container.querySelectorAll('a')))
//         .filter(linkFilter)
//         .map(link=>link.href)

//     console.log("Extracted links:",links)
    
//     if (links.length > 0) {
//         try {
//             const validUrls = links.filter(url => {
//                 try {
//                     new URL(url)
//                     return true
//                 } catch {
//                     console.warn(`Invalid URL filtered out: ${url}`)
//                     return false
//                 }
//             })

//             console.log("Validated URLs:", validUrls)

//             // Process URLs one by one
//             const fraudulentUrls: string[] = []
//             for (const url of validUrls) {
//                 try {
//                     const response = await fetch("http://localhost:8000/analyze-job", {
//                         method: 'POST',
//                         headers: {
//                             'Content-Type': 'application/json',
//                         },
//                         body: JSON.stringify({ url: url })
//                     })

//                     if (!response.ok) {
//                         const errorText = await response.text()
//                         console.error(`Server response error: ${response.status}, message: ${errorText}`)
//                         continue
//                     }
                    
//                     const result = await response.json()
//                     console.log("Backend response:", result)

//                     // Mark the link based on classification
//                     const link = Array.from(document.querySelectorAll('a'))
//                         .find(a => a.href === url)
                    
//                     if (link) {
//                         if (result.classification === 'Fraudulent') {
//                             link.style.color = 'red'
//                             link.style.textDecoration = 'line-through'
//                             link.title = 'Warning: Potentially Fraudulent Job'
//                             fraudulentUrls.push(url)
//                         } 
//                         else if(result.classification == "Unrelated"){
//                             link.style.color = 'yellow'
//                             link.title = 'Unrelated url'
//                         }
//                         else {
//                             link.style.color = 'green'
//                             link.title = 'Legitimate Job Posting'
//                         }
//                     }
//                 } catch (urlError) {
//                     console.error(`Error processing URL ${url}:`, urlError)
//                 }
//             }

//             // Store fraudulent jobs count
//             await storage.set('fraudulentJobsCount', fraudulentUrls.length)
//             console.log(`Fraudulent Jobs Count: ${fraudulentUrls.length}`)
        
//         } catch (error) {
//             console.error('Job fraud detection error:', error)
//         }
//     }
// }
        
// // Run detection on page load
// detectLinks()
        
// // Optional: Re-run detection for single-page applications
// const observer = new MutationObserver(detectLinks)
// observer.observe(document.body, { childList: true, subtree: true })

// export {detectLinks}

import {Storage} from "@plasmohq/storage"
export const config  = {
    matches: ["https://www.linkedin.com/*", "https://mail.google.com/*"]
}
const storage = new Storage

const processedUrls = new Set()

async function getUserId() {
    //let userId = await storage.get("userId")
    let userId = "user_123456789"
    if (!userId) {
        userId = "user_" + Math.random().toString(36).substring(2, 15)
        await storage.set("userId", userId)
    }
    return userId
}

async function detectLinks() {
    console.log("Detector function called")
    const platforms = {
        linkedin: {
            selector:'.feed-shared-inline-show-more-text, .comments-comment-item__main-content, .msg-s-event-listitem__body',
            linkFilter: (link:HTMLAnchorElement)=>
                !link.href.includes('linkedin.com/feed/update/')
        },
        gmail:{
            selector: 'div.ii.gt',
            linkFilter: ()=>true
        }
    }
    const currentPlatform = window.location.hostname.includes('linkedin.com')?'linkedin':'gmail'
    const {selector,linkFilter} = platforms[currentPlatform]

    const containers = document.querySelectorAll(selector)
    const links = Array.from(containers)
        .flatMap(container => Array.from(container.querySelectorAll('a')))
        .filter(linkFilter)
        .map(link=>link.href)
        //filter alreadt processed urls
        .filter(url => !processedUrls.has(url))
    console.log("New extracted links:",links)
    
    if (links.length > 0) {
        try {
            const userId = await getUserId()
            const validUrls = links.filter(url => {
                try {
                    new URL(url)
                    return true
                } catch {
                    console.warn(`Invalid URL filtered out: ${url}`)
                    return false
                }
            })

            console.log("New validated URLs:", validUrls)

            // Process URLs one by one
            const fraudulentUrls: string[] = []
            for (const url of validUrls) {
                try {
                    const response = await fetch("http://localhost:8000/analyze-job", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            url : url,
                            user_id : userId
                        })
                    })

                    if (!response.ok) {
                        const errorText = await response.text()
                        console.error(`Server response error: ${response.status}, message: ${errorText}`)
                        continue
                    }
                    
                    const result = await response.json()
                    console.log("Backend response:", result)
                    processedUrls.add(result.url)
                    // Mark the link based on classification
                    const link = Array.from(document.querySelectorAll('a'))
                        .find(a => a.href === url)
                    
                    if (link) {
                        if (result.classification === 'Fraudulent') {
                            link.style.color = 'red'
                            link.style.textDecoration = 'line-through'
                            link.title = 'Warning: Potentially Fraudulent Job'
                            fraudulentUrls.push(url)
                        } 
                        else if(result.classification == "Unrelated"){
                            link.style.color = 'yellow'
                            link.title = 'Unrelated url'
                        }
                        else {
                            link.style.color = 'green'
                            link.title = 'Legitimate Job Posting'
                        }
                    }
                } catch (urlError) {
                    console.error(`Error processing URL ${url}:`, urlError)
                }
            }

            // Store fraudulent jobs count
            await storage.set('fraudulentJobsCount', fraudulentUrls.length)
            console.log(`Fraudulent Jobs Count: ${fraudulentUrls.length}`)
        
        } catch (error) {
            console.error('Job fraud detection error:', error)
        }
    }
}
        
// Run detection on page load
detectLinks()
let debounceTimer

const observer = new MutationObserver(() =>{
    clearTimeout(debounceTimer)
    processedUrls.clear()//clear when DOM changes
    debounceTimer = setTimeout(detectLinks,2000)
})
observer.observe(document.body, { childList: true, subtree: true })

export {detectLinks}