document.getElementById('analyze').addEventListener('click', async () => {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value;
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const results = await response.json();
        
        if (response.ok) {
            displayResults(results);
        } else {
            alert(`Error: ${results.error}`);
        }
    } catch (error) {
        alert('Error analyzing page: ' + error);
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    for (const [cls, articles] of Object.entries(results)) {
        const classContainer = document.createElement('div');
        classContainer.className = 'class-container';
        
        const header = document.createElement('div');
        header.className = 'class-header';
        
        const classInfo = document.createElement('div');
        classInfo.className = 'class-info';
        classInfo.innerHTML = `
            <div class="class-name">Class: ${cls}</div>
            <div class="stats">Number of articles: ${articles.length}</div>
        `;
        
        const exportButton = document.createElement('button');
        exportButton.className = 'export-button';
        exportButton.textContent = 'Export to JSON';
        exportButton.onclick = () => exportClass(cls, articles);
        
        header.appendChild(classInfo);
        header.appendChild(exportButton);
        classContainer.appendChild(header);
        
        articles.forEach(article => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'article';
            articleDiv.textContent = article;
            classContainer.appendChild(articleDiv);
        });
        
        resultsDiv.appendChild(classContainer);
    }
}

function exportClass(className, articles) {
    // Get base URL from the input field
    const baseUrl = new URL(document.getElementById('urlInput').value).origin;
    
    fetch('/save-to-supabase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            className: className,
            articles: articles,
            baseUrl: baseUrl
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create a container for both RSS and storage links
            const linkDiv = document.createElement('div');
            linkDiv.className = 'storage-link';
            
            // RSS Feed Link
            const rssLink = document.createElement('a');
            rssLink.href = data.url;
            rssLink.target = '_blank';
            rssLink.innerHTML = '<img src="/static/img/rss-icon.png" alt="RSS" class="rss-icon"> Subscribe to RSS Feed';
            
            // Storage URL Link
            const storageLink = document.createElement('a');
            storageLink.href = data.url;
            storageLink.target = '_blank';
            storageLink.className = 'storage-url';
            storageLink.textContent = `Storage URL: ${data.url}`;
            
            // Add both links to container
            linkDiv.appendChild(rssLink);
            linkDiv.appendChild(document.createElement('br'));
            linkDiv.appendChild(storageLink);
            
            // Find the corresponding class container and append the links
            const classContainers = document.querySelectorAll('.class-container');
            for (const container of classContainers) {
                if (container.querySelector('.class-name').textContent === `Class: ${className}`) {
                    const header = container.querySelector('.class-header');
                    // Remove existing links if any
                    const existingLink = header.querySelector('.storage-link');
                    if (existingLink) {
                        existingLink.remove();
                    }
                    header.appendChild(linkDiv);
                    break;
                }
            }
        } else {
            alert('Error saving to storage');
        }
    })
    .catch(error => {
        alert('Error saving to storage: ' + error);
    });
} 