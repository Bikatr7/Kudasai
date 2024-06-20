(text) => 
{
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'downloaded_text.txt';
    a.click();
    URL.revokeObjectURL(url);
}