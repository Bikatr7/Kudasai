(...texts) =>
{
        console.log("Starting save_to_zip function");
    
        const sectionNames = [
            "Indexed Text", "Indexing Results", "Indexing Debug Log",
            "Preprocessed Text", "Preprocessing Results", "Preprocessing Debug Log",
            "Translated Text", "JE Check Text", "Translator Debug Log",
            "Overall Debug Log", "Error Log"
        ];
    
        texts.forEach((text, index) =>
        {
            console.log(`Processing section: ${sectionNames[index]}`);
            const fileName = `${sectionNames[index].replace(/ /g, '_').toLowerCase()}.txt`;
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            console.log("URL created:", url);
    
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            console.log("Download link created for", fileName);
    
            a.click();
            console.log("Download initiated for", fileName);
    
            URL.revokeObjectURL(url);
            console.log("URL revoked for", fileName);
        });
    
        console.log("save_to_zip function completed");
}