const form = document.getElementById('uploadForm');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    const response = await fetch('/summarize', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    document.getElementById('summary-box').style.display = 'block';
    document.getElementById('summary-content').innerText = data.summary;
});
