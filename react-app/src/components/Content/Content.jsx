import "./Content.css"

export default function Content( {mainContent, bigCard, mainContentRef, dataLoaded, lotCount} )
{   
    const handleDownload = async () => {
        // console.log(dataLoaded);
        try {
            const response = await fetch("/uploaded", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(dataLoaded),
            });
            const csv = await response.text();
            console.log(csv);
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.href = url;
            link.download = 'data.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Освобождаем URL
            URL.revokeObjectURL(url);
            // const result = await response.json();
        }
        catch (error) {
            console.error('Ошибка:', error);
        } finally {}
    }
    return(
        <div className="main-content" ref={mainContentRef}>
            {bigCard}
            {dataLoaded != "li" ? 
                <div className="content-header">
                    <div className="all-lot-count">
                        Всего лотов: {lotCount}
                    </div>
                
                    <button className="downloadBtn" onClick={handleDownload}>
                        Скачать CSV
                    </button>
                
                </div>
            : ""}
            
            {mainContent}
            
        </div>
    );
}