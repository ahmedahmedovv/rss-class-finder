function analyzeClasses() {
    // Extract all HTML classes and their content
    const classContent = {};
    const allElements = document.querySelectorAll('*');
    
    allElements.forEach(element => {
        if (element.classList.length > 0) {
            element.classList.forEach(cls => {
                const text = element.textContent.trim();
                if (text) {
                    if (!classContent[cls]) {
                        classContent[cls] = new Set();
                    }
                    classContent[cls].add(text);
                }
            });
        }
    });

    // Convert Sets to Arrays and filter classes
    const filteredContent = {};
    for (const [cls, texts] of Object.entries(classContent)) {
        const articlesArray = Array.from(texts);
        if (articlesArray.length > 1 && 
            articlesArray.every(text => text.split(' ').length > 1)) {
            filteredContent[cls] = articlesArray;
        }
    }

    return filteredContent;
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyze") {
        const results = analyzeClasses();
        sendResponse(results);
    }
}); 