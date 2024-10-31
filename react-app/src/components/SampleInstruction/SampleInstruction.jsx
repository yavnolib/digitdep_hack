import "./SampleInstruction.css"
export default function SampleInstruction() {
    const handleDownload = async () => {
        try {
            const response = await fetch('/sample', {
                method: 'GET',
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'Загрузочный файл - Шаблон.xlsx'); // Имя файла для загрузки
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error downloading the file:", error);
        }
    };
    return(
        <div className="sample">
            Для просмотра статистики по лотам загрузите файл по <button onClick={handleDownload} className="sample-link" href="/sample">следующему образцу</button>.
        </div>
    );
}