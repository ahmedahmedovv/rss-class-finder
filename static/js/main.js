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
    // Send to Supabase storage through Flask backend
    fetch('/save-to-supabase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            className: className,
            articles: articles
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create a clickable link to the stored file
            const linkDiv = document.createElement('div');
            linkDiv.className = 'storage-link';
            const link = document.createElement('a');
            link.href = data.url;
            link.target = '_blank';
            link.textContent = 'View Stored Results';
            linkDiv.appendChild(link);
            
            // Find the corresponding class container and append the link
            const classContainers = document.querySelectorAll('.class-container');
            for (const container of classContainers) {
                if (container.querySelector('.class-name').textContent === `Class: ${className}`) {
                    container.querySelector('.class-header').appendChild(linkDiv);
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