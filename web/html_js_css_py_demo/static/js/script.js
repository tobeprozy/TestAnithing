function sendData() {
    const input1 = document.getElementById('input1').value;
    const input2 = document.getElementById('input2').value;

    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input1, input2 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('output').value = 'Error: ' + data.error;
        } else {
            document.getElementById('output').value = data.result;
        }
    })
    .catch(error => console.error('Error:', error));
}
